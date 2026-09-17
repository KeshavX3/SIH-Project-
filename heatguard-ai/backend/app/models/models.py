"""
HeatGuard AI — SQLAlchemy Models
All database tables with proper relationships.

NOTE: PostGIS geometry columns use GeoAlchemy2.
If PostGIS is not available, the geometry columns are gracefully skipped.
"""
from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, Boolean, DateTime,
    ForeignKey, Text, Enum, JSON
)
from sqlalchemy.orm import relationship
from app.database.database import Base
import enum


# ─── Enums ─────────────────────────────────────────────────────────────────

class RoleEnum(str, enum.Enum):
    ADMIN = "ADMIN"
    AUTHORITY = "AUTHORITY"
    ANALYST = "ANALYST"
    PUBLIC = "PUBLIC"


class RiskLevelEnum(str, enum.Enum):
    SAFE = "SAFE"
    LOW = "LOW"
    MODERATE = "MODERATE"
    HIGH = "HIGH"
    EXTREME = "EXTREME"


class AlertStatusEnum(str, enum.Enum):
    ACTIVE = "ACTIVE"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    RESOLVED = "RESOLVED"


class DataSourceEnum(str, enum.Enum):
    LIVE = "LIVE"
    DEMO = "DEMO"
    HISTORICAL = "HISTORICAL"
    SYNTHETIC = "SYNTHETIC"
    FORECAST = "FORECAST"


# ─── Users & Auth ──────────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    full_name = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(RoleEnum), default=RoleEnum.ANALYST, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    last_login = Column(DateTime(timezone=True), nullable=True)

    acknowledged_alerts = relationship("AlertAction", back_populates="user")


# ─── Geography ─────────────────────────────────────────────────────────────

class City(Base):
    __tablename__ = "cities"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    state = Column(String(255), nullable=False)
    country = Column(String(100), default="India")
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    population = Column(Integer, nullable=True)
    area_sq_km = Column(Float, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    wards = relationship("Ward", back_populates="city")
    weather_data = relationship("WeatherData", back_populates="city")
    forecast_data = relationship("ForecastData", back_populates="city")


class Ward(Base):
    __tablename__ = "wards"

    id = Column(Integer, primary_key=True, index=True)
    ward_number = Column(Integer, nullable=False)
    ward_name = Column(String(255), nullable=False)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    area_sq_km = Column(Float, nullable=True)
    # GeoJSON polygon stored as JSON (PostGIS geometry as bonus if available)
    geojson_geometry = Column(JSON, nullable=True)

    city = relationship("City", back_populates="wards")
    population_data = relationship("PopulationData", back_populates="ward", uselist=False)
    weather_data = relationship("WeatherData", back_populates="ward")
    thermal_metrics = relationship("ThermalMetrics", back_populates="ward")
    risk_predictions = relationship("RiskPrediction", back_populates="ward")
    alerts = relationship("Alert", back_populates="ward")
    cooling_centers = relationship("CoolingCenter", back_populates="ward")
    hospitals = relationship("Hospital", back_populates="ward")


# ─── Population & Demographics ─────────────────────────────────────────────

class PopulationData(Base):
    __tablename__ = "population_data"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), unique=True, nullable=False)
    total_population = Column(Integer, nullable=False)
    elderly_population = Column(Integer, nullable=True)  # 60+ years
    children_population = Column(Integer, nullable=True)  # < 15 years
    outdoor_worker_population = Column(Integer, nullable=True)
    population_density = Column(Float, nullable=True)  # per sq km
    elderly_density = Column(Float, nullable=True)
    outdoor_worker_density = Column(Float, nullable=True)
    # Derived vulnerability score (0–100)
    vulnerability_score = Column(Float, nullable=True)
    vulnerability_level = Column(Enum(RiskLevelEnum), nullable=True)
    data_source = Column(Enum(DataSourceEnum), default=DataSourceEnum.DEMO)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    ward = relationship("Ward", back_populates="population_data")


