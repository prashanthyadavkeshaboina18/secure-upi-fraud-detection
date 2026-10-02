"""
Turns feature values into plain-language reasons, so a decision never reads
as just "fraud detected". Every reason returned here is derived from the
actual computed features for that specific transaction — nothing is a
static string unrelated to the data.

This is a deterministic rule layer, not a model explainability technique.
SHAP is listed as future work in the project plan and is not implemented
here; if it is added later, this function should not be described as SHAP.
"""
from app.models.transaction import RiskLevel


def build_reasons(features: dict, level: RiskLevel, max_reasons: int = 4) -> list[str]:
    if level == RiskLevel.LOW:
        return []

    candidates: list[tuple[float, str]] = []  # (priority, text) — higher priority shown first

    if features["amount_to_avg_ratio"] >= 3:
        candidates.append((
            features["amount_to_avg_ratio"],
            f"Amount is {features['amount_to_avg_ratio']:.1f}× your average transaction",
        ))

    if features["is_new_device"]:
        candidates.append((5, "Payment made from a device not seen on this account before"))

    if features["txn_count_last_5min"] >= 3:
        candidates.append((
            4 + features["txn_count_last_5min"],
            f"{features['txn_count_last_5min']} payments from this account in the last 5 minutes",
        ))

    if features["is_new_location"]:
        candidates.append((3, f"Payment made from a city not seen on this account before"))

    if features["is_night"]:
        candidates.append((1, "Payment made late at night, outside your usual hours"))

    if features["is_new_merchant_category"]:
        candidates.append((1, "First payment in this merchant category"))

    if features["device_changed"] and not features["is_new_device"]:
        candidates.append((2, "Device changed since your last payment"))

    if features["amount_zscore"] >= 2.5:
        candidates.append((
            features["amount_zscore"],
            "Amount is well outside your usual spending pattern",
        ))

    candidates.sort(key=lambda item: item[0], reverse=True)
    reasons = [text for _, text in candidates[:max_reasons]]

    # If no rule fired but the model still scored this MEDIUM/HIGH, say so
    # honestly rather than returning an empty list next to a "blocked" badge.
    if not reasons:
        reasons = ["The model scored this payment as unusual based on a combination of signals"]

    return reasons
