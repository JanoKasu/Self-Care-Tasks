import gc
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from src.database import Database
from src.task_model import TaskModel


class DatabaseTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database = Database()
        self.database.db_path = Path(self.temp_directory.name) / "test.db"
        self.database.initialize()

    def tearDown(self):
        gc.collect()
        self.temp_directory.cleanup()

    def test_add_task_writes_and_reads_all_fields(self):
        task_id = self.database.add_task(
            "Drink water",
            "Have a glass",
            "Health",
            "#ffffff",
            "Medium",
            "water",
            "2026-11-17T12:00:00+00:00",
        )

        tasks = self.database.get_tasks()

        self.assertEqual(len(tasks), 1)
        self.assertEqual(tasks[0]["id"], task_id)
        self.assertEqual(tasks[0]["title"], "Drink water")
        self.assertEqual(tasks[0]["description"], "Have a glass")
        self.assertEqual(tasks[0]["completed"], 0)

    def test_completion_update_and_delete_are_persisted(self):
        task_id = self.database.add_task(
            "Stretch",
            "Shoulders and back",
            "Movement",
            "#abcdef",
            "High",
            "stretch",
            "2026-11-17T12:00:00+00:00",
        )

        self.database.update_task_completion(task_id, True)
        tasks = self.database.get_tasks()
        self.assertEqual(tasks[0]["completed"], 1)

        self.database.delete_task(task_id)

        self.assertEqual(self.database.get_tasks(), [])

    def test_completion_history_is_persisted(self):
        task_id = self.database.add_task(
            "Meditate",
            "Five quiet minutes",
            "Mindfulness",
            "#ffffff",
            "High",
            "meditate",
            "2026-11-17T12:00:00+00:00",
        )

        self.database.update_task_completion(task_id, True)
        history = self.database.get_completion_history()

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["task_id"], task_id)
        self.assertEqual(history[0]["title"], "Meditate")
        self.assertEqual(history[0]["completion_count"], 1)

    def test_completion_history_groups_by_task_and_excludes_old_data(self):
        task_id = self.database.add_task(
            "Meditate",
            "Five quiet minutes",
            "Mindfulness",
            "#ffffff",
            "High",
            "meditate",
            "2026-11-17T12:00:00+00:00",
        )

        self.database.update_task_completion(task_id, True)
        self.database.update_task_completion(task_id, True)

        history = self.database.get_completion_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["completion_count"], 2)

        with self.database.connect() as connection:
            connection.execute(
                "UPDATE task_completions SET completed_at = ?",
                ("2025-01-01T12:00:00+00:00",),
            )
            connection.commit()

        self.assertEqual(self.database.get_completion_history(), [])

    def test_task_model_rejects_blank_title(self):
        import src.task_model as task_model_module

        original_database = task_model_module.Database
        task_model_module.Database = lambda: self.database
        try:
            model = TaskModel()
            result = model.addTask(
                "   ",
                "Description",
                "Health",
                "#ffffff",
                "Low",
                "test",
            )
        finally:
            task_model_module.Database = original_database

        self.assertFalse(result)
        self.assertEqual(model.count, 0)

    def test_frozen_app_uses_writable_user_data_directory(self):
        with patch(
            "src.database.sys.frozen",
            True,
            create=True,
        ), patch.dict(
            os.environ,
            {"XDG_DATA_HOME": self.temp_directory.name},
        ):
            self.assertEqual(
                Database.default_data_dir(),
                Path(self.temp_directory.name) / "self-care-tasks",
            )


if __name__ == "__main__":
    unittest.main()
