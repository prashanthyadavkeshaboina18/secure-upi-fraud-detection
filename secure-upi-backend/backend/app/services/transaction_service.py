"""
Orchestrates a single payment through the whole pipeline:
  compute features -> predict -> score -> reasons -> persist -> maybe alert.

Nothing here computes a prediction itself — it only calls the services that
do, in order, and writes down what happened. That separation is what makes
each step (feature_service, prediction_service, risk_service, reason_service)
independently testable.
"""
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.fraud_alert import AlertSeverity
from app.models.model_log import ModelLog
from app.models.transaction import Decision, Transaction
from app.models.user import User
from app.schemas.transaction import TransactionIn
from app.services import alert_service, feature_service, prediction_service, reason_service, risk_service
from app.utils.exceptions import bad_request, not_found
from app.utils.ids import generate_transaction_id


def _serialise(txn: Transaction) -> dict:
    return {
        "transaction_id": txn.transaction_id,
        "amount": float(txn.amount),
        "receiver_vpa": txn.receiver_vpa,
        "merchant_name": txn.merchant_name,
        "merchant_category": txn.merchant_category,
        "transaction_type": txn.transaction_type,
        "device_id": txn.device_id,
        "device_type": txn.device_type,
        "location_city": txn.location_city,
        "fraud_probability": txn.fraud_probability,
        "risk_score": txn.risk_score,
        "risk_level": txn.risk_level.value if txn.risk_level else None,
        "decision": txn.decision.value,
        "reasons": txn.reasons or [],
        "model_version": txn.model_version,
        "user_id": txn.user_id,
        "user_name": txn.user.name if txn.user else None,
        "created_at": txn.created_at,
        "timestamp": txn.created_at,
    }


def analyse_transaction(db: Session, user: User, payload: TransactionIn) -> dict:
    features = feature_service.compute_features(db, user, payload)

    # Raises HTTP 503 here if no trained pipeline is loaded — see
    # prediction_service and app/ml_runtime/loader.py.
    probability, latency_ms = prediction_service.predict_fraud_probability(features)
    score, level, decision = risk_service.evaluate(probability)
    reasons = reason_service.build_reasons(features, level)

    from app.ml_runtime import loader
    model_version = loader.model_version() or "unversioned"

    txn = Transaction(
        transaction_id=generate_transaction_id(),
        user_id=user.id,
        amount=payload.amount,
        receiver_vpa=payload.receiver_vpa,
        merchant_name=payload.merchant_name,
        merchant_category=payload.merchant_category,
        transaction_type=payload.transaction_type,
        device_id=payload.device_id,
        device_type=payload.device_type,
        location_city=payload.location_city,
        fraud_probability=probability,
        risk_score=score,
        risk_level=level,
        decision=decision,
        reasons=reasons,
        model_version=model_version,
    )
    db.add(txn)
    db.commit()
    db.refresh(txn)

    db.add(ModelLog(
        transaction_id=txn.id,
        model_name=model_version.split("-")[0] if model_version else "unknown",
        model_version=model_version,
        prediction=int(decision == Decision.BLOCKED or decision == Decision.REVIEW),
        probability=probability,
        latency_ms=latency_ms,
    ))
    db.commit()

    if decision == Decision.BLOCKED:
        summary = "; ".join(reasons[:2]) if reasons else "Multiple risk signals detected"
        alert_service.create_alert(
            db, txn, AlertSeverity.HIGH,
            f"Payment of ₹{txn.amount:,.2f} to {txn.receiver_vpa} was blocked. {summary}.",
        )

    return _serialise(txn)


def _get_owned_or_404(db: Session, user: User, transaction_id: str, allow_admin: bool = False) -> Transaction:
    txn = db.query(Transaction).filter(Transaction.transaction_id == transaction_id).first()
    if not txn:
        raise not_found("Transaction")
    is_owner = txn.user_id == user.id
    is_admin = allow_admin and user.role.value == "ADMIN"
    if not is_owner and not is_admin:
        # 404, not 403 — we don't want to reveal that a transaction_id exists
        # for someone else's account.
        raise not_found("Transaction")
    return txn


def get_transaction(db: Session, user: User, transaction_id: str) -> dict:
    txn = _get_owned_or_404(db, user, transaction_id, allow_admin=True)
    return _serialise(txn)


def confirm_transaction(db: Session, user: User, transaction_id: str) -> dict:
    txn = _get_owned_or_404(db, user, transaction_id)
    if txn.decision != Decision.REVIEW:
        raise bad_request("Only a payment awaiting verification can be confirmed")

    txn.decision = Decision.APPROVED
    txn.confirmed_at = datetime.utcnow()
    db.commit()
    db.refresh(txn)
    return _serialise(txn)


def cancel_transaction(db: Session, user: User, transaction_id: str) -> dict:
    txn = _get_owned_or_404(db, user, transaction_id)
    if txn.decision != Decision.REVIEW:
        raise bad_request("Only a payment awaiting verification can be cancelled")

    txn.decision = Decision.CANCELLED
    db.commit()
    db.refresh(txn)
    return _serialise(txn)


def _apply_filters(query, model, filters: dict):
    if filters.get("risk_level"):
        query = query.filter(model.risk_level == filters["risk_level"])
    if filters.get("decision"):
        query = query.filter(model.decision == filters["decision"])
    if filters.get("date_from"):
        query = query.filter(model.created_at >= filters["date_from"])
    if filters.get("search"):
        term = f"%{filters['search']}%"
        query = query.filter(
            (model.transaction_id.ilike(term)) | (model.receiver_vpa.ilike(term))
        )
    return query


def list_for_user(db: Session, user: User, filters: dict, skip: int, limit: int) -> tuple[list[dict], int]:
    query = db.query(Transaction).filter(Transaction.user_id == user.id)
    query = _apply_filters(query, Transaction, filters)
    query = query.order_by(Transaction.created_at.desc())
    total = query.count()
    items = [_serialise(t) for t in query.offset(skip).limit(limit).all()]
    return items, total


def list_all(db: Session, filters: dict, skip: int, limit: int) -> tuple[list[dict], int]:
    query = db.query(Transaction)
    query = _apply_filters(query, Transaction, filters)
    query = query.order_by(Transaction.created_at.desc())
    total = query.count()
    items = [_serialise(t) for t in query.offset(skip).limit(limit).all()]
    return items, total
