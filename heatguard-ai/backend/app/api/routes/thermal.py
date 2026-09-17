"""
HeatGuard AI — Thermal Routes
POST /api/thermal/calculate         — Compute all thermal indices from weather input
GET  /api/thermal/ward/{ward_id}/latest — Latest stored thermal metrics for a ward
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_db, get_current_user
from app.models.models import User, ThermalMetrics, WeatherData
from app.schemas.thermal import ThermalRequest, ThermalResponse
from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics

router = APIRouter(prefix="/thermal", tags=["Thermal Metrics"])


@router.post("/calculate", response_model=ThermalResponse)
def calculate_thermal(
    payload: ThermalRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Compute Heat Index, WBGT, UTCI (simplified), and HTSI from raw weather parameters.
    All calculations are performed in-memory — no database interaction.
    """
    weather_input = WeatherInput(
        temperature=payload.temperature,
        humidity=payload.humidity,
        wind_speed=payload.wind_speed,
        solar_radiation=payload.solar_radiation,
        pressure=payload.pressure,
        cloud_cover=payload.cloud_cover,
        heatwave_duration=payload.heatwave_duration,
    )
    result = calculate_all_thermal_metrics(weather_input)
    return ThermalResponse(
        temperature=result.temperature,
        humidity=result.humidity,
        wind_speed=result.wind_speed,
        solar_radiation=result.solar_radiation,
        heat_index=result.heat_index,
        wbgt=result.wbgt,
        utci=result.utci,
        heat_index_level=result.heat_index_level,
        wbgt_level=result.wbgt_level,
        htsi=result.htsi,
        htsi_level=result.htsi_level,
        htsi_components=result.htsi_components,
        methodology_notes=result.methodology_notes,
    )


@router.get("/ward/{ward_id}/latest")
def get_ward_latest_thermal(
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return the most recent thermal metrics stored for a ward."""
    # Get the latest weather data for this ward that has thermal metrics
    metrics = (
        db.query(ThermalMetrics)
        .filter(ThermalMetrics.ward_id == ward_id)
        .order_by(ThermalMetrics.calculated_at.desc())
        .first()
    )
    if not metrics:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No thermal metrics found for ward {ward_id}",
        )
    return {
        "ward_id": ward_id,
        "calculated_at": metrics.calculated_at,
        "heat_index": metrics.heat_index,
        "heat_index_level": metrics.heat_index_level,
        "wbgt": metrics.wbgt,
        "wbgt_level": metrics.wbgt_level,
        "htsi": metrics.htsi,
        "htsi_level": metrics.htsi_level,
        "htsi_components": {
            "temperature": metrics.htsi_temp_contribution,
            "humidity": metrics.htsi_humidity_contribution,
            "wind": metrics.htsi_wind_contribution,
            "solar_radiation": metrics.htsi_solar_contribution,
            "wbgt": metrics.htsi_wbgt_contribution,
            "duration": metrics.htsi_duration_contribution,
        },
    }
