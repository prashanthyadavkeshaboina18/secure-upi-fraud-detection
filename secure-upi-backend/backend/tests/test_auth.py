def test_register_then_login(client):
    res = client.post("/api/auth/register", json={
        "name": "Ada", "email": "ada@example.com", "phone": "9876500000", "password": "Password@123",
    })
    assert res.status_code == 201
    body = res.json()
    assert body["email"] == "ada@example.com"
    assert "password" not in body
    assert "password_hash" not in body

    res = client.post("/api/auth/login", json={"email": "ada@example.com", "password": "Password@123"})
    assert res.status_code == 200
    assert res.json()["token_type"] == "bearer"


def test_duplicate_email_is_rejected(client):
    payload = {"name": "Ada", "email": "dup@example.com", "phone": "9876500001", "password": "Password@123"}
    assert client.post("/api/auth/register", json=payload).status_code == 201
    res = client.post("/api/auth/register", json=payload)
    assert res.status_code == 409


def test_wrong_password_rejected(client):
    client.post("/api/auth/register", json={
        "name": "Ada", "email": "wrong@example.com", "phone": "9876500002", "password": "Password@123",
    })
    res = client.post("/api/auth/login", json={"email": "wrong@example.com", "password": "not-it"})
    assert res.status_code == 401


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_current_user(client, register_and_login):
    _, headers = register_and_login()
    res = client.get("/api/auth/me", headers=headers)
    assert res.status_code == 200
    assert res.json()["email"] == "user@example.com"
