"""Phase 11 — GitHub URL parser tests."""

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.url_parser import parse_github_url  # noqa: E402


@pytest.mark.parametrize(
    ("url", "expected"),
    [
        ("https://github.com/octocat/Hello-World", ("octocat", "Hello-World")),
        ("https://github.com/octocat/Hello-World/", ("octocat", "Hello-World")),
        ("https://github.com/octocat/Hello-World.git", ("octocat", "Hello-World")),
        ("http://github.com/octocat/Hello-World", ("octocat", "Hello-World")),
        ("https://www.github.com/octocat/Hello-World", ("octocat", "Hello-World")),
        (
            "https://github.com/octocat/Hello-World/tree/main",
            ("octocat", "Hello-World"),
        ),
        (
            "https://github.com/octocat/Hello-World/blob/main/README.md",
            ("octocat", "Hello-World"),
        ),
    ],
)
def test_parse_github_url_valid(url, expected):
    assert parse_github_url(url) == expected


@pytest.mark.parametrize(
    "url",
    [
        "https://gitlab.com/user/repo",
        "https://github.com/octocat",
        "",
        "   ",
    ],
)
def test_parse_github_url_invalid(url):
    with pytest.raises(ValueError):
        parse_github_url(url)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
