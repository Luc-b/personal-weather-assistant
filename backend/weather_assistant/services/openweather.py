from dataclasses import dataclass
from datetime import datetime, timedelta, date
from typing import Any

import httpx

from weather_assistant.models import WeatherSummary

@dataclass(frozen=True)
class GeoResult:
    name: str
    lat: float
    lon: float
    country: str | None = None
    state: str | None = None


class OpenWeatherClient:
    GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
    FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"

    def __init__(self, api_key: str, timeout_s: float = 10.0):
        self.api_key = api_key
        self.client = httpx.Client(timeout=timeout_s)

    def close(self) -> None:
        self.client.close()

    def geocode(self, city: str, limit: int = 1) -> GeoResult:
        city = (city or "").strip()
        if not city:
            raise ValueError("City is empty.")

        r = self.client.get(
            self.GEO_URL,
            params={"q": city, "limit": limit, "appid": self.api_key},
        )

        if r.status_code in (401, 403):
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            raise RuntimeError(f"OpenWeather auth error ({r.status_code}): {detail}")

        r.raise_for_status()
        data = r.json()

        if not data:
            raise ValueError(f"Can't find the city: '{city}'. Check input.")

        item = data[0]
        return GeoResult(
            name=item.get("name", city),
            lat=float(item["lat"]),
            lon=float(item["lon"]),
            country=item.get("country"),
            state=item.get("state"),
        )

    def forecast_5day_3h(
        self,
        lat: float,
        lon: float,
        units: str = "metric",
        lang: str = "en",
    ) -> dict[str, Any]:
        r = self.client.get(
            self.FORECAST_URL,
            params={
                "lat": lat,
                "lon": lon,
                "appid": self.api_key,
                "units": units,
                "lang": lang,
            },
        )

        if r.status_code in (401, 403):
            try:
                detail = r.json()
            except Exception:
                detail = r.text
            raise RuntimeError(f"OpenWeather auth error ({r.status_code}): {detail}")

        r.raise_for_status()
        return r.json()

    def pick_best_slot_for_date(
        self,
        forecast_json: dict[str, Any],
        requested: date,
    ) -> tuple[dict[str, Any], date, int]:

        """
        Selects the most representative forecast slot for a given date.

        OpenWeather 5-day forecast provides weather data in 3-hour UTC slots.
        This function:
        - converts all forecast slots from UTC to the city's local time
        - finds all slots that belong to the requested local date
        - selects the slot closest to 12:00 (local noon)
        - if the requested date is not available, raises an error and
        mentions the nearest available date

        Parameters
        ----------
        forecast_json : dict
            Raw JSON response from OpenWeather forecast API.
            Expected to contain:
            - forecast_json["list"] : list of forecast slots
            - forecast_json["city"]["timezone"] : timezone offset in seconds
        requested : date
            Date requested by the user (local date in the target city).

        Returns
        -------
        tuple[dict, date, int]
            - Selected forecast slot (raw slot JSON)
            - Date the slot corresponds to (local date)
            - Timezone offset in seconds

        Raises
        ------
        RuntimeError
            If forecast data is malformed or missing slots.
        ValueError
            If the requested date is outside the available forecast range.
        """

        # Timezone offset in seconds (e.g. +3600, +7200)
        tz = int(forecast_json.get("city", {}).get("timezone", 0))
        
        # List of forecast slots (3-hour intervals)
        items = forecast_json.get("list", [])
        if not items:
            raise RuntimeError("OpenWeather: forecast response missing 'list' items.")
        
        # Convert each forecast slot from UTC to local datetime
        slots_with_local: list[tuple[dict[str, Any], datetime]] = []
        for it in items:
            dt_utc = datetime.utcfromtimestamp(int(it["dt"]))
            local_dt = dt_utc + timedelta(seconds=tz)
            slots_with_local.append((it, local_dt))
            
        # Collect all unique local dates available in the forecast
        available_dates = sorted({ldt.date() for _, ldt in slots_with_local})
        if not available_dates:
            raise RuntimeError("No available dates in forecast data.")

        def pick_for(d: date) -> dict[str, Any]:
            """
            Pick the forecast slot for date `d` that is closest to 12:00 local time.
            """
            # All slots that fall on the given local date
            candidates = [(it, ldt) for it, ldt in slots_with_local if ldt.date() == d]
            if not candidates:
                raise ValueError("No slots for date")
            
            # Target time = 12:00 (noon) expressed in minutes
            target_minutes = 12 * 60
            
            # Sort by absolute distance from noon
            candidates.sort(key=lambda x: abs((x[1].hour * 60 + x[1].minute) - target_minutes))
            
            # Return the raw forecast slot closest to noon
            return candidates[0][0]
        
        # If requested date exists in forecast, return best slot for that date
        if requested in available_dates:
            return pick_for(requested), requested, tz
        
        # Otherwise, find the nearest available date and raise a helpful error
        requested_ord = requested.toordinal()
        nearest = min(available_dates, key=lambda d: abs(d.toordinal() - requested_ord))

        raise ValueError(
            f"Requested date {requested.isoformat()} is outside the available forecast range. "
            f"Nearest available date is {nearest.isoformat()}."
        )



def build_weather_summary(
    city_name: str,
    country: str | None,
    used_date: date,
    slot: dict[str, Any],
) -> WeatherSummary:
    main = slot.get("main", {})
    wind = slot.get("wind", {})
    weather_arr = slot.get("weather") or [{}]

    temp = main.get("temp")
    if temp is None:
        raise RuntimeError("OpenWeather: missing main.temp in selected forecast slot.")

    return WeatherSummary(
        city=city_name,
        country=country or "",
        date=used_date,
        description=weather_arr[0].get("description", "unknown"),
        temperature_c=float(temp),
        feels_like_c=main.get("feels_like"),
        humidity_percent=main.get("humidity"),
        wind_speed_mps=wind.get("speed"),
        precipitation_probability=float(slot.get("pop", 0.0)),
    )
