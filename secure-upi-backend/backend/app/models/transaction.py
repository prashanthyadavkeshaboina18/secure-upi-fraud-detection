import enum
from datetime import datetime

from sqlalchemy import (
    JSON, DateTime, Enum, Float, ForeignKey, Index, Integer, Numeric, String
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class RiskLevel(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class Decision(str, enum.Enum):
    APPROVED = "APPROVED"
    REVIEW = "REVIEW"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"  # a REVIEW transaction the user chose not to confirm


class Transaction(Base):
    __tablename__ = "transactions"
    __table_args__ = (
        # This index is the one that matters most: every single prediction
        # queries "this user's recent transactions ordered by time" to build
        # velocity features. Without it, that query degrades under load.
        Index("idx_txn_user_time", "user_id", "created_at"),
        Index("idx_txn_risk", "risk_level"),
        Index("idx_txn_decision", "decision"),
        Index("idx_txn_created", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[str] = mapped_column(String(40), unique=True, index=True, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)

    amount: Mapped[float] = mapped_column(Numeric(12, 2), nullable=False)
    receiver_vpa: Mapped[str] = mapped_column(String(100), nullable=False)
    merchant_name: Mapped[str | None] = mapped_column(String(120), nullable=True)
    merchant_category: Mapped[str] = mapped_column(String(60), nullable=False)
    transaction_type: Mapped[str] = mapped_column(String(20), nullable=False)

    device_id: Mapped[str] = mapped_column(String(100), nullable=False)
    device_type: Mapped[str] = mapped_column(String(20), nullable=False)
    location_city: Mapped[str] = mapped_column(String(60), nullable=False)

    fraud_probability: Mapped[float | None] = mapped_column(Float, nullable=True)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    risk_level: Mapped[RiskLevel | None] = mapped_column(Enum(RiskLevel), nullable=True)
    decision: Mapped[Decision] = mapped_column(Enum(Decision), nullable=False)
    reasons: Mapped[list | None] = mapped_column(JSON, nullable=True)
    model_version: Mapped[str | None] = mapped_column(String(40), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    user = relationship("User", back_populates="transactions")
    alert = relationship("FraudAlert", back_populates="transaction", uselist=False)
    model_logs = relationship("ModelLog", back_populates="transaction", cascade="all, delete-orphan")
