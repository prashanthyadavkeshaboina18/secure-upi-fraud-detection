from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.admin import AdminUserListOut
from app.schemas.alert import AlertListOut, AlertOut
from app.schemas.dashboard import FraudStatsOut
from app.schemas.transaction import AlertStatusUpdate, TransactionListOut
from app.services import admin_service, alert_service, dashboard_service, transaction_service
from app.utils.deps import require_role
from app.utils.pagination import Pagination, pagination_params

router = APIRouter(prefix="/api/admin", tags=["admin"])
require_admin = require_role("ADMIN")


@router.get("/transactions", response_model=TransactionListOut)
def all_transactions(
    risk_level: str | None = None,
    decision: str | None = None,
    date_from: str | None = None,
    search: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    filters = {"risk_level": risk_level, "decision": decision, "date_from": date_from, "search": search}
    items, total = transaction_service.list_all(db, filters, pagination.skip, pagination.limit)
    return TransactionListOut(items=items, total=total)


@router.get("/fraud-statistics", response_model=FraudStatsOut)
def fraud_statistics(db: Session = Depends(get_db), _admin=Depends(require_admin)):
    return dashboard_service.get_fraud_statistics(db)


@router.get("/alerts", response_model=AlertListOut)
def all_alerts(
    status: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    items, total = alert_service.list_all(db, status, pagination.skip, pagination.limit)
    return AlertListOut(items=items, total=total)


@router.patch("/alerts/{alert_id}", response_model=AlertOut)
def update_alert(
    alert_id: int,
    payload: AlertStatusUpdate,
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    return alert_service.update_status(db, alert_id, payload.status)


@router.get("/users", response_model=AdminUserListOut)
def list_users(
    search: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: Session = Depends(get_db),
    _admin=Depends(require_admin),
):
    items, total = admin_service.list_users(db, search, pagination.skip, pagination.limit)
    return AdminUserListOut(items=items, total=total)
