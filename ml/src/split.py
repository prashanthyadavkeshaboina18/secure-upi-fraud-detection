"""Stratified 80/20 split + a time-ordered variant; also builds data/processed/*.csv."""
from __future__ import annotations

import pandas as pd
from sklearn.model_selection import train_test_split

from src import config as C
from src.feature_engineering import build_features


def stratified_split(df: pd.DataFrame, target: str = C.TARGET, test_size: float = C.TEST_SIZE,
                     seed: int = C.SEED):
    return train_test_split(df, test_size=test_size, stratify=df[target], random_state=seed)


def time_split(df: pd.DataFrame, time_col: str = "timestamp", test_size: float = C.TEST_SIZE):
    """Oldest (1-test_size) of rows → train, newest → test."""
    df = df.sort_values(time_col, kind="stable")
    cut = int(len(df) * (1 - test_size))
    return df.iloc[:cut], df.iloc[cut:]


def make_upi_processed() -> None:
    interim = pd.read_csv(C.INTERIM_UPI)
    feats = build_features(interim)          # history features use only the past → safe pre-split
    feats[C.TARGET] = interim[C.TARGET].to_numpy()
    feats["timestamp"] = interim["timestamp"].to_numpy()  # kept for time-ordered analysis; NOT a feature

    C.PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    train, test = stratified_split(feats)
    train.to_csv(C.PROCESSED_DIR / "upi_train.csv", index=False)
    test.to_csv(C.PROCESSED_DIR / "upi_test.csv", index=False)
    t_train, t_test = time_split(feats)
    t_train.to_csv(C.PROCESSED_DIR / "upi_train_time.csv", index=False)
    t_test.to_csv(C.PROCESSED_DIR / "upi_test_time.csv", index=False)
    print(f"UPI  train={len(train):,} (fraud {train[C.TARGET].mean():.3%})  "
          f"test={len(test):,} (fraud {test[C.TARGET].mean():.3%})")


def make_creditcard_processed() -> None:
    if not C.RAW_CREDITCARD.exists():
        print(f"(skip) {C.RAW_CREDITCARD} not found — download the ULB dataset to include it.")
        return
    df = pd.read_csv(C.RAW_CREDITCARD).drop_duplicates()
    train, test = stratified_split(df, target="Class")
    train.to_csv(C.PROCESSED_DIR / "creditcard_train.csv", index=False)
    test.to_csv(C.PROCESSED_DIR / "creditcard_test.csv", index=False)
    print(f"CC   train={len(train):,}  test={len(test):,}")


def main() -> None:
    make_upi_processed()
    make_creditcard_processed()


if __name__ == "__main__":
    main()
