import shutil
import socket
import subprocess

from PySide6.QtCore import Property, QObject, QTimer, Signal, Slot


class NetworkController(QObject):
    connectedChanged = Signal()
    checkingChanged = Signal()
    networksChanged = Signal()
    statusChanged = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._connected = True
        self._checking = False
        self._status = ""
        self._networks = []
        self._nmcli = shutil.which("nmcli")

        QTimer.singleShot(250, self.checkConnection)

    @Property(bool, notify=connectedChanged)
    def connected(self):
        return self._connected

    @Property(bool, notify=checkingChanged)
    def checking(self):
        return self._checking

    @Property("QVariantList", notify=networksChanged)
    def networks(self):
        return self._networks

    @Property(str, notify=statusChanged)
    def status(self):
        return self._status

    def set_status(self, status):
        if status != self._status:
            self._status = status
            self.statusChanged.emit()

    def _safe_error(self, result, fallback, secrets=()):
        message = result.stderr.strip() or result.stdout.strip() or fallback
        for secret in secrets:
            if secret:
                message = message.replace(secret, "[redacted]")
        return message

    def internet_is_available(self, host="1.1.1.1", port=53, timeout=3):
        try:
            with socket.create_connection((host, port), timeout=timeout):
                return True
        except OSError:
            return False

    @Slot()
    def checkConnection(self):
        self._checking = True
        self.checkingChanged.emit()

        connected = self.internet_is_available()
        if connected:
            self._connected = True
            self.connectedChanged.emit()
            self.set_status("Internet connection available.")
        else:
            self._connected = False
            self.connectedChanged.emit()
            self.set_status(
                "No internet connection. Connect Ethernet or set up Wi-Fi."
            )
            self.scanNetworks()

        self._checking = False
        self.checkingChanged.emit()

    @Slot()
    def scanNetworks(self):
        if not self._nmcli:
            self._networks = []
            self.networksChanged.emit()
            self.set_status(
                "Network setup tool unavailable. Connect Ethernet or configure "
                "Wi-Fi through the Raspberry Pi system settings."
            )
            return

        try:
            result = subprocess.run(
                [
                    self._nmcli,
                    "-t",
                    "-f",
                    "SSID",
                    "dev",
                    "wifi",
                    "list",
                    "--rescan",
                    "yes",
                ],
                check=False,
                timeout=15,
                capture_output=True,
                text=True,
            )
        except (OSError, subprocess.SubprocessError) as error:
            self.set_status("Unable to scan for Wi-Fi networks: " + str(error))
            return

        if result.returncode != 0:
            self.set_status(
                result.stderr.strip() or "Unable to scan for Wi-Fi networks."
            )
            return

        networks = sorted({
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip()
        })
        self._networks = networks
        self.networksChanged.emit()

    @Slot(str, str, result=bool)
    def connectNetwork(self, ssid, password):
        if not ssid:
            self.set_status("Choose a Wi-Fi network.")
            return False

        if not self._nmcli:
            self.set_status(
                "Network setup tool unavailable. Connect Ethernet or configure "
                "Wi-Fi through the Raspberry Pi system settings."
            )
            return False

        self.set_status("Connecting...")
        try:
            result = subprocess.run(
                [
                    self._nmcli,
                    "--ask",
                    "dev",
                    "wifi",
                    "connect",
                    ssid,
                ],
                check=False,
                timeout=30,
                capture_output=True,
                text=True,
                input=password + "\n",
            )
        except (OSError, subprocess.SubprocessError) as error:
            self.set_status("Unable to connect to the Wi-Fi network.")
            return False

        if result.returncode != 0:
            self.set_status(
                self._safe_error(
                    result,
                    "Wi-Fi connection failed.",
                    (password,),
                )
            )
            return False

        saved = self.ensureProfileAutoconnect(ssid)
        if not saved:
            self.set_status(
                "Connected, but NetworkManager could not enable automatic "
                "reconnection."
            )
            return False

        if self.internet_is_available():
            self._connected = True
            self.connectedChanged.emit()
            self.set_status(
                "Connected to the internet. Wi-Fi settings will be restored after shutdown."
            )
            return True

        self.set_status(
            "The Wi-Fi network connected, but internet access is unavailable."
        )
        return False

    def ensureProfileAutoconnect(self, ssid):
        if not self._nmcli:
            return False

        try:
            profile_result = subprocess.run(
                [
                    self._nmcli,
                    "-t",
                    "-f",
                    "NAME",
                    "connection",
                    "show",
                ],
                check=False,
                timeout=15,
                capture_output=True,
                text=True,
            )
            if profile_result.returncode != 0:
                return False

            profile_names = {
                line.strip()
                for line in profile_result.stdout.splitlines()
                if line.strip()
            }
            profile_name = ssid if ssid in profile_names else ssid

            modify_result = subprocess.run(
                [
                    self._nmcli,
                    "connection",
                    "modify",
                    profile_name,
                    "connection.autoconnect",
                    "yes",
                    "connection.autoconnect-priority",
                    "10",
                ],
                check=False,
                timeout=15,
                capture_output=True,
                text=True,
            )
            if modify_result.returncode != 0:
                return False

            reapply_result = subprocess.run(
                [
                    self._nmcli,
                    "connection",
                    "reload",
                ],
                check=False,
                timeout=15,
                capture_output=True,
                text=True,
            )
            return reapply_result.returncode == 0
        except (OSError, subprocess.SubprocessError):
            return False
