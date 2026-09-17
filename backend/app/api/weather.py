"""
HeatGuard AI — Weather Router
"""
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import City, WeatherData, ForecastData
from app.schemas.schemas import WeatherResponse, ForecastDayResponse, HourlyForecastResponse, HourlyForecastPoint
from app.services.demo_weather_provider import get_base_weather, get_5day_forecast
from app.services.live_weather_service import fetch_live_current_weather, fetch_hourly_forecast

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/current", response_model=WeatherResponse)
def get_current_weather(mode: str = "auto", db: Session = Depends(get_db)):
    """
    Get current weather for Jaipur.
    mode="live": Always pull from Open-Meteo live feed.
    mode="auto": DB if available, fallback to live or demo.
    mode="demo": Forced deterministic synthetic heatwave.
    """
    if mode == "live":
        live = fetch_live_current_weather()
        return WeatherResponse(
            timestamp=live["timestamp"],
            temperature=live["temperature"],
            humidity=live["humidity"],
            wind_speed=live["wind_speed"],
            solar_radiation=live["solar_radiation"],
            pressure=live.get("pressure"),
            cloud_cover=live.get("cloud_cover"),
            heatwave_day_number=live.get("heatwave_day_number", 0),
            data_source=live.get("data_source", "OPEN_METEO_LIVE"),
            data_source_note=live.get("data_source_note"),
        )

    city = db.query(City).filter(City.name == "Jaipur").first()
    if city and mode != "demo":
        wx = (
            db.query(WeatherData)
            .filter(WeatherData.city_id == city.id, WeatherData.ward_id == None)
            .order_by(WeatherData.timestamp.desc())
            .first()
        )
        if wx:
            return WeatherResponse(
                id=wx.id,
                timestamp=wx.timestamp.isoformat(),
                temperature=wx.temperature,
                humidity=wx.humidity,
                wind_speed=wx.wind_speed,
                solar_radiation=wx.solar_radiation,
                pressure=wx.pressure,
                cloud_cover=wx.cloud_cover,
                heatwave_day_number=wx.heatwave_day_number or 0,
                data_source=wx.data_source.value if wx.data_source else "DEMO",
            )

    # Fallback: Live if possible, then demo provider
    try:
        live = fetch_live_current_weather()
        if live.get("data_source") == "OPEN_METEO_LIVE":
            return WeatherResponse(**live)
    except Exception:
        pass

    demo = get_base_weather()
    return WeatherResponse(
        timestamp=demo["timestamp"],
        temperature=demo["temperature"],
        humidity=demo["humidity"],
        wind_speed=demo["wind_speed"],
        solar_radiation=demo["solar_radiation"],
        pressure=demo.get("pressure"),
        cloud_cover=demo.get("cloud_cover"),
        heatwave_day_number=demo.get("heatwave_day_number", 3),
        data_source="DEMO",
        data_source_note=demo.get("data_source_note"),
    )


@router.get("/hourly-forecast", response_model=HourlyForecastResponse)
def get_hourly_forecast(hours: int = 72):
    """
    Get multi-day hourly forecast with thermal stress calculations (Heat Index, WBGT, HTSI).
    Supports 24h, 48h, or 72h early warning prediction timeline.
    """
    safe_hours = max(6, min(168, hours))
    data = fetch_hourly_forecast(hours=safe_hours)

    temps = [p["temperature"] for p in data] if data else [35.0]
    htsis = [p["htsi"] for p in data] if data else [60.0]

    max_temp = max(temps) if temps else 0.0
    max_htsi = max(htsis) if htsis else 0.0

    return HourlyForecastResponse(
        city="Jaipur",
        total_hours=len(data),
        data_source=data[0]["data_source"] if data else "OPEN_METEO",
        peak_risk_window="13:00 - 16:30 Daily Peak",
        max_temperature=round(max_temp, 1),
        max_htsi=round(max_htsi, 1),
        hourly=[HourlyForecastPoint(**p) for p in data],
    )



@router.get("/forecast", response_model=List[ForecastDayResponse])
def get_forecast(db: Session = Depends(get_db)):
    """Get 5-day forecast for Jaipur."""
    now = datetime.now(timezone.utc)
    city = db.query(City).filter(City.name == "Jaipur").first()

    if city:
        forecast_rows = (
            db.query(ForecastData)
            .filter(ForecastData.city_id == city.id, ForecastData.ward_id == None)
            .order_by(ForecastData.forecast_for_date)
            .limit(5)
            .all()
        )
        if forecast_rows:
            return [
                ForecastDayResponse(
                    day=i + 1,
                    date=row.forecast_for_date.date().isoformat(),
                    label="TODAY" if i == 0 else f"DAY {i+1}",
                    temperature_max=row.temperature_max,
                    temperature_min=row.temperature_min,
                    temperature_avg=row.temperature_avg,
                    humidity=row.humidity,
                    wind_speed=row.wind_speed,
                    solar_radiation=row.solar_radiation,
                    heat_index=row.heat_index,
                    wbgt=row.wbgt,
                    htsi=row.htsi,
                    risk_level=row.risk_level.value if row.risk_level else None,
                    mortality_risk_score=row.mortality_risk_score,
                    hospitalization_risk_score=row.hospitalization_risk_score,
                    data_source="DEMO_FORECAST",
                )
                for i, row in enumerate(forecast_rows)
            ]

    # Fallback to demo provider
    forecast_data = get_5day_forecast(now)
    from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics
    result = []
    for i, day in enumerate(forecast_data):
        wx = WeatherInput(
            temperature=day["temperature_avg"],
            humidity=day["humidity"],
            wind_speed=day["wind_speed"],
            solar_radiation=day.get("solar_radiation", 700),
            heatwave_duration=day.get("heatwave_day_number", 1),
        )
        tm = calculate_all_thermal_metrics(wx)
        result.append(ForecastDayResponse(
            day=i + 1,
            date=day["date"],
            label=day["label"],
            temperature_max=day["temperature_max"],
            temperature_min=day["temperature_min"],
            temperature_avg=day["temperature_avg"],
            humidity=day["humidity"],
            wind_speed=day["wind_speed"],
            solar_radiation=day.get("solar_radiation"),
            heat_index=tm.heat_index,
            wbgt=tm.wbgt,
            htsi=tm.htsi,
            risk_level=tm.htsi_level,
            data_source="DEMO_FORECAST",
        ))
    return result
