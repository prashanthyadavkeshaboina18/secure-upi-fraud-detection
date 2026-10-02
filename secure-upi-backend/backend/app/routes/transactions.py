from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.transaction import TransactionIn, TransactionListOut, TransactionOut
from app.services import transaction_service
from app.utils.deps import get_current_user
from app.utils.pagination import Pagination, pagination_params

router = APIRouter(prefix="/api/transactions", tags=["transactions"])


@router.post("/predict", response_model=TransactionOut)
def predict(
    payload: TransactionIn,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    The core endpoint. Computes live features from this user's transaction
    history, scores them with the trained model, decides approve / review /
    block, and persists everything — including blocked transactions.
    """
    return transaction_service.analyse_transaction(db, current_user, payload)


@router.get("", response_model=TransactionListOut)
def list_my_transactions(
    risk_level: str | None = None,
    decision: str | None = None,
    date_from: str | None = None,
    search: str | None = None,
    pagination: Pagination = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    filters = {"risk_level": risk_level, "decision": decision, "date_from": date_from, "search": search}
    items, total = transaction_service.list_for_user(db, current_user, filters, pagination.skip, pagination.limit)
    return TransactionListOut(items=items, total=total)


@router.get("/{transaction_id}", response_model=TransactionOut)
def get_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return transaction_service.get_transaction(db, current_user, transaction_id)


@router.post("/{transaction_id}/confirm", response_model=TransactionOut)
def confirm_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """User confirms a REVIEW-decision payment really was them (step-up verification)."""
    return transaction_service.confirm_transaction(db, current_user, transaction_id)


@router.post("/{transaction_id}/cancel", response_model=TransactionOut)
def cancel_transaction(
    transaction_id: str,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return transaction_service.cancel_transaction(db, current_user, transaction_id)
