"""
HeatGuard AI — Live Meteorological Data Service (Open-Meteo Integration)
========================================================================

Fetches real-time meteorological conditions and multi-day hourly forecasts
for Jaipur, Rajasthan (Lat: 26.9124, Lon: 75.7873).

Uses the Open-Meteo scientific forecast API:
- Open-access, no API key required
- Integrates ECMWF, GFS, and DWD numerical models
- Includes solar irradiance, relative humidity, pressure, and wind speed

Calculates biometeorological stress indices (Heat Index, WBGT, UTCI, HTSI)
for every hour of the 72-hour forecast timeline.
"""
import time
import logging
from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional
import requests

from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics
from app.services.demo_weather_provider import get_base_weather

logger = logging.getLogger(__name__)

JAIPUR_LAT = 26.9124
JAIPUR_LON = 75.7873
CACHE_TTL_SECONDS = 600  # 10 minutes cache

# In-memory caches
_current_cache: Dict[str, Any] = {"data": None, "expires_at": 0}
_hourly_cache: Dict[str, Any] = {"data": None, "expires_at": 0}


def fetch_live_current_weather() -> Dict[str, Any]:
    """
    Fetches real-time weather for Jaipur from Open-Meteo with caching & demo fallback.
    """
    now_ts = time.time()
    if _current_cache["data"] and now_ts < _current_cache["expires_at"]:
        return _current_cache["data"]

    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={JAIPUR_LAT}&longitude={JAIPUR_LON}&"
        f"current=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"surface_pressure,cloud_cover,wind_speed_10m,direct_normal_irradiance&"
        f"timezone=Asia%2FKolkata"
    )

    try:
        resp = requests.get(url, timeout=4.0)
        if resp.status_code == 200:
            payload = resp.json()
            curr = payload.get("current", {})

            temp = float(curr.get("temperature_2m", 35.0))
            humidity = float(curr.get("relative_humidity_2m", 40.0))
            wind = float(curr.get("wind_speed_10m", 12.0))
            solar = float(curr.get("direct_normal_irradiance", 650.0))
            pressure = float(curr.get("surface_pressure", 1008.0))
            cloud_cover = float(curr.get("cloud_cover", 10.0))

            data = {
                "timestamp": curr.get("time", datetime.now(timezone.utc).isoformat()),
                "temperature": round(temp, 1),
                "humidity": round(humidity, 1),
                "wind_speed": round(wind, 1),
                "solar_radiation": round(solar, 1),
                "pressure": round(pressure, 1),
                "cloud_cover": round(cloud_cover, 1),
                "heatwave_day_number": 2 if temp > 40.0 else 0,
                "data_source": "OPEN_METEO_LIVE",
                "data_source_note": "Live meteorological feed from Open-Meteo API (Jaipur)",
            }
            _current_cache["data"] = data
            _current_cache["expires_at"] = now_ts + CACHE_TTL_SECONDS
            logger.info("Successfully fetched live current weather from Open-Meteo")
            return data
    except Exception as exc:
        logger.warning(f"Failed to fetch live weather from Open-Meteo ({exc}). Using demo fallback.")

    # Graceful fallback to demo provider
    demo = get_base_weather()
    demo["data_source"] = "DEMO_FALLBACK"
    return demo


