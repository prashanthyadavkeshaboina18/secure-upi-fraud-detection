"""
Loads the ML pipeline exactly once, at API startup — never per request.

The API deliberately knows nothing about how the model was trained. It only
ever reads three small files that the training pipeline (ml/) produces:

  pipeline.joblib     preprocessing + model, bundled as one sklearn object
  feature_list.json   the exact ordered column names the pipeline expects
  metrics.json        evaluation results from the training run

If these files are not present (e.g. before Phase 5-7 have been run), the API
still starts, but /api/transactions/predict returns 503 rather than a guess.
That is a deliberate design choice: a hardcoded or random prediction would
violate the project's core rule of never fabricating a fraud decision.
"""

import json
import logging
from pathlib import Path

import joblib

from app.config import get_settings

logger = logging.getLogger(__name__)

_pipeline = None
_feature_list: list[str] | None = None
_metrics: dict | None = None


def _artifacts_dir() -> Path:
    return Path(get_settings().ML_ARTIFACTS_DIR)


def load() -> None:
    global _pipeline, _feature_list, _metrics

    directory = _artifacts_dir()
    pipeline_path = directory / "pipeline.joblib"
    features_path = directory / "feature_list.json"
    metrics_path = directory / "metrics.json"

    if pipeline_path.exists() and features_path.exists():
        _pipeline = joblib.load(pipeline_path)

        # feature_list.json contains a JSON object with several sections.
        # The ML pipeline expects only the ordered list inside "features".
        feature_data = json.loads(features_path.read_text())
        _feature_list = feature_data["features"]

        logger.info(
            "ML pipeline loaded from %s (%d features)",
            pipeline_path,
            len(_feature_list),
        )
    else:
        _pipeline = None
        _feature_list = None

        logger.warning(
            "No ML pipeline found at %s. /api/transactions/predict will return 503 "
            "until the training pipeline is run and artifacts are copied here "
            "(see scripts/copy_ml_artifacts.py).",
            directory,
        )

    if metrics_path.exists():
        _metrics = json.loads(metrics_path.read_text())
    else:
        _metrics = None


def is_ready() -> bool:
    return _pipeline is not None and _feature_list is not None


def get_pipeline():
    return _pipeline


def get_feature_list() -> list[str] | None:
    return _feature_list


def get_metrics() -> dict | None:
    return _metrics


def model_version() -> str | None:
    if _metrics and "selected_model" in _metrics:
        return _metrics["selected_model"].get("model_version")

    return None