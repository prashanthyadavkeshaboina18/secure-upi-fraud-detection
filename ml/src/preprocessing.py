"""Cleaning: duplicates, missing values, invalid rows, dtype fixes.  raw → interim."""
from __future__ import annotations

import pandas as pd

from src import config as C

TEXT_COLS = ["txn_id", "sender_id", "receiver_id", "txn_type", "merchant_category", "device_id", "city"]


def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Return (clean_df, report). Never mutates the input."""
    df = df.copy()
    df.columns = [c.strip() for c in df.columns]
    report = {"rows_in": len(df)}

    for c in TEXT_COLS:
        if c in df:
            df[c] = df[c].map(lambda x: x.strip() if isinstance(x, str) else x)
            df[c] = df[c].replace("", pd.NA)

    # dtype fixes (bad values become NaN/NaT, handled below)
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df["amount"] = pd.to_numeric(df["amount"], errors="coerce")
    df["account_age_days"] = pd.to_numeric(df["account_age_days"], errors="coerce")
    df[C.TARGET] = pd.to_numeric(df[C.TARGET], errors="coerce")

    # duplicates
    n = len(df)
    df = df.drop_duplicates(subset="txn_id").drop_duplicates(subset=[c for c in df.columns if c != "txn_id"])
    report["duplicates_removed"] = n - len(df)

    # invalid rows
    n = len(df)
    required = ["txn_id", "sender_id", "receiver_id", "timestamp", "amount", C.TARGET]
    df = df.dropna(subset=required)
    df = df[(df["amount"] > 0) & (df["amount"] <= C.MAX_UPI_AMOUNT) & (df[C.TARGET].isin([0, 1]))]
    report["invalid_rows_removed"] = n - len(df)

    # missing values in optional columns
    report["missing_filled"] = int(df[["txn_type", "merchant_category", "device_id", "city", "account_age_days"]].isna().sum().sum())
    df["txn_type"] = df["txn_type"].fillna("unknown")
    df["merchant_category"] = df["merchant_category"].fillna("unknown")
    df["device_id"] = df["device_id"].fillna("UNKNOWN_DEVICE")
    df["city"] = df["city"].fillna("UNKNOWN")
    df["account_age_days"] = df["account_age_days"].fillna(df["account_age_days"].median()).clip(lower=0)
    df[C.TARGET] = df[C.TARGET].astype(int)
    if "fraud_type" in df:
        df["fraud_type"] = df["fraud_type"].fillna("none")

    df = df.sort_values(["timestamp", "txn_id"], kind="stable").reset_index(drop=True)
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    report["rows_out"] = len(df)
    return df, report


def main() -> None:
    raw = pd.read_csv(C.RAW_UPI)
    df, report = clean(raw)
    C.INTERIM_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.INTERIM_UPI, index=False)
    print(report)
    print(f"Wrote {C.INTERIM_UPI}")


if __name__ == "__main__":
    main()
