import gc
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

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
        with closing(self.database.connect()) as connection:
            connection.execute(
                "INSERT INTO task_completions (task_id, completed_at) "
                "VALUES (?, ?)",
                (
                    task_id,
                    (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
                ),
            )
            connection.commit()

        history = self.database.get_completion_history()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["completion_count"], 2)

        with closing(self.database.connect()) as connection:
            connection.execute(
                "UPDATE task_completions SET completed_at = ?",
                ("2025-01-01T12:00:00+00:00",),
            )
            connection.commit()

        self.assertEqual(self.database.get_completion_history(), [])

    def test_completion_awards_persistent_xp_once_per_task_per_day(self):
        task_id = self.database.add_task(
            "Go for a walk",
            "Step outside for ten minutes",
            "Movement",
            "#abcdef",
            "High",
            "walk",
            "2026-11-17T12:00:00+00:00",
        )

        self.assertEqual(
            self.database.update_task_completion(task_id, True),
            30,
        )
        self.assertEqual(self.database.get_total_xp(), 30)

        self.database.update_task_completion(task_id, False)
        self.assertEqual(
            self.database.update_task_completion(task_id, True),
            0,
        )
        self.assertEqual(self.database.get_total_xp(), 30)
        reloaded_database = Database()
        reloaded_database.db_path = self.database.db_path
        reloaded_database.initialize()
        self.assertEqual(reloaded_database.get_total_xp(), 30)

    def test_frequency_is_persisted_and_drives_attention(self):
        created_at = (
            datetime.now(timezone.utc) - timedelta(days=3)
        ).isoformat()
        daily_id = self.database.add_task(
            "Brush teeth",
            "Morning and evening",
            "Health",
            "#ffffff",
            "Low",
            "tooth",
            created_at,
            "Daily",
        )
        self.database.add_task(
            "Read when relaxed",
            "Optional",
            "Wellbeing",
            "#ffffff",
            "Medium",
            "book",
            created_at,
            "As needed",
        )

        attention = self.database.get_attention_tasks()
        self.assertEqual(len(attention), 1)
        self.assertEqual(attention[0]["task_id"], daily_id)
        self.assertEqual(attention[0]["frequency"], "Daily")
        self.assertGreaterEqual(attention[0]["missed"], 2)

    def test_expired_daily_completion_is_reset_on_startup(self):
        task_id = self.database.add_task(
            "Daily stretch",
            "Move for five minutes",
            "Movement",
            "#ffffff",
            "Medium",
            "stretch",
            (datetime.now(timezone.utc) - timedelta(days=1)).isoformat(),
            "Daily",
        )
        with closing(self.database.connect()) as connection:
            connection.execute(
                "UPDATE tasks SET completed = 1, completed_period = ? "
                "WHERE id = ?",
                (
                    (datetime.now().astimezone().date() - timedelta(days=1))
                    .isoformat(),
                    task_id,
                ),
            )
            connection.commit()

        self.database.initialize()

        task = self.database.get_tasks()[0]
        self.assertEqual(task["completed"], 0)

    def test_task_model_tracks_xp_level_and_next_level_progress(self):
        import src.task_model as task_model_module

        task_ids = []
        for index, impact in enumerate(("High", "High", "High", "Medium")):
            task_ids.append(self.database.add_task(
                f"Task {index}",
                "Self care",
                "Wellness",
                "#ffffff",
                impact,
                "care",
                "2026-11-17T12:00:00+00:00",
            ))

        original_database = task_model_module.Database
        task_model_module.Database = lambda: self.database
        try:
            model = TaskModel()
            for task_id in task_ids:
                model.setCompleted(task_id, True)
        finally:
            task_model_module.Database = original_database

        self.assertEqual(model.xp, 110)
        self.assertEqual(model.level, 2)
        self.assertEqual(model.levelProgress, 10)
        self.assertEqual(model.pointsToNextLevel, 90)
        self.assertEqual(
            model.data(model.index(0, 0), TaskModel.PointsRole),
            30,
        )

    def test_task_model_exposes_frequency(self):
        import src.task_model as task_model_module

        original_database = task_model_module.Database
        task_model_module.Database = lambda: self.database
        try:
            model = TaskModel()
            model.addTaskWithFrequency(
                "Brush teeth",
                "Morning and evening",
                "Health",
                "#ffffff",
                "Low",
                "tooth",
                "Daily",
            )
        finally:
            task_model_module.Database = original_database

        self.assertEqual(
            model.data(model.index(0, 0), TaskModel.FrequencyRole),
            "Daily",
        )

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

if __name__ == "__main__":
    unittest.main()
