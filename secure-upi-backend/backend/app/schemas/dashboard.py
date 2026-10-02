from pydantic import BaseModel


class UserStatsOut(BaseModel):
    total_transactions: int
    approved_transactions: int
    review_transactions: int
    blocked_transactions: int
    open_alerts: int
    current_risk_level: str | None = None
    current_risk_score: int | None = None


class TimeSeriesPoint(BaseModel):
    date: str
    total: int
    fraud: int


class CategoryCount(BaseModel):
    fraud_count: int


class FraudStatsOut(BaseModel):
    total_transactions: int
    fraud_transactions: int
    fraud_rate: float
    blocked_transactions: int
    high_risk_transactions: int
    transactions_over_time: list[dict]
    fraud_by_transaction_type: list[dict]
    fraud_by_location: list[dict]
    fraud_by_device: list[dict]
    risk_distribution: list[dict]
