import unittest
from unittest.mock import patch

from src.network_controller import NetworkController


class NetworkControllerTests(unittest.TestCase):
    def setUp(self):
        self.controller = NetworkController()

    def test_internet_is_available_from_socket_connection(self):
        with patch("src.network_controller.socket.create_connection") as connection:
            connection.return_value.__enter.return_value = object()
            self.assertTrue(self.controller.internet_is_available())

    def test_internet_failure_is_reported(self):
        with patch(
            "src.network_controller.socket.create_connection",
            side_effect=OSError("offline"),
        ):
            self.assertFalse(self.controller.internet_is_available())

    def test_check_connection_sets_offline_status(self):
        with patch.object(
            self.controller,
            "internet_is_available",
            return_value=False,
        ), patch.object(self.controller, "scanNetworks"):
            self.controller.checkConnection()

            self.assertFalse(self.controller.connected)
            self.assertIn("No internet connection", self.controller.status)

    def test_check_connection_sets_online_status(self):
        with patch.object(
            self.controller,
            "internet_is_available",
            return_value=True,
        ):
            self.controller.checkConnection()

            self.assertTrue(self.controller.connected)
            self.assertIn("available", self.controller.status)

    def test_saved_profile_autoconnect_is_enabled(self):
        self.controller._nmcli = "nmcli"
        responses = [
            unittest.mock.Mock(
                returncode=0,
                stdout="Home Wi-Fi\n",
                stderr="",
            ),
            unittest.mock.Mock(returncode=0, stdout="", stderr=""),
            unittest.mock.Mock(returncode=0, stdout="", stderr=""),
        ]

        with patch(
            "src.network_controller.subprocess.run",
            side_effect=responses,
        ):
            self.assertTrue(
                self.controller.ensureProfileAutoconnect("Home Wi-Fi")
            )
