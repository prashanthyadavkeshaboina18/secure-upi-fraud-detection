"""Central configuration: paths, random seed, fraud-rate target, column names.

Everything that other modules (and the backend) need to agree on lives here.
"""
from __future__ import annotations

import os
from pathlib import Path

# ----------------------------------------------------------------------------
# Paths
# ----------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
INTERIM_DIR = DATA_DIR / "interim"
PROCESSED_DIR = DATA_DIR / "processed"
MODELS_DIR = ROOT / "models"
CANDIDATES_DIR = MODELS_DIR / "candidates"
REPORTS_DIR = ROOT / "reports"
EDA_DIR = REPORTS_DIR / "eda"
EVAL_DIR = REPORTS_DIR / "evaluation"

RAW_UPI = RAW_DIR / "upi_synthetic.csv"
RAW_CREDITCARD = RAW_DIR / "creditcard.csv"
INTERIM_UPI = INTERIM_DIR / "upi_synthetic_clean.csv"

# ----------------------------------------------------------------------------
# Reproducibility & data-generation knobs
# ----------------------------------------------------------------------------
SEED = 42
N_USERS = int(os.getenv("ML_N_USERS", 1500))
N_DAYS = int(os.getenv("ML_N_DAYS", 60))
START_DATE = "2025-01-01"
TARGET_FRAUD_RATE = float(os.getenv("ML_FRAUD_RATE", 0.02))
MAX_UPI_AMOUNT = 100_000.0

CITIES = [
    "Mumbai",
    "Delhi",
    "Bengaluru",
    "Hyderabad",
    "Chennai",
    "Kolkata",
    "Pune",
    "Ahmedabad",
]

CITY_PROBS = [
    0.20,
    0.18,
    0.16,
    0.12,
    0.10,
    0.08,
    0.08,
    0.08,
]

MERCHANT_CATEGORIES = [
    "groceries",
    "food",
    "fuel",
    "utilities",
    "shopping",
    "travel",
    "entertainment",
    "healthcare",
    "education",
    "gaming",
    "wallet_topup",
]

TXN_TYPES = [
    "P2P",
    "P2M",
    "COLLECT",
]

PAYEE_UNIVERSE = 20_000

# ----------------------------------------------------------------------------
# Columns
# ----------------------------------------------------------------------------
TARGET = "is_fraud"

LEAKAGE_COLS = [
    "fraud_type",
]

RAW_COLUMNS = [
    "txn_id",
    "timestamp",
    "sender_id",
    "receiver_id",
    "amount",
    "txn_type",
    "merchant_category",
    "device_id",
    "city",
    "account_age_days",
    "is_fraud",
    "fraud_type",
]

INPUT_COLUMNS = [
    "timestamp",
    "sender_id",
    "receiver_id",
    "amount",
    "txn_type",
    "merchant_category",
    "device_id",
    "city",
    "account_age_days",
]

# ----------------------------------------------------------------------------
# Model features.
# ORDER MATTERS.
# These must match the backend feature_service.py order.
# ----------------------------------------------------------------------------
NUMERIC_FEATURES = [
    "amount",
    "hour",
    "day_of_week",
    "is_night",
    "is_weekend",
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
    "account_age_days",
    "lifetime_txn_count",
]

CATEGORICAL_FEATURES = [
    "transaction_type",
    "merchant_category",
]

FEATURE_COLUMNS = NUMERIC_FEATURES + CATEGORICAL_FEATURES

# ----------------------------------------------------------------------------
# History feature settings
# ----------------------------------------------------------------------------
MIN_HISTORY_FOR_ZSCORE = 3
NO_HISTORY_GAP_SECONDS = 30 * 86400

# ----------------------------------------------------------------------------
# Model-selection criteria
# ----------------------------------------------------------------------------
MIN_RECALL = 0.70
MIN_PRECISION = 0.30
VALIDATION_SIZE = 0.20
TEST_SIZE = 0.20