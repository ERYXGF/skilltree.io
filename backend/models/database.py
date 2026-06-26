"""SQLite cache for analysis results and shareable links."""

import json
import random
import sqlite3
import string
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
        # Phase 60: Shareable results table
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS shared_results (
                share_id TEXT PRIMARY KEY,
                payload TEXT NOT NULL,
                view_count INTEGER NOT NULL DEFAULT 0,
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


# Phase 60: Shareable result link functions

def generate_share_id(length: int = 8) -> str:
    """
    Generate a random alphanumeric share ID.

    Args:
        length: Length of the share ID (default: 8)

    Returns:
        Random alphanumeric string of specified length

    Example:
        >>> share_id = generate_share_id()
        >>> len(share_id)
        8
        >>> share_id.isalnum()
        True
    """
    chars = string.ascii_letters + string.digits
    return ''.join(random.choice(chars) for _ in range(length))


def save_shared_result(result_data: dict[str, Any], db_path: str = "data/database.db") -> str:
    """
    Save an analysis result with a unique share ID.

    Args:
        result_data: Complete analysis result dictionary
        db_path: Path to SQLite database

    Returns:
        Generated share ID (8 characters)

    Example:
        >>> data = {"repo_url": "https://github.com/user/repo", "skills": []}
        >>> share_id = save_shared_result(data)
        >>> len(share_id)
        8
    """
    init_db(db_path)

    # Generate unique share ID (retry if collision)
    max_retries = 10
    for _ in range(max_retries):
        share_id = generate_share_id()

        # Check if ID already exists
        with _connect(db_path) as conn:
            existing = conn.execute(
                "SELECT share_id FROM shared_results WHERE share_id = ?",
                (share_id,)
            ).fetchone()

            if existing is None:
                # ID is unique, save the result
                conn.execute(
                    """
                    INSERT INTO shared_results (share_id, payload)
                    VALUES (?, ?)
                    """,
                    (share_id, json.dumps(result_data))
                )
                conn.commit()
                return share_id

    # If we couldn't generate a unique ID after max_retries, raise error
    raise RuntimeError("Failed to generate unique share ID after multiple attempts")


def get_shared_result(share_id: str, db_path: str = "data/database.db") -> dict[str, Any] | None:
    """
    Retrieve a shared analysis result by its share ID.

    Also increments the view counter for analytics.

    Args:
        share_id: The 8-character share ID
        db_path: Path to SQLite database

    Returns:
        Analysis result dictionary, or None if not found

    Example:
        >>> result = get_shared_result("abc12345")
        >>> result is None or "repo_url" in result
        True
    """
    init_db(db_path)

    with _connect(db_path) as conn:
        # Fetch the result
        row = conn.execute(
            "SELECT payload FROM shared_results WHERE share_id = ?",
            (share_id,)
        ).fetchone()

        if row is None:
            return None

        # Increment view counter
        conn.execute(
            """
            UPDATE shared_results
            SET view_count = view_count + 1
            WHERE share_id = ?
            """,
            (share_id,)
        )
        conn.commit()

        return json.loads(row["payload"])
