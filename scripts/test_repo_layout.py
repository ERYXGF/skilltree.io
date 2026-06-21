"""Phase 1 — verify project skeleton directories exist."""

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

EXPECTED_DIRS = [
    "backend",
    "backend/core",
    "backend/agent",
    "backend/models",
    "backend/data",
    "scripts",
    "frontend",
    "frontend/src",
    "frontend/src/components",
    "frontend/src/styles",
]

EXPECTED_FILES = [
    "README.md",
    ".gitignore",
    ".env.example",
]


def test_expected_directories_exist():
    missing = [d for d in EXPECTED_DIRS if not (ROOT / d).is_dir()]
    assert not missing, f"Missing directories: {missing}"


def test_expected_root_files_exist():
    missing = [f for f in EXPECTED_FILES if not (ROOT / f).is_file()]
    assert not missing, f"Missing files: {missing}"


def test_env_is_gitignored():
  gitignore = (ROOT / ".gitignore").read_text(encoding="utf-8")
  assert ".env" in gitignore, ".env must be listed in .gitignore"


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