def fetch_hourly_forecast(hours: int = 72) -> List[Dict[str, Any]]:
    """
    Fetches 72-hour forecast from Open-Meteo, computes thermal stress metrics for each hour,
    and returns a structured timeline for the early-warning dashboard.
    """
    now_ts = time.time()
    if _hourly_cache["data"] and now_ts < _hourly_cache["expires_at"]:
        return _hourly_cache["data"][:hours]

    days = 3 if hours <= 72 else 7
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={JAIPUR_LAT}&longitude={JAIPUR_LON}&"
        f"hourly=temperature_2m,relative_humidity_2m,apparent_temperature,"
        f"wind_speed_10m,direct_normal_irradiance,surface_pressure&"
        f"forecast_days={days}&timezone=Asia%2FKolkata"
    )

    try:
        resp = requests.get(url, timeout=5.0)
        if resp.status_code == 200:
            payload = resp.json()
            hourly = payload.get("hourly", {})
            times = hourly.get("time", [])
            temps = hourly.get("temperature_2m", [])
            humids = hourly.get("relative_humidity_2m", [])
            winds = hourly.get("wind_speed_10m", [])
            solars = hourly.get("direct_normal_irradiance", [])

            results: List[Dict[str, Any]] = []
            for i in range(min(len(times), hours)):
                t_str = times[i]
                t_val = float(temps[i]) if i < len(temps) and temps[i] is not None else 35.0
                h_val = float(humids[i]) if i < len(humids) and humids[i] is not None else 45.0
                w_val = float(winds[i]) if i < len(winds) and winds[i] is not None else 10.0
                s_val = float(solars[i]) if i < len(solars) and solars[i] is not None else 0.0

                # Compute biometeorological metrics via Thermal Engine
                wx = WeatherInput(
                    temperature=t_val,
                    humidity=h_val,
                    wind_speed=w_val,
                    solar_radiation=s_val,
                    heatwave_duration=1 if t_val >= 40.0 else 0,
                )
                metrics = calculate_all_thermal_metrics(wx)

                # Format short label (e.g. "Thu 14:00" or "14:00")
                try:
                    dt = datetime.fromisoformat(t_str)
                    label = dt.strftime("%a %H:%M")
                    short_time = dt.strftime("%H:%M")
                    date_str = dt.strftime("%Y-%m-%d")
                except Exception:
                    label = t_str
                    short_time = t_str
                    date_str = ""

                results.append({
                    "time": t_str,
                    "label": label,
                    "short_time": short_time,
                    "date": date_str,
                    "temperature": round(t_val, 1),
                    "humidity": round(h_val, 1),
                    "wind_speed": round(w_val, 1),
                    "solar_radiation": round(s_val, 1),
                    "heat_index": round(metrics.heat_index, 1),
                    "wbgt": round(metrics.wbgt, 1),
                    "utci": round(metrics.utci, 1) if metrics.utci else None,
                    "htsi": round(metrics.htsi, 1),
                    "risk_level": metrics.htsi_level,
                    "data_source": "OPEN_METEO_FORECAST",
                })

            _hourly_cache["data"] = results
            _hourly_cache["expires_at"] = now_ts + CACHE_TTL_SECONDS
            logger.info(f"Successfully computed {len(results)} hourly early warning forecast points")
            return results[:hours]

    except Exception as exc:
        logger.warning(f"Failed to fetch hourly forecast from Open-Meteo ({exc}). Generating synthesized forecast.")

    # Synthesized deterministic fallback
    return _generate_synthesized_hourly(hours)


def _generate_synthesized_hourly(hours: int = 72) -> List[Dict[str, Any]]:
    """Fallback generator for hourly diurnal cycles when internet is unavailable."""
    results = []
    base_time = datetime.now(timezone.utc).replace(minute=0, second=0, microsecond=0)
    for i in range(hours):
        t_current = base_time + timedelta(hours=i)
        hour = t_current.hour

        # Diurnal temperature cycle: peak around 14:00 - 15:00, coolest at 05:00
        diurnal_factor = -1.0 * ((hour - 14) / 9.0) ** 2 + 1.0
        diurnal_factor = max(-0.8, min(1.0, diurnal_factor))

        temp = round(34.0 + 9.5 * diurnal_factor, 1)
        humidity = round(max(20.0, 55.0 - 25.0 * diurnal_factor), 1)
        wind = round(max(5.0, 10.0 + 4.0 * diurnal_factor), 1)
        solar = round(max(0.0, 850.0 * diurnal_factor), 1) if 6 <= hour <= 19 else 0.0

        wx = WeatherInput(
            temperature=temp,
            humidity=humidity,
            wind_speed=wind,
            solar_radiation=solar,
            heatwave_duration=2 if temp >= 41.0 else 0,
        )
        metrics = calculate_all_thermal_metrics(wx)

        results.append({
            "time": t_current.isoformat(),
            "label": t_current.strftime("%a %H:%M"),
            "short_time": t_current.strftime("%H:%M"),
            "date": t_current.strftime("%Y-%m-%d"),
            "temperature": temp,
            "humidity": humidity,
            "wind_speed": wind,
            "solar_radiation": solar,
            "heat_index": round(metrics.heat_index, 1),
            "wbgt": round(metrics.wbgt, 1),
            "utci": round(metrics.utci, 1) if metrics.utci else None,
            "htsi": round(metrics.htsi, 1),
            "risk_level": metrics.htsi_level,
            "data_source": "SYNTHETIC_DIURNAL",
        })
    return results
