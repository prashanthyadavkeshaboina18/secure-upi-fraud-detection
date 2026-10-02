import numpy as np
import pytest

from src import config as C
from src.data_generation.build_dataset import build
from src.data_generation.inject_fraud import ARCHETYPE_MIX


@pytest.fixture(scope="module")
def df():
    return build(n_users=300, n_days=30, fraud_rate=0.02, seed=7)


def test_fraud_rate_near_target(df):
    assert abs(df[C.TARGET].mean() - 0.02) < 0.004


def test_all_four_archetypes_present(df):
    assert set(df.loc[df[C.TARGET] == 1, "fraud_type"]) == set(ARCHETYPE_MIX)


def test_labels_and_columns(df):
    assert list(df.columns) == C.RAW_COLUMNS
    assert set(df[C.TARGET].unique()) == {0, 1}
    assert df["amount"].between(1, C.MAX_UPI_AMOUNT).all()
    assert df["txn_id"].is_unique


def test_no_label_leakage(df):
    # 1. leakage columns are never model features
    assert not set(C.LEAKAGE_COLS) & set(C.FEATURE_COLUMNS)
    assert C.TARGET not in C.FEATURE_COLUMNS
    # 2. ids carry no signal: same format for both classes, and id order is not label-ordered
    for col in ["receiver_id"]:
        assert set(df.loc[df[C.TARGET] == 1, col].str[0]) == set(df.loc[df[C.TARGET] == 0, col].str[0])
    ids = df["txn_id"].str[1:].astype(int).to_numpy()
    assert abs(np.corrcoef(ids, df[C.TARGET])[0, 1]) < 0.05
    # 3. fraud is not perfectly separable by a single raw field (overlap exists)
    fr = df[df[C.TARGET] == 1]
    assert (fr["txn_type"] == "P2P").mean() < 0.95 or fr["merchant_category"].nunique() > 1


def test_reproducible():
    a = build(n_users=50, n_days=10, seed=1)
    b = build(n_users=50, n_days=10, seed=1)
    assert a.equals(b)
