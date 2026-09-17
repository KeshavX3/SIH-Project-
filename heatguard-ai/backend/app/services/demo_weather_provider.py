"""
HeatGuard AI — Demo Weather Provider
=====================================

Provides deterministic demonstration weather data for Jaipur, Rajasthan.

DATA SOURCE: DEMONSTRATION / SYNTHETIC DATA
─────────────────────────────────────────────
All data in this module is fabricated for demonstration purposes.
It is NOT official government or meteorological data.
It must NOT be used for real public-health decision-making.

Design goals:
  - Deterministic: Same output every call (based on date offsets, not random)
  - Realistic: Reflects actual Jaipur summer weather patterns
  - Demonstrable: Includes an extreme heatwave scenario for SIH demo
"""
import math
from datetime import datetime, timezone, timedelta
from typing import List, Dict, Any

# ─── Jaipur geographic constants ───────────────────────────────────────────
JAIPUR_LAT = 26.9124
JAIPUR_LON = 75.7873
JAIPUR_ELEVATION = 431  # meters
SEASONAL_NORMAL_TEMP = 28.0  # April–June average background

# ─── Demo ward base conditions ─────────────────────────────────────────────
# 91 Jaipur wards — deterministic offset from city baseline
WARD_OFFSETS = {
    # (temp_delta, humidity_delta, wind_delta, solar_delta, heatwave_duration)
    1:  (+0.5, -5.0, +2.0, +20, 1),
    2:  (+1.2, +3.0, -1.0, +40, 2),
    3:  (+0.8, +8.0, +0.5, +10, 1),
    4:  (+2.1, +12.0, -2.0, +60, 3),
    5:  (+0.3, +1.0, +3.0, -10, 0),
    6:  (+1.5, +5.0, -1.5, +30, 2),
    7:  (+0.7, +2.0, +1.0, +15, 1),
    8:  (+2.8, +15.0, -3.0, +80, 4),
    9:  (+0.2, -2.0, +4.0, -20, 0),
    10: (+1.9, +10.0, -2.5, +50, 3),
    11: (+0.6, +4.0, +0.8, +5, 1),
    12: (+3.2, +18.0, -3.5, +90, 5),
    13: (+1.1, +6.0, -1.0, +35, 2),
    14: (+0.4, +0.5, +2.5, -5, 0),
    15: (+2.5, +14.0, -2.8, +70, 4),
    16: (+0.9, +5.5, +0.3, +20, 1),
    17: (+3.5, +20.0, -4.0, +100, 6),
    18: (+4.1, +22.0, -4.5, +110, 7),  # ← EXTREME SCENARIO WARD
    19: (+2.0, +11.0, -2.0, +55, 3),
    20: (+1.3, +7.0, -1.5, +45, 2),
    21: (+0.5, +2.5, +1.5, +10, 1),
    22: (+3.0, +16.0, -3.2, +85, 5),
    23: (+1.8, +9.0, -2.0, +50, 3),
    24: (+0.7, +3.5, +1.0, +15, 1),
    25: (+2.3, +13.0, -2.5, +65, 4),
}


