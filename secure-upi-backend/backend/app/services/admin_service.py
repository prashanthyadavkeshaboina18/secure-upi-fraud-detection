from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transaction import Decision, Transaction
from app.models.user import User


def list_users(db: Session, search: str | None, skip: int, limit: int) -> tuple[list[dict], int]:
    query = db.query(User)
    if search:
        term = f"%{search}%"
        query = query.filter((User.name.ilike(term)) | (User.email.ilike(term)))

    total = query.count()
    users = query.order_by(User.created_at.desc()).offset(skip).limit(limit).all()

    items = []
    for user in users:
        txn_count = db.query(func.count(Transaction.id)).filter(Transaction.user_id == user.id).scalar() or 0
        blocked_count = (
            db.query(func.count(Transaction.id))
            .filter(Transaction.user_id == user.id, Transaction.decision == Decision.BLOCKED)
            .scalar()
            or 0
        )
        items.append({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "phone": user.phone,
            "role": user.role.value,
            "transaction_count": txn_count,
            "blocked_count": blocked_count,
            "account_created_at": user.created_at,
        })

    return items, total
