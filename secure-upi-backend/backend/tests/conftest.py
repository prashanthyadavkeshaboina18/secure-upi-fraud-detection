import os

# Force a throwaway SQLite DB before any app module is imported, so tests
# never touch a real MySQL database.
os.environ["DATABASE_URL"] = "sqlite:///./test_secure_upi.db"
os.environ["JWT_SECRET_KEY"] = "test-secret"

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import get_settings
from app.database import Base, get_db
from app.main import app

get_settings.cache_clear()

engine = create_engine("sqlite:///./test_secure_upi.db", connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(autouse=True)
def _fresh_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def client():
    return TestClient(app)


@pytest.fixture
def register_and_login(client):
    """Returns a function that registers + logs in a user, returning (user_json, headers)."""

    def _do(email="user@example.com", password="Password@123", name="Test User", phone="9876543210"):
        client.post("/api/auth/register", json={
            "name": name, "email": email, "phone": phone, "password": password,
        })
        res = client.post("/api/auth/login", json={"email": email, "password": password})
        token = res.json()["access_token"]
        return res.json()["user"], {"Authorization": f"Bearer {token}"}

    return _do


@pytest.fixture
def make_admin(client):
    """Directly promotes a freshly registered user to ADMIN via the DB session."""

    def _do(email="admin@example.com", password="Password@123"):
        client.post("/api/auth/register", json={
            "name": "Admin", "email": email, "phone": "9123456780", "password": password,
        })
        db = TestingSessionLocal()
        from app.models.user import User, UserRole
        user = db.query(User).filter(User.email == email).first()
        user.role = UserRole.ADMIN
        db.commit()
        db.close()

        res = client.post("/api/auth/login", json={"email": email, "password": password})
        token = res.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _do
