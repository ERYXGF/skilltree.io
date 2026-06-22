"""Parse GitHub repository URLs into owner and repository name."""

import re

_GITHUB_REPO_URL = re.compile(
    r"^https?://(?:www\.)?github\.com/(?P<owner>[\w.-]+)/(?P<repo>[\w.-]+?)(?:\.git)?/?(?:/.*)?$",
    re.IGNORECASE,
)


def parse_github_url(url: str) -> tuple[str, str]:
    """Return ``(owner, repo)`` from a public GitHub repository URL."""
    url = url.strip()
    if not url:
        raise ValueError("URL cannot be empty")

    if "gitlab.com" in url.lower():
        raise ValueError("URL must be a github.com repository URL, not gitlab.com")

    match = _GITHUB_REPO_URL.match(url)
    if not match:
        if re.match(r"^https?://(?:www\.)?github\.com/[\w.-]+/?$", url, re.IGNORECASE):
            raise ValueError("GitHub URL must include owner and repository name")
        raise ValueError(f"Invalid GitHub repository URL: {url}")

    return match.group("owner"), match.group("repo")
