"""Phase 8–9 — FastAPI route, CORS, and error-handler tests.
Phase 20 — POST /analyze/ingest integration and caching tests.
"""

import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

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


def test_analyze_ingest_cache_miss_then_hit(monkeypatch, tmp_path):
    """Test POST /analyze/ingest: cache miss fetches from GitHub, then cache hit returns cached data."""
    db_path = str(tmp_path / "test.db")

    # Mock settings to use test database
    mock_settings = MagicMock()
    mock_settings.db_path = db_path
    mock_settings.github_token = "test_token"
    monkeypatch.setattr("backend.main.settings", mock_settings)

    # Mock GitHub client responses
    mock_meta = {
        "owner": "testowner",
        "repo": "testrepo",
        "description": "Test repository",
        "stars": 42,
        "primary_language": "Python",
        "default_branch": "main",
    }

    mock_tree = [
        "README.md",
        "src/main.py",
        "src/utils.py",
        "requirements.txt",
        "tests/test_main.py",
    ]

    mock_requirements = "fastapi>=0.100.0\npydantic>=2.0.0\n"

    mock_client = MagicMock()
    mock_client.get_repo_meta.return_value = mock_meta
    mock_client.get_file_tree.return_value = mock_tree
    mock_client.get_file.return_value = mock_requirements

    with patch("backend.main.GitHubClient", return_value=mock_client):
        client = TestClient(create_app())

        # First request: cache miss
        response1 = client.post(
            "/analyze/ingest",
            json={"repo_url": "https://github.com/testowner/testrepo"}
        )

        assert response1.status_code == 200
        data1 = response1.json()

        assert data1["repo_url"] == "https://github.com/testowner/testrepo"
        assert data1["owner"] == "testowner"
        assert data1["repo"] == "testrepo"
        assert data1["description"] == "Test repository"
        assert data1["stars"] == 42
        assert data1["primary_language"] == "Python"
        assert data1["file_count"] == 5
        assert "Python" in data1["languages"]
        assert "python" in data1["dependencies"]
        assert "fastapi" in data1["dependencies"]["python"]
        assert "pydantic" in data1["dependencies"]["python"]

        # Verify GitHub client was called
        assert mock_client.get_repo_meta.call_count == 1
        assert mock_client.get_file_tree.call_count == 1

        # Second request: cache hit (should NOT call GitHub client again)
        response2 = client.post(
            "/analyze/ingest",
            json={"repo_url": "https://github.com/testowner/testrepo"}
        )

        assert response2.status_code == 200
        data2 = response2.json()

        # Data should be identical
        assert data2 == data1

        # Verify GitHub client was NOT called again
        assert mock_client.get_repo_meta.call_count == 1  # Still 1, not 2
        assert mock_client.get_file_tree.call_count == 1  # Still 1, not 2


def test_analyze_ingest_with_javascript_deps(monkeypatch, tmp_path):
    """Test POST /analyze/ingest with JavaScript dependencies."""
    db_path = str(tmp_path / "test_js.db")

    mock_settings = MagicMock()
    mock_settings.db_path = db_path
    mock_settings.github_token = ""
    monkeypatch.setattr("backend.main.settings", mock_settings)

    mock_meta = {
        "owner": "jsuser",
        "repo": "jsproject",
        "description": "JavaScript project",
        "stars": 100,
        "primary_language": "JavaScript",
        "default_branch": "main",
    }

    mock_tree = [
        "package.json",
        "src/index.js",
        "src/components/App.jsx",
    ]

    mock_package_json = """{
        "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        },
        "devDependencies": {
            "vite": "^4.0.0"
        }
    }"""

    mock_client = MagicMock()
    mock_client.get_repo_meta.return_value = mock_meta
    mock_client.get_file_tree.return_value = mock_tree
    mock_client.get_file.return_value = mock_package_json

    with patch("backend.main.GitHubClient", return_value=mock_client):
        client = TestClient(create_app())

        response = client.post(
            "/analyze/ingest",
            json={"repo_url": "https://github.com/jsuser/jsproject"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["owner"] == "jsuser"
        assert data["repo"] == "jsproject"
        assert data["primary_language"] == "JavaScript"
        assert "javascript" in data["dependencies"]
        assert "react" in data["dependencies"]["javascript"]
        assert "react-dom" in data["dependencies"]["javascript"]
        assert "vite" in data["dependencies"]["javascript"]
        assert "JavaScript" in data["languages"]


def test_analyze_ingest_invalid_url():
    """Test POST /analyze/ingest with invalid URL returns validation error."""
    client = TestClient(create_app())

    response = client.post(
        "/analyze/ingest",
        json={"repo_url": "not-a-valid-url"}
    )

    assert response.status_code == 422  # Validation error


def test_analyze_ingest_no_dependencies(monkeypatch, tmp_path):
    """Test POST /analyze/ingest with repository that has no manifest files."""
    db_path = str(tmp_path / "test_nodeps.db")

    mock_settings = MagicMock()
    mock_settings.db_path = db_path
    mock_settings.github_token = ""
    monkeypatch.setattr("backend.main.settings", mock_settings)

    mock_meta = {
        "owner": "simple",
        "repo": "project",
        "description": "Simple project",
        "stars": 5,
        "primary_language": "Markdown",
        "default_branch": "main",
    }

    mock_tree = ["README.md", "docs/guide.md"]

    mock_client = MagicMock()
    mock_client.get_repo_meta.return_value = mock_meta
    mock_client.get_file_tree.return_value = mock_tree

    with patch("backend.main.GitHubClient", return_value=mock_client):
        client = TestClient(create_app())

        response = client.post(
            "/analyze/ingest",
            json={"repo_url": "https://github.com/simple/project"}
        )

        assert response.status_code == 200
        data = response.json()

        assert data["owner"] == "simple"
        assert data["repo"] == "project"
        assert data["dependencies"] == {}  # No dependencies
        assert data["file_count"] == 2
        assert "Markdown" in data["languages"]


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
