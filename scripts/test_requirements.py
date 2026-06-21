"""Phase 2 — verify requirements.txt lists pinned core packages."""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REQUIREMENTS = ROOT / "requirements.txt"

CORE_PACKAGES = [
    "fastapi",
    "uvicorn",
    "pydantic",
    "pydantic-settings",
    "anthropic",
    "httpx",
    "python-dotenv",
    "pytest",
]

PIN_PATTERN = re.compile(r"^([a-zA-Z0-9_-]+)==[\d.]+(?:[a-zA-Z0-9_.-]*)?$")


def _parse_requirements() -> dict[str, str]:
    lines = REQUIREMENTS.read_text(encoding="utf-8").splitlines()
    parsed: dict[str, str] = {}
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        assert PIN_PATTERN.match(line), f"Package must be pinned with ==: {line}"
        name, version = line.split("==", 1)
        parsed[name.lower()] = version
    return parsed


def test_requirements_file_exists():
    assert REQUIREMENTS.is_file()


def test_core_packages_pinned():
    parsed = _parse_requirements()
    missing = [pkg for pkg in CORE_PACKAGES if pkg not in parsed]
    assert not missing, f"Missing core packages: {missing}"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
