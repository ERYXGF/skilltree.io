"""Phase 8–9 — FastAPI route, CORS, and error-handler tests."""

import sys
from pathlib import Path
from unittest.mock import MagicMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.main import create_app  # noqa: E402


def _make_client() -> TestClient:
    return TestClient(create_app())


def test_health_returns_ok():
    client = _make_client()
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_cors_headers_on_preflight():
    client = _make_client()
    response = client.options(
        "/health",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert response.headers.get("access-control-allow-origin") == "http://localhost:5173"


def test_forced_error_returns_clean_json(monkeypatch):
    """Intentionally triggers RuntimeError('boom'); handler must return clean JSON."""
    mock_logger = MagicMock()
    monkeypatch.setattr("backend.main.logger", mock_logger)

    app = create_app()

    @app.get("/test-error")
    async def test_error():
        raise RuntimeError("boom")

    client = TestClient(app, raise_server_exceptions=False)
    response = client.get("/test-error")
    assert response.status_code == 500
    body = response.json()
    assert body["detail"] == "Internal server error"
    assert "boom" in body["error"]
    mock_logger.exception.assert_called_once()


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
