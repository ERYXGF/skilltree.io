"""Phase 8–9 — FastAPI route, CORS, and error-handler tests.
Phase 20 — POST /analyze/ingest integration and caching tests.
Phase 32 — POST /analyze full pipeline and agent orchestration tests.
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


def test_analyze_endpoint_cache_miss_then_hit(monkeypatch, tmp_path):
    """
    Test POST /analyze: Full pipeline with cache miss, then cache hit.

    This test verifies:
    1. First request triggers full pipeline (GitHub + AI agent)
    2. Response matches AnalyzeResponse schema
    3. Second request returns cached data immediately
    4. External services (GitHub, Anthropic) are only called once
    """
    db_path = str(tmp_path / "test_analyze.db")

    # Mock settings
    mock_settings = MagicMock()
    mock_settings.db_path = db_path
    mock_settings.github_token = "test_token"
    monkeypatch.setattr("backend.main.settings", mock_settings)

    # Mock GitHub client responses
    mock_meta = {
        "owner": "testuser",
        "repo": "awesome-project",
        "description": "An awesome test project",
        "stars": 150,
        "primary_language": "Python",
        "default_branch": "main",
    }

    mock_tree = [
        "README.md",
        "src/main.py",
        "src/api.py",
        "requirements.txt",
        "tests/test_api.py",
    ]

    mock_requirements = "fastapi>=0.100.0\npydantic>=2.0.0\npytest>=7.0.0\n"

    mock_client = MagicMock()
    mock_client.get_repo_meta.return_value = mock_meta
    mock_client.get_file_tree.return_value = mock_tree
    mock_client.get_file.return_value = mock_requirements

    # Mock orchestrator to return sample bullets
    mock_orchestrator_output = """
    Here are your resume bullets:

    • Architected REST API using FastAPI framework with async/await patterns
    • Implemented comprehensive test suite using Pytest with 95% code coverage
    • Built Pydantic data models for request/response validation
    """

    with patch("backend.main.GitHubClient", return_value=mock_client), \
         patch("backend.main.run_orchestrator", return_value=mock_orchestrator_output):

        client = TestClient(create_app())

        # First request: cache miss (full pipeline)
        response1 = client.post(
            "/analyze",
            json={"repo_url": "https://github.com/testuser/awesome-project"}
        )

        assert response1.status_code == 200
        data1 = response1.json()

        # Verify response structure matches AnalyzeResponse schema
        assert "repo_url" in data1
        assert "resume_markdown" in data1
        assert "bullets" in data1
        assert "skills" in data1

        assert data1["repo_url"] == "https://github.com/testuser/awesome-project"

        # Verify bullets were cleaned and structured
        assert isinstance(data1["bullets"], list)
        assert len(data1["bullets"]) > 0

        for bullet in data1["bullets"]:
            assert "text" in bullet
            assert "category" in bullet
            assert isinstance(bullet["text"], str)
            assert len(bullet["text"]) > 0

        # Verify skills were generated
        assert isinstance(data1["skills"], list)
        assert len(data1["skills"]) > 0

        for skill in data1["skills"]:
            assert "skill" in skill
            assert "score" in skill
            assert "rationale" in skill
            assert 0 <= skill["score"] <= 100

        # Verify resume markdown was generated
        assert isinstance(data1["resume_markdown"], str)
        assert len(data1["resume_markdown"]) > 0
        assert "Technical Resume" in data1["resume_markdown"]

        # Verify external services were called
        assert mock_client.get_repo_meta.call_count == 1
        assert mock_client.get_file_tree.call_count == 1

        # Second request: cache hit (should NOT call external services again)
        response2 = client.post(
            "/analyze",
            json={"repo_url": "https://github.com/testuser/awesome-project"}
        )

        assert response2.status_code == 200
        data2 = response2.json()

        # Data should be identical except for share_id (Phase 60: each has unique share_id)
        assert data2["repo_url"] == data1["repo_url"]
        assert data2["resume_markdown"] == data1["resume_markdown"]
        assert data2["bullets"] == data1["bullets"]
        assert data2["skills"] == data1["skills"]
        assert data2["chart_data"] == data1["chart_data"]
        assert data2["skill_tree"] == data1["skill_tree"]

        # Both should have share_ids (may be different)
        assert "share_id" in data1
        assert "share_id" in data2
        assert isinstance(data1["share_id"], str)
        assert isinstance(data2["share_id"], str)

        # Verify external services were NOT called again
        assert mock_client.get_repo_meta.call_count == 1  # Still 1, not 2
        assert mock_client.get_file_tree.call_count == 1  # Still 1, not 2


def test_analyze_endpoint_invalid_url():
    """Test POST /analyze with invalid URL returns 422 validation error."""
    client = TestClient(create_app())

    response = client.post(
        "/analyze",
        json={"repo_url": "not-a-valid-github-url"}
    )

    assert response.status_code == 422  # Pydantic validation error


def test_analyze_endpoint_github_api_error(monkeypatch, tmp_path):
    """Test POST /analyze handles GitHub API errors gracefully."""
    db_path = str(tmp_path / "test_github_error.db")

    mock_settings = MagicMock()
    mock_settings.db_path = db_path
    mock_settings.github_token = "test_token"
    monkeypatch.setattr("backend.main.settings", mock_settings)

    # Mock GitHub client to raise an error
    mock_client = MagicMock()
    mock_client.get_repo_meta.side_effect = Exception("Repository not found")

    with patch("backend.main.GitHubClient", return_value=mock_client):
        client = TestClient(create_app(), raise_server_exceptions=False)

        response = client.post(
            "/analyze",
            json={"repo_url": "https://github.com/nonexistent/repo"}
        )

        assert response.status_code == 400
        data = response.json()
        assert "detail" in data
        assert "Failed to fetch repository data" in data["detail"]


def test_analyze_endpoint_orchestrator_error(monkeypatch, tmp_path):
    """Test POST /analyze handles orchestrator failures gracefully."""
    db_path = str(tmp_path / "test_orchestrator_error.db")

    mock_settings = MagicMock()
    mock_settings.db_path = db_path
    mock_settings.github_token = "test_token"
    monkeypatch.setattr("backend.main.settings", mock_settings)

    # Mock GitHub client to succeed
    mock_meta = {
        "owner": "testuser",
        "repo": "project",
        "description": "Test",
        "stars": 10,
        "primary_language": "Python",
        "default_branch": "main",
    }

    mock_tree = ["README.md", "main.py"]

    mock_client = MagicMock()
    mock_client.get_repo_meta.return_value = mock_meta
    mock_client.get_file_tree.return_value = mock_tree

    # Mock orchestrator to raise an error
    with patch("backend.main.GitHubClient", return_value=mock_client), \
         patch("backend.main.run_orchestrator", side_effect=RuntimeError("API timeout")):

        client = TestClient(create_app(), raise_server_exceptions=False)

        response = client.post(
            "/analyze",
            json={"repo_url": "https://github.com/testuser/project"}
        )

        assert response.status_code == 500
        data = response.json()
        assert "detail" in data
        assert "AI agent orchestration failed" in data["detail"]


def test_analyze_endpoint_bullet_cleaning_and_verification(monkeypatch, tmp_path):
    """
    Test POST /analyze properly cleans bullets and verifies grounding.

    Verifies that:
    1. Conversational filler is removed
    2. Bullets are deduplicated
    3. Ungrounded bullets (mentioning undetected tech) are filtered out
    """
    db_path = str(tmp_path / "test_cleaning.db")

    mock_settings = MagicMock()
    mock_settings.db_path = db_path
    mock_settings.github_token = "test_token"
    monkeypatch.setattr("backend.main.settings", mock_settings)

    # Mock GitHub client
    mock_meta = {
        "owner": "jsdev",
        "repo": "react-app",
        "description": "React application",
        "stars": 50,
        "primary_language": "JavaScript",
        "default_branch": "main",
    }

    mock_tree = ["package.json", "src/App.jsx", "src/index.js"]

    mock_package_json = """{
        "dependencies": {
            "react": "^18.0.0",
            "react-dom": "^18.0.0"
        }
    }"""

    mock_client = MagicMock()
    mock_client.get_repo_meta.return_value = mock_meta
    mock_client.get_file_tree.return_value = mock_tree
    mock_client.get_file.return_value = mock_package_json

    # Mock orchestrator with messy output including ungrounded tech
    mock_orchestrator_output = """
    Here are your bullets:

    • Built React application with modern hooks
    • Built React application with modern hooks
    • Deployed to Kubernetes cluster with auto-scaling
    • Implemented state management with React Context

    Let me know if you need more!
    """

    with patch("backend.main.GitHubClient", return_value=mock_client), \
         patch("backend.main.run_orchestrator", return_value=mock_orchestrator_output):

        client = TestClient(create_app())

        response = client.post(
            "/analyze",
            json={"repo_url": "https://github.com/jsdev/react-app"}
        )

        assert response.status_code == 200
        data = response.json()

        # Extract bullet texts
        bullet_texts = [b["text"] for b in data["bullets"]]

        # Verify deduplication (duplicate React bullet should appear only once)
        react_bullets = [b for b in bullet_texts if "React application" in b]
        assert len(react_bullets) == 1

        # Verify ungrounded bullet was filtered out (Kubernetes not detected)
        kubernetes_bullets = [b for b in bullet_texts if "Kubernetes" in b or "kubernetes" in b]
        assert len(kubernetes_bullets) == 0

        # Verify grounded bullets remain
        assert any("React" in b for b in bullet_texts)


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
