"""
The single most important module in this backend.

This function is used TWICE across the whole project:
  1. Here, at serving time, computing features from live database queries.
  2. In ml/src/feature_engineering.py, at training time, computing the same
     features from a historical DataFrame.

If those two ever define a feature differently, the model's live behaviour
silently diverges from its reported offline metrics — a failure mode called
training/serving skew. Keeping FEATURE_ORDER and each feature's definition
identical in both places (or, ideally, importing this exact module from the
training script) is what makes this project's metrics trustworthy.

Every feature below is written in raw, human-checkable form. Categorical
columns (transaction_type, merchant_category) are left as strings — the
saved sklearn pipeline is responsible for encoding them, exactly as it did
during training.
"""
import statistics
from datetime import datetime, timedelta

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Transaction
from app.models.user import User
from app.schemas.transaction import TransactionIn

# The exact column order the ML pipeline was trained on lives in
# feature_list.json (produced by training, loaded by ml_runtime.loader).
# This constant is the *fallback* used only if that file is missing, and
# must be kept in sync with ml/src/feature_engineering.py by hand.
FEATURE_ORDER: list[str] = [
    "amount",
    "hour",
    "day_of_week",
    "is_night",
    "is_weekend",
    "transaction_type",
    "merchant_category",
    "txn_count_last_5min",
    "txn_count_last_1h",
    "txn_count_last_24h",
    "amount_sum_last_1h",
    "seconds_since_last_txn",
    "amount_to_avg_ratio",
    "amount_zscore",
    "is_new_merchant_category",
    "is_new_device",
    "distinct_devices_30d",
    "device_changed",
    "is_new_location",
    "location_changed",
    "account_age_days",
    "lifetime_txn_count",
]


def _get_recent_transactions(db: Session, user_id: int, since: datetime) -> list[Transaction]:
    return (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id, Transaction.created_at >= since)
        .order_by(Transaction.created_at.desc())
        .all()
    )


def compute_features(db: Session, user: User, payload: TransactionIn, now: datetime | None = None) -> dict:
    """
    Builds one raw feature row for the incoming transaction.

    `now` is injectable so tests can freeze time instead of racing the clock;
    the API itself always calls this with the default (datetime.utcnow()).
    """
    now = now or datetime.utcnow()

    history_24h = _get_recent_transactions(db, user.id, now - timedelta(hours=24))
    history_5min = [t for t in history_24h if t.created_at >= now - timedelta(minutes=5)]
    history_1h = [t for t in history_24h if t.created_at >= now - timedelta(hours=1)]

    # Lifetime stats use every past transaction, not just the last 24h window.
    lifetime_txn_count = db.query(func.count(Transaction.id)).filter(
        Transaction.user_id == user.id
    ).scalar() or 0

    # Computed in Python rather than with SQL STDDEV(), which SQLite (used in
    # tests and quick local dev) does not support — this keeps the function
    # portable across SQLite, MySQL and Postgres without behaving differently.
    past_amounts = [
        float(row[0])
        for row in db.query(Transaction.amount).filter(Transaction.user_id == user.id).all()
    ]
    avg_amount = statistics.fmean(past_amounts) if past_amounts else None
    std_amount = statistics.pstdev(past_amounts) if len(past_amounts) > 1 else 0.0

    last_txn = (
        db.query(Transaction)
        .filter(Transaction.user_id == user.id)
        .order_by(Transaction.created_at.desc())
        .first()
    )

    known_devices = {
        row[0]
        for row in db.query(Transaction.device_id)
        .filter(Transaction.user_id == user.id, Transaction.created_at >= now - timedelta(days=30))
        .distinct()
    }
    known_merchant_categories = {
        row[0]
        for row in db.query(Transaction.merchant_category)
        .filter(Transaction.user_id == user.id)
        .distinct()
    }
    known_cities = {
        row[0]
        for row in db.query(Transaction.location_city)
        .filter(Transaction.user_id == user.id)
        .distinct()
    }

    # --- cold start: a brand-new user has no history, so ratios/z-scores
    # default to "unremarkable" (1.0 / 0.0) rather than crashing or blowing up. ---
    amount_to_avg_ratio = (payload.amount / avg_amount) if avg_amount else 1.0
    amount_zscore = ((payload.amount - avg_amount) / std_amount) if avg_amount and std_amount > 0 else 0.0

    seconds_since_last_txn = (
        (now - last_txn.created_at).total_seconds() if last_txn else 999_999
    )

    return {
        "amount": float(payload.amount),
        "hour": now.hour,
        "day_of_week": now.weekday(),
        "is_night": int(now.hour < 6 or now.hour >= 23),
        "is_weekend": int(now.weekday() >= 5),
        "transaction_type": payload.transaction_type,
        "merchant_category": payload.merchant_category,
        "txn_count_last_5min": len(history_5min),
        "txn_count_last_1h": len(history_1h),
        "txn_count_last_24h": len(history_24h),
        "amount_sum_last_1h": float(sum(float(t.amount) for t in history_1h)),
        "seconds_since_last_txn": seconds_since_last_txn,
        "amount_to_avg_ratio": amount_to_avg_ratio,
        "amount_zscore": amount_zscore,
        "is_new_merchant_category": int(payload.merchant_category not in known_merchant_categories),
        "is_new_device": int(payload.device_id not in known_devices),
        "distinct_devices_30d": len(known_devices),
        "device_changed": int(bool(last_txn) and last_txn.device_id != payload.device_id),
        "is_new_location": int(payload.location_city not in known_cities),
        "location_changed": int(bool(last_txn) and last_txn.location_city != payload.location_city),
        "account_age_days": (now - user.created_at).days,
        "lifetime_txn_count": int(lifetime_txn_count),
    }
