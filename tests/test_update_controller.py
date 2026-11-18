import subprocess
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from src.update_controller import UpdateController


def command(returncode=0, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=[],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


class UpdateControllerTests(unittest.TestCase):
    def setUp(self):
        self.controller = UpdateController(Path(__file__).resolve().parent.parent)

    def test_check_reports_available_updates(self):
        self.controller._run_git = Mock(
            side_effect=[
                command(),
                command(stdout="origin/main\n"),
                command(stdout="local\n"),
                command(stdout="remote\n"),
                command(stdout="2\n"),
            ]
        )

        self.controller._check_for_updates()

        self.assertTrue(self.controller.available)
        self.assertIn("2 updates", self.controller.status)
        self.assertFalse(self.controller.busy)

    def test_check_reports_up_to_date_checkout(self):
        self.controller._run_git = Mock(
            side_effect=[
                command(),
                command(stdout="origin/main\n"),
                command(stdout="same\n"),
                command(stdout="same\n"),
                command(stdout="0\n"),
            ]
        )

        self.controller._check_for_updates()

        self.assertFalse(self.controller.available)
        self.assertEqual(self.controller.status, "Up to date.")

    def test_apply_refuses_dirty_tracked_files(self):
        self.controller._run_git = Mock(
            return_value=command(stdout=" M main.py\n")
        )

        self.controller._apply_update()

        self.assertIn("tracked files", self.controller.status)
        self.controller._run_git.assert_called_once_with(
            "status", "--porcelain", "--untracked-files=no"
        )

    @patch("src.update_controller.subprocess.run")
    def test_apply_installs_dependencies_when_requirements_change(self, run):
        run.return_value = command()
        self.controller._run_git = Mock(
            side_effect=[
                command(),
                command(stdout="old-revision\n"),
                command(),
                command(returncode=1),
            ]
        )

        self.controller._apply_update()

        self.assertIn("pip", run.call_args.args[0])
        self.assertTrue(run.call_args.args[0][-1].endswith("requirements.txt"))
        self.assertEqual(
            self.controller.status,
            "Update complete. Restart to use the new version.",
        )

    @patch("src.update_controller.subprocess.run")
    def test_apply_retries_dependencies_after_an_install_failure(self, run):
        self.controller._dependencies_pending = True
        run.return_value = command()
        self.controller._run_git = Mock(
            side_effect=[
                command(),
                command(stdout="current-revision\n"),
                command(),
                command(returncode=0),
            ]
        )

        self.controller._apply_update()

        run.assert_called_once()
        self.assertFalse(self.controller._dependencies_pending)
        self.assertTrue(self.controller.status.startswith("Update complete"))


if __name__ == "__main__":
    unittest.main()
