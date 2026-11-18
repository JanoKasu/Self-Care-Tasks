import subprocess
import sys
import threading
from pathlib import Path

from PySide6.QtCore import Property, QObject, QProcess, QTimer, Signal, Slot


class UpdateController(QObject):
    availableChanged = Signal()
    busyChanged = Signal()
    statusChanged = Signal()

    def __init__(self, project_dir, parent=None):
        super().__init__(parent)
        self._project_dir = Path(project_dir).resolve()
        self._available = False
        self._busy = False
        self._dependencies_pending = False
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

    def _check_for_updates(self):
        self._set_busy(True)
        self._set_status("Checking for updates...")
        try:
            fetch = self._run_git("fetch", "--quiet")
            if fetch.returncode != 0:
                self._set_status(
                    "Update check failed: "
                    + self._command_error(fetch, "could not reach the repository")
                )
                return

            upstream = self._run_git(
                "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"
            )
            if upstream.returncode != 0:
                self._set_status(
                    "Updates unavailable: this checkout has no tracked remote branch."
                )
                return

            local = self._run_git("rev-parse", "HEAD")
            remote = self._run_git("rev-parse", upstream.stdout.strip())
            behind = self._run_git(
                "rev-list", "--count", "HEAD..@{upstream}"
            )
            if (
                local.returncode != 0
                or remote.returncode != 0
                or behind.returncode != 0
            ):
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
            elif local.stdout.strip() == remote.stdout.strip():
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

            old_head = self._run_git("rev-parse", "HEAD")
            if old_head.returncode != 0:
                self._set_status("Update failed: current revision could not be read.")
                return

            pull = self._run_git("pull", "--ff-only")
            if pull.returncode != 0:
                self._set_status(
                    "Update failed: "
                    + self._command_error(
                        pull, "the repository could not be fast-forwarded"
                    )
                )
                return

            requirements_result = self._run_git(
                "diff",
                "--quiet",
                old_head.stdout.strip(),
                "HEAD",
                "--",
                "requirements.txt",
            )
            if requirements_result.returncode not in (0, 1):
                self._dependencies_pending = True
                self._set_status(
                    "Code updated, but dependency changes could not be checked: "
                    + self._command_error(
                        requirements_result, "git diff could not compare revisions"
                    )
                )
                return
            requirements_changed = requirements_result.returncode == 1
            if requirements_changed:
                self._dependencies_pending = True
            if self._dependencies_pending:
                self._set_status("Updating Python dependencies...")
                install = subprocess.run(
                    [
                        sys.executable,
                        "-m",
                        "pip",
                        "install",
                        "-r",
                        str(self._project_dir / "requirements.txt"),
                    ],
                    cwd=self._project_dir,
                    check=False,
                    capture_output=True,
                    text=True,
                    timeout=300,
                )
                if install.returncode != 0:
                    self._set_status(
                        "Code updated, but dependency installation failed: "
                        + self._command_error(
                            install, "pip could not install the requirements"
                        )
                    )
                    return
                self._dependencies_pending = False

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
        if not QProcess.startDetached(executable, [entrypoint], str(self._project_dir)):
            self._set_status("The updated app could not be restarted automatically.")
            return False

        from PySide6.QtGui import QGuiApplication

        app = QGuiApplication.instance()
        if app is not None:
            app.quit()
        return True
