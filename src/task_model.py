
from datetime import datetime, timedelta, timezone
import random

from PySide6.QtCore import (
    QAbstractListModel,
    QModelIndex,
    Property,
    QTimer,
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

    def __init__(self, database=None):
        super().__init__()
        self.database = database or Database()
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


class TaskAttentionModel(QAbstractListModel):
    countChanged = Signal()

    TaskIdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = TaskIdRole + 1
    DescriptionRole = TitleRole + 1
    BackgroundColorRole = DescriptionRole + 1
    ImpactRole = BackgroundColorRole + 1
    IconRole = ImpactRole + 1
    FrequencyRole = IconRole + 1
    MissedRole = FrequencyRole + 1
    CompletionRateRole = MissedRole + 1

    def __init__(self, database=None):
        super().__init__()
        self.database = database or Database()
        self.entries = self.database.get_attention_tasks()

    def roleNames(self):
        return {
            self.TaskIdRole: b"taskId",
            self.TitleRole: b"title",
            self.DescriptionRole: b"description",
            self.BackgroundColorRole: b"backgroundColor",
            self.ImpactRole: b"impact",
            self.IconRole: b"taskIcon",
            self.FrequencyRole: b"frequency",
            self.MissedRole: b"missed",
            self.CompletionRateRole: b"completionRate",
        }

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else len(self.entries)

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or not 0 <= index.row() < len(self.entries):
            return None
        entry = self.entries[index.row()]
        return {
            self.TaskIdRole: entry["task_id"],
            self.TitleRole: entry["title"],
            self.DescriptionRole: entry["description"],
            self.BackgroundColorRole: entry["background_color"],
            self.ImpactRole: entry["impact"],
            self.IconRole: entry["icon"],
            self.FrequencyRole: entry["frequency"],
            self.MissedRole: entry["missed"],
            self.CompletionRateRole: entry["completion_rate"],
        }.get(role)

    @Property(int, notify=countChanged)
    def count(self):
        return len(self.entries)

    def refresh(self):
        self.beginResetModel()
        self.entries = self.database.get_attention_tasks()
        self.endResetModel()
        self.countChanged.emit()


class TaskModel(QAbstractListModel):
    countChanged = Signal()
    completedCountChanged = Signal()
    progressChanged = Signal()
    xpChanged = Signal()
    rewardEarned = Signal(int, int, bool)
    statsChanged = Signal()

    IdRole = Qt.ItemDataRole.UserRole + 1
    TitleRole = IdRole + 1
    DescriptionRole = IdRole + 2
    CategoryRole = IdRole + 3
    BackgroundColorRole = IdRole + 4
    ImpactRole = IdRole + 5
    IconRole = IdRole + 6
    CreatedAtRole = IdRole + 7
    CompletedRole = IdRole + 8
    PointsRole = IdRole + 9
    FrequencyRole = IdRole + 10
    DurationStartedAtRole = IdRole + 11

    XP_PER_LEVEL = 100
    TASK_EMOJIS = (
        "🌿",
        "💧",
        "🧘",
        "🚶",
        "🍎",
        "🌞",
        "🛁",
        "🦷",
        "📖",
        "😴",
        "🧹",
        "🫶",
        "🎨",
        "🌙",
        "🫧",
        "☀️",
    )

    def __init__(self, history_model=None, attention_model=None, database=None):
        super().__init__()

        self.database = database or Database()
        self.tasks = self.database.get_tasks()
        self.history_model = history_model
        self.attention_model = attention_model
        self.total_xp = self.database.get_total_xp()
        self.stats = self.database.get_progress_stats()
        self.period_timer = QTimer(self)
        self.period_timer.setSingleShot(True)
        self.period_timer.timeout.connect(self.refreshPeriods)
        self._schedule_period_refresh()

    def _schedule_period_refresh(self):
        now = datetime.now().astimezone()
        reset_times = [
            self.database.next_period_start(task["frequency"], now)
            for task in self.tasks
            if task["frequency"] != "As needed"
        ]
        reset_times = [value for value in reset_times if value is not None]
        if not reset_times:
            self.period_timer.stop()
            return

        next_reset = min(reset_times)
        self.period_timer.start(
            max(1000, int((next_reset - now).total_seconds() * 1000))
        )

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
            self.DurationStartedAtRole: b"durationStartedAt",
            self.CompletedRole: b"completed",
            self.PointsRole: b"points",
            self.FrequencyRole: b"frequency",
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
            self.DurationStartedAtRole: self._duration_started_at(task),
            self.CompletedRole: bool(task["completed"]),
            self.PointsRole: self.database.XP_BY_IMPACT.get(task["impact"], 10),
            self.FrequencyRole: task["frequency"],
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

        old_level = self.level
        awarded_points = self.database.update_task_completion(
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
        self.stats = self.database.get_progress_stats()
        self.statsChanged.emit()

        if awarded_points:
            self.total_xp += awarded_points
            self.xpChanged.emit()
            self.rewardEarned.emit(
                awarded_points,
                self.level,
                self.level > old_level,
            )

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
                if updated and self.attention_model is not None:
                    self.attention_model.refresh()
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

    @Property(int, notify=xpChanged)
    def xp(self):
        return self.total_xp

    @Property(int, notify=xpChanged)
    def level(self):
        return self.total_xp // self.XP_PER_LEVEL + 1

    @Property(int, notify=xpChanged)
    def levelProgress(self):
        return self.total_xp % self.XP_PER_LEVEL

    @Property(int, notify=xpChanged)
    def pointsToNextLevel(self):
        return self.XP_PER_LEVEL - self.levelProgress

    @Slot()
    def refreshPeriods(self):
        try:
            self.database.reset_expired_tasks()
            self.beginResetModel()
            self.tasks = self.database.get_tasks()
            self.endResetModel()
            self.completedCountChanged.emit()
            self.progressChanged.emit()
            self.stats = self.database.get_progress_stats()
            self.statsChanged.emit()
            if self.attention_model is not None:
                self.attention_model.refresh()
        finally:
            self._schedule_period_refresh()

    @Property(int, notify=statsChanged)
    def totalCompletions(self):
        return self.stats["total_completions"]

    @Property(int, notify=statsChanged)
    def activeDays(self):
        return self.stats["active_days"]

    @Property(int, notify=statsChanged)
    def currentStreak(self):
        return self.stats["current_streak"]

    @Property(int, notify=statsChanged)
    def bestStreak(self):
        return self.stats["best_streak"]

    @Property(int, notify=statsChanged)
    def completionRate(self):
        return self.stats["completion_rate"]

    @Slot(str, str, str, str, str, str)
    def addTask(self, title, description, category,
                background_color, impact, icon):
        return self._add_task(
            title,
            description,
            category,
            background_color,
            impact,
            icon,
            "Daily",
        )

    @Slot(str, str, str, str, str, str, str)
    def addTaskWithFrequency(self, title, description, category,
                             background_color, impact, icon, frequency):
        return self._add_task(
            title,
            description,
            category,
            background_color,
            impact,
            icon,
            frequency,
        )

    def _add_task(self, title, description, category,
                  background_color, impact, icon, frequency):
        title = title.strip()
        if not title:
            return False

        now = datetime.now(timezone.utc).isoformat()
        if not icon.strip():
            icon = random.choice(self.TASK_EMOJIS)
        task_id = self.database.add_task(
            title,
            description.strip(),
            category,
            background_color,
            impact,
            icon,
            now,
            frequency,
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
            "frequency": frequency,
        })
        self.endInsertRows()
        self.countChanged.emit()
        self.progressChanged.emit()
        if self.attention_model is not None:
            self.attention_model.refresh()
        self._schedule_period_refresh()
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
                self.stats = self.database.get_progress_stats()
                self.statsChanged.emit()
                if self.history_model is not None:
                    self.history_model.refresh()
                if self.attention_model is not None:
                    self.attention_model.refresh()
                self._schedule_period_refresh()
                return True

        return False

    def _duration_started_at(self, task):
        created = datetime.fromisoformat(task["created_at"]).astimezone()
        if task["frequency"] == "As needed":
            return created.isoformat()

        period_start = self.database.current_period_start(task["frequency"])
        return max(created, period_start).isoformat()

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
