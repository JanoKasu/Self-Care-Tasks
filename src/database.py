
import sqlite3
import os
import sys
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path


class Database:
    def __init__(self, data_dir=None):
        if data_dir is None:
            data_dir = self.default_data_dir()

        data_dir = Path(data_dir)
        data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = data_dir / "dashboard.db"

        self.initialize()

    @staticmethod
    def default_data_dir():
        if getattr(sys, "frozen", False):
            data_home = os.environ.get(
                "XDG_DATA_HOME",
                str(Path.home() / ".local" / "share"),
            )
            return Path(data_home) / "self-care-tasks"

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
                    completed INTEGER DEFAULT 0
                )
            """)
            connection.execute("""
                CREATE TABLE IF NOT EXISTS task_completions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task_id INTEGER NOT NULL,
                    completed_at TEXT NOT NULL,
                    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE
                )
            """)
            cutoff = (datetime.now(timezone.utc) - timedelta(days=30)).isoformat()
            connection.execute(
                "DELETE FROM task_completions WHERE completed_at < ?",
                (cutoff,)
            )
            connection.commit()

    def get_tasks(self):
        with closing(self.connect()) as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY id"
            ).fetchall()

            return [dict(row) for row in rows]

    def update_task_completion(self, task_id, completed):
        with closing(self.connect()) as connection:
            connection.execute(
                """
                UPDATE tasks
                SET completed = ?
                WHERE id = ?
                """,
                (int(completed), task_id)
            )
            if completed:
                connection.execute(
                    """
                    INSERT INTO task_completions (task_id, completed_at)
                    VALUES (?, ?)
                    """,
                    (task_id, datetime.now(timezone.utc).isoformat())
                )
            connection.commit()

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
                 background_color, impact, icon, created_at):
        with closing(self.connect()) as connection:
            cursor = connection.execute(
                """
                INSERT INTO tasks (
                    title, description, category,
                    background_color, impact, icon,
                    created_at, completed
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, 0)
                """,
                (
                    title, description, category,
                    background_color, impact, icon,
                    created_at
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
