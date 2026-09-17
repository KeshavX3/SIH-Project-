"""
HeatGuard AI — Alert Schemas
"""
from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel
from app.models.models import RiskLevelEnum, AlertStatusEnum


class AlertOut(BaseModel):
    id: int
    ward_id: int
    created_at: datetime
    updated_at: datetime
    severity: RiskLevelEnum
    status: AlertStatusEnum
    title: str
    reason: Optional[str] = None
    htsi_value: Optional[float] = None
    recommendations: Optional[Any] = None
    sms_sent: bool
    whatsapp_sent: bool
    email_sent: bool
    notification_simulated: bool

    model_config = {"from_attributes": True}


class AlertAcknowledge(BaseModel):
    notes: Optional[str] = None


class AlertSummary(BaseModel):
    """Lightweight alert summary for dashboard."""
    id: int
    ward_id: int
    ward_name: Optional[str] = None
    severity: RiskLevelEnum
    status: AlertStatusEnum
    title: str
    htsi_value: Optional[float] = None
    created_at: datetime

    model_config = {"from_attributes": True}
