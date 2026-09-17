"""
HeatGuard AI — Alerts Router
"""
from datetime import datetime, timezone
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database.database import get_db
from app.models.models import Alert, AlertAction, Ward, User, AlertStatusEnum
from app.schemas.schemas import AlertResponse, AlertAcknowledgeRequest
from app.alerts.alert_engine import get_recommendations

router = APIRouter(prefix="/api/alerts", tags=["Alerts"])


def _alert_to_response(alert: Alert, db: Session) -> AlertResponse:
    ward = db.query(Ward).filter(Ward.id == alert.ward_id).first()
    return AlertResponse(
        id=alert.id,
        ward_id=alert.ward_id,
        ward_name=ward.ward_name if ward else "Unknown",
        severity=alert.severity.value if hasattr(alert.severity, "value") else str(alert.severity),
        status=alert.status.value if hasattr(alert.status, "value") else str(alert.status),
        title=alert.title,
        reason=alert.reason,
        htsi_value=alert.htsi_value,
        recommendations=alert.recommendations,
        created_at=alert.created_at,
        updated_at=alert.updated_at,
    )


@router.get("", response_model=List[AlertResponse])
def get_alerts(status: str = None, db: Session = Depends(get_db)):
    """Get all alerts, optionally filtered by status."""
    query = db.query(Alert)
    if status:
        try:
            status_enum = AlertStatusEnum(status.upper())
            query = query.filter(Alert.status == status_enum)
        except ValueError:
            pass
    alerts = query.order_by(Alert.created_at.desc()).all()
    return [_alert_to_response(a, db) for a in alerts]


@router.get("/active", response_model=List[AlertResponse])
def get_active_alerts(db: Session = Depends(get_db)):
    """Get all active (unacknowledged) alerts."""
    alerts = (
        db.query(Alert)
        .filter(Alert.status == AlertStatusEnum.ACTIVE)
        .order_by(Alert.created_at.desc())
        .all()
    )
    return [_alert_to_response(a, db) for a in alerts]


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert(
    alert_id: int,
    request: AlertAcknowledgeRequest,
    db: Session = Depends(get_db),
):
    """Acknowledge an active alert."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    if alert.status != AlertStatusEnum.ACTIVE:
        raise HTTPException(
            status_code=400,
            detail=f"Alert is already {alert.status.value}"
        )

    alert.status = AlertStatusEnum.ACKNOWLEDGED
    alert.updated_at = datetime.now(timezone.utc)

    action = AlertAction(
        alert_id=alert.id,
        action="ACKNOWLEDGED",
        notes=request.notes,
        timestamp=datetime.now(timezone.utc),
    )
    db.add(action)
    db.commit()
    db.refresh(alert)

    return _alert_to_response(alert, db)


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
def resolve_alert(alert_id: int, db: Session = Depends(get_db)):
    """Mark an alert as resolved."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")

    alert.status = AlertStatusEnum.RESOLVED
    alert.updated_at = datetime.now(timezone.utc)

    action = AlertAction(
        alert_id=alert.id,
        action="RESOLVED",
        timestamp=datetime.now(timezone.utc),
    )
    db.add(action)
    db.commit()
    db.refresh(alert)

    return _alert_to_response(alert, db)


@router.get("/{alert_id}", response_model=AlertResponse)
def get_alert(alert_id: int, db: Session = Depends(get_db)):
    """Get a specific alert by ID."""
    alert = db.query(Alert).filter(Alert.id == alert_id).first()
    if not alert:
        raise HTTPException(status_code=404, detail=f"Alert {alert_id} not found")
    return _alert_to_response(alert, db)


@router.get("/recommendations/{ward_id}")
def get_ward_recommendations(ward_id: int, db: Session = Depends(get_db)):
    """Get recommended actions for a ward based on current risk level."""
    from app.models.models import RiskPrediction
    rp = (
        db.query(RiskPrediction)
        .filter(RiskPrediction.ward_id == ward_id)
        .order_by(RiskPrediction.predicted_at.desc())
        .first()
    )

    if not rp:
        return {"ward_id": ward_id, "risk_level": "SAFE", "recommendations": get_recommendations("SAFE")}

    level = rp.overall_risk_level.value if hasattr(rp.overall_risk_level, "value") else str(rp.overall_risk_level)
    return {
        "ward_id": ward_id,
        "risk_level": level,
        "htsi": rp.htsi,
        "mortality_risk_score": rp.mortality_risk_score,
        "hospitalization_risk_score": rp.hospitalization_risk_score,
        "recommendations": get_recommendations(level),
    }
