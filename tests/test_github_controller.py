import json
import os
import unittest
from unittest.mock import Mock, patch

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QByteArray, QObject, QSize, Signal
from PySide6.QtGui import QGuiApplication
from PySide6.QtNetwork import QNetworkReply, QNetworkRequest
from keyring.errors import KeyringError

from src.github_controller import (
    ACCOUNT, DEVICE_URL, SERVICE, GitHubController, GitHubQrProvider,
)


class FakeReply(QObject):
    finished = Signal()

    def __init__(self, body=b'{"ok": true}', status=200):
        super().__init__()
        self.body = body
        self.status = status

    def attribute(self, attribute):
        return self.status

    def error(self):
        return QNetworkReply.NoError

    def readAll(self):
        return QByteArray(self.body)

    def abort(self):
        self.finished.emit()


class GitHubControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def setUp(self):
        with patch.dict(os.environ, {"SELF_CARE_GITHUB_CLIENT_ID": "client-id"}):
            with patch("src.github_controller.QTimer.singleShot"):
                self.controller = GitHubController()
        self.controller._post = Mock()

    def tearDown(self):
        self.controller._poll_timer.stop()
        self.controller._refresh_timer.stop()

    def start_signin(self):
        controller = self.controller
        controller.connectGitHub()
        self.assertEqual(controller._post.call_args.args[1], {
            "client_id": "client-id", "scope": "",
        })
        controller._device_response({
            "device_code": "device",
            "user_code": "ABCD-1234",
            "interval": 5,
            "expires_in": 900,
            "verification_uri": DEVICE_URL,
        }, "")

    def test_default_client_id_starts_device_signin_without_configuration(self):
        with patch.dict(os.environ, {}, clear=True):
            with patch("src.github_controller.QTimer.singleShot"):
                controller = GitHubController()
        controller._post = Mock()

        controller.connectGitHub()

        self.assertEqual(controller._post.call_args.args[1], {
            "client_id": "Ov23liEf6GF5YVJ4QaOb", "scope": "",
        })
        controller._device_response({
            "device_code": "device",
            "user_code": "ABCD-1234",
            "interval": 5,
            "expires_in": 900,
            "verification_uri": DEVICE_URL,
        }, "")
        self.assertEqual(controller.userCode, "ABCD-1234")
        controller._poll_timer.stop()

    def test_signin_polls_and_restores_saved_token(self):
        self.start_signin()
        controller = self.controller
        self.assertEqual(controller.userCode, "ABCD-1234")
        self.assertEqual(controller._poll_timer.interval(), 5000)
        controller._poll()
        self.assertEqual(controller._post.call_args.args[1], {
            "client_id": "client-id", "device_code": "device",
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
        })
        controller._token_response({"error": "authorization_pending"}, "")
        self.assertTrue(controller._poll_timer.isActive())
        controller._token_response({"error": "slow_down", "interval": 10}, "")
        self.assertEqual(controller._poll_timer.interval(), 10000)
        with patch("src.github_controller.keyring.set_password") as save:
            controller._token_response({"access_token": "saved", "scope": ""}, "")
        save.assert_called_once_with(SERVICE, ACCOUNT, "saved")
        self.assertTrue(controller.connected)
        self.assertEqual(controller.userCode, "")
        self.assertEqual(controller._post.call_args.args[3], "saved")

        with patch("src.github_controller.keyring.get_password", return_value="saved"):
            with patch("src.github_controller.QTimer.singleShot"):
                restored = GitHubController()
            restored._post = Mock()
            restored._restore()
        self.assertTrue(restored.connected)
        self.assertEqual(restored._post.call_args.args[3], "saved")
        restored._refresh_timer.stop()

    def test_disconnect_cancels_and_removes_token(self):
        controller = self.controller
        controller._token = "saved"
        controller._login = "tester"
        controller._weeks = [{"contributionDays": []}]
        controller._reply = Mock()
        with patch("src.github_controller.keyring.delete_password") as delete:
            controller.disconnectGitHub()
        delete.assert_called_once_with(SERVICE, ACCOUNT)
        self.assertFalse(controller.connected)
        self.assertEqual(controller.weeks, [])
        self.assertEqual(controller.login, "")
        self.assertEqual(controller._generation, 1)

    def test_keyring_failure_does_not_claim_signin_or_disconnect(self):
        self.start_signin()
        with patch("src.github_controller.keyring.set_password", side_effect=KeyringError("locked")):
            self.controller._token_response({"access_token": "saved", "scope": ""}, "")
        self.assertFalse(self.controller.connected)
        self.assertIn("keyring", self.controller.status)
        self.controller._token = "saved"
        with patch("src.github_controller.keyring.delete_password", side_effect=KeyringError("locked")):
            self.controller.disconnectGitHub()
        self.assertTrue(self.controller.connected)
        self.assertIn("Could not remove", self.controller.status)

    def test_rejects_unexpected_scopes_incomplete_tokens_and_bad_device_url(self):
        for response in (
            {"access_token": "saved", "scope": "repo"},
            {"access_token": "saved", "scope": "", "expires_in": 28800},
            {"access_token": "saved", "scope": "", "expires_in": None},
            {"access_token": "saved", "scope": None},
        ):
            with self.subTest(response=response):
                self.start_signin()
                with patch("src.github_controller.keyring.set_password") as save:
                    self.controller._token_response(response, "")
                save.assert_not_called()
                self.assertFalse(self.controller.connected)
                self.assertFalse(self.controller.busy)
        self.controller.connectGitHub()
        self.controller._device_response({
            "device_code": "device", "user_code": "ABCD-1234",
            "interval": 5, "expires_in": 900, "verification_uri": "https://example.com",
        }, "")
        self.assertEqual(self.controller.userCode, "")
        self.assertFalse(self.controller.busy)

    def test_expiring_tokens_are_saved_and_refreshed_after_restart(self):
        self.start_signin()
        with patch("src.github_controller.time.time", return_value=1000):
            with patch("src.github_controller.keyring.set_password") as save:
                self.controller._token_response({
                    "access_token": "access-one", "scope": "",
                    "refresh_token": "refresh-one", "expires_in": 3600,
                }, "")
        stored = json.loads(save.call_args.args[2])
        self.assertEqual(stored, {
            "access_token": "access-one", "refresh_token": "refresh-one",
            "expires_at": 4600, "client_id": "client-id",
        })
        self.assertTrue(self.controller.connected)

        with patch("src.github_controller.QTimer.singleShot"):
            restored = GitHubController()
        restored._post = Mock()
        with patch("src.github_controller.keyring.get_password", return_value=json.dumps(stored)):
            with patch("src.github_controller.time.time", return_value=4600):
                restored._restore()
        self.assertEqual(restored._post.call_args.args[1], {
            "client_id": "client-id", "grant_type": "refresh_token",
            "refresh_token": "refresh-one",
        })
        with patch("src.github_controller.time.time", return_value=4600):
            with patch("src.github_controller.keyring.set_password") as save:
                restored._refresh_token_response({
                    "access_token": "access-two", "scope": "",
                    "refresh_token": "refresh-two", "expires_in": 3600,
                }, "")
        rotated = json.loads(save.call_args.args[2])
        self.assertEqual(rotated["access_token"], "access-two")
        self.assertEqual(rotated["refresh_token"], "refresh-two")
        self.assertEqual(rotated["expires_at"], 8200)
        self.assertEqual(restored._post.call_args.args[3], "access-two")
        restored._refresh_timer.stop()

    def test_refresh_storage_failure_keeps_rotated_tokens_for_retry(self):
        controller = self.controller
        controller._token = "old-access"
        controller._refresh_token = "old-refresh"
        controller._token_client_id = "client-id"
        controller._busy = True
        with patch("src.github_controller.keyring.set_password", side_effect=KeyringError("locked")):
            controller._refresh_token_response({
                "access_token": "new-access", "scope": "",
                "refresh_token": "new-refresh", "expires_in": 3600,
            }, "")
        self.assertTrue(controller.connected)
        self.assertTrue(controller._credentials_dirty)
        self.assertIn("Retry before closing", controller.status)
        with patch("src.github_controller.keyring.set_password") as save:
            controller.refresh()
        stored = json.loads(save.call_args.args[2])
        self.assertEqual(stored["refresh_token"], "new-refresh")
        self.assertFalse(controller._credentials_dirty)
        self.assertEqual(controller._post.call_args.args[3], "new-access")

    def test_bad_refresh_token_requires_signin_again(self):
        self.controller._busy = True
        self.controller._refresh_timer.start()
        self.controller._refresh_token_response({"error": "bad_refresh_token"}, "")
        self.assertFalse(self.controller.busy)
        self.assertFalse(self.controller._refresh_timer.isActive())
        self.assertIn("Disconnect and sign in again", self.controller.status)

    def test_bad_refresh_token_http_error_is_reported_as_expired(self):
        controller = self.controller
        del controller._post
        controller._network = Mock()
        reply = FakeReply(body=b'{"error":"bad_refresh_token"}', status=400)
        controller._network.post.return_value = reply
        controller._token = "old-access"
        controller._refresh_token = "old-refresh"
        controller._token_client_id = "client-id"
        controller._access_expires_at = 1
        controller.refresh()
        reply.finished.emit()
        self.assertIn("Disconnect and sign in again", controller.status)
        self.assertFalse(controller.busy)

    def test_anonymized_private_counts_are_displayed(self):
        calendar = {
            "totalContributions": 5,
            "weeks": [{"contributionDays": []}],
        }
        self.controller._contributions_response({"data": {"viewer": {
            "login": "tester",
            "contributionsCollection": {
                "hasAnyRestrictedContributions": True,
                "contributionCalendar": calendar,
            },
        }}}, "")
        self.assertEqual(self.controller.weeks, calendar["weeks"])
        self.assertEqual(self.controller.total, 5)
        self.assertEqual(
            self.controller.status,
            "Contribution activity for the past year.",
        )

    def test_missing_client_id_and_network_errors_are_visible(self):
        self.controller._client_id = ""
        self.controller.connectGitHub()
        self.assertIn("SELF_CARE_GITHUB_CLIENT_ID", self.controller.status)
        self.controller._client_id = "client-id"
        self.controller.connectGitHub()
        self.controller._device_response(None, "Network error")
        self.assertFalse(self.controller.busy)
        self.assertEqual(self.controller.status, "Network error")

    def test_expired_code_stops_polling(self):
        self.start_signin()
        self.controller._expires_at = 0
        self.controller._post.reset_mock()
        self.controller._poll()
        self.controller._post.assert_not_called()
        self.assertFalse(self.controller.busy)
        self.assertEqual(self.controller.userCode, "")
        self.assertIn("expired", self.controller.status)

    def test_qr_provider_returns_readable_image(self):
        provider = GitHubQrProvider()
        size = QSize()
        image = provider.requestImage("qr", size, QSize())
        self.assertEqual(image.size(), size)
        self.assertGreater(size.width(), 20)
        self.assertEqual(image.pixelColor(0, 0).name(), "#ffffff")
        self.assertEqual(image.pixelColor(4, 4).name(), "#000000")

    def test_network_request_encodes_body_and_ignores_cancelled_reply(self):
        controller = self.controller
        del controller._post
        reply = FakeReply()
        controller._network = Mock()
        controller._network.post.return_value = reply
        callback = Mock()
        controller._post("https://github.com/login/device/code", {
            "client_id": "client-id", "scope": "",
        }, callback)
        request, body = controller._network.post.call_args.args
        self.assertEqual(request.url().toString(), "https://github.com/login/device/code")
        self.assertEqual(body, b"client_id=client-id&scope=")
        self.assertEqual(
            request.attribute(QNetworkRequest.RedirectPolicyAttribute),
            QNetworkRequest.ManualRedirectPolicy,
        )
        reply.finished.emit()
        callback.assert_called_once_with({"ok": True}, "")

        reply2 = FakeReply()
        controller._network.post.return_value = reply2
        callback.reset_mock()
        controller._post("https://api.github.com/graphql", {"query": "query"}, callback, "saved")
        request, body = controller._network.post.call_args.args
        self.assertEqual(bytes(request.rawHeader("Authorization")), b"Bearer saved")
        controller.disconnectGitHub()
        callback.assert_not_called()
