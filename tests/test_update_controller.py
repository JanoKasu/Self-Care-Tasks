import os
import subprocess
import tempfile
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
        self.project_dir = Path(__file__).resolve().parent.parent
        self.signers_dir = tempfile.TemporaryDirectory()
        self.signers_file = Path(self.signers_dir.name) / "allowed_signers"
        self.signers_file.write_text(
            "release@example.com ssh-ed25519 AAAAC3NzaC1lZDI1NTE5AAAAITest\n",
            encoding="utf-8",
        )
        self.environment = patch.dict(
            os.environ,
            {"SELF_CARE_UPDATE_ALLOWED_SIGNERS": str(self.signers_file)},
        )
        self.environment.start()
        self.controller = UpdateController(self.project_dir)

    def tearDown(self):
        self.environment.stop()
        self.signers_dir.cleanup()

    def test_check_reports_available_updates(self):
        local = "a" * 40
        remote = "b" * 40
        self.controller._resolve_update_candidate = Mock(
            return_value=(local, remote)
        )
        self.controller._run_git = Mock(return_value=command(stdout="2\n"))

        self.controller._check_for_updates()

        self.assertTrue(self.controller.available)
        self.assertIn("2 updates", self.controller.status)
        self.assertFalse(self.controller.busy)

    def test_check_reports_up_to_date_checkout(self):
        revision = "a" * 40
        self.controller._resolve_update_candidate = Mock(
            return_value=(revision, revision)
        )
        self.controller._run_git = Mock(return_value=command(stdout="0\n"))

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

    def test_candidate_must_come_from_trusted_remote_and_signed_commit(self):
        local = "a" * 40
        remote = "b" * 40
        self.controller._run_git = Mock(
            side_effect=[
                command(
                    stdout="https://github.com/JanoKasu/Self-Care-Tasks.git\n"
                ),
                command(),
                command(stdout="origin/main\n"),
                command(stdout=local + "\n"),
                command(stdout=remote + "\n"),
                command(),
            ]
        )

        self.assertEqual(
            self.controller._resolve_update_candidate(),
            (local, remote),
        )
        verify_call = self.controller._run_git.call_args_list[-1]
        self.assertIn("verify-commit", verify_call.args)
        self.assertIn(remote, verify_call.args)

    def test_candidate_rejects_unsigned_commit(self):
        local = "a" * 40
        remote = "b" * 40
        self.controller._run_git = Mock(
            side_effect=[
                command(
                    stdout="https://github.com/JanoKasu/Self-Care-Tasks.git\n"
                ),
                command(),
                command(stdout="origin/main\n"),
                command(stdout=local + "\n"),
                command(stdout=remote + "\n"),
                command(returncode=1, stderr="No principal matched"),
            ]
        )

        self.assertIsNone(self.controller._resolve_update_candidate())
        self.assertIn("trusted signature", self.controller.status)

    def test_apply_refuses_dependency_changes_before_checkout(self):
        local = "a" * 40
        remote = "b" * 40
        self.controller._resolve_update_candidate = Mock(
            return_value=(local, remote)
        )
        self.controller._run_git = Mock(
            side_effect=[
                command(),
                command(),
                command(returncode=1),
            ]
        )

        self.controller._apply_update()

        self.assertIn("requirements changed", self.controller.status)
        self.assertNotIn(
            "merge",
            [call.args[0] for call in self.controller._run_git.call_args_list],
        )

    def test_apply_merges_verified_revision_without_running_pip(self):
        local = "a" * 40
        remote = "b" * 40
        self.controller._resolve_update_candidate = Mock(
            return_value=(local, remote)
        )
        self.controller._run_git = Mock(
            side_effect=[
                command(),
                command(),
                command(),
                command(),
            ]
        )

        self.controller._apply_update()

        self.assertEqual(
            self.controller._run_git.call_args.args,
            ("merge", "--ff-only", remote),
        )
        self.assertEqual(
            self.controller.status,
            "Update complete. Restart to use the new version.",
        )


if __name__ == "__main__":
    unittest.main()
