"""Simulate genuine transaction streams per user."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import CITIES, MAX_UPI_AMOUNT, MERCHANT_CATEGORIES, PAYEE_UNIVERSE


def payee_ids(ids: np.ndarray) -> np.ndarray:
    """Format integer ids as payee strings. Shared by genuine AND fraud rows (no prefix leakage)."""
    return np.array([f"P{int(i):06d}" for i in ids], dtype=object)


def generate_transactions(
    users: pd.DataFrame, rng: np.random.Generator, n_days: int, start: str
) -> pd.DataFrame:
    start_ts = pd.Timestamp(start)
    frames = []
    for u in users.itertuples(index=False):
        n = int(rng.poisson(u.txns_per_day * n_days))
        if n == 0:
            continue
        day = rng.integers(0, n_days, n)
        hour = rng.normal(u.peak_hour, 4.0, n) % 24
        secs = day * 86400 + (hour * 3600).astype(int) + rng.integers(0, 60, n)
        ts = start_ts + pd.to_timedelta(secs, unit="s")

        amount = rng.lognormal(np.log(u.median_amount), u.amount_sigma, n)
        round_mask = rng.random(n) < 0.15  # people often pay round amounts too
        amount = np.where(round_mask, np.maximum(10, np.round(amount / 10) * 10), amount)
        amount = np.clip(amount, 1, MAX_UPI_AMOUNT).round(2)

        is_p2p = rng.random(n) < u.p2p_share
        txn_type = np.where(is_p2p, "P2P", "P2M").astype(object)
        txn_type[is_p2p & (rng.random(n) < 0.05)] = "COLLECT"  # genuine collect requests exist
        merchant = rng.choice(MERCHANT_CATEGORIES, n, p=u.category_probs).astype(object)
        merchant[txn_type != "P2M"] = "person"

        pool = rng.integers(0, PAYEE_UNIVERSE, u.n_payees)
        recv_int = rng.choice(pool, n)
        new_payee = rng.random(n) < 0.05  # genuine users do pay new people
        recv_int = np.where(new_payee, rng.integers(0, PAYEE_UNIVERSE, n), recv_int)

        device = np.array(
            [
                f"D{u.sender_id}_{rng.integers(2, 9999)}" if r < 0.01   # genuine new phone
                else f"D{u.sender_id}_1" if r < 0.09                    # genuine 2nd device
                else f"D{u.sender_id}_0"
                for r in rng.random(n)
            ],
            dtype=object,
        )
        away = rng.random(n) < 0.03  # genuine travel
        city = np.where(away, rng.choice(CITIES, n), u.home_city)

        frames.append(
            pd.DataFrame(
                {
                    "timestamp": ts,
                    "sender_id": u.sender_id,
                    "receiver_id": payee_ids(recv_int),
                    "amount": amount,
                    "txn_type": txn_type,
                    "merchant_category": merchant,
                    "device_id": device,
                    "city": city,
                    "account_age_days": u.account_age_days + day,
                    "is_fraud": 0,
                    "fraud_type": "none",
                }
            )
        )
    return pd.concat(frames, ignore_index=True)
