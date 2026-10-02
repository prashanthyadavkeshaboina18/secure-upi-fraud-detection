"""★★★ The most important tests in the project.

They guarantee (1) the output contract, (2) point-in-time correctness (no future leakage),
(3) batch/order invariance, and (4) that single-transaction scoring — what the backend does —
gives the same numbers as training-time batch features.
"""
import numpy as np
import pandas as pd
import pytest

from src import config as C
from src.data_generation.build_dataset import build
from src.feature_engineering import build_features, compute_single


def _txn(ts, amount=100.0, recv="P1", dev="D0", city="Delhi", sender="U1", **kw):
    d = dict(timestamp=ts, sender_id=sender, receiver_id=recv, amount=amount, txn_type="P2P",
             merchant_category="person", device_id=dev, city=city, account_age_days=200)
    d.update(kw)
    return d


def _frame(rows):
    return pd.DataFrame(rows)


def test_output_contract():
    out = build_features(_frame([_txn("2025-01-01 10:00:00")]))
    assert list(out.columns) == C.FEATURE_COLUMNS
    assert not out.isna().any().any()


def test_missing_input_column_raises():
    with pytest.raises(ValueError):
        build_features(_frame([_txn("2025-01-01 10:00:00")]).drop(columns=["city"]))


def test_first_transaction_has_neutral_history_features():
    r = build_features(_frame([_txn("2025-01-01 10:00:00")])).iloc[0]
    for c in ["is_new_payee", "is_new_device", "is_new_city", "txn_count_1h", "txn_count_24h",
              "amount_sum_24h", "amount_zscore"]:
        assert r[c] == 0
    assert r["amount_ratio_to_max"] == 1


def test_new_payee_device_city_flags():
    f = build_features(_frame([
        _txn("2025-01-01 10:00:00"),
        _txn("2025-01-01 11:00:00"),                                             # all familiar
        _txn("2025-01-01 12:00:00", recv="P2", dev="D9", city="Pune"),           # all new
        _txn("2025-01-01 13:00:00", recv="P2", dev="D9", city="Pune"),           # now familiar
    ]))
    assert f[["is_new_payee", "is_new_device", "is_new_city"]].to_numpy().tolist() == [
        [0, 0, 0], [0, 0, 0], [1, 1, 1], [0, 0, 0]]


def test_velocity_windows_use_only_the_past():
    f = build_features(_frame([
        _txn("2025-01-01 10:00:00", amount=10),
        _txn("2025-01-01 10:20:00", amount=20),
        _txn("2025-01-01 10:40:00", amount=30),
        _txn("2025-01-02 11:00:00", amount=40),   # >24h after the others
    ]))
    assert f["txn_count_1h"].tolist() == [0, 1, 2, 0]
    assert f["amount_sum_24h"].tolist() == [0, 10, 30, 0]
    assert f["txn_count_24h"].tolist() == [0, 1, 2, 0]


def test_amount_zscore_flags_outlier():
    rows = [_txn(f"2025-01-0{d} 10:00:00", amount=100 + d) for d in range(1, 8)]
    rows.append(_txn("2025-01-09 10:00:00", amount=50_000))
    f = build_features(_frame(rows))
    assert f["amount_zscore"].iloc[-1] > 5
    assert f["amount_ratio_to_max"].iloc[-1] > 100 or f["amount_ratio_to_max"].iloc[-1] == 20


def test_senders_do_not_share_history():
    f = build_features(_frame([
        _txn("2025-01-01 10:00:00", sender="A", recv="P1"),
        _txn("2025-01-01 10:01:00", sender="B", recv="P1"),
    ]))
    assert f["is_new_payee"].tolist() == [0, 0]   # each is that sender's FIRST txn
    assert f["txn_count_1h"].tolist() == [0, 0]


def test_no_future_leakage():
    rows = [_txn(f"2025-01-01 {h:02d}:00:00", amount=100 + h, recv=f"P{h % 3}") for h in range(1, 10)]
    base = build_features(_frame(rows[:5]))
    tampered = rows[:5] + [dict(r, amount=99_999, recv="ZZZ", device_id="X", city="Pune") for r in rows[5:]]
    after = build_features(_frame(tampered)).iloc[:5]
    pd.testing.assert_frame_equal(base, after)


def test_row_order_and_index_invariance():
    df = build(n_users=40, n_days=15, seed=3).head(400)
    a = build_features(df)
    shuffled = df.sample(frac=1, random_state=0)
    b = build_features(shuffled)
    assert b.index.equals(shuffled.index)
    pd.testing.assert_frame_equal(a, b.loc[a.index])   # same features per row, any input order


def test_batch_matches_single_transaction_scoring():
    """What the backend does (one txn + history) must equal what training did (batch)."""
    df = build(n_users=25, n_days=20, seed=5)
    batch = build_features(df)
    rng = np.random.default_rng(0)
    for i in rng.choice(len(df), size=60, replace=False):
        row = df.iloc[i]
        past = df.iloc[:i]                                   # df is sorted by time
        single = compute_single(row.to_dict(), past)
        pd.testing.assert_frame_equal(
            single, batch.iloc[[i]].reset_index(drop=True), check_exact=False, rtol=1e-9, atol=1e-9)


def test_single_without_history_is_neutral():
    out = compute_single(_txn("2025-01-01 10:00:00"), None)
    assert out.loc[0, "is_new_payee"] == 0 and out.loc[0, "txn_count_24h"] == 0
