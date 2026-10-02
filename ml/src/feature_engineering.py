"""Fast backend-compatible feature engineering."""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.config import FEATURE_COLUMNS, INPUT_COLUMNS


def _history_features(
    timestamps,
    amounts,
    merchant_categories,
    devices,
    cities,
    account_age_days,
):
    n = len(timestamps)

    txn_count_last_5min = np.zeros(n, dtype=float)
    txn_count_last_1h = np.zeros(n, dtype=float)
    txn_count_last_24h = np.zeros(n, dtype=float)
    amount_sum_last_1h = np.zeros(n, dtype=float)

    seconds_since_last_txn = np.full(
        n, 999999.0, dtype=float
    )

    amount_to_avg_ratio = np.ones(n, dtype=float)
    amount_zscore = np.zeros(n, dtype=float)

    is_new_merchant_category = np.zeros(n, dtype=float)
    is_new_device = np.zeros(n, dtype=float)
    distinct_devices_30d = np.zeros(n, dtype=float)
    device_changed = np.zeros(n, dtype=float)

    is_new_location = np.zeros(n, dtype=float)
    location_changed = np.zeros(n, dtype=float)

    lifetime_txn_count = np.arange(
        n, dtype=float
    )

    # Convert timestamps to integer seconds.
    time_seconds = (
        timestamps.astype("datetime64[s]")
        .astype(np.int64)
    )

    # Running statistics for historical amounts.
    running_count = 0
    running_sum = 0.0
    running_sum_sq = 0.0

    # Historical sets.
    merchant_seen = set()
    city_seen = set()

    # Store previous transactions for rolling windows.
    left_5min = 0
    left_1h = 0
    left_24h = 0

    rolling_sum_1h = 0.0

    # Device timestamps.
    device_history = []

    for i in range(n):

        current_time = time_seconds[i]

        # --------------------------------
        # Remove transactions outside
        # rolling windows.
        # --------------------------------

        while (
            left_5min < i
            and current_time - time_seconds[left_5min]
            > 5 * 60
        ):
            left_5min += 1

        while (
            left_1h < i
            and current_time - time_seconds[left_1h]
            > 60 * 60
        ):
            rolling_sum_1h -= amounts[left_1h]
            left_1h += 1

        while (
            left_24h < i
            and current_time - time_seconds[left_24h]
            > 24 * 60 * 60
        ):
            left_24h += 1

        # --------------------------------
        # Rolling transaction counts
        # --------------------------------

        txn_count_last_5min[i] = (
            i - left_5min
        )

        txn_count_last_1h[i] = (
            i - left_1h
        )

        txn_count_last_24h[i] = (
            i - left_24h
        )

        amount_sum_last_1h[i] = (
            rolling_sum_1h
        )

        # --------------------------------
        # Historical amount statistics
        # --------------------------------

        if running_count > 0:

            avg_amount = (
                running_sum / running_count
            )

            if avg_amount != 0:

                amount_to_avg_ratio[i] = (
                    amounts[i] / avg_amount
                )

            if running_count > 1:

                variance = (
                    running_sum_sq
                    / running_count
                    - avg_amount * avg_amount
                )

                # Numerical protection.
                variance = max(
                    variance,
                    0.0
                )

                std_amount = np.sqrt(
                    variance
                )

                if std_amount > 0:

                    amount_zscore[i] = (
                        amounts[i]
                        - avg_amount
                    ) / std_amount

        # --------------------------------
        # Previous transaction gap
        # --------------------------------

        if i > 0:

            seconds_since_last_txn[i] = (
                current_time
                - time_seconds[i - 1]
            )

        # --------------------------------
        # Merchant category
        # --------------------------------

        current_merchant = (
            merchant_categories[i]
        )

        is_new_merchant_category[i] = int(
            current_merchant
            not in merchant_seen
        )

        # --------------------------------
        # Device
        # --------------------------------

        current_device = devices[i]

        devices_30d = {

            device

            for timestamp, device

            in device_history

            if current_time - timestamp
            <= 30 * 86400
        }

        distinct_devices_30d[i] = len(
            devices_30d
        )

        is_new_device[i] = int(
            current_device
            not in devices_30d
        )

        if i > 0:

            device_changed[i] = int(
                devices[i - 1]
                != devices[i]
            )

        # --------------------------------
        # Location
        # --------------------------------

        current_city = cities[i]

        is_new_location[i] = int(
            current_city
            not in city_seen
        )

        if i > 0:

            location_changed[i] = int(
                cities[i - 1]
                != cities[i]
            )

        # --------------------------------
        # Update running state AFTER
        # calculating current features.
        # --------------------------------

        running_count += 1

        running_sum += amounts[i]

        running_sum_sq += (
            amounts[i] * amounts[i]
        )

        rolling_sum_1h += amounts[i]

        merchant_seen.add(
            current_merchant
        )

        city_seen.add(
            current_city
        )

        device_history.append(
            (
                current_time,
                current_device,
            )
        )

    return {
        "txn_count_last_5min":
            txn_count_last_5min,

        "txn_count_last_1h":
            txn_count_last_1h,

        "txn_count_last_24h":
            txn_count_last_24h,

        "amount_sum_last_1h":
            amount_sum_last_1h,

        "seconds_since_last_txn":
            seconds_since_last_txn,

        "amount_to_avg_ratio":
            amount_to_avg_ratio,

        "amount_zscore":
            amount_zscore,

        "is_new_merchant_category":
            is_new_merchant_category,

        "is_new_device":
            is_new_device,

        "distinct_devices_30d":
            distinct_devices_30d,

        "device_changed":
            device_changed,

        "is_new_location":
            is_new_location,

        "location_changed":
            location_changed,

        "lifetime_txn_count":
            lifetime_txn_count,
    }


