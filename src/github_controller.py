import json
import math
import os
import time
from urllib.parse import urlencode

import keyring
import qrcode
from keyring.errors import KeyringError
from PySide6.QtCore import Property, QObject, QTimer, QUrl, Signal, Slot
from PySide6.QtGui import QColor, QImage
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest
from PySide6.QtQuick import QQuickImageProvider


DEVICE_URL = "https://github.com/login/device"
DEFAULT_CLIENT_ID = "Ov23liEf6GF5YVJ4QaOb"
SERVICE = "Self-Care-Tasks GitHub"
ACCOUNT = "oauth-token"
QUERY = """
query {
  viewer {
    login
    contributionsCollection {
      hasAnyRestrictedContributions
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date weekday contributionCount contributionLevel } }
      }
    }
  }
}
"""


class GitHubQrProvider(QQuickImageProvider):
    def __init__(self):
        super().__init__(QQuickImageProvider.Image)
        qr = qrcode.QRCode(border=4)
        qr.add_data(DEVICE_URL)
        qr.make(fit=True)
        matrix = qr.get_matrix()
        self.image = QImage(len(matrix), len(matrix), QImage.Format_RGB32)
        for y, row in enumerate(matrix):
            for x, black in enumerate(row):
                self.image.setPixelColor(x, y, QColor("black" if black else "white"))

    def requestImage(self, image_id, size, requested_size):
        if size is not None:
            size.setWidth(self.image.width())
            size.setHeight(self.image.height())
        return self.image


