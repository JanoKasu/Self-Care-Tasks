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
from src.network_controller import NetworkController
from src.update_controller import UpdateController


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
            "networkController",
            cls.network_controller
        )
        cls.engine.rootContext().setContextProperty(
            "updateController",
            cls.update_controller
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

        for index in (0, 1, 2, 3):
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

    def test_virtual_keyboard_is_loaded(self):
        virtual_keyboard = self.root_objects[0].findChild(
            QObject,
            "virtualKeyboard"
        )
        self.assertIsNotNone(virtual_keyboard)

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


if __name__ == "__main__":
    unittest.main()
