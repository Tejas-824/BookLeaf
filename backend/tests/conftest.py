import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401
from app.core.security import hash_password
from app.db.base import Base
from app.db.session import get_db
from app.main import app
from app.models.author import Author
from app.models.user import User

PASSWORD = "pass1234"


@pytest.fixture()
def db():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine, expire_on_commit=False)()
    h = hash_password(PASSWORD)
    for i in (1, 2):
        session.add(Author(author_id=f"AUTH_T{i}", name=f"Test Author{i}", email=f"a{i}@test.com"))
        session.flush()
        session.add(User(email=f"a{i}@test.com", password_hash=h, name=f"Test Author{i}", role="author", author_id=f"AUTH_T{i}"))
    session.add(User(email="admin@test.com", password_hash=h, name="Admin", role="admin"))
    session.commit()
    yield session
    session.close()


@pytest.fixture()
def client(db, monkeypatch):
    app.dependency_overrides[get_db] = lambda: db
    monkeypatch.setattr("app.api.routes.tickets.run_pipeline", lambda ticket_id: None)  # no AI in tests
    yield TestClient(app)
    app.dependency_overrides.clear()


def login(client, email: str) -> dict:
    r = client.post("/api/auth/login", json={"email": email, "password": PASSWORD})
    return {"Authorization": f"Bearer {r.json()['access_token']}"}