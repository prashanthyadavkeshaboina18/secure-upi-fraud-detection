from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.alert import AlertListOut
from app.services import alert_service
from app.utils.deps import get_current_user
from app.utils.pagination import Pagination, pagination_params

router = APIRouter(prefix="/api/alerts", tags=["alerts"])


@router.get("", response_model=AlertListOut)
def list_my_alerts(
    pagination: Pagination = Depends(pagination_params),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    items, total = alert_service.list_for_user(db, current_user, pagination.skip, pagination.limit)
    return AlertListOut(items=items, total=total)
