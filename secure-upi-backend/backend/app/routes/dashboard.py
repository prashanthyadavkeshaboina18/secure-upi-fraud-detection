from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.dashboard import UserStatsOut
from app.services import dashboard_service
from app.utils.deps import get_current_user

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/stats", response_model=UserStatsOut)
def user_stats(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    return dashboard_service.get_user_stats(db, current_user)
