"""
HeatGuard AI — Thermal Router
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Ward, WeatherData, ThermalMetrics
from app.schemas.schemas import ThermalResponse, ThermalCalculationRequest
from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics

router = APIRouter(prefix="/api/thermal", tags=["Thermal"])


@router.post("/calculate", response_model=ThermalResponse)
def calculate_thermal(request: ThermalCalculationRequest):
    """
    Calculate all thermal metrics from provided weather inputs.
    Does NOT require database — pure calculation endpoint.
    Useful for real-time calculations and testing.
    """
    weather = WeatherInput(
        temperature=request.temperature,
        humidity=request.humidity,
        wind_speed=request.wind_speed,
        solar_radiation=request.solar_radiation,
        pressure=request.pressure,
        cloud_cover=request.cloud_cover,
        heatwave_duration=request.heatwave_duration,
    )
    result = calculate_all_thermal_metrics(weather)

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


@router.get("/ward/{ward_id}", response_model=ThermalResponse)
def get_ward_thermal(ward_id: int, db: Session = Depends(get_db)):
    """Get latest thermal metrics for a specific ward."""
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail=f"Ward {ward_id} not found")

    wx = (
        db.query(WeatherData)
        .filter(WeatherData.ward_id == ward.id)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )

    if not wx:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="No weather data for this ward")

    tm = db.query(ThermalMetrics).filter(ThermalMetrics.weather_data_id == wx.id).first()
    if not tm:
        # Calculate on-the-fly
        weather = WeatherInput(
            temperature=wx.temperature,
            humidity=wx.humidity,
            wind_speed=wx.wind_speed,
            solar_radiation=wx.solar_radiation or 700,
            heatwave_duration=wx.heatwave_day_number or 0,
        )
        result = calculate_all_thermal_metrics(weather)
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
        )

    return ThermalResponse(
        temperature=wx.temperature,
        humidity=wx.humidity,
        wind_speed=wx.wind_speed,
        solar_radiation=wx.solar_radiation,
        heat_index=tm.heat_index or 0,
        wbgt=tm.wbgt or 0,
        utci=tm.utci,
        heat_index_level=tm.heat_index_level.value if tm.heat_index_level else "SAFE",
        wbgt_level=tm.wbgt_level.value if tm.wbgt_level else "SAFE",
        htsi=tm.htsi or 0,
        htsi_level=tm.htsi_level.value if tm.htsi_level else "SAFE",
        htsi_components={
            "temperature": tm.htsi_temp_contribution or 0,
            "humidity": tm.htsi_humidity_contribution or 0,
            "wind": tm.htsi_wind_contribution or 0,
            "solar_radiation": tm.htsi_solar_contribution or 0,
            "wbgt": tm.htsi_wbgt_contribution or 0,
            "duration": tm.htsi_duration_contribution or 0,
        },
    )


@router.get("/current")
def get_current_city_thermal(db: Session = Depends(get_db)):
    """Get city-wide thermal summary (representative ward 18)."""
    from app.models.models import City
    city = db.query(City).filter(City.name == "Jaipur").first()
    if not city:
        return {"error": "City not found"}

    from app.models.models import Ward as WardModel
    ward = db.query(WardModel).filter(
        WardModel.city_id == city.id, WardModel.ward_number == 18
    ).first()

    if not ward:
        ward = db.query(WardModel).filter(WardModel.city_id == city.id).first()

    if not ward:
        return {"error": "No wards found"}

    return get_ward_thermal(ward.id, db)
