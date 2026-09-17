"""
HeatGuard AI — Dashboard Router
"""
from datetime import datetime, timezone
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import (
    City, Ward, WeatherData, ThermalMetrics, RiskPrediction,
    Alert, AlertStatusEnum
)
from app.schemas.schemas import DashboardSummaryResponse
from app.core.config import settings
from app.services.live_weather_service import fetch_live_current_weather
from app.thermal.thermal_engine import WeatherInput, calculate_all_thermal_metrics

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard summary for the city.
    Weather values are fetched live from Open-Meteo (Jaipur) in real-time.
    Risk/ward data comes from the database.
    """
    city = db.query(City).filter(City.name == "Jaipur").first()
    if not city:
        from app.database.seed import run_seed
        run_seed()
        city = db.query(City).filter(City.name == "Jaipur").first()

    wards = db.query(Ward).filter(Ward.city_id == city.id).all()

    # ── Step 1: Get LIVE weather from Open-Meteo ──────────────────────────────
    live_wx = fetch_live_current_weather()
    is_live = live_wx.get("data_source") in ("OPEN_METEO_LIVE", "OPEN_METEO")

    # Compute thermal metrics from live weather
    wx_input = WeatherInput(
        temperature=live_wx["temperature"],
        humidity=live_wx["humidity"],
        wind_speed=live_wx["wind_speed"],
        solar_radiation=live_wx.get("solar_radiation", 700.0),
        heatwave_duration=live_wx.get("heatwave_day_number", 1),
    )
    live_thermal = calculate_all_thermal_metrics(wx_input)

    temp = live_wx["temperature"]
    humidity = live_wx["humidity"]
    wind_speed = live_wx["wind_speed"]
    solar_radiation = live_wx.get("solar_radiation", 700.0)
    heat_index = round(live_thermal.heat_index, 1)
    wbgt = round(live_thermal.wbgt, 1)
    htsi = round(live_thermal.htsi, 1)
    utci = round(live_thermal.utci, 1) if live_thermal.utci else None

    # Determine overall risk
    if htsi >= 81:
        overall_risk = "EXTREME"
        htsi_level_str = "EXTREME"
    elif htsi >= 66:
        overall_risk = "HIGH"
        htsi_level_str = "HIGH"
    elif htsi >= 51:
        overall_risk = "MODERATE"
        htsi_level_str = "MODERATE"
    else:
        overall_risk = "LOW"
        htsi_level_str = "LOW"

    # ── Step 2: Aggregate risk counts from DB ────────────────────────────────
    risk_counts = {"EXTREME": 0, "HIGH": 0, "MODERATE": 0, "LOW": 0, "SAFE": 0}
    total_mortality = 0.0
    total_hosp = 0.0
    risk_count = 0
    highest_htsi = 0.0
    highest_risk_ward = None
    highest_risk_ward_id = None

    for ward in wards:
        rp = (
            db.query(RiskPrediction)
            .filter(RiskPrediction.ward_id == ward.id)
            .order_by(RiskPrediction.predicted_at.desc())
            .first()
        )
        if rp:
            level = rp.overall_risk_level.value if hasattr(rp.overall_risk_level, 'value') else str(rp.overall_risk_level)
            risk_counts[level] = risk_counts.get(level, 0) + 1
            total_mortality += rp.mortality_risk_score or 0
            total_hosp += rp.hospitalization_risk_score or 0
            risk_count += 1
            if (rp.htsi or 0) > highest_htsi:
                highest_htsi = rp.htsi
                highest_risk_ward = ward.ward_name
                highest_risk_ward_id = ward.id

    avg_mortality = total_mortality / risk_count if risk_count else 50.0
    avg_hosp = total_hosp / risk_count if risk_count else 50.0

    active_alerts = db.query(Alert).filter(Alert.status == AlertStatusEnum.ACTIVE).count()

    system_status = {
        "backend": "HEALTHY",
        "database": "CONNECTED",
        "ml_engine": "READY",
        "gis": "LOADED",
        "weather": "LIVE_OPEN_METEO" if is_live else "DEMO_MODE",
        "notifications": "SIMULATION_MODE" if settings.NOTIFICATION_MODE == "mock" else "LIVE",
    }

    return DashboardSummaryResponse(
        city=city.name,
        state=city.state,
        timestamp=datetime.now(timezone.utc).isoformat(),
        data_source="OPEN_METEO_LIVE" if is_live else "DEMO_SYNTHETIC",

        temperature=temp,
        humidity=humidity,
        wind_speed=wind_speed,
        solar_radiation=solar_radiation,

        heat_index=heat_index,
        wbgt=wbgt,
        htsi=htsi,
        utci=utci,

        overall_risk_level=overall_risk,
        htsi_level=htsi_level_str,
        mortality_risk_score=round(avg_mortality, 1),
        hospitalization_risk_score=round(avg_hosp, 1),

        total_wards=len(wards),
        extreme_wards=risk_counts.get("EXTREME", 0),
        high_wards=risk_counts.get("HIGH", 0),
        moderate_wards=risk_counts.get("MODERATE", 0),
        safe_wards=risk_counts.get("SAFE", 0) + risk_counts.get("LOW", 0),
        active_alerts=active_alerts,

        highest_risk_ward=highest_risk_ward,
        highest_risk_ward_id=highest_risk_ward_id,
        system_status=system_status,
    )

