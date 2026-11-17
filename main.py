import sys

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from src.task_model import TaskModel


def main():
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    task_model = TaskModel()

    engine.rootContext().setContextProperty(
        "taskModel",
        task_model
    )

    engine.load("qml/Main.qml")

    if not engine.rootObjects():
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
