"""
Read-only aggregation queries for the user and admin dashboards. Kept
separate from transaction_service (which mutates data) so the two are easy
to reason about and test independently.
"""
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.fraud_alert import AlertStatus, FraudAlert
from app.models.transaction import Decision, RiskLevel, Transaction
from app.models.user import User


def get_user_stats(db: Session, user: User) -> dict:
    counts = dict(
        db.query(Transaction.decision, func.count(Transaction.id))
        .filter(Transaction.user_id == user.id)
        .group_by(Transaction.decision)
        .all()
    )
    total = sum(counts.values())

    open_alerts = (
        db.query(func.count(FraudAlert.id))
        .filter(FraudAlert.user_id == user.id, FraudAlert.status == AlertStatus.NEW)
        .scalar()
        or 0
    )

    recent_scores = [
        row[0]
        for row in db.query(Transaction.risk_score)
        .filter(Transaction.user_id == user.id, Transaction.risk_score.isnot(None))
        .order_by(Transaction.created_at.desc())
        .limit(5)
        .all()
    ]
    current_score = round(sum(recent_scores) / len(recent_scores)) if recent_scores else None
    if current_score is None:
        current_level = None
    elif current_score <= 30:
        current_level = RiskLevel.LOW.value
    elif current_score <= 70:
        current_level = RiskLevel.MEDIUM.value
    else:
        current_level = RiskLevel.HIGH.value

    return {
        "total_transactions": total,
        "approved_transactions": counts.get(Decision.APPROVED, 0),
        "review_transactions": counts.get(Decision.REVIEW, 0),
        "blocked_transactions": counts.get(Decision.BLOCKED, 0),
        "open_alerts": open_alerts,
        "current_risk_level": current_level,
        "current_risk_score": current_score,
    }


def get_fraud_statistics(db: Session, days: int = 14) -> dict:
    total = db.query(func.count(Transaction.id)).scalar() or 0

    fraud_flagged = (
        db.query(func.count(Transaction.id))
        .filter(Transaction.decision.in_([Decision.REVIEW, Decision.BLOCKED]))
        .scalar()
        or 0
    )
    blocked = db.query(func.count(Transaction.id)).filter(Transaction.decision == Decision.BLOCKED).scalar() or 0
    high_risk = db.query(func.count(Transaction.id)).filter(Transaction.risk_level == RiskLevel.HIGH).scalar() or 0
    fraud_rate = (fraud_flagged / total) if total else 0.0

    since = datetime.utcnow() - timedelta(days=days)
    rows = (
        db.query(Transaction.created_at, Transaction.decision)
        .filter(Transaction.created_at >= since)
        .all()
    )
    by_day: dict[str, dict[str, int]] = {}
    for created_at, decision in rows:
        key = created_at.strftime("%Y-%m-%d")
        bucket = by_day.setdefault(key, {"total": 0, "fraud": 0})
        bucket["total"] += 1
        if decision in (Decision.REVIEW, Decision.BLOCKED):
            bucket["fraud"] += 1
    transactions_over_time = [
        {"date": day, "total": v["total"], "fraud": v["fraud"]}
        for day, v in sorted(by_day.items())
    ]

    def _fraud_group_by(column):
        rows = (
            db.query(column, func.count(Transaction.id))
            .filter(Transaction.decision.in_([Decision.REVIEW, Decision.BLOCKED]))
            .group_by(column)
            .all()
        )
        return rows

    fraud_by_type = [
        {"transaction_type": t, "fraud_count": c}
        for t, c in _fraud_group_by(Transaction.transaction_type)
    ]
    fraud_by_location = [
        {"location_city": l, "fraud_count": c}
        for l, c in _fraud_group_by(Transaction.location_city)
    ]
    fraud_by_device = [
        {"device_type": d, "fraud_count": c}
        for d, c in _fraud_group_by(Transaction.device_type)
    ]

    risk_rows = (
        db.query(Transaction.risk_level, func.count(Transaction.id))
        .filter(Transaction.risk_level.isnot(None))
        .group_by(Transaction.risk_level)
        .all()
    )
    risk_distribution = [
        {"risk_level": level.value, "count": count} for level, count in risk_rows
    ]

    return {
        "total_transactions": total,
        "fraud_transactions": fraud_flagged,
        "fraud_rate": round(fraud_rate, 4),
        "blocked_transactions": blocked,
        "high_risk_transactions": high_risk,
        "transactions_over_time": transactions_over_time,
        "fraud_by_transaction_type": fraud_by_type,
        "fraud_by_location": fraud_by_location,
        "fraud_by_device": fraud_by_device,
        "risk_distribution": risk_distribution,
    }
