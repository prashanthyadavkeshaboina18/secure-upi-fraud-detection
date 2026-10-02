"""
Sanity checks for feature_service — the module that must stay identical
between training and serving. These don't test ML correctness (there's no
model here); they test that every declared feature is always produced,
including for a brand-new user with zero transaction history.
"""
from datetime import datetime

from app.database import SessionLocal, Base, engine
from app.models.user import User
from app.schemas.transaction import TransactionIn
from app.services import feature_service
from app.utils.security import hash_password


def _make_session():
    Base.metadata.create_all(bind=engine)
    return SessionLocal()


def test_cold_start_user_gets_safe_defaults():
    db = _make_session()
    user = User(
        name="New User", email="cold@example.com", phone="9000000002",
        password_hash=hash_password("x"), created_at=datetime.utcnow(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    payload = TransactionIn(
        amount=250, receiver_vpa="a@bank", merchant_category="Groceries",
        transaction_type="P2M", device_id="DEV-NEW", device_type="ANDROID",
        location_city="Hyderabad",
    )

    features = feature_service.compute_features(db, user, payload)

    assert set(features.keys()) == set(feature_service.FEATURE_ORDER)
    assert features["is_new_device"] == 1
    assert features["is_new_location"] == 1
    assert features["amount_to_avg_ratio"] == 1.0
    assert features["amount_zscore"] == 0.0
    assert features["lifetime_txn_count"] == 0

    db.close()
