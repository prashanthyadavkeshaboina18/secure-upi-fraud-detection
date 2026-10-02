"""Simulate a population of users, each with individual spending habits."""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import CITIES, CITY_PROBS, MERCHANT_CATEGORIES


def generate_users(n_users: int, rng: np.random.Generator) -> pd.DataFrame:
    """One row per user. These parameters drive that user's *genuine* behaviour."""
    category_probs = rng.dirichlet(np.ones(len(MERCHANT_CATEGORIES)) * 0.6, n_users)
    users = pd.DataFrame(
        {
            "sender_id": [f"U{i:05d}" for i in range(n_users)],
            "home_city": rng.choice(CITIES, n_users, p=CITY_PROBS),
            "median_amount": rng.lognormal(np.log(400), 0.8, n_users),
            "amount_sigma": rng.uniform(0.4, 1.0, n_users),
            "txns_per_day": rng.gamma(2.0, 0.6, n_users) + 0.15,
            "peak_hour": np.clip(rng.normal(15, 3, n_users), 9, 21),
            "account_age_days": rng.integers(30, 2000, n_users),
            "n_payees": rng.integers(3, 15, n_users),
            "p2p_share": rng.beta(2, 3, n_users),
        }
    )
    users["category_probs"] = list(category_probs)
    return users
