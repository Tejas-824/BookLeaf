from tests.conftest import login

BODY = {"subject": "Royalty question", "description": "Where is my royalty for the last quarter?"}


def test_author_cannot_see_other_authors_ticket(client):
    h1, h2 = login(client, "a1@test.com"), login(client, "a2@test.com")
    tid = client.post("/api/tickets", json=BODY, headers=h1).json()["id"]
    assert client.get(f"/api/tickets/{tid}", headers=h1).status_code == 200
    assert client.get(f"/api/tickets/{tid}", headers=h2).status_code == 404


def test_author_blocked_from_admin_routes(client):
    h = login(client, "a1@test.com")
    assert client.get("/api/admin/tickets", headers=h).status_code == 403


def test_admin_can_list_and_reply(client):
    ha, hadm = login(client, "a1@test.com"), login(client, "admin@test.com")
    tid = client.post("/api/tickets", json=BODY, headers=ha).json()["id"]
    assert client.get("/api/admin/tickets", headers=hadm).json()["total"] == 1
    r = client.post(f"/api/admin/tickets/{tid}/reply", json={"body": "We are checking this."}, headers=hadm)
    assert r.status_code == 201
    assert client.get(f"/api/tickets/{tid}", headers=ha).json()["messages"][0]["body"] == "We are checking this."


def test_double_submit_creates_one_ticket(client):
    h = login(client, "a1@test.com")
    h["Idempotency-Key"] = "same-key-123"
    a = client.post("/api/tickets", json=BODY, headers=h).json()["id"]
    b = client.post("/api/tickets", json=BODY, headers=h).json()["id"]
    assert a == b


def test_validation_error_shape(client):
    h = login(client, "a1@test.com")
    r = client.post("/api/tickets", json={"subject": "x", "description": "short"}, headers=h)
    assert r.status_code == 422 and r.json()["error"]["code"] == "validation_error"