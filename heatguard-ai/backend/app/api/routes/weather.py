"""
HeatGuard AI — Weather Routes
GET /api/weather/{city_id}/current    — Latest weather observation for a city
GET /api/weather/{city_id}/history    — Recent weather history (last N hours)
GET /api/weather/{city_id}/forecast   — Forecast data for a city
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.models import City, WeatherData, ForecastData, User
from app.schemas.weather import WeatherDataOut, ForecastDataOut

router = APIRouter(prefix="/weather", tags=["Weather"])


@router.get("/{city_id}/current", response_model=WeatherDataOut)
def get_current_weather(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the most recent weather observation for the city."""
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    latest = (
        db.query(WeatherData)
        .filter(WeatherData.city_id == city_id)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )
    if not latest:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No weather data available for this city",
        )
    return latest


@router.get("/{city_id}/history", response_model=List[WeatherDataOut])
def get_weather_history(
    city_id: int,
    hours: int = Query(default=24, ge=1, le=168, description="Number of hours of history"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return recent weather observations for the city (default: last 24h)."""
    from datetime import datetime, timedelta, timezone

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    since = datetime.now(timezone.utc) - timedelta(hours=hours)
    records = (
        db.query(WeatherData)
        .filter(WeatherData.city_id == city_id, WeatherData.timestamp >= since)
        .order_by(WeatherData.timestamp.desc())
        .limit(200)
        .all()
    )
    return records


@router.get("/{city_id}/forecast", response_model=List[ForecastDataOut])
def get_forecast(
    city_id: int,
    days: int = Query(default=5, ge=1, le=10, description="Number of forecast days"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return upcoming forecast data for the city."""
    from datetime import datetime, timezone

    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    now = datetime.now(timezone.utc)
    records = (
        db.query(ForecastData)
        .filter(ForecastData.city_id == city_id, ForecastData.forecast_for_date >= now)
        .order_by(ForecastData.forecast_for_date.asc())
        .limit(days)
        .all()
    )
    return records
