
import sqlite3
from contextlib import closing
from datetime import date, datetime, timedelta, timezone
from pathlib import Path


class Database:
    XP_BY_IMPACT = {
        "Low": 10,
        "Medium": 20,
        "High": 30,
    }

    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = self.default_data_dir()

        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = data_dir / "dashboard.db"

        self.initialize()

    @staticmethod
    def default_data_dir():
        return Path(__file__).resolve().parent.parent / "data"

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with closing(self.connect()) as connection:
            connection.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    description TEXT DEFAULT '',
                    category TEXT NOT NULL,
                    background_color TEXT NOT NULL,
                    impact TEXT NOT NULL,
                    icon TEXT DEFAULT '',
                    created_at TEXT NOT NULL,
                    completed INTEGER DEFAULT 0,
                    frequency TEXT DEFAULT 'Daily',
                    completed_period TEXT DEFAULT ''
                )
            """)
            task_columns = {
                row["name"]
                for row in connection.execute("PRAGMA table_info(tasks)")
            }
            if "frequency" not in task_columns:
                connection.execute(
                    "ALTER TABLE tasks ADD COLUMN frequency TEXT DEFAULT 'Daily'"
                )
            if "completed_period" not in task_columns:
                connection.execute(
                    "ALTER TABLE tasks ADD COLUMN completed_period TEXT DEFAULT ''"
                )
            connection.execute("""
                CREATE TABLE IF NOT EXISTS task_completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    completed_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS task_xp (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    earned_on TEXT NOT NULL,
                    points INTEGER NOT NULL,
                    UNIQUE(task_id, earned_on)
                )
            """)
            connection.execute("""
                INSERT OR IGNORE INTO task_xp (task_id, earned_on, points)
                SELECT
                    c.task_id,
                    DATE(c.completed_at, 'localtime'),
                    MAX(
                        CASE t.impact
                            WHEN 'High' THEN 30
                            WHEN 'Medium' THEN 20
                            ELSE 10
                        END
                    )
                FROM task_completions AS c
                JOIN tasks AS t ON t.id = c.task_id
                GROUP BY c.task_id, DATE(c.completed_at, 'localtime')
            """)
            connection.execute(
                "UPDATE tasks SET frequency = 'Daily' "
                "WHERE frequency IS NULL OR frequency = ''"
            )
            current_daily = self.current_period("Daily")
            current_weekly = self.current_period("Weekly")
            connection.execute(
                """
                UPDATE tasks
                SET completed_period = CASE
                    WHEN frequency = 'Weekly' THEN ?
                    ELSE ?
                END
                WHERE completed = 1
                  AND (completed_period IS NULL OR completed_period = '')
                """,
                (current_weekly, current_daily),
            )
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            connection.execute(
                "DELETE FROM task_completions WHERE completed_at < ?",
                (cutoff,)
            )
            connection.commit()
        self.reset_expired_tasks()

    def reset_expired_tasks(self):
        with closing(self.connect()) as connection:
            tasks = connection.execute(
                "SELECT id, frequency, completed_period FROM tasks "
                "WHERE completed = 1 AND frequency != 'As needed'"
            ).fetchall()
            expired_ids = [
                task["id"]
                for task in tasks
                if task["completed_period"] != self.current_period(task["frequency"])
            ]
            connection.executemany(
                "UPDATE tasks SET completed = 0 WHERE id = ?",
                [(task_id,) for task_id in expired_ids],
            )
            connection.commit()
        return bool(expired_ids)

    @staticmethod
    def current_period(frequency, value=None):
        current_date = (value or datetime.now().astimezone().date())
        if frequency == "Weekly":
            week_start = current_date - timedelta(days=current_date.weekday())
            return week_start.isoformat()
        if frequency == "As needed":
            return "ongoing"
        return current_date.isoformat()

    def get_tasks(self):
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY id"
            ).fetchall()

            return [dict(row) for row in rows]

    def update_task_completion(self, task_id, completed):
        with closing(self.connect()) as connection:
            completed_at = datetime.now(timezone.utc)
            task = connection.execute(
                "SELECT impact, frequency, completed_period "
                "FROM tasks WHERE id = ?",
                (task_id,)
            ).fetchone()
            if task is None:
                return 0
            completed_period = self.current_period(task["frequency"])
            connection.execute(
                """
                UPDATE tasks
                SET completed = ?, completed_period = ?
                WHERE id = ?
                """,
                (
                    int(completed),
                    completed_period if completed else task["completed_period"],
                    task_id,
                )
            )
            if completed:
                points = self.XP_BY_IMPACT.get(
                    task["impact"] if task is not None else "",
                    self.XP_BY_IMPACT["Low"],
                )
                award = connection.execute(
                    """
                    INSERT OR IGNORE INTO task_xp (task_id, earned_on, points)
                    VALUES (?, ?, ?)
                    """,
                    (
                        task_id,
                        completed_period,
                        points,
                    )
                )
                awarded_points = points if award.rowcount else 0
                if awarded_points:
                    connection.execute(
                        """
                        INSERT INTO task_completions (task_id, completed_at)
                        VALUES (?, ?)
                        """,
                        (task_id, completed_at.isoformat())
                    )
            else:
                awarded_points = 0

            connection.commit()
            return awarded_points

    def get_progress_stats(self):
        today = datetime.now().astimezone().date()
        with closing(self.connect()) as connection:
            completion_dates = [
                date.fromisoformat(row["earned_on"])
                for row in connection.execute(
                    "SELECT DISTINCT DATE(completed_at, 'localtime') AS earned_on "
                    "FROM task_completions "
                    "ORDER BY earned_on"
                )
                if row["earned_on"] is not None
            ]
            total_completions = connection.execute(
                "SELECT COUNT(*) AS count FROM task_completions"
            ).fetchone()["count"]
            scheduled = self._schedule_performance(connection, today)

        unique_dates = set(completion_dates)
        streak_cursor = today if today in unique_dates else today - timedelta(days=1)
        current_streak = 0
        while streak_cursor in unique_dates:
            current_streak += 1
            streak_cursor -= timedelta(days=1)

        best_streak = 0
        running_streak = 0
        previous = None
        for completed_on in sorted(unique_dates):
            if previous is not None and completed_on == previous + timedelta(days=1):
                running_streak += 1
            else:
                running_streak = 1
            best_streak = max(best_streak, running_streak)
            previous = completed_on

        expected = sum(item["expected"] for item in scheduled)
        completed = sum(min(item["completed"], item["expected"]) for item in scheduled)
        return {
            "total_completions": total_completions,
            "active_days": len(unique_dates),
            "current_streak": current_streak,
            "best_streak": best_streak,
            "completion_rate": round(completed * 100 / expected) if expected else 0,
        }

    def _schedule_performance(self, connection, today):
        tasks = connection.execute(
            "SELECT id, title, description, background_color, impact, icon, "
            "frequency, created_at FROM tasks "
            "WHERE frequency != 'As needed' ORDER BY id"
        ).fetchall()
        completions = {}
        for row in connection.execute(
            "SELECT task_id, DATE(completed_at, 'localtime') AS completed_on "
            "FROM task_completions"
        ):
            completions.setdefault(row["task_id"], set()).add(row["completed_on"])

        results = []
        thirty_days_ago = today - timedelta(days=29)
        for task in tasks:
            created = datetime.fromisoformat(task["created_at"]).astimezone().date()
            if task["frequency"] == "Weekly":
                current_week = today - timedelta(days=today.weekday())
                period = max(
                    created - timedelta(days=created.weekday()),
                    current_week - timedelta(weeks=4),
                )
                periods = []
                while period < current_week:
                    periods.append(period.isoformat())
                    period += timedelta(weeks=1)
                completed_periods = {
                    self.current_period(
                        "Weekly",
                        date.fromisoformat(completed_on),
                    )
                    for completed_on in completions.get(task["id"], set())
                    if completed_on is not None
                }
            else:
                period = max(created, thirty_days_ago)
                periods = []
                while period < today:
                    periods.append(period.isoformat())
                    period += timedelta(days=1)
                completed_periods = completions.get(task["id"], set())

            completed = len(set(periods) & completed_periods)
            expected = len(periods)
            missed = max(0, expected - completed)
            results.append({
                "task_id": task["id"],
                "title": task["title"],
                "description": task["description"],
                "background_color": task["background_color"],
                "impact": task["impact"],
                "icon": task["icon"],
                "frequency": task["frequency"],
                "expected": expected,
                "completed": completed,
                "missed": missed,
                "completion_rate": (
                    round(completed * 100 / expected) if expected else 100
                ),
            })

        return results

    def get_attention_tasks(self):
        with closing(self.connect()) as connection:
            entries = self._schedule_performance(
                connection,
                datetime.now().astimezone().date(),
            )
        return sorted(
            (entry for entry in entries if entry["missed"] > 0),
            key=lambda entry: (-entry["missed"], entry["completion_rate"]),
        )

    def get_total_xp(self):
        with closing(self.connect()) as connection:
            row = connection.execute(
                "SELECT COALESCE(SUM(points), 0) AS points FROM task_xp"
            ).fetchone()
            return row["points"]

    def get_completion_history(self):
        cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
        with closing(self.connect()) as connection:
            connection.execute(
                "DELETE FROM task_completions WHERE completed_at < ?",
                (cutoff,)
            )
            connection.commit()

            rows = connection.execute(
                """
                SELECT
                    c.task_id,
                    t.title,
                    t.description,
                    t.category,
                    t.background_color,
                    t.impact,
                    t.icon,
                    COUNT(*) AS completion_count,
                    MAX(c.completed_at) AS last_completed_at
                FROM task_completions AS c
                JOIN tasks AS t ON t.id = c.task_id
                WHERE c.completed_at >= ?
                GROUP BY
                    c.task_id,
                    t.title,
                    t.description,
                    t.category,
                    t.background_color,
                    t.impact,
                    t.icon
                ORDER BY last_completed_at DESC
                """
                ,
                (cutoff,)
            ).fetchall()

            return [dict(row) for row in rows]

    def add_task(self, title, description, category,
                 background_color, impact, icon, created_at, frequency="Daily"):
        with closing(self.connect()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    title, description, category,
                    background_color, impact, icon,
                    created_at, completed, frequency, completed_period
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0, ?, '')
                """,
                (
                    title, description, category,
                    background_color, impact, icon,
                    created_at, frequency
                )
            )
            connection.commit()

            return cursor.lastrowid

    def delete_task(self, task_id):
        with closing(self.connect()) as connection:
            connection.execute(
                "DELETE FROM task_completions WHERE task_id = ?",
                (task_id,)
            )
            connection.execute(
                "DELETE FROM tasks WHERE id = ?",
                (task_id,)
            )
            connection.commit()
