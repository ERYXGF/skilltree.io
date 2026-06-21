"""SQLite cache for analysis results."""

import json
import sqlite3
from pathlib import Path
from typing import Any


def _connect(db_path: str) -> sqlite3.Connection:
    Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: str) -> None:
    with _connect(db_path) as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS analysis_cache (
                repo_url TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        conn.commit()


def cache_get(db_path: str, repo_url: str) -> dict[str, Any] | None:
    init_db(db_path)
    with _connect(db_path) as conn:
        row = conn.execute(
            "SELECT payload FROM analysis_cache WHERE repo_url = ?",
            (repo_url,),
        ).fetchone()
    if row is None:
        return None
    return json.loads(row["payload"])


def cache_set(db_path: str, repo_url: str, payload: dict[str, Any]) -> None:
    init_db(db_path)
    with _connect(db_path) as conn:
        conn.execute(
            """
            INSERT INTO analysis_cache (repo_url, payload)
            VALUES (?, ?)
            ON CONFLICT(repo_url) DO UPDATE SET
                payload = excluded.payload,
                created_at = CURRENT_TIMESTAMP
            """,
            (repo_url, json.dumps(payload)),
        )
        conn.commit()
