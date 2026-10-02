"""★ Inject 4 fraud archetypes, with noise/overlap so the problem isn't trivially separable.

Archetypes
  account_takeover    new device, often another city, often at night, big amount, new payee
  social_engineering  victim pays / approves a COLLECT on their OWN device & city; new payee
  mule_burst          rapid burst of small transfers to many new payees
  high_value_drain    very large, often round amount to a new payee / risky category

Overlap (why models can't hit 100%):
  * STEALTH_PROB of fraud rows copy the victim's normal habits (hour, device, city, amount).
  * Genuine traffic (see generate_transactions) already contains new payees, new devices,
    travel and round amounts.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import CITIES, MAX_UPI_AMOUNT, PAYEE_UNIVERSE
from src.data_generation.generate_transactions import payee_ids

ARCHETYPE_MIX = {
    "account_takeover": 0.30,
    "social_engineering": 0.35,
    "mule_burst": 0.20,
    "high_value_drain": 0.15,
}
STEALTH_PROB = 0.25


def _pick_victims(users: pd.DataFrame, n: int, rng) -> pd.DataFrame:
    return users.iloc[rng.integers(0, len(users), n)].reset_index(drop=True)


def _random_ts(n: int, rng, start: str, n_days: int) -> pd.Series:
    secs = rng.integers(0, n_days * 86400, n)
    return pd.Series(pd.Timestamp(start) + pd.to_timedelta(secs, unit="s"))


def _set_hour(ts: pd.Series, hours: np.ndarray, rng) -> pd.Series:
    return ts.dt.normalize() + pd.to_timedelta(hours * 3600 + rng.integers(0, 3600, len(ts)), unit="s")


def _finish(v, ts, amount, txn_type, merchant, device, city, receiver, ftype, start) -> pd.DataFrame:
    day = (pd.Series(ts) - pd.Timestamp(start)).dt.days.to_numpy()
    amount = np.clip(np.asarray(amount, dtype=float), 1, MAX_UPI_AMOUNT).round(2)
    return pd.DataFrame(
        {
            "timestamp": pd.Series(ts).to_numpy(),
            "sender_id": v["sender_id"].to_numpy(),
            "receiver_id": receiver,
            "amount": amount,
            "txn_type": txn_type,
            "merchant_category": merchant,
            "device_id": device,
            "city": city,
            "account_age_days": v["account_age_days"].to_numpy() + day,
            "is_fraud": 1,
            "fraud_type": ftype,
        }
    )


def _new_device(v, rng):
    return np.array([f"D{s}_{rng.integers(2, 9999)}" for s in v["sender_id"]], dtype=object)


def _own_device(v):
    return np.array([f"D{s}_0" for s in v["sender_id"]], dtype=object)


def _other_city(v, rng, p_away: float):
    away = rng.random(len(v)) < p_away
    return np.where(away, rng.choice(CITIES, len(v)), v["home_city"].to_numpy())


def _new_payees(n, rng):
    return payee_ids(rng.integers(0, PAYEE_UNIVERSE, n))


# ---------------------------------------------------------------------------
def _account_takeover(n, users, rng, start, n_days):
    v = _pick_victims(users, n, rng)
    stealth = rng.random(n) < STEALTH_PROB
    ts = _random_ts(n, rng, start, n_days)
    night = rng.random(n) < 0.6
    hours = np.where(night, rng.integers(0, 5, n), rng.integers(6, 23, n))
    hours = np.where(stealth, v["peak_hour"].astype(int).to_numpy(), hours)
    ts = _set_hour(ts, hours, rng)
    mult = np.where(stealth, rng.uniform(0.8, 2.0, n), rng.uniform(3, 12, n))
    device = np.where(stealth & (rng.random(n) < 0.5), _own_device(v), _new_device(v, rng))
    city = _other_city(v, rng, 0.0)
    city = np.where(stealth, city, _other_city(v, rng, 0.7))
    return _finish(v, ts, v["median_amount"].to_numpy() * mult, np.full(n, "P2P", dtype=object),
                   np.full(n, "person", dtype=object), device, city, _new_payees(n, rng),
                   "account_takeover", start)


def _social_engineering(n, users, rng, start, n_days):
    v = _pick_victims(users, n, rng)
    stealth = rng.random(n) < STEALTH_PROB
    ts = _set_hour(_random_ts(n, rng, start, n_days), rng.integers(9, 22, n), rng)
    mult = np.where(stealth, rng.uniform(0.8, 1.5, n), rng.uniform(2, 8, n))
    txn_type = np.where(rng.random(n) < 0.6, "COLLECT", "P2P").astype(object)
    return _finish(v, ts, v["median_amount"].to_numpy() * mult, txn_type,
                   np.full(n, "person", dtype=object), _own_device(v), _other_city(v, rng, 0.0),
                   _new_payees(n, rng), "social_engineering", start)


def _mule_burst(n, users, rng, start, n_days):
    parts, remaining = [], n
    while remaining > 0:
        k = int(min(remaining, rng.integers(3, 9)))
        v = _pick_victims(users, 1, rng).loc[np.repeat(0, k)].reset_index(drop=True)
        stealth = rng.random() < STEALTH_PROB
        gaps = rng.integers(900, 7200, k) if stealth else rng.integers(10, 150, k)
        t0 = _random_ts(1, rng, start, n_days).iloc[0]
        ts = pd.Series(t0 + pd.to_timedelta(np.cumsum(gaps), unit="s"))
        device = _new_device(v.iloc[:1], rng).repeat(k) if rng.random() < 0.5 else _own_device(v)
        parts.append(
            _finish(v, ts, rng.uniform(150, 1800, k), np.full(k, "P2P", dtype=object),
                    np.full(k, "person", dtype=object), device, _other_city(v, rng, 0.0),
                    _new_payees(k, rng), "mule_burst", start)
        )
        remaining -= k
    return pd.concat(parts, ignore_index=True)


def _high_value_drain(n, users, rng, start, n_days):
    v = _pick_victims(users, n, rng)
    stealth = rng.random(n) < STEALTH_PROB
    ts = _set_hour(_random_ts(n, rng, start, n_days), rng.integers(0, 24, n), rng)
    big = np.maximum(2000, np.round(v["median_amount"].to_numpy() * rng.uniform(8, 30, n) / 1000) * 1000)
    small = v["median_amount"].to_numpy() * rng.uniform(1, 3, n)
    amount = np.where(stealth, small, big)
    is_p2m = rng.random(n) < 0.6
    txn_type = np.where(is_p2m, "P2M", "P2P").astype(object)
    merchant = np.where(is_p2m, rng.choice(["gaming", "wallet_topup", "shopping"], n), "person").astype(object)
    device = np.where(rng.random(n) < 0.4, _new_device(v, rng), _own_device(v))
    return _finish(v, ts, amount, txn_type, merchant, device, _other_city(v, rng, 0.3),
                   _new_payees(n, rng), "high_value_drain", start)


_BUILDERS = {
    "account_takeover": _account_takeover,
    "social_engineering": _social_engineering,
    "mule_burst": _mule_burst,
    "high_value_drain": _high_value_drain,
}


def inject_fraud(genuine, users, rng, target_rate, start, n_days) -> pd.DataFrame:
    """Return genuine + fraud rows so that fraud share ≈ target_rate."""
    n_fraud = int(round(target_rate / (1 - target_rate) * len(genuine)))
    counts = {k: int(round(n_fraud * w)) for k, w in ARCHETYPE_MIX.items()}
    counts["account_takeover"] += n_fraud - sum(counts.values())
    fraud = [_BUILDERS[k](c, users, rng, start, n_days) for k, c in counts.items() if c > 0]
    return pd.concat([genuine] + fraud, ignore_index=True)
