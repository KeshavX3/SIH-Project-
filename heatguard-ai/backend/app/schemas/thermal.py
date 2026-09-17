"""
HeatGuard AI — Thermal Schemas
"""
from typing import Dict, Optional
from pydantic import BaseModel, Field


class ThermalRequest(BaseModel):
    """Weather conditions to compute thermal indices from."""
    temperature: float = Field(..., ge=-10, le=60, description="Air temperature °C")
    humidity: float = Field(..., ge=0, le=100, description="Relative humidity %")
    wind_speed: float = Field(..., ge=0, le=200, description="Wind speed km/h")
    solar_radiation: float = Field(500.0, ge=0, le=1500, description="Solar irradiance W/m²")
    pressure: float = Field(1013.25, ge=800, le=1100, description="Atmospheric pressure hPa")
    cloud_cover: float = Field(0.0, ge=0, le=100, description="Cloud cover %")
    heatwave_duration: int = Field(0, ge=0, le=30, description="Consecutive heatwave days")


class ThermalResponse(BaseModel):
    """All calculated thermal metrics."""
    # Inputs echoed back
    temperature: float
    humidity: float
    wind_speed: float
    solar_radiation: float

    # Standard indices
    heat_index: float
    wbgt: float
    utci: float

    # Risk classifications
    heat_index_level: str
    wbgt_level: str

    # HTSI
    htsi: float
    htsi_level: str
    htsi_components: Dict[str, float]

    # Methodology transparency
    methodology_notes: str
