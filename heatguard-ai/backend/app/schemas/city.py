"""
HeatGuard AI — City & Ward Schemas
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from app.models.models import RiskLevelEnum


class CityOut(BaseModel):
    id: int
    name: str
    state: str
    country: str
    latitude: float
    longitude: float
    population: Optional[int] = None
    area_sq_km: Optional[float] = None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class PopulationDataOut(BaseModel):
    total_population: int
    elderly_population: Optional[int] = None
    children_population: Optional[int] = None
    outdoor_worker_population: Optional[int] = None
    population_density: Optional[float] = None
    vulnerability_score: Optional[float] = None
    vulnerability_level: Optional[RiskLevelEnum] = None

    model_config = {"from_attributes": True}


class WardOut(BaseModel):
    id: int
    ward_number: int
    ward_name: str
    city_id: int
    latitude: float
    longitude: float
    area_sq_km: Optional[float] = None
    geojson_geometry: Optional[Any] = None

    model_config = {"from_attributes": True}


class WardWithMetrics(WardOut):
    """Ward with latest risk snapshot for dashboard use."""
    population_data: Optional[PopulationDataOut] = None
    latest_htsi: Optional[float] = None
    latest_risk_level: Optional[RiskLevelEnum] = None
    active_alert_count: int = 0

    model_config = {"from_attributes": True}
