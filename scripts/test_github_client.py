"""Phases 12–15 — GitHub client tests (all httpx responses mocked)."""

import base64
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import httpx
import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.config import Settings  # noqa: E402
from backend.core.github_client import (  # noqa: E402
    GitHubClient,
    GitHubClientError,
    GitHubRateLimitError,
)


def _mock_response(
    *,
    status_code: int = 200,
    json_data: dict | list | None = None,
    text: str = "",
    headers: dict | None = None,
) -> MagicMock:
    response = MagicMock()
    response.status_code = status_code
    response.is_success = 200 <= status_code < 300
    response.json.return_value = json_data if json_data is not None else {}
    response.text = text or str(json_data)
    response.headers = headers or {}
    return response


# Phase 12 — metadata
def test_get_repo_meta_parsed_fields():
    repo_payload = {
        "owner": {"login": "octocat"},
        "name": "Hello-World",
        "description": "My first repository on GitHub!",
        "stargazers_count": 42,
        "language": "Python",
        "default_branch": "main",
    }

    with patch("backend.core.github_client.httpx.Client") as mock_client_cls:
        mock_client_cls.return_value.request.return_value = _mock_response(json_data=repo_payload)
        client = GitHubClient(token="ghp_test")
        meta = client.get_repo_meta("octocat", "Hello-World")

    assert meta == {
        "owner": "octocat",
        "repo": "Hello-World",
        "description": "My first repository on GitHub!",
        "stars": 42,
        "primary_language": "Python",
        "default_branch": "main",
    }


def test_token_forwarded_from_settings():
    with patch("backend.core.github_client.httpx.Client") as mock_client_cls:
        mock_request = mock_client_cls.return_value.request
        mock_request.return_value = _mock_response(
            json_data={
                "owner": {"login": "acme"},
                "name": "demo",
                "description": "",
                "stargazers_count": 0,
                "language": None,
                "default_branch": "main",
            }
        )

        settings = Settings(
            _env_file=None,
            anthropic_api_key="test-key",
            github_token="ghp_from_settings",
        )
        client = GitHubClient(settings.github_token)
        client.get_repo_meta("acme", "demo")

    _, kwargs = mock_request.call_args
    assert kwargs["headers"]["Authorization"] == "Bearer ghp_from_settings"


# Phase 13 — file tree
def test_get_file_tree_flat_paths():
    repo_payload = {
        "owner": {"login": "acme"},
        "name": "app",
        "description": "",
        "stargazers_count": 1,
        "language": "Python",
        "default_branch": "main",
    }
    branch_payload = {"commit": {"sha": "commit123"}}
    commit_payload = {"tree": {"sha": "tree456"}}
    tree_payload = {
        "tree": [
            {"path": "README.md", "type": "blob"},
            {"path": "src", "type": "tree"},
            {"path": "src/main.py", "type": "blob"},
            {"path": "requirements.txt", "type": "blob"},
        ]
    }

    with patch("backend.core.github_client.httpx.Client") as mock_client_cls:
        mock_client_cls.return_value.request.side_effect = [
            _mock_response(json_data=repo_payload),
            _mock_response(json_data=branch_payload),
            _mock_response(json_data=commit_payload),
            _mock_response(json_data=tree_payload),
        ]
        client = GitHubClient()
        paths = client.get_file_tree("acme", "app")

    assert paths == ["README.md", "src/main.py", "requirements.txt"]


# Phase 14 — file contents
@pytest.mark.parametrize(
    "path,plain_text",
    [
        ("requirements.txt", "fastapi==0.115.6\nhttpx==0.28.1\n"),
        ("package.json", '{"name": "demo", "dependencies": {}}'),
        ("README.md", "# Demo\n\nA sample project."),
        ("pyproject.toml", '[project]\nname = "demo"\n'),
    ],
)
def test_get_file_decodes_base64(path, plain_text):
    encoded = base64.b64encode(plain_text.encode("utf-8")).decode("ascii")
    content_payload = {
        "content": encoded,
        "encoding": "base64",
    }

    with patch("backend.core.github_client.httpx.Client") as mock_client_cls:
        mock_client_cls.return_value.request.return_value = _mock_response(
            json_data=content_payload
        )
        client = GitHubClient()
        text = client.get_file("acme", "app", path)

    assert text == plain_text


# Phase 15 — rate limit + auth
def test_rate_limit_raises_graceful_error_not_raw_httpx():
    with patch("backend.core.github_client.httpx.Client") as mock_client_cls:
        mock_client_cls.return_value.request.return_value = _mock_response(
            status_code=403,
            json_data={"message": "API rate limit exceeded"},
            text='{"message": "API rate limit exceeded"}',
            headers={"x-ratelimit-remaining": "0"},
        )
        client = GitHubClient()

        with pytest.raises(GitHubRateLimitError) as exc_info:
            client.get_repo_meta("acme", "app")

    message = str(exc_info.value).lower()
    assert "rate limit" in message
    assert "token" in message


def test_network_error_raises_client_error_not_raw_httpx():
    with patch("backend.core.github_client.httpx.Client") as mock_client_cls:
        mock_client_cls.return_value.request.side_effect = httpx.ConnectError("connection refused")
        client = GitHubClient()

        with pytest.raises(GitHubClientError) as exc_info:
            client.get_repo_meta("acme", "app")

        assert not isinstance(exc_info.value, httpx.HTTPError)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
