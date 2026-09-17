"""
HeatGuard AI — Weather Schemas
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from app.models.models import RiskLevelEnum, DataSourceEnum


class WeatherDataOut(BaseModel):
    id: int
    city_id: int
    ward_id: Optional[int] = None
    timestamp: datetime
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    pressure: Optional[float] = None
    cloud_cover: Optional[float] = None
    feels_like: Optional[float] = None
    data_source: DataSourceEnum
    heatwave_day_number: int

    model_config = {"from_attributes": True}


class ForecastDataOut(BaseModel):
    id: int
    city_id: int
    ward_id: Optional[int] = None
    forecast_for_date: datetime
    created_at: datetime
    temperature_min: float
    temperature_max: float
    temperature_avg: float
    humidity: float
    wind_speed: float
    solar_radiation: Optional[float] = None
    heat_index: Optional[float] = None
    wbgt: Optional[float] = None
    htsi: Optional[float] = None
    risk_level: Optional[RiskLevelEnum] = None
    mortality_risk_score: Optional[float] = None
    hospitalization_risk_score: Optional[float] = None
    data_source: DataSourceEnum

    model_config = {"from_attributes": True}
