"""
HeatGuard AI — Dashboard Schemas
"""
from typing import List, Optional
from pydantic import BaseModel
from app.models.models import RiskLevelEnum
from app.schemas.alert import AlertSummary


class WardSnapshot(BaseModel):
    ward_id: int
    ward_name: str
    ward_number: int
    htsi: Optional[float] = None
    risk_level: Optional[RiskLevelEnum] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None
    vulnerability_score: Optional[float] = None
    active_alerts: int = 0


class RiskDistribution(BaseModel):
    safe: int = 0
    low: int = 0
    moderate: int = 0
    high: int = 0
    extreme: int = 0


class DashboardSummary(BaseModel):
    city_name: str
    city_id: int
    total_wards: int
    active_alerts_count: int
    extreme_alerts_count: int
    high_alerts_count: int
    risk_distribution: RiskDistribution
    avg_htsi: Optional[float] = None
    max_htsi: Optional[float] = None
    avg_temperature: Optional[float] = None
    worst_wards: List[WardSnapshot]
    recent_alerts: List[AlertSummary]
    demo_mode: bool
