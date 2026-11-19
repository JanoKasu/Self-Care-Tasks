import unittest
from unittest.mock import Mock, patch

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

    def test_connect_passes_wifi_password_only_on_stdin(self):
        self.controller._nmcli = "nmcli"
        password = "secret-password"
        command_result = Mock(returncode=1, stdout="", stderr="authentication failed")

        with patch(
            "src.network_controller.subprocess.run",
            return_value=command_result,
        ) as run:
            self.assertFalse(
                self.controller.connectNetwork("Home Wi-Fi", password)
            )

        arguments = run.call_args.args[0]
        self.assertNotIn(password, arguments)
        self.assertEqual(run.call_args.kwargs["input"], password + "\n")
        self.assertIn("--ask", arguments)

    def test_connect_redacts_wifi_password_from_error_output(self):
        self.controller._nmcli = "nmcli"
        password = "secret-password"
        command_result = Mock(
            returncode=1,
            stdout="",
            stderr=f"nmcli rejected {password}",
        )

        with patch(
            "src.network_controller.subprocess.run",
            return_value=command_result,
        ):
            self.controller.connectNetwork("Home Wi-Fi", password)

        self.assertNotIn(password, self.controller.status)
        self.assertIn("[redacted]", self.controller.status)
