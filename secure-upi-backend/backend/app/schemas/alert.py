from datetime import datetime

from pydantic import BaseModel


class AlertOut(BaseModel):
    id: int
    transaction_id: str | None = None
    user_id: int
    user_name: str | None = None
    alert_type: str
    message: str
    severity: str
    status: str
    created_at: datetime
    reviewed_at: datetime | None = None

    class Config:
        from_attributes = True


class AlertListOut(BaseModel):
    items: list[AlertOut]
    total: int
