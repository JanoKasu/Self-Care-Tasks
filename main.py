import sys
import os
from pathlib import Path

os.environ.setdefault("QT_IM_MODULE", "QtVirtualKeyboard")

from PySide6.QtGui import QGuiApplication
from PySide6.QtQml import QQmlApplicationEngine

from src.inactivity_controller import InactivityController
from src.network_controller import NetworkController
from src.task_model import (
    CompletionHistoryModel,
    TaskAttentionModel,
    TaskModel,
)


def resource_path(*parts):
    base_path = Path(
        getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)
    )
    return base_path.joinpath(*parts)


def main():
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    history_model = CompletionHistoryModel()
    attention_model = TaskAttentionModel()
    task_model = TaskModel(history_model, attention_model)
    network_controller = NetworkController()
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
        "attentionModel",
        attention_model
    )
    engine.rootContext().setContextProperty(
        "inactivityController",
        inactivity_controller
    )
    engine.rootContext().setContextProperty(
        "networkController",
        network_controller
    )

    engine.load(str(resource_path("qml", "Main.qml")))

    if not engine.rootObjects():
        return -1

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
