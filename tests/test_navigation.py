import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtCore import QObject, QUrl
from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine, QQmlComponent

from src.task_model import (
    CompletionHistoryModel,
    TaskAttentionModel,
    TaskModel,
)
from src.update_controller import UpdateController
from src.network_controller import NetworkController
from src.inactivity_controller import InactivityController
from src.weather_controller import WeatherController


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])
        cls.engine = QQmlApplicationEngine()
        project_root = Path(__file__).resolve().parent.parent
        cls.history_model = CompletionHistoryModel()
        cls.attention_model = TaskAttentionModel()
        cls.task_model = TaskModel(cls.history_model, cls.attention_model)
        cls.network_controller = NetworkController()
        cls.update_controller = UpdateController(project_root)
        cls.inactivity_controller = InactivityController(timeout_seconds=30)
        cls.inactivity_controller._run_xset = lambda *arguments: None
        cls.weather_controller = WeatherController(
            project_root / "tests" / ".weather-data"
        )
        cls.engine.rootContext().setContextProperty("taskModel", cls.task_model)
        cls.engine.rootContext().setContextProperty(
            "historyModel",
            cls.history_model
        )
        cls.engine.rootContext().setContextProperty(
            "attentionModel",
            cls.attention_model
        )
        cls.engine.rootContext().setContextProperty(
            "updateController",
            cls.update_controller
        )
        cls.engine.rootContext().setContextProperty(
            "networkController",
            cls.network_controller
        )
        cls.engine.rootContext().setContextProperty(
            "inactivityController",
            cls.inactivity_controller
        )
        cls.engine.rootContext().setContextProperty(
            "weatherController",
            cls.weather_controller
        )
        cls.engine.load(str(project_root / "qml" / "Main.qml"))
        cls.root_objects = cls.engine.rootObjects()

    @classmethod
    def tearDownClass(cls):
        cls.engine.deleteLater()

    def setUp(self):
        self.assertTrue(self.root_objects, "Main.qml failed to load")
        self.navigation = self.root_objects[0].findChild(QObject, "navigation")

    def test_navigation_and_page_stack_are_bound_by_current_index(self):
        navigation = self.navigation
        self.assertIsNotNone(navigation)

        page_stack = self.root_objects[0].findChild(QObject, "pageStack")
        self.assertIsNotNone(page_stack)

        for index in (0, 1, 2, 3, 4):
            navigation.setProperty("currentIndex", index)
            self.app.processEvents()
            self.assertEqual(navigation.property("currentIndex"), index)
            self.assertEqual(page_stack.property("currentIndex"), index)

    def test_settings_page_is_not_loaded(self):
        settings_page = self.root_objects[0].findChild(
            QObject,
            "settingsPage"
        )
        self.assertIsNone(settings_page)

    def test_weather_tab_is_bound_to_weather_page(self):
        weather_tab = self.root_objects[0].findChild(QObject, "weatherTab")

        self.assertIsNotNone(weather_tab)
        self.navigation.setProperty("currentIndex", 4)
        self.app.processEvents()
        self.assertEqual(weather_tab.property("checked"), True)

    def test_progress_stats_fill_the_available_page_width(self):
        self.navigation.setProperty("currentIndex", 2)
        self.app.processEvents()

        stats_grid = self.root_objects[0].findChild(QObject, "statsGrid")

        self.assertIsNotNone(stats_grid)
        self.assertGreater(stats_grid.property("width"), 350)

    def test_weather_content_scrolls_at_full_page_width(self):
        self.weather_controller._has_location = True
        self.weather_controller.changed.emit()
        self.navigation.setProperty("currentIndex", 4)
        self.app.processEvents()

        weather_scroll = self.root_objects[0].findChild(
            QObject,
            "weatherScroll",
        )

        self.assertIsNotNone(weather_scroll)
        self.assertGreater(weather_scroll.property("availableWidth"), 500)
        self.assertGreaterEqual(
            weather_scroll.property("contentWidth"),
            weather_scroll.property("availableWidth") - 1,
        )
        self.weather_controller._has_location = False
        self.weather_controller.changed.emit()

    def test_added_task_is_instantiated_as_a_task_card(self):
        title = "Regression test task"
        self.task_model.addTaskWithFrequency(
            title,
            "Verifies that a new task is rendered",
            "Anytime",
            "#ffffff",
            "Medium",
            "test",
            "Daily",
        )
        task_id = self.task_model.tasks[-1]["id"]

        try:
            self.app.processEvents()
            task_grid = self.root_objects[0].findChild(QObject, "taskGrid")
            self.assertIsNotNone(task_grid)
            self.assertGreater(task_grid.property("implicitHeight"), 0)
        finally:
            self.task_model.deleteTask(task_id)
            self.app.processEvents()

    def test_tasks_view_is_touch_flickable_and_tracks_grid_height(self):
        self.navigation.setProperty("currentIndex", 1)
        self.app.processEvents()

        task_scroll = self.root_objects[0].findChild(
            QObject,
            "taskScrollView",
        )
        task_grid = self.root_objects[0].findChild(QObject, "taskGrid")

        self.assertIsNotNone(task_scroll)
        self.assertIsNotNone(task_grid)
        self.assertTrue(task_scroll.property("interactive"))
        self.assertGreater(task_scroll.property("contentWidth"), 0)
        self.assertGreaterEqual(
            task_scroll.property("contentHeight"),
            task_grid.property("implicitHeight") - 1,
        )

    def test_virtual_keyboard_is_loaded(self):
        virtual_keyboard = self.root_objects[0].findChild(
            QObject,
            "virtualKeyboard"
        )
        self.assertIsNotNone(virtual_keyboard)

    def test_inactivity_dimmer_tracks_controller_state(self):
        dimmer = self.root_objects[0].findChild(QObject, "inactivityDimmer")
        self.assertIsNotNone(dimmer)
        self.assertFalse(dimmer.property("visible"))
        self.assertEqual(dimmer.property("opacity"), 0.85)

        self.inactivity_controller.sleep()
        self.app.processEvents()
        self.assertTrue(dimmer.property("visible"))

        self.inactivity_controller.wake()
        self.app.processEvents()
        self.assertFalse(dimmer.property("visible"))

    def test_theme_uses_dark_mode_between_eight_pm_and_six_am(self):
        project_root = Path(__file__).resolve().parent.parent
        component = QQmlComponent(self.engine)
        component.setData(
            b"""
                import QtQuick
                import "." as AppTheme

                QtObject {
                    id: themeProbe

                    property bool receivedDarkModeSignal: false
                    property Connections themeChangeListener: Connections {
                        target: AppTheme.Theme
                        function onThemeChanged(darkMode) {
                            if (darkMode)
                                themeProbe.receivedDarkModeSignal = true
                        }
                    }

                    readonly property bool beforeSix: AppTheme.Theme.isNightHour(5)
                    readonly property bool atSix: AppTheme.Theme.isNightHour(6)
                    readonly property bool beforeEight: AppTheme.Theme.isNightHour(19)
                    readonly property bool atEight: AppTheme.Theme.isNightHour(20)
                    readonly property int beforeSixMilliseconds:
                        AppTheme.Theme.millisecondsUntilNextSwitch(
                            new Date(2026, 0, 15, 5, 30)
                        )
                    readonly property int atSixMilliseconds:
                        AppTheme.Theme.millisecondsUntilNextSwitch(
                            new Date(2026, 0, 15, 6, 0)
                        )
                    readonly property int beforeEightMilliseconds:
                        AppTheme.Theme.millisecondsUntilNextSwitch(
                            new Date(2026, 0, 15, 19, 30)
                        )
                    readonly property int afterEightMilliseconds:
                        AppTheme.Theme.millisecondsUntilNextSwitch(
                            new Date(2026, 0, 15, 20, 30)
                        )

                    Component.onCompleted: {
                        AppTheme.Theme.currentTime = new Date(2026, 0, 15, 12, 0)
                        AppTheme.Theme.currentTime = new Date(2026, 0, 15, 20, 0)
                        AppTheme.Theme.currentTime = new Date()
                    }
                }
            """,
            QUrl.fromLocalFile(str(project_root / "qml" / "ThemeHoursTest.qml"))
        )
        theme_hours = component.create()
        self.assertIsNotNone(theme_hours, component.errorString())
        self.assertTrue(theme_hours.property("beforeSix"))
        self.assertFalse(theme_hours.property("atSix"))
        self.assertFalse(theme_hours.property("beforeEight"))
        self.assertTrue(theme_hours.property("atEight"))
        self.assertEqual(theme_hours.property("beforeSixMilliseconds"), 1800000)
        self.assertEqual(theme_hours.property("atSixMilliseconds"), 50400000)
        self.assertEqual(theme_hours.property("beforeEightMilliseconds"), 1800000)
        self.assertEqual(theme_hours.property("afterEightMilliseconds"), 34200000)
        self.assertTrue(theme_hours.property("receivedDarkModeSignal"))
        theme_hours.deleteLater()

    def test_touchscreen_entry_points_are_keyboard_accessible(self):
        home_task_button = self.root_objects[0].findChild(
            QObject,
            "openTasksButton"
        )
        update_tab = self.root_objects[0].findChild(QObject, "updateTab")

        self.assertIsNotNone(home_task_button)
        self.assertTrue(home_task_button.property("activeFocusOnTab"))
        self.assertIsNotNone(update_tab)

    def test_task_duration_disappears_when_completed(self):
        project_root = Path(__file__).resolve().parent.parent
        component = QQmlComponent(self.engine)
        component.setData(
            b"""
                import QtQuick
                import "components"

                TaskCard {
                    objectName: "durationTaskCard"
                    completed: false
                }
            """,
            QUrl.fromLocalFile(
                str(project_root / "qml" / "DurationTaskCardTest.qml")
            ),
        )
        task_card = component.create()
        self.assertIsNotNone(task_card, component.errorString())
        duration_pill = task_card.findChild(QObject, "durationPill")
        self.assertIsNotNone(duration_pill)
        self.assertTrue(duration_pill.property("visible"))

        task_card.setProperty("completed", True)
        self.app.processEvents()

        self.assertFalse(duration_pill.property("visible"))
        task_card.deleteLater()


if __name__ == "__main__":
    unittest.main()
