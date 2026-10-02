from datetime import datetime

from sqlalchemy.orm import Session

from app.models.fraud_alert import AlertSeverity, AlertStatus, FraudAlert
from app.models.transaction import Transaction
from app.models.user import User
from app.utils.exceptions import not_found


def create_alert(db: Session, transaction: Transaction, severity: AlertSeverity, message: str) -> FraudAlert:
    alert = FraudAlert(
        transaction_id=transaction.id,
        user_id=transaction.user_id,
        alert_type="HIGH_RISK_TRANSACTION",
        message=message,
        severity=severity,
        status=AlertStatus.NEW,
    )
    db.add(alert)
    db.commit()
    db.refresh(alert)
    return alert


def _serialise(alert: FraudAlert) -> dict:
    return {
        "id": alert.id,
        "transaction_id": alert.transaction.transaction_id if alert.transaction else None,
        "user_id": alert.user_id,
        "user_name": alert.user.name if alert.user else None,
        "alert_type": alert.alert_type,
        "message": alert.message,
        "severity": alert.severity.value,
        "status": alert.status.value,
        "created_at": alert.created_at,
        "reviewed_at": alert.reviewed_at,
    }


def list_for_user(db: Session, user: User, skip: int, limit: int) -> tuple[list[dict], int]:
    query = db.query(FraudAlert).filter(FraudAlert.user_id == user.id).order_by(FraudAlert.created_at.desc())
    total = query.count()
    items = [_serialise(a) for a in query.offset(skip).limit(limit).all()]
    return items, total


def list_all(db: Session, status: str | None, skip: int, limit: int) -> tuple[list[dict], int]:
    query = db.query(FraudAlert).order_by(FraudAlert.created_at.desc())
    if status:
        query = query.filter(FraudAlert.status == AlertStatus(status))
    total = query.count()
    items = [_serialise(a) for a in query.offset(skip).limit(limit).all()]
    return items, total


def update_status(db: Session, alert_id: int, new_status: str) -> dict:
    alert = db.get(FraudAlert, alert_id)
    if not alert:
        raise not_found("Alert")

    alert.status = AlertStatus(new_status)
    if new_status in ("REVIEWED", "DISMISSED"):
        alert.reviewed_at = datetime.utcnow()

    db.commit()
    db.refresh(alert)
    return _serialise(alert)
