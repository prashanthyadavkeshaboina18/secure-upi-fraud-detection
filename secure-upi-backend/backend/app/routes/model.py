from fastapi import APIRouter, Depends

from app.ml_runtime import loader
from app.utils.deps import require_role

router = APIRouter(prefix="/api/model", tags=["model"])


@router.get("/performance")
def model_performance(_admin=Depends(require_role("ADMIN"))):
    """
    Returns exactly what the training pipeline wrote to metrics.json.
    If no model has been trained yet, selected_model is omitted and the
    frontend shows an explicit empty state instead of inventing numbers.
    """
    metrics = loader.get_metrics()
    if metrics is None:
        return {"selected_model": None, "comparison": [], "trained_at": None}
    return metrics
