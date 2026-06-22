"""Phase 11 — GitHub URL parser tests."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.url_parser import parse_github_url  # noqa: E402


def test_parse_standard_https_url():
    assert parse_github_url("https://github.com/octocat/Hello-World") == (
        "octocat",
        "Hello-World",
    )


def test_parse_trailing_slash():
    assert parse_github_url("https://github.com/octocat/Hello-World/") == (
        "octocat",
        "Hello-World",
    )


def test_parse_git_suffix():
    assert parse_github_url("https://github.com/octocat/Hello-World.git") == (
        "octocat",
        "Hello-World",
    )


def test_parse_branch_url():
    assert parse_github_url(
        "https://github.com/octocat/Hello-World/tree/main"
    ) == ("octocat", "Hello-World")


def test_parse_http_with_www():
    assert parse_github_url("http://www.github.com/octocat/Hello-World") == (
        "octocat",
        "Hello-World",
    )


def test_rejects_gitlab_url():
    with pytest.raises(ValueError, match="gitlab.com"):
        parse_github_url("https://gitlab.com/user/repo")


def test_rejects_single_segment():
    with pytest.raises(ValueError, match="owner and repository"):
        parse_github_url("https://github.com/octocat")


def test_rejects_empty_string():
    with pytest.raises(ValueError, match="empty"):
        parse_github_url("")


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
