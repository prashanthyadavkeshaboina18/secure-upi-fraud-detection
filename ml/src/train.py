"""Train LR / RF / XGBoost, save every candidate (full preprocessor+model pipeline).

Usage:  python -m src.train [--dataset upi|creditcard] [--smote]

Imbalance: class weights by default (`--smote` adds SMOTE inside the pipeline → train only).
Threshold: each model is fit on 80% of train; the decision threshold that maximises F1 is
chosen on the remaining 20% (validation). The test set is never used for tuning.
"""
from __future__ import annotations

import argparse
import json
import warnings

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_curve
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from src import config as C
from src.imbalance import scale_pos_weight, smote_step


# --------------------------------------------------------------------------- datasets
def dataset_spec(name: str) -> dict:
    if name == "upi":
        return dict(name=name, train=C.PROCESSED_DIR / "upi_train.csv",
                    test=C.PROCESSED_DIR / "upi_test.csv", target=C.TARGET,
                    numeric=C.NUMERIC_FEATURES, categorical=C.CATEGORICAL_FEATURES,
                    models_dir=C.CANDIDATES_DIR, reports_dir=C.EVAL_DIR)
    if name == "creditcard":
        path = C.PROCESSED_DIR / "creditcard_train.csv"
        cols = [c for c in pd.read_csv(path, nrows=1).columns if c != "Class"]
        return dict(name=name, train=path, test=C.PROCESSED_DIR / "creditcard_test.csv",
                    target="Class", numeric=cols, categorical=[],
                    models_dir=C.CANDIDATES_DIR / "creditcard",
                    reports_dir=C.EVAL_DIR / "creditcard")
    raise ValueError(name)


def load_xy(path, spec):
    df = pd.read_csv(path)
    return df[spec["numeric"] + spec["categorical"]], df[spec["target"]].to_numpy()


# --------------------------------------------------------------------------- models
def build_preprocessor(numeric, categorical) -> ColumnTransformer:
    parts = [("num", StandardScaler(), numeric)]
    if categorical:
        parts.append(("cat", OneHotEncoder(handle_unknown="ignore", sparse_output=False), categorical))
    return ColumnTransformer(parts)


def candidate_models(y_train) -> dict:
    models = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced", random_state=C.SEED),
        "random_forest": RandomForestClassifier(
            n_estimators=300, min_samples_leaf=3, class_weight="balanced_subsample",
            n_jobs=-1, random_state=C.SEED),
    }
    try:
        from xgboost import XGBClassifier
        models["xgboost"] = XGBClassifier(
            n_estimators=400, max_depth=5, learning_rate=0.05, subsample=0.8,
            colsample_bytree=0.8, scale_pos_weight=scale_pos_weight(y_train),
            eval_metric="aucpr", n_jobs=-1, random_state=C.SEED)
    except ImportError:
        warnings.warn("xgboost not installed — skipping the XGBoost candidate.")
    return models


def make_pipeline(model, spec, use_smote: bool):
    pre = build_preprocessor(spec["numeric"], spec["categorical"])
    if use_smote:
        from imblearn.pipeline import Pipeline as ImbPipeline
        return ImbPipeline([("pre", pre), ("smote", smote_step(C.SEED)), ("model", model)])
    return Pipeline([("pre", pre), ("model", model)])


def best_f1_threshold(y_true, proba) -> float:
    p, r, thr = precision_recall_curve(y_true, proba)
    f1 = 2 * p[:-1] * r[:-1] / np.clip(p[:-1] + r[:-1], 1e-12, None)
    return float(thr[int(np.argmax(f1))])


# --------------------------------------------------------------------------- main
def train_all(dataset: str = "upi", use_smote: bool = False) -> dict:
    spec = dataset_spec(dataset)
    X, y = load_xy(spec["train"], spec)
    X_fit, X_val, y_fit, y_val = train_test_split(
        X, y, test_size=C.VALIDATION_SIZE, stratify=y, random_state=C.SEED)

    spec["models_dir"].mkdir(parents=True, exist_ok=True)
    thresholds = {}
    for name, model in candidate_models(y_fit).items():
        print(f"Training {name} …")
        pipe = make_pipeline(model, spec, use_smote)
        pipe.fit(X_fit, y_fit)
        thresholds[name] = best_f1_threshold(y_val, pipe.predict_proba(X_val)[:, 1])
        joblib.dump(pipe, spec["models_dir"] / f"{name}.joblib")
        print(f"  saved; validation-tuned threshold = {thresholds[name]:.3f}")
    (spec["models_dir"] / "thresholds.json").write_text(json.dumps(thresholds, indent=2))
    return thresholds


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="upi", choices=["upi", "creditcard"])
    ap.add_argument("--smote", action="store_true")
    args = ap.parse_args()
    train_all(args.dataset, args.smote)


if __name__ == "__main__":
    main()
