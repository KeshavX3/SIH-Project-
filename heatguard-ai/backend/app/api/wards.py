"""
HeatGuard AI — Wards Router
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Ward, WeatherData, ThermalMetrics, PopulationData, RiskPrediction, City
from app.schemas.schemas import WardDetailResponse, WardListResponse, WeatherResponse, ThermalResponse, VulnerabilityResponse, RiskResponse

router = APIRouter(prefix="/api/wards", tags=["Wards"])


def _build_ward_list_item(ward: Ward, db: Session) -> dict:
    rp = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.ward_id == ward.id)
        .order_by(RiskPrediction.predicted_at.desc())
        .first()
    )
    pop = db.query(PopulationData).filter(PopulationData.ward_id == ward.id).first()

    return {
        "id": ward.id,
        "ward_number": ward.ward_number,
        "ward_name": ward.ward_name,
        "latitude": ward.latitude,
        "longitude": ward.longitude,
        "risk_level": (rp.overall_risk_level.value if rp and hasattr(rp.overall_risk_level, "value") else str(rp.overall_risk_level)) if rp else "SAFE",
        "htsi": rp.htsi if rp else None,
        "mortality_risk_score": rp.mortality_risk_score if rp else None,
        "vulnerability_score": pop.vulnerability_score if pop else None,
    }


@router.get("", response_model=List[WardListResponse])
def list_wards(db: Session = Depends(get_db)):
    """List all wards with current risk levels."""
    city = db.query(City).filter(City.name == "Jaipur").first()
    if not city:
        return []

    wards = db.query(Ward).filter(Ward.city_id == city.id).order_by(Ward.ward_number).all()
    return [_build_ward_list_item(w, db) for w in wards]


@router.get("/{ward_id}", response_model=WardDetailResponse)
def get_ward_detail(ward_id: int, db: Session = Depends(get_db)):
    """Get complete ward detail including weather, thermal, vulnerability, and risk."""
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=404, detail=f"Ward {ward_id} not found")

    # Latest weather
    wx = (
        db.query(WeatherData)
        .filter(WeatherData.ward_id == ward.id)
        .order_by(WeatherData.timestamp.desc())
        .first()
    )

    # Thermal metrics
    tm = None
    if wx:
        tm = db.query(ThermalMetrics).filter(ThermalMetrics.weather_data_id == wx.id).first()

    # Population & vulnerability
    pop = db.query(PopulationData).filter(PopulationData.ward_id == ward.id).first()

    # Risk prediction
    rp = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.ward_id == ward.id)
        .order_by(RiskPrediction.predicted_at.desc())
        .first()
    )

    weather_resp = None
    if wx:
        weather_resp = WeatherResponse(
            id=wx.id,
            ward_id=wx.ward_id,
            timestamp=wx.timestamp.isoformat() if wx.timestamp else None,
            temperature=wx.temperature,
            humidity=wx.humidity,
            wind_speed=wx.wind_speed,
            solar_radiation=wx.solar_radiation,
            pressure=wx.pressure,
            cloud_cover=wx.cloud_cover,
            heatwave_day_number=wx.heatwave_day_number or 0,
            data_source=wx.data_source.value if wx.data_source else "DEMO",
        )

    thermal_resp = None
    if tm:
        thermal_resp = ThermalResponse(
            temperature=wx.temperature if wx else 0,
            humidity=wx.humidity if wx else 0,
            wind_speed=wx.wind_speed if wx else 0,
            solar_radiation=wx.solar_radiation if wx else None,
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

    vuln_resp = None
    if pop:
        vuln_resp = VulnerabilityResponse(
            ward_id=ward.id,
            ward_name=ward.ward_name,
            vulnerability_score=pop.vulnerability_score or 0,
            vulnerability_level=pop.vulnerability_level.value if pop.vulnerability_level else "SAFE",
            population_density=pop.population_density or 0,
            elderly_density=pop.elderly_density or 0,
            outdoor_worker_density=pop.outdoor_worker_density or 0,
            children_density=(pop.children_population / (ward.area_sq_km or 1)) if pop.children_population else 0,
            total_population=pop.total_population,
            elderly_population=pop.elderly_population,
            children_population=pop.children_population,
            outdoor_worker_population=pop.outdoor_worker_population,
            data_source="DEMO",
        )

    risk_resp = None
    if rp:
        risk_resp = RiskResponse(
            ward_id=ward.id,
            ward_name=ward.ward_name,
            overall_risk_level=rp.overall_risk_level.value if hasattr(rp.overall_risk_level, "value") else str(rp.overall_risk_level),
            htsi=rp.htsi or 0,
            mortality_risk_score=rp.mortality_risk_score or 0,
            hospitalization_risk_score=rp.hospitalization_risk_score or 0,
            mortality_risk_level=rp.mortality_risk_level.value if rp.mortality_risk_level else "SAFE",
            hospitalization_risk_level=rp.hospitalization_risk_level.value if rp.hospitalization_risk_level else "SAFE",
            vulnerability_score=rp.vulnerability_score,
            temperature_anomaly=rp.temperature_anomaly,
            heatwave_duration=rp.heatwave_duration,
            feature_importance=rp.feature_importance,
        )

    return WardDetailResponse(
        id=ward.id,
        ward_number=ward.ward_number,
        ward_name=ward.ward_name,
        city_id=ward.city_id,
        latitude=ward.latitude,
        longitude=ward.longitude,
        area_sq_km=ward.area_sq_km,
        weather=weather_resp,
        thermal=thermal_resp,
        vulnerability=vuln_resp,
        risk=risk_resp,
    )
