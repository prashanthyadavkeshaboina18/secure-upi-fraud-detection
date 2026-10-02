from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TransactionIn(BaseModel):
    """What the frontend's payment form submits."""
    amount: float = Field(gt=0, le=100000, description="UPI per-transaction ceiling is ₹1,00,000")
    receiver_vpa: str = Field(min_length=3, max_length=100)
    merchant_name: str | None = Field(default=None, max_length=120)
    merchant_category: str = Field(max_length=60)
    transaction_type: str = Field(max_length=20)
    device_id: str = Field(min_length=1, max_length=100)
    device_type: str = Field(max_length=20)
    location_city: str = Field(max_length=60)


class TransactionOut(BaseModel):
    """
    Returned by /predict, by the list/detail endpoints, and by confirm/cancel.
    One shape everywhere keeps the frontend's TransactionResult, history table
    and detail page all rendering the same object.
    """
    transaction_id: str
    amount: float
    receiver_vpa: str
    merchant_name: str | None = None
    merchant_category: str
    transaction_type: str
    device_id: str
    device_type: str
    location_city: str

    fraud_probability: float | None = None
    risk_score: int | None = None
    risk_level: str | None = None
    decision: str
    reasons: list[str] = []
    model_version: str | None = None

    user_id: int | None = None
    user_name: str | None = None

    created_at: datetime
    timestamp: datetime | None = None  # alias for created_at, matches the Phase-1 API contract

    model_config = ConfigDict(from_attributes=True, protected_namespaces=())


class TransactionListOut(BaseModel):
    items: list[TransactionOut]
    total: int


class AlertStatusUpdate(BaseModel):
    status: str = Field(pattern="^(NEW|REVIEWED|DISMISSED)$")