class HealthIndicator(Base):
    __tablename__ = "health_indicators"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False)
    year = Column(Integer, nullable=False)
    heat_related_deaths = Column(Float, nullable=True)  # Per 100k
    heat_hospitalizations = Column(Float, nullable=True)  # Per 100k
    hospital_beds = Column(Integer, nullable=True)
    data_source = Column(Enum(DataSourceEnum), default=DataSourceEnum.DEMO)
    notes = Column(Text, nullable=True)


# ─── Weather ───────────────────────────────────────────────────────────────

class WeatherData(Base):
    __tablename__ = "weather_data"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    temperature = Column(Float, nullable=False)      # °C
    humidity = Column(Float, nullable=False)          # %
    wind_speed = Column(Float, nullable=False)        # km/h
    solar_radiation = Column(Float, nullable=True)   # W/m²
    pressure = Column(Float, nullable=True)           # hPa
    cloud_cover = Column(Float, nullable=True)        # %
    feels_like = Column(Float, nullable=True)         # °C
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    data_source = Column(Enum(DataSourceEnum), default=DataSourceEnum.DEMO)
    heatwave_day_number = Column(Integer, default=0)  # consecutive days of heat

    city = relationship("City", back_populates="weather_data")
    ward = relationship("Ward", back_populates="weather_data")
    thermal_metrics = relationship("ThermalMetrics", back_populates="weather_data", uselist=False)


class ForecastData(Base):
    __tablename__ = "forecast_data"

    id = Column(Integer, primary_key=True, index=True)
    city_id = Column(Integer, ForeignKey("cities.id"), nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    forecast_for_date = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    temperature_min = Column(Float, nullable=False)
    temperature_max = Column(Float, nullable=False)
    temperature_avg = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    wind_speed = Column(Float, nullable=False)
    solar_radiation = Column(Float, nullable=True)
    cloud_cover = Column(Float, nullable=True)
    data_source = Column(Enum(DataSourceEnum), default=DataSourceEnum.DEMO)
    # Calculated thermal metrics for the forecast day
    heat_index = Column(Float, nullable=True)
    wbgt = Column(Float, nullable=True)
    htsi = Column(Float, nullable=True)
    risk_level = Column(Enum(RiskLevelEnum), nullable=True)
    mortality_risk_score = Column(Float, nullable=True)
    hospitalization_risk_score = Column(Float, nullable=True)

    city = relationship("City", back_populates="forecast_data")
    ward = relationship("Ward")


# ─── Thermal Metrics ───────────────────────────────────────────────────────

class ThermalMetrics(Base):
    __tablename__ = "thermal_metrics"

    id = Column(Integer, primary_key=True, index=True)
    weather_data_id = Column(Integer, ForeignKey("weather_data.id"), unique=True, nullable=False)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=True)
    calculated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    # Standard thermal indices
    heat_index = Column(Float, nullable=True)        # °C (NOAA methodology)
    wbgt = Column(Float, nullable=True)               # °C (approximation)
    utci = Column(Float, nullable=True)               # °C (if implemented)

    # Thermal stress classifications
    heat_index_level = Column(Enum(RiskLevelEnum), nullable=True)
    wbgt_level = Column(Enum(RiskLevelEnum), nullable=True)

    # Project-specific composite index
    htsi = Column(Float, nullable=True)               # 0–100
    htsi_level = Column(Enum(RiskLevelEnum), nullable=True)

    # HTSI component breakdown (for explainability)
    htsi_temp_contribution = Column(Float, nullable=True)
    htsi_humidity_contribution = Column(Float, nullable=True)
    htsi_wind_contribution = Column(Float, nullable=True)
    htsi_solar_contribution = Column(Float, nullable=True)
    htsi_wbgt_contribution = Column(Float, nullable=True)
    htsi_duration_contribution = Column(Float, nullable=True)

    weather_data = relationship("WeatherData", back_populates="thermal_metrics")
    ward = relationship("Ward", back_populates="thermal_metrics")


