from datetime import datetime

from pydantic import BaseModel, EmailStr


class AdminUserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: str
    role: str
    transaction_count: int
    blocked_count: int
    account_created_at: datetime

    class Config:
        from_attributes = True


class AdminUserListOut(BaseModel):
    items: list[AdminUserOut]
    total: int
