from tests.conftest import PASSWORD


def test_login_ok(client):
    r = client.post("/api/auth/login", json={"email": "a1@test.com", "password": PASSWORD})
    assert r.status_code == 200 and r.json()["role"] == "author"


def test_login_wrong_password(client):
    r = client.post("/api/auth/login", json={"email": "a1@test.com", "password": "wrong"})
    assert r.status_code == 401
    assert r.json()["error"]["code"] == "invalid_credentials"


def test_route_needs_token(client):
    assert client.get("/api/books").status_code == 401