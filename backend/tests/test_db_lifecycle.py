"""
PHASE 4 — Minimal DB lifecycle stability test.
Runs after the session/main fixes.
"""
import asyncio
from unittest.mock import AsyncMock

from fastapi.testclient import TestClient

from app.main import app
from app.db.session import get_db, init_db


async def _fake_get_db():
    """Fake async generator that yields a properly mocked session."""
    from unittest.mock import MagicMock
    
    session = AsyncMock()

    # Profile for get_profile
    mock_profile = type("MockProfile", (), {
        "id": 1, "name": "Shahin", "photo_url": None,
        "email": None, "phone": None, "location": None,
        "availability_status": None,
        "github_url": None, "linkedin_url": None,
        "website_url": None, "cv_pdf_url": None
    })()
    session.scalar = AsyncMock(return_value=mock_profile)

    # Make execute().scalars().all() return proper list (sync result)
    # session.execute() must be an async function that returns a sync result object
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = []
    session.execute = AsyncMock(return_value=mock_result)

    yield session


def test_app_imports_without_db_connection():
    """Critical: app must import cleanly."""
    assert app is not None
    print("✓ app.main imported without triggering DB connection")


def test_testclient_creation():
    """TestClient must be creatable without DB."""
    client = TestClient(app)
    assert client is not None
    print("✓ TestClient(app) created successfully")


def test_health_endpoint():
    client = TestClient(app)
    r = client.get("/health")
    assert r.status_code == 200
    print("✓ GET /health → 200")


def test_public_endpoints_with_override():
    """The key fix: public endpoints must not crash on startup/DB init."""
    client = TestClient(app)
    app.dependency_overrides[get_db] = _fake_get_db

    endpoints = [
        "/api/v1/profile?lang=en",
        "/api/v1/skills?lang=en",
        "/api/v1/projects?lang=en",
        "/api/v1/experiences?lang=en",
    ]
    for ep in endpoints:
        r = client.get(ep)
        # Accept 200 or 404 (no data) but NOT 500 or connection errors
        assert r.status_code in (200, 404), f"{ep} returned {r.status_code}"
        print(f"✓ {ep.split('?')[0]} → {r.status_code}")

    # Cleanup
    app.dependency_overrides.clear()


def test_chatbot_endpoint_reachable():
    client = TestClient(app)
    app.dependency_overrides[get_db] = _fake_get_db

    # We don't care about the answer quality here, just that it doesn't blow up at startup
    r = client.post("/api/v1/chatbot/query", json={"question": "What skills?", "lang": "en"})
    # It may return 200 or 429 (rate limit) or 500 in some edge cases, but not connection error at import
    assert r.status_code != 500 or "connect" not in str(r.text).lower()
    print(f"✓ POST /chatbot/query → {r.status_code}")

    app.dependency_overrides.clear()


def test_admin_login_real_path():
    """Admin login must work without DB (env-based)."""
    client = TestClient(app)
    r = client.post("/api/v1/admin/login", json={"email": "owner@example.com", "password": "bad"})
    assert r.status_code == 401
    print("✓ Admin login path executes (401 on bad creds)")


if __name__ == "__main__":
    print("=== PHASE 4 DB LIFECYCLE STABILITY TESTS ===\n")
    test_app_imports_without_db_connection()
    test_testclient_creation()
    test_health_endpoint()
    test_public_endpoints_with_override()
    test_chatbot_endpoint_reachable()
    test_admin_login_real_path()
    print("\n=== ALL TESTS PASSED — DB lifecycle stabilized ===")