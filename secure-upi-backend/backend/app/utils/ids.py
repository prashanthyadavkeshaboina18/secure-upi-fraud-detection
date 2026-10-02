import secrets
from datetime import datetime


def generate_transaction_id() -> str:
    """e.g. TXN20260917A4F92C — date-prefixed so IDs sort roughly chronologically."""
    stamp = datetime.utcnow().strftime("%Y%m%d")
    suffix = secrets.token_hex(3).upper()
    return f"TXN{stamp}{suffix}"
