"""Parse GitHub repository URLs into owner and repository name."""

import re
from urllib.parse import urlparse

_OWNER_REPO_PATH = re.compile(
    r"^/([^/]+)/([^/]+?)(?:\.git)?(?:/.*)?/?$",
    re.IGNORECASE,
)


def parse_github_url(url: str) -> tuple[str, str]:
    """Extract ``(owner, repo)`` from a GitHub repository URL.

    Handles http/https, optional www., trailing slashes, ``.git`` suffix,
    and extra path segments (branches, blobs, etc.).

    Raises:
        ValueError: If the URL is empty, not github.com, or missing owner/repo.
    """
    if not url or not url.strip():
        raise ValueError("URL must not be empty")

    normalized = url.strip()
    if "://" not in normalized:
        normalized = f"https://{normalized}"

    parsed = urlparse(normalized)

    if parsed.scheme.lower() not in ("http", "https"):
        raise ValueError(f"Invalid GitHub URL: unsupported scheme '{parsed.scheme}'")

    host = parsed.netloc.lower()
    if host.startswith("www."):
        host = host[4:]

    if host != "github.com":
        raise ValueError("URL must be a github.com repository link")

    match = _OWNER_REPO_PATH.match(parsed.path)
    if not match:
        raise ValueError("URL must include owner and repository name")

    owner, repo = match.group(1), match.group(2)
    return owner, repo
