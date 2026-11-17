
import sqlite3
from pathlib import Path


class Database:
    def __init__(self):
        # Store the database in a persistent local data directory.
        project_dir = Path(__file__).resolve().parent.parent
        data_dir = project_dir / "data"
        data_dir.mkdir(parents=True, exist_ok=True)

        self.db_path = data_dir / "dashboard.db"

        self.initialize()

    def connect(self):
        connection = sqlite3.connect(self.db_path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self):
        with self.connect() as connection:
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

    def get_tasks(self):
        with self.connect() as connection:
            rows = connection.execute(
                "SELECT * FROM tasks ORDER BY id"
            ).fetchall()

            return [dict(row) for row in rows]

    def update_task_completion(self, task_id, completed):
        with self.connect() as connection:
            connection.execute(
                """
                UPDATE tasks
                SET completed = ?
                WHERE id = ?
                """,
                (int(completed), task_id)
            )

    def add_task(self, title, description, category,
                 background_color, impact, icon, created_at):
        with self.connect() as connection:
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

            return cursor.lastrowid
