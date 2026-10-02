from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ModelLog(Base):
    """
    One row per prediction. This is what makes 'the prediction came from the
    actual model, not a hardcoded value' a checkable claim rather than an
    assertion — every inference is logged with the model that produced it.
    """
    __tablename__ = "model_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    transaction_id: Mapped[int] = mapped_column(ForeignKey("transactions.id"), nullable=False)

    model_name: Mapped[str] = mapped_column(String(60), nullable=False)
    model_version: Mapped[str] = mapped_column(String(40), nullable=False)
    prediction: Mapped[int] = mapped_column(Integer, nullable=False)  # 0 = genuine, 1 = fraud
    probability: Mapped[float] = mapped_column(Float, nullable=False)
    latency_ms: Mapped[int] = mapped_column(Integer, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    transaction = relationship("Transaction", back_populates="model_logs")
