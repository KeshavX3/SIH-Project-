"""
HeatGuard AI — Weather Router
"""
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import City, WeatherData, ForecastData
from app.schemas.schemas import WeatherResponse, ForecastDayResponse
from app.services.demo_weather_provider import get_base_weather, get_5day_forecast

router = APIRouter(prefix="/api/weather", tags=["Weather"])


@router.get("/current", response_model=WeatherResponse)
def get_current_weather(db: Session = Depends(get_db)):
    """Get current weather for Jaipur (latest from DB or demo provider)."""
    city = db.query(City).filter(City.name == "Jaipur").first()
    if city:
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

    # Fallback to demo provider
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
