import os
import sys
import unittest
from pathlib import Path

os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtCore import QObject

from src.task_model import TaskModel


class NavigationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])
        cls.engine = QQmlApplicationEngine()
        cls.task_model = TaskModel()
        cls.engine.rootContext().setContextProperty("taskModel", cls.task_model)

        project_root = Path(__file__).resolve().parent.parent
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


if __name__ == "__main__":
    unittest.main()
