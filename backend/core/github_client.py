"""GitHub REST API client for repository metadata, file trees, and contents."""

from __future__ import annotations

import base64
from typing import Any

import httpx

from backend.core.logging_config import get_logger

logger = get_logger("github_client")

GITHUB_API_BASE = "https://api.github.com"


class GitHubClientError(Exception):
    """Raised when a GitHub API request fails."""


class GitHubRateLimitError(GitHubClientError):
    """Raised when GitHub rate limits the request or returns 403."""


class GitHubClient:
    def __init__(self, token: str = "") -> None:
        self.token = token
        self._client = httpx.Client(base_url=GITHUB_API_BASE, timeout=30.0)

    def _headers(self) -> dict[str, str]:
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    def _request(self, method: str, url: str, **kwargs: Any) -> Any:
        try:
            response = self._client.request(method, url, headers=self._headers(), **kwargs)
        except httpx.HTTPError as exc:
            logger.error("GitHub request failed: %s %s — %s", method, url, exc)
            raise GitHubClientError(
                f"Could not reach GitHub ({exc}). Check your network connection."
            ) from exc

        if response.status_code == 403:
            body = response.text.lower()
            remaining = response.headers.get("x-ratelimit-remaining", "")
            if remaining == "0" or "rate limit" in body:
                logger.error("GitHub rate limit exceeded (403) for %s", url)
                raise GitHubRateLimitError(
                    "GitHub API rate limit exceeded. Add a GITHUB_TOKEN to your .env "
                    "or wait before retrying."
                )
            logger.error("GitHub access forbidden (403) for %s", url)
            raise GitHubRateLimitError(
                "GitHub denied access (403). Check your GITHUB_TOKEN permissions "
                "or repository visibility."
            )

        if response.status_code == 404:
            logger.error("GitHub resource not found: %s", url)
            raise GitHubClientError(f"Repository or file not found: {url}")

        if not response.is_success:
            logger.error(
                "GitHub API error %s for %s: %s",
                response.status_code,
                url,
                response.text[:200],
            )
            raise GitHubClientError(
                f"GitHub API returned {response.status_code}. Please try again later."
            )

        return response.json()

    def get_repo_meta(self, owner: str, repo: str) -> dict[str, Any]:
        data = self._request("GET", f"/repos/{owner}/{repo}")
        return {
            "owner": data.get("owner", {}).get("login", owner),
            "repo": data.get("name", repo),
            "description": data.get("description") or "",
            "stars": data.get("stargazers_count", 0),
            "primary_language": data.get("language"),
            "default_branch": data.get("default_branch", "main"),
        }

    def get_file_tree(self, owner: str, repo: str) -> list[str]:
        meta = self.get_repo_meta(owner, repo)
        branch = meta["default_branch"]

        branch_data = self._request("GET", f"/repos/{owner}/{repo}/branches/{branch}")
        commit_sha = branch_data["commit"]["sha"]

        commit_data = self._request("GET", f"/repos/{owner}/{repo}/git/commits/{commit_sha}")
        tree_sha = commit_data["tree"]["sha"]

        tree_data = self._request(
            "GET",
            f"/repos/{owner}/{repo}/git/trees/{tree_sha}",
            params={"recursive": "1"},
        )

        return [
            item["path"]
            for item in tree_data.get("tree", [])
            if item.get("type") == "blob"
        ]

    def get_file(self, owner: str, repo: str, path: str) -> str:
        normalized = path.lstrip("/")
        data = self._request("GET", f"/repos/{owner}/{repo}/contents/{normalized}")

        if isinstance(data, list):
            raise GitHubClientError(f"Path '{path}' is a directory, not a file.")

        content = data.get("content", "")
        encoding = data.get("encoding", "base64")

        if encoding == "base64":
            return base64.b64decode(content).decode("utf-8")

        return content
