"""Class-imbalance handling: class weights (default) and SMOTE (train fold only)."""
from __future__ import annotations

import numpy as np


def class_weights(y) -> dict[int, float]:
    """'Balanced' weights: n / (2 * count_c)."""
    y = np.asarray(y)
    n = len(y)
    return {int(c): n / (2.0 * (y == c).sum()) for c in (0, 1)}


def scale_pos_weight(y) -> float:
    """negatives / positives — the value XGBoost expects."""
    y = np.asarray(y)
    return float((y == 0).sum() / max((y == 1).sum(), 1))


def smote_step(seed: int, sampling_strategy: float = 0.2):
    """A SMOTE sampler for use INSIDE an imblearn Pipeline.

    Inside a Pipeline, resampling is applied to whatever data `fit` receives and is
    skipped at predict time, so it can never touch validation/test data.
    Never call fit_resample on the full dataset before splitting.
    Note: applied after one-hot encoding, so synthetic rows have fractional category
    values — treat SMOTE as an experiment; class weights are the default.
    """
    try:
        from imblearn.over_sampling import SMOTE
    except ImportError as exc:  # pragma: no cover
        raise ImportError("SMOTE needs `pip install imbalanced-learn`") from exc
    return SMOTE(sampling_strategy=sampling_strategy, random_state=seed)
