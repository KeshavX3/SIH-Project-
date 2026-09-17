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

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Get comprehensive dashboard summary for the city.
    Aggregates weather, thermal, risk, and alert data.
    """
    city = db.query(City).filter(City.name == "Jaipur").first()
    if not city:
        from app.database.seed import run_seed
        run_seed()
        city = db.query(City).filter(City.name == "Jaipur").first()

    wards = db.query(Ward).filter(Ward.city_id == city.id).all()

    # Get latest weather for a representative ward (Ward 18 = showcase ward)
    rep_ward = next((w for w in wards if w.ward_number == 18), wards[0] if wards else None)

    latest_wx = None
    latest_tm = None
    if rep_ward:
        latest_wx = (
            db.query(WeatherData)
            .filter(WeatherData.ward_id == rep_ward.id)
            .order_by(WeatherData.timestamp.desc())
            .first()
        )
        if latest_wx:
            latest_tm = (
                db.query(ThermalMetrics)
                .filter(ThermalMetrics.weather_data_id == latest_wx.id)
                .first()
            )

    # Aggregate risk across all wards
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

    # System status
    system_status = {
        "backend": "HEALTHY",
        "database": "CONNECTED",
        "ml_engine": "READY",
        "gis": "LOADED",
        "weather": "DEMO_MODE" if settings.DEMO_MODE else "LIVE",
        "notifications": "SIMULATION_MODE" if settings.NOTIFICATION_MODE == "mock" else "LIVE",
    }

    return DashboardSummaryResponse(
        city=city.name,
        state=city.state,
        timestamp=datetime.now(timezone.utc).isoformat(),
        data_source="DEMO",

        # Weather
        temperature=latest_wx.temperature if latest_wx else 43.0,
        humidity=latest_wx.humidity if latest_wx else 62.0,
        wind_speed=latest_wx.wind_speed if latest_wx else 5.5,
        solar_radiation=latest_wx.solar_radiation if latest_wx else 860.0,

        # Thermal
        heat_index=latest_tm.heat_index if latest_tm else 55.2,
        wbgt=latest_tm.wbgt if latest_tm else 34.1,
        htsi=latest_tm.htsi if latest_tm else 85.0,
        utci=latest_tm.utci if latest_tm else None,

        # Risk
        overall_risk_level="EXTREME" if (latest_tm and latest_tm.htsi and latest_tm.htsi >= 81) else "HIGH",
        htsi_level=latest_tm.htsi_level.value if (latest_tm and latest_tm.htsi_level) else "HIGH",
        mortality_risk_score=round(avg_mortality, 1),
        hospitalization_risk_score=round(avg_hosp, 1),

        # Counts
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
