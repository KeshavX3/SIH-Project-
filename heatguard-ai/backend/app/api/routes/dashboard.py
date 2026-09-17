"""
HeatGuard AI — Dashboard Route
GET /api/dashboard/summary  — High-level operational summary for the first city
GET /api/dashboard/summary/{city_id} — Summary for a specific city
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.api.deps import get_db, get_current_user
from app.core.config import settings
from app.models.models import (
    City, Ward, Alert, AlertStatusEnum, RiskLevelEnum,
    RiskPrediction, WeatherData, PopulationData, User,
)
from app.schemas.dashboard import DashboardSummary, WardSnapshot, RiskDistribution
from app.schemas.alert import AlertSummary

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def _build_summary(city_id: int, db: Session) -> DashboardSummary:
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    wards = db.query(Ward).filter(Ward.city_id == city_id).all()
    ward_ids = [w.id for w in wards]

    # Alert stats
    active_alerts = (
        db.query(Alert)
        .filter(Alert.ward_id.in_(ward_ids), Alert.status == AlertStatusEnum.ACTIVE)
        .all()
    )
    extreme_count = sum(1 for a in active_alerts if a.severity == RiskLevelEnum.EXTREME)
    high_count = sum(1 for a in active_alerts if a.severity == RiskLevelEnum.HIGH)

    # Latest risk predictions per ward
    ward_snapshots: List[WardSnapshot] = []
    htsi_values: List[float] = []
    temp_values: List[float] = []
    risk_dist = RiskDistribution()

    ward_name_map = {w.id: w.ward_name for w in wards}
    ward_num_map = {w.id: w.ward_number for w in wards}

    for ward in wards:
        pred = (
            db.query(RiskPrediction)
            .filter(RiskPrediction.ward_id == ward.id)
            .order_by(RiskPrediction.predicted_at.desc())
            .first()
        )
        weather = (
            db.query(WeatherData)
            .filter(WeatherData.ward_id == ward.id)
            .order_by(WeatherData.timestamp.desc())
            .first()
        )
        pop = (
            db.query(PopulationData)
            .filter(PopulationData.ward_id == ward.id)
            .first()
        )
        active_count = sum(1 for a in active_alerts if a.ward_id == ward.id)

        htsi = pred.htsi if pred else None
        risk_level = pred.overall_risk_level if pred else None

        if htsi is not None:
            htsi_values.append(htsi)
        if weather:
            temp_values.append(weather.temperature)

        # Tally risk distribution
        if risk_level:
            level_str = risk_level.value.lower()
            if level_str == "safe":
                risk_dist.safe += 1
            elif level_str == "low":
                risk_dist.low += 1
            elif level_str == "moderate":
                risk_dist.moderate += 1
            elif level_str == "high":
                risk_dist.high += 1
            elif level_str == "extreme":
                risk_dist.extreme += 1
        else:
            risk_dist.safe += 1

        ward_snapshots.append(
            WardSnapshot(
                ward_id=ward.id,
                ward_name=ward.ward_name,
                ward_number=ward.ward_number,
                htsi=htsi,
                risk_level=risk_level,
                temperature=weather.temperature if weather else None,
                humidity=weather.humidity if weather else None,
                vulnerability_score=pop.vulnerability_score if pop else None,
                active_alerts=active_count,
            )
        )

    # Sort by HTSI descending for "worst wards"
    worst_wards = sorted(
        ward_snapshots,
        key=lambda w: (w.htsi or 0),
        reverse=True,
    )[:5]

    # Recent active alerts with ward names
    recent_alerts: List[AlertSummary] = []
    for a in sorted(active_alerts, key=lambda x: x.created_at, reverse=True)[:10]:
        recent_alerts.append(
            AlertSummary(
                id=a.id,
                ward_id=a.ward_id,
                ward_name=ward_name_map.get(a.ward_id),
                severity=a.severity,
                status=a.status,
                title=a.title,
                htsi_value=a.htsi_value,
                created_at=a.created_at,
            )
        )

    return DashboardSummary(
        city_name=city.name,
        city_id=city.id,
        total_wards=len(wards),
        active_alerts_count=len(active_alerts),
        extreme_alerts_count=extreme_count,
        high_alerts_count=high_count,
        risk_distribution=risk_dist,
        avg_htsi=round(sum(htsi_values) / len(htsi_values), 2) if htsi_values else None,
        max_htsi=round(max(htsi_values), 2) if htsi_values else None,
        avg_temperature=round(sum(temp_values) / len(temp_values), 2) if temp_values else None,
        worst_wards=worst_wards,
        recent_alerts=recent_alerts,
        demo_mode=settings.DEMO_MODE,
    )


@router.get("/summary", response_model=DashboardSummary)
def get_dashboard_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return operational dashboard summary for the first active city."""
    city = db.query(City).filter(City.is_active == True).first()
    if not city:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No cities found. Run the demo seeder first.",
        )
    return _build_summary(city.id, db)


@router.get("/summary/{city_id}", response_model=DashboardSummary)
def get_city_dashboard_summary(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Return operational dashboard summary for a specific city."""
    return _build_summary(city_id, db)
