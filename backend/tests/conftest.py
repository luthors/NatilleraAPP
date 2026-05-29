"""
Pytest configuration and shared fixtures for the Natillera backend.

Uses SQLite in-memory for speed. All tests share the schema but each
test function gets a fresh database session (transaction rollback strategy).

Usage:
    pytest                      # all tests
    pytest -m auth              # auth tests only
    pytest -m natillera         # natillera tests
    pytest -m integration       # integration tests (requires live DB)
"""
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from fastapi.testclient import TestClient

from app.core.config import settings
from app.database import Base, get_db
from app.main import app


# ─── Test database ────────────────────────────────────────────────────────────

TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="session", autouse=True)
def create_tables():
    """Create all tables once per test session."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture()
def db():
    """
    Provide a transactional test database session.

    Each test runs in a transaction that is rolled back after the test,
    so tests are fully isolated without needing to truncate tables.
    """
    connection = engine.connect()
    transaction = connection.begin()
    session = TestingSessionLocal(bind=connection)

    yield session

    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture()
def client(db):
    """
    FastAPI TestClient with the test DB injected via dependency override.
    """
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c
    app.dependency_overrides.clear()


# ─── Helpers ──────────────────────────────────────────────────────────────────

@pytest.fixture()
def usuario_data():
    return {
        "nombre": "Test User",
        "email": "test@example.com",
        "password": "Passw0rd!Test",
    }


@pytest.fixture()
def usuario_registrado(client, usuario_data):
    """Register a user and return (tokens, user_data)."""
    resp = client.post("/api/v1/auth/registro", json=usuario_data)
    assert resp.status_code == 201, resp.json()
    return resp.json(), usuario_data


@pytest.fixture()
def auth_headers(usuario_registrado):
    """Bearer auth headers for the registered test user."""
    tokens, _ = usuario_registrado
    return {"Authorization": f"Bearer {tokens['access_token']}"}
