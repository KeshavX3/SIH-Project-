"""
HeatGuard AI — Pydantic Schemas
All request/response schemas for the API.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, EmailStr, field_validator


# ─── Auth ──────────────────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserResponse"

class UserResponse(BaseModel):
    id: int
    email: str
    full_name: str
    role: str
    is_active: bool

    class Config:
        from_attributes = True


# ─── Weather ────────────────────────────────────────────────────────────────

class WeatherResponse(BaseModel):
    id: Optional[int] = None
    ward_id: Optional[int] = None
    timestamp: Optional[str] = None
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    pressure: Optional[float] = None
    cloud_cover: Optional[float] = None
    heatwave_day_number: int = 0
    data_source: str = "DEMO"
    data_source_note: Optional[str] = None

    class Config:
        from_attributes = True


class ForecastDayResponse(BaseModel):
    day: int
    date: str
    label: str
    temperature_max: float
    temperature_min: float
    temperature_avg: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    heat_index: Optional[float] = None
    wbgt: Optional[float] = None
    htsi: Optional[float] = None
    risk_level: Optional[str] = None
    mortality_risk_score: Optional[float] = None
    hospitalization_risk_score: Optional[float] = None
    data_source: str = "DEMO_FORECAST"


# ─── Thermal ────────────────────────────────────────────────────────────────

class ThermalResponse(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    heat_index: float
    wbgt: float
    utci: Optional[float] = None
    heat_index_level: str
    wbgt_level: str
    htsi: float
    htsi_level: str
    htsi_components: Dict[str, float] = {}
    methodology_notes: Optional[str] = None


class ThermalCalculationRequest(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: float = 700.0
    pressure: float = 1013.25
    cloud_cover: float = 0.0
    heatwave_duration: int = 0


# ─── Vulnerability ──────────────────────────────────────────────────────────

class VulnerabilityResponse(BaseModel):
    ward_id: int
    ward_name: Optional[str] = None
    vulnerability_score: float
    vulnerability_level: str
    components: Dict[str, float] = {}
    population_density: float
    elderly_density: float
    outdoor_worker_density: float
    children_density: float
    total_population: Optional[int] = None
    elderly_population: Optional[int] = None
    children_population: Optional[int] = None
    outdoor_worker_population: Optional[int] = None
    explanation: Optional[str] = None
    data_source: str = "DEMO"


# ─── Risk ───────────────────────────────────────────────────────────────────

class RiskResponse(BaseModel):
    ward_id: int
    ward_name: Optional[str] = None
    overall_risk_level: str
    htsi: float
    mortality_risk_score: float
    hospitalization_risk_score: float
    mortality_risk_level: str
    hospitalization_risk_level: str
    risk_factors: Dict[str, float] = {}
    explanation: Optional[str] = None
    model_used: str = "rule_based"
    vulnerability_score: Optional[float] = None
    temperature_anomaly: Optional[float] = None
    heatwave_duration: Optional[int] = None
    feature_importance: Optional[Dict[str, float]] = None


# ─── Ward ───────────────────────────────────────────────────────────────────

class WardDetailResponse(BaseModel):
    id: int
    ward_number: int
    ward_name: str
    city_id: int
    latitude: float
    longitude: float
    area_sq_km: Optional[float] = None
    weather: Optional[WeatherResponse] = None
    thermal: Optional[ThermalResponse] = None
    vulnerability: Optional[VulnerabilityResponse] = None
    risk: Optional[RiskResponse] = None

    class Config:
        from_attributes = True


class WardListResponse(BaseModel):
    id: int
    ward_number: int
    ward_name: str
    latitude: float
    longitude: float
    risk_level: Optional[str] = None
    htsi: Optional[float] = None
    mortality_risk_score: Optional[float] = None
    vulnerability_score: Optional[float] = None

    class Config:
        from_attributes = True


# ─── Alert ──────────────────────────────────────────────────────────────────

class AlertResponse(BaseModel):
    id: int
    ward_id: int
    ward_name: Optional[str] = None
    severity: str
    status: str
    title: str
    reason: Optional[str] = None
    htsi_value: Optional[float] = None
    recommendations: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    metrics: Optional[Dict[str, float]] = None

    class Config:
        from_attributes = True


class AlertAcknowledgeRequest(BaseModel):
    notes: Optional[str] = None


# ─── Dashboard ──────────────────────────────────────────────────────────────

class DashboardSummaryResponse(BaseModel):
    city: str
    state: str
    timestamp: str
    data_source: str

    # City-level weather (average/representative)
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None

    # City-level thermal
    heat_index: float
    wbgt: float
    htsi: float
    utci: Optional[float] = None

    # Risk levels
    overall_risk_level: str
    htsi_level: str
    mortality_risk_score: float
    hospitalization_risk_score: float

    # Counts
    total_wards: int
    extreme_wards: int
    high_wards: int
    moderate_wards: int
    safe_wards: int
    active_alerts: int

    # Top vulnerable ward
    highest_risk_ward: Optional[str] = None
    highest_risk_ward_id: Optional[int] = None

    # System status
    system_status: Dict[str, str] = {}


# ─── ML Prediction ──────────────────────────────────────────────────────────

class MLPredictRequest(BaseModel):
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: float
    heat_index: Optional[float] = None
    wbgt: Optional[float] = None
    htsi: Optional[float] = None
    temperature_anomaly: float = 0.0
    heatwave_duration: int = 0
    population_density: float = 5000.0
    elderly_density: float = 150.0
    outdoor_worker_density: float = 200.0
    historical_health_indicator: float = 50.0
    vulnerability_score: float = 50.0


class MLPredictResponse(BaseModel):
    success: bool
    predicted_class: Optional[str] = None
    risk_score: Optional[float] = None
    class_probabilities: Optional[Dict[str, float]] = None
    feature_importance: Optional[Dict[str, float]] = None
    model_version: Optional[str] = None
    disclaimer: Optional[str] = None
    error: Optional[str] = None


# ─── Health Check ───────────────────────────────────────────────────────────

class HealthCheckResponse(BaseModel):
    status: str
    services: Dict[str, str]
    timestamp: str
    version: str
    demo_mode: bool
