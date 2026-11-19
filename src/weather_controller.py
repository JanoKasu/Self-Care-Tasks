import json
from datetime import datetime
from pathlib import Path

from PySide6.QtCore import (
    Property,
    QObject,
    QTimer,
    QUrl,
    QUrlQuery,
    Signal,
    Slot,
)
from PySide6.QtNetwork import QNetworkAccessManager, QNetworkReply, QNetworkRequest

from src.database import Database


class WeatherController(QObject):
    changed = Signal()
    busyChanged = Signal()
    requestFailed = Signal(str)

    WEATHER_URL = "https://api.open-meteo.com/v1/forecast"
    GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"

    def __init__(self, data_dir=None, parent=None, auto_refresh=True):
        super().__init__(parent)
        self.manager = QNetworkAccessManager(self)
        self.manager.finished.connect(self._request_finished)
        self.settings_path = (
            Path(data_dir or Database.default_data_dir()) / "weather.json"
        )
        self._busy = False
        self._status = "Choose a city to load the forecast."
        self._location_name = ""
        self._latitude = None
        self._longitude = None
        self._search_results = []
        self._current = {}
        self._hourly = []
        self._daily = []
        self._has_location = False

        self.refresh_timer = QTimer(self)
        self.refresh_timer.setInterval(15 * 60 * 1000)
        self.refresh_timer.timeout.connect(self.refresh)

        self._load_location()
        if self._has_location:
            if auto_refresh:
                self.refresh()
                self.refresh_timer.start()

    @Property(bool, notify=changed)
    def hasLocation(self):
        return self._has_location

    @Property(bool, notify=busyChanged)
    def busy(self):
        return self._busy

    @Property(str, notify=changed)
    def status(self):
        return self._status

    @Property(str, notify=changed)
    def locationName(self):
        return self._location_name

    @Property("QVariantList", notify=changed)
    def searchResults(self):
        return self._search_results

    @Property("QVariantMap", notify=changed)
    def current(self):
        return self._current

    @Property("QVariantList", notify=changed)
    def hourly(self):
        return self._hourly

    @Property("QVariantList", notify=changed)
    def daily(self):
        return self._daily

    def _set_busy(self, busy):
        if self._busy == busy:
            return
        self._busy = busy
        self.busyChanged.emit()

    def _load_location(self):
        if not self.settings_path.exists():
            return
        try:
            location = json.loads(self.settings_path.read_text(encoding="utf-8"))
            self._latitude = float(location["latitude"])
            self._longitude = float(location["longitude"])
            self._location_name = str(location["name"])
            self._has_location = True
            self._status = "Loading forecast..."
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, OSError) as exc:
            self._status = f"Weather location could not be loaded: {exc}"
            self.requestFailed.emit(self._status)

    def _save_location(self):
        self.settings_path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = self.settings_path.with_suffix(".tmp")
        temporary_path.write_text(
            json.dumps({
                "name": self._location_name,
                "latitude": self._latitude,
                "longitude": self._longitude,
            }),
            encoding="utf-8",
        )
        temporary_path.replace(self.settings_path)

    @Slot(str)
    def search(self, city):
        city = city.strip()
        if not city:
            self._search_results = []
            self.changed.emit()
            return

        url = QUrl(self.GEOCODING_URL)
        query = QUrlQuery()
        query.addQueryItem("name", city)
        query.addQueryItem("count", "6")
        query.addQueryItem("language", "en")
        query.addQueryItem("format", "json")
        url.setQuery(query)
        self._set_busy(True)
        self._status = f"Searching for {city}..."
        self.changed.emit()
        reply = self.manager.get(QNetworkRequest(url))
        reply.setProperty("weatherRequest", "search")

    @Slot(float, float, str)
    def selectLocation(self, latitude, longitude, name):
        self._latitude = latitude
        self._longitude = longitude
        self._location_name = name.strip()
        self._has_location = True
        try:
            self._save_location()
        except OSError as exc:
            self._status = f"Location selected, but could not be saved: {exc}"
            self.requestFailed.emit(self._status)
            self.changed.emit()
        self._search_results = []
        self.refresh_timer.start()
        self.refresh()

    @Slot()
    def refresh(self):
        if not self._has_location:
            self._status = "Choose a city to load the forecast."
            self.changed.emit()
            return

        url = QUrl(self.WEATHER_URL)
        query = QUrlQuery()
        parameters = {
            "latitude": str(self._latitude),
            "longitude": str(self._longitude),
            "current": (
                "temperature_2m,relative_humidity_2m,apparent_temperature,"
                "is_day,precipitation,weather_code,wind_speed_10m"
            ),
            "hourly": (
                "temperature_2m,precipitation_probability,weather_code"
            ),
            "daily": (
                "weather_code,temperature_2m_max,temperature_2m_min,"
                "precipitation_probability_max,sunrise,sunset"
            ),
            "temperature_unit": "fahrenheit",
            "wind_speed_unit": "mph",
            "precipitation_unit": "inch",
            "timezone": "auto",
            "forecast_days": "7",
        }
        for key, value in parameters.items():
            query.addQueryItem(key, value)
        url.setQuery(query)
        self._set_busy(True)
        self._status = "Refreshing forecast..."
        self.changed.emit()
        reply = self.manager.get(QNetworkRequest(url))
        reply.setProperty("weatherRequest", "forecast")

    def _request_finished(self, reply):
        self._set_busy(False)
        try:
            if reply.error() != QNetworkReply.NetworkError.NoError:
                raise RuntimeError(reply.errorString())
            payload = json.loads(bytes(reply.readAll()).decode("utf-8"))
            if reply.property("weatherRequest") == "search":
                self._search_results = self._parse_search_results(payload)
                self._status = (
                    "Choose a result."
                    if self._search_results
                    else "No matching cities found."
                )
            else:
                self._current, self._hourly, self._daily = self._parse_forecast(
                    payload
                )
                self._status = "Updated just now"
        except (json.JSONDecodeError, KeyError, TypeError, ValueError, RuntimeError) as exc:
            self._status = f"Weather is unavailable: {exc}"
            self.requestFailed.emit(self._status)
        finally:
            self.changed.emit()
            reply.deleteLater()

    @staticmethod
    def _parse_search_results(payload):
        return [
            {
                "name": result["name"],
                "region": result.get("admin1", result.get("country", "")),
                "country": result.get("country", ""),
                "displayName": ", ".join(
                    part
                    for part in (
                        result["name"],
                        result.get("admin1", ""),
                        result.get("country", ""),
                    )
                    if part
                ),
                "latitude": float(result["latitude"]),
                "longitude": float(result["longitude"]),
            }
            for result in payload.get("results", [])
        ]

    @classmethod
    def _parse_forecast(cls, payload):
        current_data = payload["current"]
        description, icon = cls._weather_code(current_data["weather_code"])
        current = {
            "temperature": round(float(current_data["temperature_2m"])),
            "feelsLike": round(float(current_data["apparent_temperature"])),
            "humidity": int(current_data["relative_humidity_2m"]),
            "precipitation": float(current_data["precipitation"]),
            "windSpeed": round(float(current_data["wind_speed_10m"])),
            "isDay": bool(current_data["is_day"]),
            "description": description,
            "icon": icon,
        }

        current_time = datetime.fromisoformat(current_data["time"])
        hourly = []
        for index, time_text in enumerate(payload["hourly"]["time"]):
            forecast_time = datetime.fromisoformat(time_text)
            if forecast_time < current_time.replace(minute=0, second=0):
                continue
            description, icon = cls._weather_code(
                payload["hourly"]["weather_code"][index]
            )
            hourly.append({
                "time": (
                    "Now"
                    if forecast_time == current_time.replace(minute=0, second=0)
                    else cls._hour_label(forecast_time)
                ),
                "temperature": round(
                    float(payload["hourly"]["temperature_2m"][index])
                ),
                "precipitation": int(
                    payload["hourly"]["precipitation_probability"][index] or 0
                ),
                "description": description,
                "icon": icon,
            })
            if len(hourly) == 8:
                break

        daily = []
        for index, date_text in enumerate(payload["daily"]["time"]):
            forecast_date = datetime.fromisoformat(date_text)
            description, icon = cls._weather_code(
                payload["daily"]["weather_code"][index]
            )
            daily.append({
                "day": "Today" if index == 0 else forecast_date.strftime("%a"),
                "high": round(
                    float(payload["daily"]["temperature_2m_max"][index])
                ),
                "low": round(
                    float(payload["daily"]["temperature_2m_min"][index])
                ),
                "precipitation": int(
                    payload["daily"]["precipitation_probability_max"][index] or 0
                ),
                "description": description,
                "icon": icon,
            })
        return current, hourly, daily

    @staticmethod
    def _hour_label(value):
        hour = value.hour % 12 or 12
        return f"{hour} {'AM' if value.hour < 12 else 'PM'}"

    @staticmethod
    def _weather_code(code):
        mapping = {
            0: ("Clear", "☀"),
            1: ("Mostly clear", "🌤"),
            2: ("Partly cloudy", "⛅"),
            3: ("Cloudy", "☁"),
            45: ("Fog", "🌫"),
            48: ("Rime fog", "🌫"),
            51: ("Light drizzle", "🌦"),
            53: ("Drizzle", "🌦"),
            55: ("Heavy drizzle", "🌧"),
            56: ("Freezing drizzle", "🌧"),
            57: ("Freezing drizzle", "🌧"),
            61: ("Light rain", "🌦"),
            63: ("Rain", "🌧"),
            65: ("Heavy rain", "🌧"),
            66: ("Freezing rain", "🌧"),
            67: ("Freezing rain", "🌧"),
            71: ("Light snow", "🌨"),
            73: ("Snow", "🌨"),
            75: ("Heavy snow", "❄"),
            77: ("Snow grains", "🌨"),
            80: ("Light showers", "🌦"),
            81: ("Showers", "🌧"),
            82: ("Heavy showers", "🌧"),
            85: ("Snow showers", "🌨"),
            86: ("Heavy snow showers", "🌨"),
            95: ("Thunderstorm", "⛈"),
            96: ("Thunderstorm with hail", "⛈"),
            99: ("Thunderstorm with hail", "⛈"),
        }
        return mapping.get(int(code), ("Unknown conditions", "🌡"))
