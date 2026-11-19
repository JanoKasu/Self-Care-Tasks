import json
import tempfile
import unittest
from pathlib import Path

from PySide6.QtGui import QGuiApplication

from src.weather_controller import WeatherController


class WeatherControllerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QGuiApplication.instance() or QGuiApplication([])

    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.data_dir = Path(self.temp_directory.name)

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_saved_location_is_loaded(self):
        (self.data_dir / "weather.json").write_text(
            json.dumps({
                "name": "Nashville, Tennessee, United States",
                "latitude": 36.16,
                "longitude": -86.78,
            }),
            encoding="utf-8",
        )

        controller = WeatherController(self.data_dir, auto_refresh=False)

        self.assertTrue(controller.hasLocation)
        self.assertEqual(
            controller.locationName,
            "Nashville, Tennessee, United States",
        )

    def test_select_location_persists_without_network(self):
        controller = WeatherController(self.data_dir, auto_refresh=False)

        # Avoid starting a real forecast request while testing persistence.
        controller._has_location = True
        controller._latitude = 36.16
        controller._longitude = -86.78
        controller._location_name = "Nashville"
        controller._save_location()

        saved = json.loads(
            (self.data_dir / "weather.json").read_text(encoding="utf-8")
        )
        self.assertEqual(saved["name"], "Nashville")
        self.assertEqual(saved["latitude"], 36.16)

    def test_forecast_payload_is_reduced_for_qml(self):
        payload = {
            "current": {
                "time": "2026-11-18T20:15",
                "temperature_2m": 54.6,
                "relative_humidity_2m": 68,
                "apparent_temperature": 52.2,
                "is_day": 0,
                "precipitation": 0,
                "weather_code": 3,
                "wind_speed_10m": 7.2,
            },
            "hourly": {
                "time": [
                    "2026-11-18T20:00",
                    "2026-11-18T21:00",
                ],
                "temperature_2m": [54.6, 53.1],
                "precipitation_probability": [10, 15],
                "weather_code": [3, 61],
            },
            "daily": {
                "time": ["2026-11-18", "2026-11-19"],
                "weather_code": [3, 1],
                "temperature_2m_max": [58.2, 61.4],
                "temperature_2m_min": [41.2, 43.1],
                "precipitation_probability_max": [10, 5],
            },
        }

        current, hourly, daily = WeatherController._parse_forecast(payload)

        self.assertEqual(current["temperature"], 55)
        self.assertEqual(current["description"], "Cloudy")
        self.assertEqual(hourly[0]["time"], "Now")
        self.assertEqual(hourly[1]["time"], "9 PM")
        self.assertEqual(daily[0]["day"], "Today")
        self.assertEqual(daily[1]["high"], 61)


if __name__ == "__main__":
    unittest.main()
