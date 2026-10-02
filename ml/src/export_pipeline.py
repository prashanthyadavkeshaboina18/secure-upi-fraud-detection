"""Bundle the winner into models/: pipeline.joblib, feature_list.json, metrics.json, model_card.md."""
from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone

import pandas as pd
import sklearn

from src import config as C
from src.evaluate import evaluate_all


def main() -> None:
    results, _, y, spec = evaluate_all("upi")
    info = json.loads((C.CANDIDATES_DIR / "winner.json").read_text())
    winner = info["winner"]
    m = results[winner]

    C.MODELS_DIR.mkdir(exist_ok=True)
    shutil.copy(C.CANDIDATES_DIR / f"{winner}.joblib", C.MODELS_DIR / "pipeline.joblib")

    (C.MODELS_DIR / "feature_list.json").write_text(json.dumps({
        "features": C.FEATURE_COLUMNS,                 # exact column order the pipeline expects
        "numeric": C.NUMERIC_FEATURES,
        "categorical": C.CATEGORICAL_FEATURES,
        "input_columns": C.INPUT_COLUMNS,
        "decision_threshold": m["threshold"],
        "model_name": winner,
    }, indent=2))

    train = pd.read_csv(C.PROCESSED_DIR / "upi_train.csv", usecols=[C.TARGET])
    metrics = {
        "model": winner,
        "trained_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "sklearn_version": sklearn.__version__,
        "decision_threshold": m["threshold"],
        "test_set": {"rows": int(len(y)), "fraud_rate": float(y.mean())},
        "train_set": {"rows": int(len(train)), "fraud_rate": float(train[C.TARGET].mean())},
        "metrics": {k: m[k] for k in ["precision", "recall", "f1", "roc_auc", "pr_auc"]},
        "confusion_matrix": m["confusion_matrix"],
        "selection": info,
        "candidates": {n: {k: r[k] for k in ["precision", "recall", "f1", "roc_auc", "pr_auc"]}
                       for n, r in results.items()},
    }
    (C.MODELS_DIR / "metrics.json").write_text(json.dumps(metrics, indent=2))

    cm = m["confusion_matrix"]
    card = f"""# Model card — UPI fraud detector

**Model:** {winner}  ·  **Trained:** {metrics['trained_at']}  ·  **Threshold:** {m['threshold']:.3f}

## Data
Synthetic UPI-like transactions ({C.N_USERS:,} simulated users, {C.N_DAYS} days, target fraud rate
{C.TARGET_FRAUD_RATE:.1%}). Four fraud archetypes are injected — account takeover, social
engineering / collect scams, mule bursts, high-value drains — with deliberate overlap
with genuine behaviour. Real UPI fraud data is not public; the public ULB credit-card set is
used only as an optional benchmark.

## Test performance (held-out {len(y):,} rows, fraud rate {y.mean():.2%})
| Precision | Recall | F1 | ROC-AUC | PR-AUC |
|---|---|---|---|---|
| {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['roc_auc']:.3f} | {m['pr_auc']:.3f} |

Confusion matrix: TN={cm['tn']:,}  FP={cm['fp']:,}  FN={cm['fn']:,}  TP={cm['tp']:,}.
The winner was chosen by recall/precision floors then PR-AUC — never accuracy.

## How it scores
Input = the 9 transaction fields in `feature_list.json`. Features (`src/feature_engineering.py`)
combine the transaction with the sender's *past* transactions (new payee/device/city, amount vs
personal norm, 1h/24h velocity). The backend must reproduce them exactly.

## Limitations
* Results reflect the simulator's assumptions, not real-world fraud; expect lower performance on real data.
* Cold start: a sender's first transactions have no history, so history features are neutral.
* Not evaluated for fairness across user groups; city/txn-type are the only categorical inputs.
* Threshold was tuned for F1 on validation data; business costs of FP vs FN may justify another.
* Fraud patterns drift — retrain and monitor PR-AUC over time.
"""
    (C.MODELS_DIR / "model_card.md").write_text(card)
    print(f"Exported {winner} → {C.MODELS_DIR}")


if __name__ == "__main__":
    main()
