import numpy as np
import pandas as pd

from src import config as C
from src.preprocessing import clean


def _row(**kw):
    base = dict(txn_id="T1", timestamp="2025-01-01 10:00:00", sender_id="U1", receiver_id="P1",
                amount=100.0, txn_type="P2P", merchant_category="person", device_id="D1",
                city="Delhi", account_age_days=100, is_fraud=0, fraud_type="none")
    base.update(kw)
    return base


def test_duplicates_removed():
    df = pd.DataFrame([_row(), _row(), _row(txn_id="T2", amount=5.0)])
    out, rep = clean(df)
    assert len(out) == 2 and rep["duplicates_removed"] == 1


def test_invalid_rows_dropped():
    df = pd.DataFrame([
        _row(txn_id="a"), _row(txn_id="b", amount=-5), _row(txn_id="c", amount=0),
        _row(txn_id="d", amount="abc"), _row(txn_id="e", timestamp="not a date"),
        _row(txn_id="f", amount=C.MAX_UPI_AMOUNT * 2), _row(txn_id="g", is_fraud=3),
        _row(txn_id="h", sender_id=None),
    ])
    out, rep = clean(df)
    assert out["txn_id"].tolist() == ["a"]
    assert rep["invalid_rows_removed"] == 7


def test_missing_values_filled_and_dtypes_fixed():
    df = pd.DataFrame([_row(txn_id="a", city=None, merchant_category=None, account_age_days=np.nan),
                       _row(txn_id="b", account_age_days="50", amount="12.5")])
    out, _ = clean(df)
    assert out["city"].iloc[0] == "UNKNOWN"
    assert out["merchant_category"].iloc[0] == "unknown"
    assert not out.isna().any().any()
    assert pd.api.types.is_numeric_dtype(out["amount"])
    assert out[C.TARGET].dtype.kind == "i"


def test_input_not_mutated_and_sorted_by_time():
    df = pd.DataFrame([_row(txn_id="b", timestamp="2025-01-02 00:00:00"), _row(txn_id="a")])
    before = df.copy()
    out, _ = clean(df)
    pd.testing.assert_frame_equal(df, before)
    assert out["txn_id"].tolist() == ["a", "b"]
