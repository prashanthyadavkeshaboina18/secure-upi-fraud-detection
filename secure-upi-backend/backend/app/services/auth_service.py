from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.auth import LoginIn, RegisterIn
from app.utils.exceptions import duplicate_email, invalid_credentials
from app.utils.security import create_access_token, hash_password, verify_password


def register_user(db: Session, payload: RegisterIn) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise duplicate_email()

    user = User(
        name=payload.name,
        email=payload.email,
        phone=payload.phone,
        password_hash=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, payload: LoginIn) -> tuple[User, str]:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.password_hash):
        raise invalid_credentials()

    token = create_access_token(subject=str(user.id), role=user.role.value)
    return user, token
