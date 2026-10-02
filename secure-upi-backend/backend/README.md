# Secure UPI — Backend

FastAPI service for **Secure UPI: Machine Learning–Driven Fraud Detection for
UPI Transactions**. Handles auth, the real-time fraud-prediction endpoint,
persistence, alerting, and the aggregations behind both dashboards.

> Academic prototype. No bank, PSP or UPI network is connected and no money
> moves. See `/health` and `/docs` once running.

## Stack

FastAPI · SQLAlchemy 2 · Alembic · MySQL (PostgreSQL/SQLite also work) ·
python-jose (JWT) · passlib/bcrypt · pytest

## Getting started

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

API is now at `http://localhost:8000`, interactive docs at `/docs`.

On startup the app calls `Base.metadata.create_all()` as a local-dev
convenience, so **SQLite works with zero extra setup** — just leave
`DATABASE_URL=sqlite:///./secure_upi.db` in `.env`. For MySQL, create a
database and point `DATABASE_URL` at it, then prefer Alembic for schema
management (see below) over relying on `create_all`.

### Seed a demo login

```bash
python -m scripts.seed_data
```
Creates `admin@secureupi.local` / `Admin@12345` and `demo@secureupi.local` / `Demo@12345`.

### Connect the trained model

Until the ML pipeline (`ml/`) has been trained, `/api/transactions/predict`
correctly returns **503** — this is by design, not a bug (see
`app/ml_runtime/loader.py`). Once `ml/src/train.py` has produced
`pipeline.joblib`, `feature_list.json` and `metrics.json`:

```bash
python -m scripts.copy_ml_artifacts ../ml/models
# then restart the API
```

## Running tests

```bash
pytest -v
```
Tests run against a throwaway SQLite database (see `tests/conftest.py`) and
never touch your real `DATABASE_URL`. 14 tests cover registration/login,
role-based access control, transaction validation, the 503-without-a-model
behaviour, and that `feature_service` returns safe defaults for a brand-new
user with no transaction history.

## Database migrations (Alembic)

```bash
alembic upgrade head                 # apply migrations
alembic revision --autogenerate -m "describe the change"   # after editing app/models/
```
`alembic/env.py` reads `DATABASE_URL` from the same `.env` as the app, so
migrations always target the database you're actually running against.

## Project layout

```
app/
  main.py            FastAPI app, CORS, startup (loads the ML pipeline once)
  config.py          Settings from .env
  database.py        Engine, session, Base
  models/            SQLAlchemy tables: User, Transaction, FraudAlert, ModelLog
  schemas/           Pydantic request/response shapes
  routes/            Thin HTTP layer — parse request, call one service, return
  services/          All business logic (see below)
  ml_runtime/        Loads pipeline.joblib once at startup; never re-trains
  utils/             security, auth deps, ids, pagination, error helpers
scripts/             seed_data.py, copy_ml_artifacts.py
tests/               pytest suite, SQLite-backed
alembic/             migrations
```

### Why `services/feature_service.py` matters most

It computes the model's input features — transaction velocity, behavioural
deviation, device/location novelty, account age — from **live database
queries** at prediction time. `ml/src/feature_engineering.py` (the training
side, built in a later phase) must define every one of these features
identically. If the two ever diverge, the model's live predictions silently
stop matching its reported offline metrics — a failure mode called
training/serving skew. `tests/test_feature_service.py` exists to catch
exactly this class of bug early.

### Request flow for a payment

```
POST /api/transactions/predict
  -> feature_service.compute_features()      live DB query -> raw feature dict
  -> prediction_service.predict_fraud_probability()   loaded pipeline.joblib
  -> risk_service.evaluate()                 probability -> score/level/decision
  -> reason_service.build_reasons()          feature values -> plain-language reasons
  -> persist Transaction + ModelLog rows
  -> if BLOCKED: alert_service.create_alert()
```

No step here ever hardcodes or randomises a result. If the pipeline isn't
loaded, the request fails with 503 rather than guessing.

## API summary

| Method | Path | Auth | Notes |
|---|---|---|---|
| POST | `/api/auth/register` | — | |
| POST | `/api/auth/login` | — | Returns a JWT |
| GET | `/api/auth/me` | user | |
| POST | `/api/transactions/predict` | user | Core endpoint |
| GET | `/api/transactions` | user | Own history, filterable, paginated |
| GET | `/api/transactions/{id}` | user | 404 if not yours |
| POST | `/api/transactions/{id}/confirm` | user | REVIEW → APPROVED |
| POST | `/api/transactions/{id}/cancel` | user | REVIEW → CANCELLED |
| GET | `/api/alerts` | user | Own alerts |
| GET | `/api/dashboard/stats` | user | |
| GET | `/api/admin/transactions` | admin | |
| GET | `/api/admin/fraud-statistics` | admin | Powers the charts |
| GET | `/api/admin/alerts` | admin | |
| PATCH | `/api/admin/alerts/{id}` | admin | Update status |
| GET | `/api/admin/users` | admin | |
| GET | `/api/model/performance` | admin | Reads `metrics.json` verbatim |
| GET | `/health` | — | `{"status":"ok","model_loaded": bool}` |

Full request/response schemas are in Swagger at `/docs` — generated
automatically from the Pydantic models in `app/schemas/`, not hand-written.

## Security notes

Passwords are bcrypt-hashed (`passlib`), never logged or returned by any
endpoint. Every protected route depends on `get_current_user`; admin routes
additionally depend on `require_role("ADMIN")`, which is the actual
enforcement — the frontend hiding admin links is a UX nicety, not security.
All database access goes through the SQLAlchemy ORM (parameterised
queries), so standard SQL injection via user input is not possible through
this layer. This is a prototype, not a production banking security system —
see the project's Phase 1 document for the full list of stated limitations.

## Deployment (Render)

1. New Web Service, root directory `backend`.
2. Build: `pip install -r requirements.txt`. Start: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`.
3. Environment variables: `DATABASE_URL` (your managed MySQL/PostgreSQL),
   `JWT_SECRET_KEY` (a real random value), `CORS_ORIGINS` (your deployed
   frontend's exact origin).
4. Run `alembic upgrade head` once against the production database before
   first boot, or let `create_all` handle it for a demo deployment.
5. Copy the trained model artifacts into `app/ml_runtime/artifacts/` as part
   of the build, or commit them if the repo is private and they're small.