# ─── Risk Predictions ──────────────────────────────────────────────────────

class RiskPrediction(Base):
    __tablename__ = "risk_predictions"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False)
    predicted_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    valid_for = Column(DateTime(timezone=True), nullable=False)

    # Thermal risk
    overall_risk_level = Column(Enum(RiskLevelEnum), nullable=False)
    htsi = Column(Float, nullable=True)

    # Health risks
    mortality_risk_score = Column(Float, nullable=True)   # 0–100
    hospitalization_risk_score = Column(Float, nullable=True)  # 0–100
    mortality_risk_level = Column(Enum(RiskLevelEnum), nullable=True)
    hospitalization_risk_level = Column(Enum(RiskLevelEnum), nullable=True)

    # ML model info
    model_version_id = Column(Integer, ForeignKey("model_versions.id"), nullable=True)
    prediction_features = Column(JSON, nullable=True)  # Input features used
    feature_importance = Column(JSON, nullable=True)    # Top contributing factors

    # Combined score inputs
    vulnerability_score = Column(Float, nullable=True)
    temperature_anomaly = Column(Float, nullable=True)
    heatwave_duration = Column(Integer, nullable=True)

    ward = relationship("Ward", back_populates="risk_predictions")
    model_version = relationship("ModelVersion")


# ─── Alerts ────────────────────────────────────────────────────────────────

class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    severity = Column(Enum(RiskLevelEnum), nullable=False)
    status = Column(Enum(AlertStatusEnum), default=AlertStatusEnum.ACTIVE)

    title = Column(String(500), nullable=False)
    reason = Column(Text, nullable=True)
    htsi_value = Column(Float, nullable=True)
    recommendations = Column(JSON, nullable=True)  # List of recommended actions

    # Notification tracking
    sms_sent = Column(Boolean, default=False)
    whatsapp_sent = Column(Boolean, default=False)
    email_sent = Column(Boolean, default=False)
    notification_simulated = Column(Boolean, default=False)

    ward = relationship("Ward", back_populates="alerts")
    actions = relationship("AlertAction", back_populates="alert")


class AlertAction(Base):
    __tablename__ = "alert_actions"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)  # ACKNOWLEDGED / RESOLVED / NOTIFIED
    timestamp = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    notes = Column(Text, nullable=True)

    alert = relationship("Alert", back_populates="actions")
    user = relationship("User", back_populates="acknowledged_alerts")


# ─── Infrastructure ────────────────────────────────────────────────────────

class CoolingCenter(Base):
    __tablename__ = "cooling_centers"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    capacity = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=False)  # Activated during alerts
    contact = Column(String(100), nullable=True)

    ward = relationship("Ward", back_populates="cooling_centers")


class Hospital(Base):
    __tablename__ = "hospitals"

    id = Column(Integer, primary_key=True, index=True)
    ward_id = Column(Integer, ForeignKey("wards.id"), nullable=False)
    name = Column(String(255), nullable=False)
    address = Column(Text, nullable=True)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    bed_count = Column(Integer, nullable=True)
    icu_beds = Column(Integer, nullable=True)
    contact = Column(String(100), nullable=True)

    ward = relationship("Ward", back_populates="hospitals")


# ─── ML Model Registry ─────────────────────────────────────────────────────

class ModelVersion(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False)
    version = Column(String(50), nullable=False)
    algorithm = Column(String(100), nullable=False)
    training_date = Column(DateTime(timezone=True), nullable=True)
    features = Column(JSON, nullable=True)      # List of feature names
    target = Column(String(100), nullable=True)
    evaluation_metrics = Column(JSON, nullable=True)
    dataset_description = Column(Text, nullable=True)
    model_path = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    notes = Column(Text, nullable=True)
