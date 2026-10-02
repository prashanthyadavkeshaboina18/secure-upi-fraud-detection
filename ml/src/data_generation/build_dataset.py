"""Orchestrate users → genuine transactions → fraud injection → data/raw/upi_synthetic.csv"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src import config as C
from src.data_generation.generate_transactions import generate_transactions
from src.data_generation.generate_users import generate_users
from src.data_generation.inject_fraud import inject_fraud


def build(n_users=C.N_USERS, n_days=C.N_DAYS, fraud_rate=C.TARGET_FRAUD_RATE,
          seed=C.SEED, start=C.START_DATE) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    users = generate_users(n_users, rng)
    genuine = generate_transactions(users, rng, n_days, start)
    df = inject_fraud(genuine, users, rng, fraud_rate, start, n_days)

    # Sort by time, THEN assign ids, so txn_id order carries no label information.
    df = df.sort_values("timestamp", kind="stable").reset_index(drop=True)
    df.insert(0, "txn_id", [f"T{i:08d}" for i in range(len(df))])
    df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")
    return df[C.RAW_COLUMNS]


def main() -> None:
    df = build()
    C.RAW_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(C.RAW_UPI, index=False)
    print(f"Wrote {len(df):,} rows → {C.RAW_UPI}")
    print(f"Fraud rate: {df[C.TARGET].mean():.4%} (target {C.TARGET_FRAUD_RATE:.2%})")
    print(df.loc[df[C.TARGET] == 1, "fraud_type"].value_counts().to_string())


if __name__ == "__main__":
    main()
