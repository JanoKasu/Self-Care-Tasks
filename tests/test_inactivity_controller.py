import unittest
from unittest.mock import Mock, patch

from PySide6.QtGui import QGuiApplication

from src.inactivity_controller import InactivityController


class InactivityControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    @patch("src.inactivity_controller.QGuiApplication.restoreOverrideCursor")
    @patch("src.inactivity_controller.QGuiApplication.setOverrideCursor")
    def test_sleep_enters_dpms_low_power_mode(
        self,
        set_override_cursor,
        restore_override_cursor,
    ):
        controller = InactivityController(timeout_seconds=30)
        controller._run_xset = Mock()

        controller.sleep()

        self.assertTrue(controller.asleep)
        set_override_cursor.assert_called_once()
        controller._run_xset.assert_any_call("+dpms")
        controller._run_xset.assert_any_call("dpms", "force", "off")
        self.assertEqual(controller._run_xset.call_count, 2)

        controller.sleep()
        set_override_cursor.assert_called_once()
        self.assertEqual(controller._run_xset.call_count, 2)

    @patch("src.inactivity_controller.QGuiApplication.restoreOverrideCursor")
    @patch("src.inactivity_controller.QGuiApplication.setOverrideCursor")
    def test_wake_turns_dpms_on_and_resets_timer(
        self,
        set_override_cursor,
        restore_override_cursor,
    ):
        controller = InactivityController(timeout_seconds=30)
        controller._run_xset = Mock()
        controller.resetTimer = Mock()

        controller.sleep()
        controller.wake()

        self.assertFalse(controller.asleep)
        restore_override_cursor.assert_called_once()
        controller._run_xset.assert_any_call("dpms", "force", "on")
        controller.resetTimer.assert_called_once()

    def test_timeout_seconds_starts_single_shot_timer(self):
        controller = InactivityController(timeout_seconds=7)

        self.assertTrue(controller._idle_timer.isSingleShot())
        self.assertEqual(controller._idle_timer.interval(), 7000)
        controller._idle_timer.stop()


if __name__ == "__main__":
    unittest.main()
