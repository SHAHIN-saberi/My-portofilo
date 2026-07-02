"""Tests for the admin list endpoints added in this package.

Scope: route wiring (path + method registered) and auth enforcement via
TestClient. These don't require a live Postgres instance since the 401
response from `require_admin` is raised before any DB query executes (the
`AsyncSession` from `get_db` is only opened lazily, never connected to
verify credentials).
"""
import inspect

from fastapi.testclient import TestClient

from app.main import app
from app.services import admin_service

LIST_ENDPOINTS = {
    "/api/v1/admin/experiences": admin_service.list_experiences,
    "/api/v1/admin/education": admin_service.list_education,
    "/api/v1/admin/courses": admin_service.list_courses,
    "/api/v1/admin/certificates": admin_service.list_certificates,
    "/api/v1/admin/projects": admin_service.list_projects,
    "/api/v1/admin/social-links": admin_service.list_social_links,
    "/api/v1/admin/ai-knowledge": admin_service.list_ai_knowledge_entries,
}


def test_all_expected_list_functions_exist_and_are_async():
    for path, func in LIST_ENDPOINTS.items():
        assert inspect.iscoroutinefunction(func), f"{path} -> {func.__name__} must be async"
        params = list(inspect.signature(func).parameters)
        # Should have session, and optionally limit/offset
        assert "session" in params, f"{func.__name__} should have `session` parameter"


def test_get_route_registered_for_every_list_endpoint():
    registered: dict[str, set] = {}
    for route in app.routes:
        path = getattr(route, "path", None)
        if path in LIST_ENDPOINTS:
            registered.setdefault(path, set()).update(getattr(route, "methods", set()))
    for path in LIST_ENDPOINTS:
        assert path in registered, f"missing route: {path}"
        assert "GET" in registered[path], f"{path} missing GET method"


def test_list_endpoints_require_admin_auth():
    client = TestClient(app)
    for path in LIST_ENDPOINTS:
        response = client.get(path)
        assert response.status_code == 401, f"{path} should require auth, got {response.status_code}"
