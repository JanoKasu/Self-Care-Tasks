import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine
from PySide6.QtWebEngineQuick import QtWebEngineQuick

from src.inactivity_controller import InactivityController
from src.task_model import CompletionHistoryModel, TaskModel


def main():
    QtWebEngineQuick.initialize()
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    history_model = CompletionHistoryModel()
    task_model = TaskModel(history_model)
    inactivity_controller = InactivityController(timeout_seconds=30)
    app.installEventFilter(inactivity_controller)

    engine.rootContext().setContextProperty(
        "taskModel",
        task_model
    )
    engine.rootContext().setContextProperty(
        "historyModel",
        history_model
    )
    engine.rootContext().setContextProperty(
        "inactivityController",
        inactivity_controller
    )

    engine.load("qml/Main.qml")

    if not engine.rootObjects():
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
