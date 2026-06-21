"""Phase 7 — SQLite cache layer tests."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.models.database import cache_get, cache_set, init_db  # noqa: E402


def test_cache_round_trip(tmp_path):
    db_path = str(tmp_path / "test.db")
    repo_url = "https://github.com/octocat/Hello-World"
    payload = {"summary": "test repo", "languages": ["Python"]}

    init_db(db_path)
    assert cache_get(db_path, repo_url) is None

    cache_set(db_path, repo_url, payload)
    cached = cache_get(db_path, repo_url)
    assert cached == payload


def test_cache_overwrites_existing_entry(tmp_path):
    db_path = str(tmp_path / "test.db")
    repo_url = "https://github.com/octocat/Hello-World"

    cache_set(db_path, repo_url, {"version": 1})
    cache_set(db_path, repo_url, {"version": 2})
    assert cache_get(db_path, repo_url) == {"version": 2}


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