class GitHubController(QObject):
    changed = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._client_id = os.environ.get(
            "SELF_CARE_GITHUB_CLIENT_ID", DEFAULT_CLIENT_ID
        ).strip()
        self._token = ""
        self._refresh_token = ""
        self._token_client_id = ""
        self._access_expires_at = 0
        self._credentials_dirty = False
        self._login = ""
        self._weeks = []
        self._total = 0
        self._status = "Connect GitHub to see your contributions."
        self._user_code = ""
        self._device_code = ""
        self._interval = 5
        self._expires_at = 0
        self._busy = False
        self._generation = 0
        self._reply = None
        self._network = QNetworkAccessManager(self)
        self._poll_timer = QTimer(self)
        self._poll_timer.setSingleShot(True)
        self._poll_timer.timeout.connect(self._poll)
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setInterval(15 * 60 * 1000)
        self._refresh_timer.timeout.connect(self.refresh)
        QTimer.singleShot(0, self._restore)

    @Property(bool, notify=changed)
    def connected(self):
        return bool(self._token)

    @Property(bool, notify=changed)
    def busy(self):
        return self._busy

    @Property(str, notify=changed)
    def status(self):
        return self._status

    @Property(str, notify=changed)
    def userCode(self):
        return self._user_code

    @Property(str, notify=changed)
    def login(self):
        return self._login

    @Property(int, notify=changed)
    def total(self):
        return self._total

    @Property("QVariantList", notify=changed)
    def weeks(self):
        return self._weeks

    def _restore(self):
        try:
            saved = keyring.get_password(SERVICE, ACCOUNT) or ""
        except (KeyringError, OSError, RuntimeError) as error:
            self._status = "System keyring unavailable: " + str(error)
            self.changed.emit()
            return
        if saved.startswith("{"):
            try:
                credentials = json.loads(saved)
                token = credentials["access_token"]
                refresh_token = credentials["refresh_token"]
                client_id = credentials["client_id"]
                expires_at = credentials["expires_at"]
                if (not isinstance(token, str) or not token
                        or not isinstance(refresh_token, str) or not refresh_token
                        or not isinstance(client_id, str) or not client_id
                        or isinstance(expires_at, bool)
                        or not isinstance(expires_at, (int, float))
                        or not math.isfinite(expires_at) or expires_at <= 0):
                    raise ValueError("Invalid saved credentials")
                self._token = token
                self._refresh_token = refresh_token
                self._token_client_id = client_id
                self._access_expires_at = expires_at
            except (KeyError, TypeError, ValueError):
                self._status = "Saved GitHub sign-in is invalid. Please connect again."
        else:
            self._token = saved
        if self._token:
            self._refresh_timer.start()
            self.refresh()
        else:
            self.changed.emit()

    def _save_credentials(self):
        if self._refresh_token:
            saved = json.dumps({
                "access_token": self._token,
                "refresh_token": self._refresh_token,
                "client_id": self._token_client_id,
                "expires_at": self._access_expires_at,
            })
        else:
            saved = self._token
        keyring.set_password(SERVICE, ACCOUNT, saved)
        self._credentials_dirty = False

    def _read_token_response(self, data, require_refresh=False):
        token = data.get("access_token")
        if not isinstance(token, str) or not token:
            raise ValueError("GitHub sign-in failed or expired. Please try again.")
        if "scope" not in data or not isinstance(data["scope"], str):
            raise ValueError("GitHub did not report the granted permissions. Please sign in again.")
        if data["scope"] != "":
            raise ValueError(
                "GitHub returned unexpected permissions. Revoke the app's authorization "
                "in GitHub and try again."
            )
        expires_in = data.get("expires_in")
        refresh_token = data.get("refresh_token")
        if ("expires_in" not in data and "refresh_token" not in data
                and not require_refresh):
            return token, "", 0
        if (isinstance(expires_in, bool) or not isinstance(expires_in, int)
                or expires_in <= 0 or not isinstance(refresh_token, str)
                or not refresh_token):
            raise ValueError("GitHub returned incomplete token information. Please sign in again.")
        return token, refresh_token, time.time() + expires_in

    def _post(self, url, payload, callback, token=None):
        request = QNetworkRequest(QUrl(url))
        request.setRawHeader(b"Accept", b"application/json")
        request.setRawHeader(b"User-Agent", b"Self-Care-Tasks")
        request.setAttribute(
            QNetworkRequest.RedirectPolicyAttribute,
            QNetworkRequest.ManualRedirectPolicy,
        )
        request.setTransferTimeout(15000)
        if token:
            request.setRawHeader(b"Authorization", ("Bearer " + token).encode())
            request.setHeader(QNetworkRequest.ContentTypeHeader, "application/json")
            body = json.dumps(payload).encode()
        else:
            request.setHeader(
                QNetworkRequest.ContentTypeHeader, "application/x-www-form-urlencoded"
            )
            body = urlencode(payload).encode()
        generation = self._generation
        reply = self._network.post(request, body)
        self._reply = reply

        def finished():
            if self._reply is reply:
                self._reply = None
            try:
                if generation != self._generation:
                    return
                status = reply.attribute(QNetworkRequest.HttpStatusCodeAttribute)
                if reply.error() != QNetworkReply.NoError or not status or not 200 <= status < 300:
                    if status == 400 and url == "https://github.com/login/oauth/access_token":
                        try:
                            data = json.loads(bytes(reply.readAll()))
                        except (ValueError, UnicodeDecodeError):
                            data = None
                        if isinstance(data, dict) and data.get("error") == "bad_refresh_token":
                            callback(data, "")
                            return
                    callback(None, "GitHub request failed. Check your connection or sign in again.")
                    return
                try:
                    data = json.loads(bytes(reply.readAll()))
                    if not isinstance(data, dict):
                        raise ValueError("Expected an object")
                except (ValueError, UnicodeDecodeError):
                    callback(None, "GitHub returned an invalid response.")
                    return
                callback(data, "")
            finally:
                reply.deleteLater()

        reply.finished.connect(finished)

    @Slot()
    def connectGitHub(self):
        if self._busy or self._token:
            return
        if not self._client_id:
            self._status = "Set SELF_CARE_GITHUB_CLIENT_ID to your OAuth app's client ID."
            self.changed.emit()
            return
        self._busy = True
        self._status = "Requesting a GitHub sign-in code..."
        self.changed.emit()
        self._post(
            "https://github.com/login/device/code",
            {"client_id": self._client_id, "scope": ""},
            self._device_response,
        )

    def _device_response(self, data, error):
        if error:
            self._finish_signin(error)
            return
        try:
            device_code = data["device_code"]
            user_code = data["user_code"]
            interval = int(data["interval"])
            expires = int(data["expires_in"])
            if (not isinstance(device_code, str) or not device_code
                    or not isinstance(user_code, str) or not user_code
                    or interval <= 0 or expires <= 0
                    or data["verification_uri"] != DEVICE_URL):
                raise ValueError("Invalid device response")
        except (KeyError, TypeError, ValueError):
            self._finish_signin("GitHub could not start device sign-in. Check your OAuth app settings.")
            return
        self._device_code = device_code
        self._user_code = user_code
        self._interval = interval
        self._expires_at = time.monotonic() + expires
        self._status = "Scan the code and enter the code shown here on GitHub."
        self.changed.emit()
        self._schedule_poll()

    def _schedule_poll(self):
        if time.monotonic() + self._interval >= self._expires_at:
            self._finish_signin("The sign-in code expired. Please try again.")
            return
        self._poll_timer.start(self._interval * 1000)

    def _poll(self):
        if time.monotonic() >= self._expires_at:
            self._finish_signin("The sign-in code expired. Please try again.")
            return
        self._post(
            "https://github.com/login/oauth/access_token",
            {
                "client_id": self._client_id,
                "device_code": self._device_code,
                "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            },
            self._token_response,
        )

    def _token_response(self, data, error):
        if error:
            self._finish_signin(error)
            return
        reason = data.get("error")
        if reason in ("authorization_pending", "slow_down"):
            if reason == "slow_down":
                self._interval += 5
                if isinstance(data.get("interval"), int):
                    self._interval = max(self._interval, data["interval"])
            self._schedule_poll()
            return
        try:
            token, refresh_token, expires_at = self._read_token_response(data)
        except ValueError as error:
            self._finish_signin(str(error))
            return
        self._token = token
        self._refresh_token = refresh_token
        self._token_client_id = self._client_id
        self._access_expires_at = expires_at
        try:
            self._save_credentials()
        except (KeyringError, OSError, RuntimeError) as error:
            self._token = ""
            self._refresh_token = ""
            self._token_client_id = ""
            self._access_expires_at = 0
            self._finish_signin("Could not save GitHub sign-in in the system keyring: " + str(error))
            return
        self._finish_signin("Connected. Loading contributions...")
        self._refresh_timer.start()
        self.refresh()

    def _finish_signin(self, status):
        self._poll_timer.stop()
        self._device_code = ""
        self._user_code = ""
        self._busy = False
        self._status = status
        self.changed.emit()

    @Slot()
    def refresh(self):
        if not self._token or self._busy:
            return
        if self._credentials_dirty:
            try:
                self._save_credentials()
            except (KeyringError, OSError, RuntimeError) as error:
                self._status = "Could not save refreshed GitHub sign-in. Retry before closing the app: " + str(error)
                self.changed.emit()
                return
        self._busy = True
        if self._refresh_token and time.time() >= self._access_expires_at - 300:
            self._status = "Refreshing GitHub sign-in..."
            self.changed.emit()
            self._post(
                "https://github.com/login/oauth/access_token",
                {
                    "client_id": self._token_client_id,
                    "grant_type": "refresh_token",
                    "refresh_token": self._refresh_token,
                },
                self._refresh_token_response,
            )
            return
        self._load_contributions()

    def _refresh_token_response(self, data, error):
        if error:
            self._busy = False
            self._status = error
            self.changed.emit()
            return
        if data.get("error") == "bad_refresh_token":
            self._busy = False
            self._refresh_timer.stop()
            self._status = "GitHub sign-in has expired. Disconnect and sign in again."
            self.changed.emit()
            return
        try:
            token, refresh_token, expires_at = self._read_token_response(
                data, require_refresh=True
            )
        except ValueError as error:
            self._busy = False
            self._status = str(error) + " Disconnect and sign in again."
            self.changed.emit()
            return
        self._token = token
        self._refresh_token = refresh_token
        self._access_expires_at = expires_at
        self._credentials_dirty = True
        try:
            self._save_credentials()
        except (KeyringError, OSError, RuntimeError) as error:
            self._busy = False
            self._status = "Could not save refreshed GitHub sign-in. Retry before closing the app: " + str(error)
            self.changed.emit()
            return
        self._load_contributions()

    def _load_contributions(self):
        self._status = "Loading GitHub contributions..."
        self.changed.emit()
        self._post(
            "https://api.github.com/graphql",
            {"query": QUERY},
            self._contributions_response,
            self._token,
        )

    def _contributions_response(self, data, error):
        self._busy = False
        if error:
            self._status = error
        else:
            try:
                if data.get("errors"):
                    raise ValueError("GraphQL error")
                viewer = data["data"]["viewer"]
                collection = viewer["contributionsCollection"]
                if collection["hasAnyRestrictedContributions"]:
                    self._login = viewer["login"]
                    self._weeks = []
                    self._total = 0
                    self._status = (
                        "Your public GitHub profile includes private contribution counts. "
                        "Turn off private contributions on your GitHub profile to show public-only activity."
                    )
                else:
                    calendar = collection["contributionCalendar"]
                    self._login = viewer["login"]
                    self._total = calendar["totalContributions"]
                    self._weeks = calendar["weeks"]
                    self._status = "Public contribution activity for the past year."
            except (KeyError, TypeError, ValueError):
                self._status = "GitHub could not load contributions. Please try again."
        self.changed.emit()

    @Slot()
    def disconnectGitHub(self):
        if self._token:
            try:
                keyring.delete_password(SERVICE, ACCOUNT)
            except (KeyringError, OSError, RuntimeError) as error:
                self._status = "Could not remove GitHub sign-in from the system keyring: " + str(error)
                self.changed.emit()
                return
        self._generation += 1
        if self._reply:
            self._reply.abort()
            self._reply = None
        self._poll_timer.stop()
        self._refresh_timer.stop()
        self._token = ""
        self._refresh_token = ""
        self._token_client_id = ""
        self._access_expires_at = 0
        self._credentials_dirty = False
        self._login = ""
        self._weeks = []
        self._total = 0
        self._finish_signin("Disconnected from GitHub on this device.")
