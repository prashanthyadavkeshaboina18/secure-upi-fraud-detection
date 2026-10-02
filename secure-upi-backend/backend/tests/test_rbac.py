def test_user_cannot_access_admin_routes(client, register_and_login):
    _, headers = register_and_login()
    res = client.get("/api/admin/users", headers=headers)
    assert res.status_code == 403


def test_admin_can_access_admin_routes(client, make_admin):
    headers = make_admin()
    res = client.get("/api/admin/users", headers=headers)
    assert res.status_code == 200
    assert "items" in res.json()


def test_admin_route_requires_token(client):
    assert client.get("/api/admin/users").status_code == 401
