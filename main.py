import sys
import os
from pathlib import Path

os.environ.setdefault("QT_IM_MODULE", "QtVirtualKeyboard")

from PySide6.QtCore import QUrl
from PySide6.QtGui import QGuiApplication, QWindow
from PySide6.QtQml import QQmlApplicationEngine

from src.inactivity_controller import InactivityController
from src.network_controller import NetworkController
from src.task_model import CompletionHistoryModel, TaskModel


def main():
    app = QGuiApplication(sys.argv)

    engine = QQmlApplicationEngine()

    history_model = CompletionHistoryModel()
    task_model = TaskModel(history_model)
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
        "inactivityController",
        inactivity_controller
    )
    engine.rootContext().setContextProperty(
        "networkController",
        network_controller
    )

    project_dir = Path(__file__).resolve().parent
    engine.load(QUrl.fromLocalFile(str(project_dir / "qml" / "Main.qml")))

    if not engine.rootObjects():
        return -1

    if os.environ.get("SELF_CARE_FULLSCREEN", "").lower() in {
        "1",
        "true",
        "yes",
    }:
        engine.rootObjects()[0].setProperty(
            "visibility",
            QWindow.Visibility.FullScreen,
        )

    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
