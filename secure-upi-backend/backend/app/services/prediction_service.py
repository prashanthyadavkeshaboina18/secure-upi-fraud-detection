"""
Runs the loaded pipeline on a feature row. This module never invents a
probability: if the pipeline is not loaded, it raises rather than guessing
(see app/utils/exceptions.py: model_unavailable).
"""
import time

import pandas as pd

from app.ml_runtime import loader
from app.utils.exceptions import model_unavailable


def predict_fraud_probability(features: dict) -> tuple[float, int]:
    """
    Returns (fraud_probability, latency_ms).
    Raises HTTPException(503) if no trained pipeline is loaded.
    """
    if not loader.is_ready():
        raise model_unavailable()

    pipeline = loader.get_pipeline()
    feature_order = loader.get_feature_list()

    row = {name: features.get(name) for name in feature_order}
    frame = pd.DataFrame([row], columns=feature_order)

    start = time.perf_counter()
    probability = float(pipeline.predict_proba(frame)[0, 1])
    latency_ms = int((time.perf_counter() - start) * 1000)

    return probability, latency_ms
