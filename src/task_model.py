
from datetime import datetime, timezone

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Qt,
    Slot,
)

from src.database import Database


class TaskModel(QAbstractListModel):

    IdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = IdRole + 1
    DescriptionRole = IdRole + 2
    CategoryRole = IdRole + 3
    BackgroundColorRole = IdRole + 4
    ImpactRole = IdRole + 5
    IconRole = IdRole + 6
    CreatedAtRole = IdRole + 7
    CompletedRole = IdRole + 8

    def __init__(self):
        super().__init__()

        self.database = Database()
        self.tasks = self.database.get_tasks()

        if not self.tasks:
            self._create_sample_tasks()

    # Expose database fields to QML
    def roleNames(self):
        return {
            self.IdRole: b"taskId",
            self.TitleRole: b"title",
            self.DescriptionRole: b"description",
            self.CategoryRole: b"category",
            self.BackgroundColorRole: b"backgroundColor",
            self.ImpactRole: b"impact",
            self.IconRole: b"taskIcon",
            self.CreatedAtRole: b"createdAt",
            self.CompletedRole: b"completed",
        }

    # Number of tasks in the model
    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0

        return len(self.tasks)

    # Return data for a particular task
    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid():
            return None

        if index.row() < 0 or index.row() >= len(self.tasks):
            return None

        task = self.tasks[index.row()]

        roles = {
            self.IdRole: task["id"],
            self.TitleRole: task["title"],
            self.DescriptionRole: task["description"],
            self.CategoryRole: task["category"],
            self.BackgroundColorRole: task["background_color"],
            self.ImpactRole: task["impact"],
            self.IconRole: task["icon"],
            self.CreatedAtRole: task["created_at"],
            self.CompletedRole: bool(task["completed"]),
        }

        return roles.get(role)

    # Save changes to the database
    def setData(self, index, value, role=Qt.ItemDataRole.EditRole):
        if not index.isValid():
            return False

        if index.row() < 0 or index.row() >= len(self.tasks):
            return False

        if role != self.CompletedRole:
            return False

        task = self.tasks[index.row()]
        completed = bool(value)

        if bool(task["completed"]) == completed:
            return True

        self.database.update_task_completion(
            task["id"],
            completed
        )

        task["completed"] = int(completed)

        self.dataChanged.emit(
            index,
            index,
            [self.CompletedRole]
        )

        return True

    # Function called from QML
    @Slot(int, bool)
    def setCompleted(self, task_id, completed):
        for row, task in enumerate(self.tasks):
            if task["id"] == task_id:
                return self.setData(
                    self.index(row, 0),
                    completed,
                    self.CompletedRole
                )

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

    # Create initial tasks if the database is empty
    def _create_sample_tasks(self):
        now = datetime.now(timezone.utc).isoformat()

        samples = [
            {
                "title": "Drink Water",
                "description": "Stay hydrated throughout the day.",
                "category": "Anytime",
                "background_color": "#DCEFE5",
                "impact": "High",
                "icon": "💧",
            },
            {
                "title": "Exercise",
                "description": "Get moving, even if it's just a walk.",
                "category": "Anytime",
                "background_color": "#DCEFE5",
                "impact": "Medium",
                "icon": "🏃",
            },
            {
                "title": "Read Something",
                "description": "Feed your mind.",
                "category": "Anytime",
                "background_color": "#FBE3D5",
                "impact": "Low",
                "icon": "📖",
            },
            {
                "title": "Prepare for Bed",
                "description": "Wind down for a good night's sleep.",
                "category": "Evening",
                "background_color": "#F9EDC9",
                "impact": "High",
                "icon": "🌙",
            },
        ]

        for task in samples:
            self.database.add_task(
                task["title"],
                task["description"],
                task["category"],
                task["background_color"],
                task["impact"],
                task["icon"],
                now,
            )

        self.beginResetModel()
        self.tasks = self.database.get_tasks()
        self.endResetModel()
