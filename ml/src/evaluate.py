"""precision / recall / F1 / ROC-AUC / PR-AUC + confusion matrix, on the held-out test set.

Usage:  python -m src.evaluate [--dataset upi|creditcard]
Accuracy is reported for completeness only — with ~2% fraud it is meaningless.
"""
from __future__ import annotations

import argparse
import json

import joblib
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from sklearn.metrics import (  # noqa: E402
    accuracy_score, average_precision_score, confusion_matrix, f1_score,
    precision_recall_curve, precision_score, recall_score, roc_auc_score, roc_curve,
)

from src.train import dataset_spec, load_xy  # noqa: E402


def compute_metrics(y_true, proba, threshold: float) -> dict:
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_true, pred, labels=[0, 1]).ravel()
    return {
        "threshold": float(threshold),
        "precision": float(precision_score(y_true, pred, zero_division=0)),
        "recall": float(recall_score(y_true, pred, zero_division=0)),
        "f1": float(f1_score(y_true, pred, zero_division=0)),
        "roc_auc": float(roc_auc_score(y_true, proba)),
        "pr_auc": float(average_precision_score(y_true, proba)),
        "accuracy": float(accuracy_score(y_true, pred)),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
    }


def evaluate_all(dataset: str = "upi"):
    spec = dataset_spec(dataset)
    X, y = load_xy(spec["test"], spec)
    thresholds = json.loads((spec["models_dir"] / "thresholds.json").read_text())
    results, probas = {}, {}
    for path in sorted(spec["models_dir"].glob("*.joblib")):
        name = path.stem
        proba = joblib.load(path).predict_proba(X)[:, 1]
        probas[name] = proba
        results[name] = compute_metrics(y, proba, thresholds[name])
    return results, probas, y, spec


def plot_all(results, probas, y, out_dir) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(6, 5))
    for n, p in probas.items():
        fpr, tpr, _ = roc_curve(y, p)
        ax.plot(fpr, tpr, label=f"{n} (AUC {results[n]['roc_auc']:.3f})")
    ax.plot([0, 1], [0, 1], "k--", lw=0.8)
    ax.set(xlabel="False positive rate", ylabel="True positive rate", title="ROC curves")
    ax.legend(); fig.tight_layout(); fig.savefig(out_dir / "roc_curves.png", dpi=130); plt.close(fig)

    fig, ax = plt.subplots(figsize=(6, 5))
    for n, p in probas.items():
        pr, rc, _ = precision_recall_curve(y, p)
        ax.plot(rc, pr, label=f"{n} (AP {results[n]['pr_auc']:.3f})")
    ax.axhline(y.mean(), color="k", ls="--", lw=0.8, label="no-skill")
    ax.set(xlabel="Recall", ylabel="Precision", title="Precision–recall curves")
    ax.legend(); fig.tight_layout(); fig.savefig(out_dir / "pr_curves.png", dpi=130); plt.close(fig)

    fig, axes = plt.subplots(1, len(results), figsize=(4.2 * len(results), 3.8), squeeze=False)
    for ax, (n, m) in zip(axes[0], results.items()):
        cm = m["confusion_matrix"]
        mat = np.array([[cm["tn"], cm["fp"]], [cm["fn"], cm["tp"]]])
        ax.imshow(mat, cmap="Blues")
        for (i, j), v in np.ndenumerate(mat):
            ax.text(j, i, f"{v:,}", ha="center", va="center")
        ax.set(title=n, xticks=[0, 1], yticks=[0, 1], xticklabels=["pred 0", "pred 1"],
               yticklabels=["true 0", "true 1"])
    fig.tight_layout(); fig.savefig(out_dir / "confusion_matrices.png", dpi=130); plt.close(fig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dataset", default="upi", choices=["upi", "creditcard"])
    args = ap.parse_args()
    results, probas, y, spec = evaluate_all(args.dataset)
    plot_all(results, probas, y, spec["reports_dir"])
    for n, m in results.items():
        print(f"{n:22s} P={m['precision']:.3f} R={m['recall']:.3f} F1={m['f1']:.3f} "
              f"ROC={m['roc_auc']:.3f} PR={m['pr_auc']:.3f}")


if __name__ == "__main__":
    main()
