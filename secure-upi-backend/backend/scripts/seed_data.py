"""
Creates the tables (quick local/dev convenience — production should use
Alembic instead) and inserts a demo admin and a demo user so the frontend
has something to log into immediately.

Run from the backend/ directory:
    python -m scripts.seed_data
"""
from app.database import Base, SessionLocal, engine
from app.models.user import User, UserRole
from app.utils.security import hash_password


def run():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        if not db.query(User).filter(User.email == "admin@secureupi.local").first():
            db.add(User(
                name="Admin",
                email="admin@secureupi.local",
                phone="9000000000",
                password_hash=hash_password("Admin@12345"),
                role=UserRole.ADMIN,
            ))
            print("Created admin@secureupi.local / Admin@12345")

        if not db.query(User).filter(User.email == "demo@secureupi.local").first():
            db.add(User(
                name="Demo User",
                email="demo@secureupi.local",
                phone="9000000001",
                password_hash=hash_password("Demo@12345"),
                role=UserRole.USER,
            ))
            print("Created demo@secureupi.local / Demo@12345")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    run()
