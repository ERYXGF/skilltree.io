"""Phase 4 — config loader tests."""

import os
import sys
from pathlib import Path

import pytest
from pydantic import ValidationError

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.config import Settings  # noqa: E402


def test_settings_load_from_env(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    env_file = tmp_path / ".env"
    env_file.write_text(
        "\n".join(
            [
                "ANTHROPIC_API_KEY=test-key-123",
                "GITHUB_TOKEN=ghp_test",
                "MODEL_NAME=claude-test",
                "DB_PATH=custom.db",
            ]
        ),
        encoding="utf-8",
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key-123")
    monkeypatch.setenv("GITHUB_TOKEN", "ghp_test")
    monkeypatch.setenv("MODEL_NAME", "claude-test")
    monkeypatch.setenv("DB_PATH", "custom.db")

    settings = Settings(_env_file=str(env_file))
    assert settings.anthropic_api_key == "test-key-123"
    assert settings.github_token == "ghp_test"
    assert settings.model_name == "claude-test"
    assert settings.db_path == "custom.db"


def test_missing_required_key_raises_clearly(monkeypatch):
    for key in list(os.environ):
        if key.startswith(("ANTHROPIC_", "GITHUB_", "MODEL_", "DB_")):
            monkeypatch.delenv(key, raising=False)
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)

    with pytest.raises(ValidationError) as exc_info:
        Settings(_env_file=None)

    errors = exc_info.value.errors()
    fields = {err["loc"][0] for err in errors}
    assert "anthropic_api_key" in fields


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
