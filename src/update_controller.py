import os
import re
import subprocess
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Property, QObject, QProcess, QTimer, Signal, Slot


class UpdateController(QObject):
    TRUSTED_REMOTE_URLS = {
        "https://github.com/JanoKasu/Self-Care-Tasks.git",
        "git@github.com:JanoKasu/Self-Care-Tasks.git",
        "ssh://git@github.com/JanoKasu/Self-Care-Tasks.git",
    }
    UPDATE_SIGNERS_ENV = "SELF_CARE_UPDATE_ALLOWED_SIGNERS"
    DEFAULT_ALLOWED_SIGNERS = (
        Path.home() / ".config" / "self-care-tasks" / "allowed_signers"
    )
    REVISION_PATTERN = re.compile(r"^[0-9a-f]{40,64}$")

    availableChanged = Signal()
    busyChanged = Signal()
    statusChanged = Signal()

    def __init__(self, project_dir, parent=None):
        super().__init__(parent)
        self._project_dir = Path(project_dir).resolve()
        self._available = False
        self._busy = False
        self._status = "Checking for updates..."
        QTimer.singleShot(1500, self.checkForUpdates)

    @Property(bool, notify=availableChanged)
    def available(self):
        return self._available

    @Property(bool, notify=busyChanged)
    def busy(self):
        return self._busy

    @Property(str, notify=statusChanged)
    def status(self):
        return self._status

    def _set_available(self, value):
        if value != self._available:
            self._available = value
            self.availableChanged.emit()

    def _set_busy(self, value):
        if value != self._busy:
            self._busy = value
            self.busyChanged.emit()

    def _set_status(self, message):
        if message != self._status:
            self._status = message
            self.statusChanged.emit()

    def _run_git(self, *arguments):
        return subprocess.run(
            ["git", *arguments],
            cwd=self._project_dir,
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )

    def _command_error(self, result, fallback):
        return result.stderr.strip() or result.stdout.strip() or fallback

    def _allowed_signers_file(self):
        configured_path = os.environ.get(self.UPDATE_SIGNERS_ENV)
        candidate = (
            Path(configured_path)
            if configured_path
            else self.DEFAULT_ALLOWED_SIGNERS
        )
        path = candidate.expanduser().resolve()
        if not path.is_file():
            return None

        try:
            path.relative_to(self._project_dir)
        except ValueError:
            return path

        return None

    def _revision(self, result):
        revision = result.stdout.strip()
        if result.returncode != 0 or not self.REVISION_PATTERN.fullmatch(revision):
            return None
        return revision

    def _resolve_update_candidate(self):
        allowed_signers = self._allowed_signers_file()
        if allowed_signers is None:
            self._set_status(
                "Automatic updates are unavailable: configure the persistent "
                "~/.config/self-care-tasks/allowed_signers file or set "
                f"{self.UPDATE_SIGNERS_ENV}."
            )
            return None

        remote_url = self._run_git("remote", "get-url", "origin")
        normalized_url = remote_url.stdout.strip().removesuffix("/")
        if (
            remote_url.returncode != 0
            or normalized_url not in self.TRUSTED_REMOTE_URLS
        ):
            self._set_status(
                "Automatic updates are unavailable: the origin remote is not trusted."
            )
            return None

        fetch = self._run_git("fetch", "--quiet", "origin")
        if fetch.returncode != 0:
            self._set_status(
                "Update check failed: "
                + self._command_error(fetch, "could not reach the repository")
            )
            return None

        upstream = self._run_git(
            "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
        )
        upstream_name = upstream.stdout.strip()
        if upstream.returncode != 0 or not upstream_name.startswith("origin/"):
            self._set_status(
                "Updates unavailable: the checkout is not tracking an origin branch."
            )
            return None

        local_result = self._run_git("rev-parse", "HEAD")
        remote_result = self._run_git("rev-parse", upstream_name)
        local_revision = self._revision(local_result)
        remote_revision = self._revision(remote_result)
        if local_revision is None or remote_revision is None:
            self._set_status("Update check failed: repository revisions are invalid.")
            return None

        verification = self._run_git(
            "-c",
            "gpg.format=ssh",
            "-c",
            f"gpg.ssh.allowedSignersFile={allowed_signers}",
            "verify-commit",
            remote_revision,
        )
        if verification.returncode != 0:
            self._set_status(
                "Update rejected: the available revision has no trusted signature."
            )
            return None

        return local_revision, remote_revision

    def _check_for_updates(self):
        self._set_busy(True)
        self._set_status("Checking for updates...")
        try:
            candidate = self._resolve_update_candidate()
            if candidate is None:
                self._set_available(False)
                return

            local_revision, remote_revision = candidate
            behind = self._run_git("rev-list", "--count", f"{local_revision}..{remote_revision}")
            if behind.returncode != 0:
                self._set_status("Update check failed: repository state could not be read.")
                return

            try:
                updates = int(behind.stdout.strip())
            except ValueError:
                self._set_status("Update check failed: invalid repository response.")
                return

            self._set_available(updates > 0)
            if updates:
                self._set_status(
                    f"{updates} update{' is' if updates == 1 else 's are'} ready to install."
                )
            elif local_revision == remote_revision:
                self._set_status("Up to date.")
            else:
                self._set_available(False)
                self._set_status(
                    "This checkout has local commits; automatic updates are disabled."
                )
        except (OSError, subprocess.SubprocessError) as error:
            self._set_status(f"Update check failed: {error}")
        finally:
            self._set_busy(False)

    def _apply_update(self):
        self._set_busy(True)
        self._set_status("Installing update...")
        try:
            dirty = self._run_git(
                "status", "--porcelain", "--untracked-files=no"
            )
            if dirty.returncode != 0:
                self._set_status(
                    "Update failed: "
                    + self._command_error(dirty, "repository status unavailable")
                )
                return
            if dirty.stdout.strip():
                self._set_status(
                    "Update stopped: close other changes to tracked files before updating."
                )
                return

            candidate = self._resolve_update_candidate()
            if candidate is None:
                return
            old_head, remote_revision = candidate

            fast_forward = self._run_git(
                "merge-base", "--is-ancestor", old_head, remote_revision
            )
            if fast_forward.returncode != 0:
                self._set_status(
                    "Update stopped: this checkout has diverged from the signed revision."
                )
                return

            requirements_result = self._run_git(
                "diff",
                "--quiet",
                old_head,
                remote_revision,
                "--",
                "requirements.txt",
            )
            if requirements_result.returncode not in (0, 1):
                self._set_status(
                    "Update stopped: dependency changes could not be checked: "
                    + self._command_error(
                        requirements_result, "git diff could not compare revisions"
                    )
                )
                return
            if requirements_result.returncode == 1:
                self._set_status(
                    "Update stopped: requirements changed and need manual review and installation."
                )
                return

            merge = self._run_git("merge", "--ff-only", remote_revision)
            if merge.returncode != 0:
                self._set_status(
                    "Update failed: "
                    + self._command_error(
                        merge, "the repository could not be fast-forwarded"
                    )
                )
                return

            self._set_available(False)
            self._set_status("Update complete. Restart to use the new version.")
        except (OSError, subprocess.SubprocessError) as error:
            self._set_status(f"Update failed: {error}")
        finally:
            self._set_busy(False)

    @Slot()
    def checkForUpdates(self):
        if self._busy:
            return
        threading.Thread(target=self._check_for_updates, daemon=True).start()

    @Slot()
    def applyUpdate(self):
        if self._busy:
            return
        threading.Thread(target=self._apply_update, daemon=True).start()

    @Slot(result=bool)
    def restart(self):
        executable = str(Path(sys.executable).resolve())
        entrypoint = str(self._project_dir / "main.py")
        allowed_signers = self._allowed_signers_file()
        if allowed_signers is None:
            self._set_status(
                "The updated app could not be restarted without a trusted signer file."
            )
            return False

        try:
            dirty = self._run_git("status", "--porcelain", "--untracked-files=no")
            head_result = self._run_git("rev-parse", "HEAD")
            head = self._revision(head_result)
            if dirty.returncode != 0 or dirty.stdout.strip():
                self._set_status("Restart stopped: close tracked-file changes first.")
                return False
            if head is None:
                self._set_status("Restart stopped: the current revision is invalid.")
                return False
            verification = self._run_git(
                "-c",
                "gpg.format=ssh",
                "-c",
                f"gpg.ssh.allowedSignersFile={allowed_signers}",
                "verify-commit",
                head,
            )
            if verification.returncode != 0:
                self._set_status(
                    "Restart stopped: the current revision has no trusted signature."
                )
                return False
        except (OSError, subprocess.SubprocessError) as error:
            self._set_status(f"Restart stopped: {error}")
            return False

        if not QProcess.startDetached(executable, [entrypoint], str(self._project_dir)):
            self._set_status("The updated app could not be restarted automatically.")
            return False

        from PySide6.QtGui import QGuiApplication

        app = QGuiApplication.instance()
        if app is not None:
            app.quit()
        return True
