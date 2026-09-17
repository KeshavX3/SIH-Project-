"""
HeatGuard AI — Risk Router
"""
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import City, Ward, WeatherData, ThermalMetrics, PopulationData, RiskPrediction
from app.schemas.schemas import RiskResponse, VulnerabilityResponse

router = APIRouter(prefix="/api/risk", tags=["Risk"])


def _build_risk_response(ward: Ward, db: Session) -> RiskResponse:
    rp = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.ward_id == ward.id)
        .order_by(RiskPrediction.predicted_at.desc())
        .first()
    )
    pop = db.query(PopulationData).filter(PopulationData.ward_id == ward.id).first()

    if rp:
        return RiskResponse(
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
            risk_factors=rp.prediction_features or {},
        )

    return RiskResponse(
        ward_id=ward.id,
        ward_name=ward.ward_name,
        overall_risk_level="SAFE",
        htsi=0.0,
        mortality_risk_score=0.0,
        hospitalization_risk_score=0.0,
        mortality_risk_level="SAFE",
        hospitalization_risk_level="SAFE",
    )


@router.get("/current", response_model=List[RiskResponse])
def get_all_wards_risk(db: Session = Depends(get_db)):
    """Get current risk for all wards."""
    city = db.query(City).filter(City.name == "Jaipur").first()
    if not city:
        return []
    wards = db.query(Ward).filter(Ward.city_id == city.id).all()
    return [_build_risk_response(w, db) for w in wards]


@router.get("/ward/{ward_id}", response_model=RiskResponse)
def get_ward_risk(ward_id: int, db: Session = Depends(get_db)):
    """Get risk for a specific ward."""
    from fastapi import HTTPException
    ward = db.query(Ward).filter(Ward.id == ward_id).first()
    if not ward:
        raise HTTPException(status_code=404, detail=f"Ward {ward_id} not found")
    return _build_risk_response(ward, db)


@router.get("/vulnerability", response_model=List[VulnerabilityResponse])
def get_all_vulnerability(db: Session = Depends(get_db)):
    """Get vulnerability scores for all wards, sorted by score descending."""
    city = db.query(City).filter(City.name == "Jaipur").first()
    if not city:
        return []

    wards = db.query(Ward).filter(Ward.city_id == city.id).all()
    results = []
    for ward in wards:
        pop = db.query(PopulationData).filter(PopulationData.ward_id == ward.id).first()
        if pop:
            results.append(VulnerabilityResponse(
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
            ))

    return sorted(results, key=lambda x: x.vulnerability_score, reverse=True)
