"""
HeatGuard AI — Alert Routes
GET  /api/alerts/                       — List alerts (filterable)
GET  /api/alerts/{alert_id}             — Get single alert
POST /api/alerts/{alert_id}/acknowledge — Acknowledge an active alert
POST /api/alerts/{alert_id}/resolve     — Resolve an alert
"""
from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_db, get_current_user
from app.models.models import Alert, AlertAction, AlertStatusEnum, RiskLevelEnum, User
from app.schemas.alert import AlertOut, AlertAcknowledge

router = APIRouter(prefix="/alerts", tags=["Alerts"])


@router.get("/", response_model=List[AlertOut])
def list_alerts(
    alert_status: Optional[AlertStatusEnum] = Query(None, alias="status"),
    severity: Optional[RiskLevelEnum] = Query(None),
    ward_id: Optional[int] = Query(None),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List alerts with optional filters for status, severity, and ward."""
    q = db.query(Alert)
    if alert_status:
        q = q.filter(Alert.status == alert_status)
    if severity:
        q = q.filter(Alert.severity == severity)
    if ward_id:
        q = q.filter(Alert.ward_id == ward_id)
    return q.order_by(Alert.created_at.desc()).limit(limit).all()


@router.get("/{alert_id}", response_model=AlertOut)
def get_alert(
    alert_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    return alert


@router.post("/{alert_id}/acknowledge", response_model=AlertOut)
def acknowledge_alert(
    alert_id: int,
    payload: AlertAcknowledge,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as ACKNOWLEDGED and record the action."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    if alert.status != AlertStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Alert is already {alert.status.value}",
        )

    alert.status = AlertStatusEnum.ACKNOWLEDGED
    alert.updated_at = datetime.now(timezone.utc)

    action = AlertAction(
        alert_id=alert_id,
        user_id=current_user.id,
        action="ACKNOWLEDGED",
        notes=payload.notes,
    )
    db.add(action)
    db.commit()
    db.refresh(alert)
    return alert


@router.post("/{alert_id}/resolve", response_model=AlertOut)
def resolve_alert(
    alert_id: int,
    payload: AlertAcknowledge,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark an alert as RESOLVED."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    if alert.status == AlertStatusEnum.RESOLVED:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Alert already resolved")

    alert.status = AlertStatusEnum.RESOLVED
    alert.updated_at = datetime.now(timezone.utc)

    action = AlertAction(
        alert_id=alert_id,
        user_id=current_user.id,
        action="RESOLVED",
        notes=payload.notes,
    )
    db.add(action)
    db.commit()
    db.refresh(alert)
    return alert
