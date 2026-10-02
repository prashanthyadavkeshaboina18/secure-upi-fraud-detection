"""Pick the winner by the stated criteria — NOT by accuracy.

Criteria (see config.MIN_RECALL / MIN_PRECISION):
  1. Keep candidates that catch enough fraud (recall >= MIN_RECALL) without drowning
     analysts in false alarms (precision >= MIN_PRECISION) at their tuned threshold.
  2. Among those, highest PR-AUC (threshold-independent, right metric for rare fraud).
  3. Tie-break on F1.  If nobody qualifies, fall back to ranking all candidates.
"""
from __future__ import annotations

import argparse
import csv
import json

from src import config as C
from src.evaluate import evaluate_all, plot_all


def select_winner(results: dict, min_recall=C.MIN_RECALL, min_precision=C.MIN_PRECISION):
    eligible = {k: v for k, v in results.items()
                if v["recall"] >= min_recall and v["precision"] >= min_precision}
    pool = eligible or results
    ranked = sorted(pool, key=lambda k: (pool[k]["pr_auc"], pool[k]["f1"]), reverse=True)
    return ranked[0], bool(eligible)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="upi", choices=["upi", "creditcard"])
    args = ap.parse_args()

    results, probas, y, spec = evaluate_all(args.dataset)
    plot_all(results, probas, y, spec["reports_dir"])
    winner, met_criteria = select_winner(results)

    spec["reports_dir"].mkdir(parents=True, exist_ok=True)
    cols = ["model", "threshold", "precision", "recall", "f1", "roc_auc", "pr_auc", "accuracy"]
    with open(spec["reports_dir"] / "comparison_table.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        for name, m in results.items():
            w.writerow([name] + [round(m[c], 4) for c in cols[1:]])

    (spec["models_dir"] / "winner.json").write_text(json.dumps(
        {"winner": winner, "met_criteria": met_criteria,
         "criteria": {"min_recall": C.MIN_RECALL, "min_precision": C.MIN_PRECISION,
                      "rank_by": ["pr_auc", "f1"]}}, indent=2))
    print(open(spec["reports_dir"] / "comparison_table.csv").read())
    print(f"Winner: {winner}  (met recall/precision floors: {met_criteria})")


if __name__ == "__main__":
    main()
