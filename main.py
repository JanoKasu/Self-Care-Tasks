import sys
import os
from pathlib import Path

os.environ.setdefault("QT_IM_MODULE", "QtVirtualKeyboard")

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from src.inactivity_controller import InactivityController
from src.task_model import (
    CompletionHistoryModel,
    TaskAttentionModel,
    TaskModel,
)
from src.update_controller import UpdateController
from src.weather_controller import WeatherController
from src.database import Database

PROJECT_DIR = Path(__file__).resolve().parent


def resource_path(*parts):
    return PROJECT_DIR.joinpath(*parts)


def main():
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    database = Database()
    history_model = CompletionHistoryModel(database)
    attention_model = TaskAttentionModel(database)
    task_model = TaskModel(history_model, attention_model, database)
    update_controller = UpdateController(PROJECT_DIR)
    inactivity_controller = InactivityController(timeout_seconds=30)
    weather_controller = WeatherController()
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
        "attentionModel",
        attention_model
    )
    engine.rootContext().setContextProperty(
        "inactivityController",
        inactivity_controller
    )
    engine.rootContext().setContextProperty(
        "updateController",
        update_controller
    )
    engine.rootContext().setContextProperty(
        "weatherController",
        weather_controller
    )

    engine.load(str(resource_path("qml", "Main.qml")))

    if not engine.rootObjects():
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
