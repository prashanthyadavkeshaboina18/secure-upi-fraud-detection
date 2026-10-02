"""CLI: score a single transaction for manual sanity checks.

python -m src.predict --txn '{"timestamp":"2025-02-01 02:14:00","sender_id":"U00001",
  "receiver_id":"P123456","amount":48000,"txn_type":"P2P","merchant_category":"person",
  "device_id":"D_new","city":"Delhi","account_age_days":400}' --history data/interim/upi_synthetic_clean.csv
"""
from __future__ import annotations

import argparse
import json

import joblib
import pandas as pd

from src import config as C
from src.feature_engineering import compute_single


def score(txn: dict, history: pd.DataFrame | None = None, model_dir=C.MODELS_DIR) -> dict:
    meta = json.loads((model_dir / "feature_list.json").read_text())
    pipe = joblib.load(model_dir / "pipeline.joblib")
    feats = compute_single(txn, history)[meta["features"]]
    p = float(pipe.predict_proba(feats)[0, 1])
    return {"fraud_probability": p, "is_fraud": p >= meta["decision_threshold"],
            "threshold": meta["decision_threshold"], "features": feats.iloc[0].to_dict()}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--txn", required=True, help="JSON string or path to a .json file")
    ap.add_argument("--history", help="CSV of past transactions (same columns as interim data)")
    args = ap.parse_args()
    txn = json.loads(open(args.txn).read() if args.txn.endswith(".json") else args.txn)
    history = pd.read_csv(args.history) if args.history else None
    print(json.dumps(score(txn, history), indent=2, default=str))


if __name__ == "__main__":
    main()
