from PySide6.QtCore import (
    Property,
    QEvent,
    QObject,
    QTimer,
    Signal,
)
from PySide6.QtGui import QGuiApplication, QCursor
from PySide6.QtCore import Qt

import shutil
import subprocess
import logging


logger = logging.getLogger(__name__)


class InactivityController(QObject):
    asleepChanged = Signal()

    INPUT_EVENTS = {
        QEvent.Type.MouseButtonPress,
        QEvent.Type.MouseButtonRelease,
        QEvent.Type.MouseMove,
        QEvent.Type.TouchBegin,
        QEvent.Type.TouchUpdate,
        QEvent.Type.TouchEnd,
        QEvent.Type.KeyPress,
        QEvent.Type.KeyRelease,
    }

    WAKE_EVENTS = {
        QEvent.Type.MouseButtonPress,
        QEvent.Type.TouchBegin,
        QEvent.Type.KeyPress,
    }

    def __init__(self, timeout_seconds=30, parent=None):
        super().__init__(parent)
        self._asleep = False
        self._timeout_ms = timeout_seconds * 1000
        self._xset = shutil.which("xset")
        if not self._xset:
            logger.warning(
                "DPMS control unavailable: xset is not installed or X11 is not active"
            )

        self._idle_timer = QTimer(self)
        self._idle_timer.setSingleShot(True)
        self._idle_timer.timeout.connect(self.sleep)
        self._idle_timer.start(self._timeout_ms)

    def _run_xset(self, *arguments):
        if not self._xset:
            return

        try:
            completed = subprocess.run(
                [self._xset, *arguments],
                check=False,
                timeout=2,
                capture_output=True,
                text=True,
            )
            if completed.returncode != 0:
                logger.warning(
                    "DPMS command failed (%s): %s",
                    " ".join(arguments),
                    completed.stderr.strip() or "xset returned no error details",
                )
        except (OSError, subprocess.SubprocessError) as error:
            logger.warning("Unable to run DPMS command: %s", error)

    @Property(bool, notify=asleepChanged)
    def asleep(self):
        return self._asleep

    def sleep(self):
        if not self._asleep:
            self._asleep = True
            self.asleepChanged.emit()
            QGuiApplication.setOverrideCursor(
                QCursor(Qt.CursorShape.BlankCursor)
            )
            self._run_xset("dpms", "force", "off")

    def wake(self):
        if self._asleep:
            self._asleep = False
            self.asleepChanged.emit()
            QGuiApplication.restoreOverrideCursor()
            self._run_xset("dpms", "force", "on")
        self.resetTimer()

    def resetTimer(self):
        if not self._asleep:
            self._idle_timer.start(self._timeout_ms)

    def eventFilter(self, watched, event):
        event_type = event.type()

        if event_type not in self.INPUT_EVENTS:
            return super().eventFilter(watched, event)

        if self._asleep and event_type in self.WAKE_EVENTS:
            self.wake()
            return True

        if not self._asleep:
            self.resetTimer()

        return super().eventFilter(watched, event)