def get_base_weather(reference_date: datetime = None) -> Dict[str, Any]:
    """
    Get base Jaipur city weather for a given date.
    Deterministic — same date always returns same values.
    Based on Jaipur summer climatology (May-June peak heat).
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    # Use day-of-year to create realistic seasonal variation
    doy = reference_date.timetuple().tm_yday

    # Jaipur summer peak: May 15 – June 15 (day 135–166)
    # Temperature: sinusoidal seasonal pattern
    season_factor = math.sin((doy - 80) * math.pi / 120)  # peak around May
    base_temp = 38.0 + 7.0 * max(0, season_factor)

    # Humidity low in May, rises with pre-monsoon
    base_humidity = 35.0 + 25.0 * max(0, season_factor * 0.8)

    # Wind: afternoon breeze pattern
    base_wind = 10.0 + 5.0 * math.sin(doy * 0.05)

    # Solar radiation: high in summer, consistent
    base_solar = 750.0 + 200.0 * max(0, season_factor)

    # For demo purposes, force extreme conditions to showcase the system
    # (Typical June heatwave in Jaipur)
    return {
        "city": "Jaipur",
        "state": "Rajasthan",
        "country": "India",
        "timestamp": reference_date.isoformat(),
        "temperature": round(base_temp, 1),
        "humidity": round(min(95, max(15, base_humidity)), 1),
        "wind_speed": round(max(0, base_wind), 1),
        "solar_radiation": round(min(1050, base_solar), 0),
        "pressure": 1008.0,
        "cloud_cover": round(max(0, 20 - season_factor * 15), 1),
        "latitude": JAIPUR_LAT,
        "longitude": JAIPUR_LON,
        "heatwave_day_number": 3,  # 3rd consecutive day
        "data_source": "DEMO",
        "data_source_note": (
            "DEMONSTRATION DATA — Not official government or meteorological data. "
            "For SIH prototype demonstration only."
        ),
    }


def get_ward_weather(ward_id: int, reference_date: datetime = None) -> Dict[str, Any]:
    """Get weather for a specific ward with deterministic local variation."""
    base = get_base_weather(reference_date)
    offset = WARD_OFFSETS.get(ward_id, (0, 0, 0, 0, 0))

    return {
        **base,
        "ward_id": ward_id,
        "temperature": round(base["temperature"] + offset[0], 1),
        "humidity": round(min(95, max(15, base["humidity"] + offset[1])), 1),
        "wind_speed": round(max(0, base["wind_speed"] + offset[2]), 1),
        "solar_radiation": round(min(1050, base["solar_radiation"] + offset[3]), 0),
        "heatwave_day_number": offset[4],
    }


def get_5day_forecast(reference_date: datetime = None) -> List[Dict[str, Any]]:
    """
    Generate 5-day deterministic forecast for Jaipur.
    
    SOURCE: DEMO FORECAST — Not official meteorological forecast.
    """
    if reference_date is None:
        reference_date = datetime.now(timezone.utc)

    # Forecast pattern: builds to extreme then moderates
    forecast_pattern = [
        # (temp_delta, humidity_delta, wind_delta, solar_delta, heatwave_delta)
        (0.0, 0.0, 0.0, 0.0, 0),      # Day 1: Current (base)
        (+1.5, +5.0, -1.0, +30, 1),    # Day 2: Getting worse
        (+3.0, +8.0, -2.0, +50, 2),    # Day 3: Peak extreme
        (+2.0, +6.0, -1.5, +30, 3),    # Day 4: Still extreme
        (-1.0, -5.0, +3.0, -20, 4),    # Day 5: Slight relief
    ]

    base = get_base_weather(reference_date)
    forecast = []

    for day_idx, pattern in enumerate(forecast_pattern):
        day_date = reference_date + timedelta(days=day_idx)
        day_weather = {
            "day": day_idx + 1,
            "date": day_date.date().isoformat(),
            "label": (
                "TODAY" if day_idx == 0 else
                f"DAY {day_idx + 1}"
            ),
            "temperature_max": round(base["temperature"] + pattern[0] + 2, 1),
            "temperature_min": round(base["temperature"] + pattern[0] - 4, 1),
            "temperature_avg": round(base["temperature"] + pattern[0], 1),
            "humidity": round(min(95, max(15, base["humidity"] + pattern[1])), 1),
            "wind_speed": round(max(0, base["wind_speed"] + pattern[2]), 1),
            "solar_radiation": round(min(1050, base["solar_radiation"] + pattern[3]), 0),
            "heatwave_day_number": base["heatwave_day_number"] + pattern[4],
            "data_source": "DEMO_FORECAST",
        }
        forecast.append(day_weather)

    return forecast


def get_all_wards_demo_data(reference_date: datetime = None) -> List[Dict[str, Any]]:
    """Get weather data for all 25 demo wards."""
    return [get_ward_weather(w, reference_date) for w in range(1, 26)]
