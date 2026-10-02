"""
No trained model exists in this test environment (there is no
pipeline.joblib on disk), which is the correct state before the ML phase
runs. These tests confirm the API fails *safely and honestly* — a 503,
never a fabricated prediction — matching the project's rule against
hardcoded fraud decisions.
"""

VALID_PAYLOAD = {
    "amount": 500,
    "receiver_vpa": "merchant@okbank",
    "merchant_name": "Test Merchant",
    "merchant_category": "Groceries",
    "transaction_type": "P2M",
    "device_id": "DEV-001",
    "device_type": "ANDROID",
    "location_city": "Hyderabad",
}


def test_predict_requires_auth(client):
    res = client.post("/api/transactions/predict", json=VALID_PAYLOAD)
    assert res.status_code == 401


def test_predict_returns_503_without_a_trained_model(client, register_and_login):
    _, headers = register_and_login()
    res = client.post("/api/transactions/predict", json=VALID_PAYLOAD, headers=headers)
    assert res.status_code == 503


def test_predict_rejects_amount_over_upi_limit(client, register_and_login):
    _, headers = register_and_login()
    payload = {**VALID_PAYLOAD, "amount": 200000}
    res = client.post("/api/transactions/predict", json=payload, headers=headers)
    assert res.status_code == 422


def test_list_transactions_empty_for_new_user(client, register_and_login):
    _, headers = register_and_login()
    res = client.get("/api/transactions", headers=headers)
    assert res.status_code == 200
    assert res.json() == {"items": [], "total": 0}


def test_get_missing_transaction_is_404(client, register_and_login):
    _, headers = register_and_login()
    res = client.get("/api/transactions/TXN00000000000000", headers=headers)
    assert res.status_code == 404
