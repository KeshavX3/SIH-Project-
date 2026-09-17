"""
HeatGuard AI — City & Ward Routes
GET /api/cities/                        — List all active cities
GET /api/cities/{city_id}               — Get a single city
GET /api/cities/{city_id}/wards         — List wards with latest risk snapshot
GET /api/cities/{city_id}/wards/{ward_id} — Single ward detail
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, get_current_user
from app.models.models import City, Ward, RiskPrediction, Alert, AlertStatusEnum, User
from app.schemas.city import CityOut, WardOut, WardWithMetrics

router = APIRouter(prefix="/cities", tags=["Cities & Wards"])


@router.get("/", response_model=List[CityOut])
def list_cities(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all active cities."""
    return db.query(City).filter(City.is_active == True).all()


@router.get("/{city_id}", response_model=CityOut)
def get_city(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")
    return city


@router.get("/{city_id}/wards", response_model=List[WardWithMetrics])
def list_wards(
    city_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    List all wards for a city, enriched with:
    - Latest HTSI and risk level from the most recent RiskPrediction
    - Active alert count
    - Population data
    """
    city = db.query(City).filter(City.id == city_id).first()
    if not city:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="City not found")

    wards = (
        db.query(Ward)
        .options(joinedload(Ward.population_data))
        .filter(Ward.city_id == city_id)
        .all()
    )

    result: List[WardWithMetrics] = []
    for ward in wards:
        # Latest risk prediction
        latest_pred = (
            db.query(RiskPrediction)
            .filter(RiskPrediction.ward_id == ward.id)
            .order_by(RiskPrediction.predicted_at.desc())
            .first()
        )
        # Active alert count
        active_alerts = (
            db.query(Alert)
            .filter(Alert.ward_id == ward.id, Alert.status == AlertStatusEnum.ACTIVE)
            .count()
        )

        ward_data = WardWithMetrics(
            id=ward.id,
            ward_number=ward.ward_number,
            ward_name=ward.ward_name,
            city_id=ward.city_id,
            latitude=ward.latitude,
            longitude=ward.longitude,
            area_sq_km=ward.area_sq_km,
            geojson_geometry=ward.geojson_geometry,
            population_data=ward.population_data,
            latest_htsi=latest_pred.htsi if latest_pred else None,
            latest_risk_level=latest_pred.overall_risk_level if latest_pred else None,
            active_alert_count=active_alerts,
        )
        result.append(ward_data)

    return result


@router.get("/{city_id}/wards/{ward_id}", response_model=WardWithMetrics)
def get_ward(
    city_id: int,
    ward_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    ward = (
        db.query(Ward)
        .options(joinedload(Ward.population_data))
        .filter(Ward.id == ward_id, Ward.city_id == city_id)
        .first()
    )
    if not ward:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ward not found")

    latest_pred = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.ward_id == ward_id)
        .order_by(RiskPrediction.predicted_at.desc())
        .first()
    )
    active_alerts = (
        db.query(Alert)
        .filter(Alert.ward_id == ward_id, Alert.status == AlertStatusEnum.ACTIVE)
        .count()
    )

    return WardWithMetrics(
        id=ward.id,
        ward_number=ward.ward_number,
        ward_name=ward.ward_name,
        city_id=ward.city_id,
        latitude=ward.latitude,
        longitude=ward.longitude,
        area_sq_km=ward.area_sq_km,
        geojson_geometry=ward.geojson_geometry,
        population_data=ward.population_data,
        latest_htsi=latest_pred.htsi if latest_pred else None,
        latest_risk_level=latest_pred.overall_risk_level if latest_pred else None,
        active_alert_count=active_alerts,
    )
