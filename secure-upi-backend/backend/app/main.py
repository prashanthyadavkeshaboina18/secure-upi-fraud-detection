import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.core.logging_config import configure_logging
from app.database import Base, engine
from app.ml_runtime import loader
from app.routes import admin, alerts, auth, dashboard, model, transactions

settings = get_settings()
configure_logging(settings.ENV)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Convenience for local/demo use so the app never 500s on a missing
    # table. Real environments should manage schema with Alembic (see
    # alembic/) instead of relying on this.
    Base.metadata.create_all(bind=engine)

    loader.load()
    logger.info("%s starting | model loaded: %s", settings.APP_NAME, loader.is_ready())
    yield


app = FastAPI(
    title=settings.APP_NAME,
    description=(
        "Academic prototype for ML-driven UPI fraud detection. "
        "No bank, PSP or UPI network is connected — no real money moves."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(transactions.router)
app.include_router(alerts.router)
app.include_router(dashboard.router)
app.include_router(admin.router)
app.include_router(model.router)


@app.get("/health", tags=["health"])
def health():
    return {"status": "ok", "model_loaded": loader.is_ready()}
