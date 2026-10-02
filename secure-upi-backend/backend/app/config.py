"""
Central application settings, loaded from environment variables / .env.
Nothing in this file should ever contain a real secret — see .env.example
for what belongs in the actual .env, which is gitignored.
"""
from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    APP_NAME: str = "Secure UPI API"
    ENV: str = "development"  # development | production

    # --- Database ---
    # Example MySQL:  mysql+pymysql://user:password@localhost:3306/secure_upi
    # Example SQLite (quick local dev / tests): sqlite:///./secure_upi.db
    DATABASE_URL: str = "sqlite:///./secure_upi.db"

    # --- Auth ---
    JWT_SECRET_KEY: str = "change-this-in-your-.env-file"
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 12  # 12 hours

    # --- CORS ---
    # Comma-separated list in .env, e.g. "http://localhost:5173,https://secure-upi.vercel.app"
    CORS_ORIGINS: str = "http://localhost:5173"

    # --- Risk thresholds (see docs/RISK_THRESHOLDS.md for how these were chosen) ---
    # A risk_score (0-100) <= RISK_LOW_MAX is LOW; up to RISK_MEDIUM_MAX is MEDIUM; above is HIGH.
    RISK_LOW_MAX: int = 30
    RISK_MEDIUM_MAX: int = 70

    # --- ML runtime ---
    ML_ARTIFACTS_DIR: str = "app/ml_runtime/artifacts"

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]


@lru_cache
def get_settings() -> Settings:
    # lru_cache means the .env file is only parsed once per process.
    return Settings()