def build_features(df: pd.DataFrame) -> pd.DataFrame:
    """Build the 22 backend-compatible features."""

    missing = [
        column
        for column in INPUT_COLUMNS
        if column not in df.columns
    ]

    if missing:

        raise ValueError(
            f"Missing input columns: {missing}"
        )

    if len(df) == 0:

        return pd.DataFrame(
            columns=FEATURE_COLUMNS
        )

    d = df.reset_index(
        drop=True
    ).copy()

    n = len(d)

    timestamps = pd.to_datetime(
        d["timestamp"],
        errors="raise",
    ).to_numpy()

    amounts = pd.to_numeric(
        d["amount"],
        errors="raise",
    ).to_numpy(
        dtype=float
    )

    sender_codes, _ = pd.factorize(
        d["sender_id"]
    )

    merchant_categories = (
        d["merchant_category"]
        .fillna("unknown")
        .astype(str)
        .to_numpy()
    )

    devices = (
        d["device_id"]
        .fillna("UNKNOWN_DEVICE")
        .astype(str)
        .to_numpy()
    )

    cities = (
        d["city"]
        .fillna("UNKNOWN")
        .astype(str)
        .to_numpy()
    )

    # Sort by sender and timestamp.
    order = np.lexsort(
        (
            np.arange(n),
            timestamps.astype(
                "datetime64[ns]"
            ).astype(np.int64),
            sender_codes,
        )
    )

    sorted_sender = (
        sender_codes[order]
    )

    sorted_timestamps = (
        timestamps[order]
    )

    sorted_amounts = (
        amounts[order]
    )

    sorted_merchants = (
        merchant_categories[order]
    )

    sorted_devices = (
        devices[order]
    )

    sorted_cities = (
        cities[order]
    )

    history_names = [
        "txn_count_last_5min",
        "txn_count_last_1h",
        "txn_count_last_24h",
        "amount_sum_last_1h",
        "seconds_since_last_txn",
        "amount_to_avg_ratio",
        "amount_zscore",
        "is_new_merchant_category",
        "is_new_device",
        "distinct_devices_30d",
        "device_changed",
        "is_new_location",
        "location_changed",
        "lifetime_txn_count",
    ]

    sorted_out = {

        name: np.zeros(
            n,
            dtype=float
        )

        for name in history_names
    }

    boundaries = np.concatenate(
        [
            [0],

            np.flatnonzero(
                np.diff(
                    sorted_sender
                )
            ) + 1,

            [n],
        ]
    )

    for start, end in zip(
        boundaries[:-1],
        boundaries[1:],
    ):

        result = _history_features(

            sorted_timestamps[
                start:end
            ],

            sorted_amounts[
                start:end
            ],

            sorted_merchants[
                start:end
            ],

            sorted_devices[
                start:end
            ],

            sorted_cities[
                start:end
            ],

            np.zeros(
                end - start
            ),
        )

        for name in history_names:

            sorted_out[name][
                start:end
            ] = result[name]

    out = pd.DataFrame(
        index=range(n)
    )

    for name in history_names:

        restored = np.empty(
            n,
            dtype=float
        )

        restored[order] = (
            sorted_out[name]
        )

        out[name] = restored

    # --------------------------------
    # Time features
    # --------------------------------

    ts = pd.to_datetime(
        d["timestamp"]
    )

    hour = ts.dt.hour.to_numpy()

    day_of_week = (
        ts.dt.dayofweek.to_numpy()
    )

    out["amount"] = amounts

    out["hour"] = (
        hour.astype(float)
    )

    out["day_of_week"] = (
        day_of_week.astype(float)
    )

    out["is_night"] = (
        (
            (hour < 6)
            |
            (hour >= 23)
        )
        .astype(float)
    )

    out["is_weekend"] = (
        (day_of_week >= 5)
        .astype(float)
    )

    # --------------------------------
    # Categorical features
    # --------------------------------

    out["transaction_type"] = (
        d["txn_type"]
        .fillna("unknown")
        .astype(str)
        .to_numpy()
    )

    out["merchant_category"] = (
        d["merchant_category"]
        .fillna("unknown")
        .astype(str)
        .to_numpy()
    )

    # --------------------------------
    # Account age
    # --------------------------------

    out["account_age_days"] = (
        pd.to_numeric(
            d["account_age_days"],
            errors="coerce",
        )
        .fillna(0)
        .to_numpy(
            dtype=float
        )
    )

    # --------------------------------
    # Final feature order
    # --------------------------------

    out = out[
        FEATURE_COLUMNS
    ]

    out.index = df.index

    return out


def compute_single(
    txn: dict,
    history: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Compute features for one live transaction."""

    row = pd.DataFrame([txn])

    parts = []

    if (
        history is not None
        and len(history)
    ):

        sender_history = history[
            history["sender_id"]
            == txn["sender_id"]
        ]

        if len(sender_history):

            history_columns = [
                column
                for column in INPUT_COLUMNS
                if column
                in sender_history.columns
            ]

            parts.append(
                sender_history[
                    history_columns
                ]
            )

    row_columns = [
        column
        for column in INPUT_COLUMNS
        if column in row.columns
    ]

    parts.append(
        row[row_columns]
    )

    frame = pd.concat(
        parts,
        ignore_index=True,
    )

    return (
        build_features(frame)
        .iloc[[-1]]
        .reset_index(drop=True)
    )