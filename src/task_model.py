
from datetime import datetime, timezone

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Property,
    Signal,
    Qt,
    Slot,
)

from src.database import Database


class CompletionHistoryModel(QAbstractListModel):
    countChanged = Signal()

    TaskIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = TaskIdRole + 1
    DescriptionRole = TitleRole + 1
    CategoryRole = DescriptionRole + 1
    BackgroundColorRole = CategoryRole + 1
    ImpactRole = BackgroundColorRole + 1
    IconRole = ImpactRole + 1
    CompletionCountRole = IconRole + 1
    LastCompletedAtRole = CompletionCountRole + 1

    def __init__(self):
        super().__init__()
        self.database = Database()
        self.entries = self.database.get_completion_history()

    def roleNames(self):
        return {
            self.TaskIdRole: b"taskId",
            self.TitleRole: b"title",
            self.DescriptionRole: b"description",
            self.CategoryRole: b"category",
            self.BackgroundColorRole: b"backgroundColor",
            self.ImpactRole: b"impact",
            self.IconRole: b"taskIcon",
            self.CompletionCountRole: b"completionCount",
            self.LastCompletedAtRole: b"lastCompletedAt",
        }

    def rowCount(self, parent=QModelIndex()):
        if parent.isValid():
            return 0
        return len(self.entries)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.entries):
            return None

        entry = self.entries[index.row()]
        roles = {
            self.TaskIdRole: entry["task_id"],
            self.TitleRole: entry["title"],
            self.DescriptionRole: entry["description"],
            self.CategoryRole: entry["category"],
            self.BackgroundColorRole: entry["background_color"],
            self.ImpactRole: entry["impact"],
            self.IconRole: entry["icon"],
            self.CompletionCountRole: entry["completion_count"],
            self.LastCompletedAtRole: entry["last_completed_at"],
        }
        return roles.get(role)

    @Property(int, notify=countChanged)
    def count(self):
        return len(self.entries)

    def refresh(self):
        self.beginResetModel()
        self.entries = self.database.get_completion_history()
        self.endResetModel()
        self.countChanged.emit()


class TaskModel(QAbstractListModel):
    countChanged = Signal()
    completedCountChanged = Signal()
    progressChanged = Signal()

    IdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = IdRole + 1
    DescriptionRole = IdRole + 2
    CategoryRole = IdRole + 3
    BackgroundColorRole = IdRole + 4
    ImpactRole = IdRole + 5
    IconRole = IdRole + 6
    CreatedAtRole = IdRole + 7
    CompletedRole = IdRole + 8

    def __init__(self, history_model=None):
        super().__init__()

        self.database = Database()
        self.tasks = self.database.get_tasks()
        self.history_model = history_model

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
        self.completedCountChanged.emit()
        self.progressChanged.emit()

        return True

    # Function called from QML
    @Slot(int, bool)
    def setCompleted(self, task_id, completed):
        for row, task in enumerate(self.tasks):
            if task["id"] == task_id:
                updated = self.setData(
                    self.index(row, 0),
                    completed,
                    self.CompletedRole
                )
                if updated and completed and self.history_model is not None:
                    self.history_model.refresh()
                return updated

        return False

    @Property(int, notify=countChanged)
    def count(self):
        return len(self.tasks)

    @Property(int, notify=completedCountChanged)
    def completedCount(self):
        return sum(1 for task in self.tasks if task["completed"])

    @Property(int, notify=progressChanged)
    def progress(self):
        if not self.tasks:
            return 0

        return round(self.completedCount * 100 / len(self.tasks))

    @Slot(str, str, str, str, str, str)
    def addTask(self, title, description, category,
                background_color, impact, icon):
        title = title.strip()
        if not title:
            return False

        now = datetime.now(timezone.utc).isoformat()
        task_id = self.database.add_task(
            title,
            description.strip(),
            category,
            background_color,
            impact,
            icon,
            now,
        )

        self.beginInsertRows(QModelIndex(), len(self.tasks), len(self.tasks))
        self.tasks.append({
            "id": task_id,
            "title": title,
            "description": description.strip(),
            "category": category,
            "background_color": background_color,
            "impact": impact,
            "icon": icon,
            "created_at": now,
            "completed": 0,
        })
        self.endInsertRows()
        self.countChanged.emit()
        self.progressChanged.emit()
        return True

    @Slot(int)
    def deleteTask(self, task_id):
        for row, task in enumerate(self.tasks):
            if task["id"] == task_id:
                self.beginRemoveRows(QModelIndex(), row, row)
                self.database.delete_task(task_id)
                del self.tasks[row]
                self.endRemoveRows()
                self.countChanged.emit()
                self.completedCountChanged.emit()
                self.progressChanged.emit()
                return True

        return False

    def flags(self, index):
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags

        return (
            Qt.ItemFlag.ItemIsEnabled
            | Qt.ItemFlag.ItemIsSelectable
            | Qt.ItemFlag.ItemIsEditable
        )

        self.countChanged.emit()
        self.completedCountChanged.emit()
        self.progressChanged.emit()
