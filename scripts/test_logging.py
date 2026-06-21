"""Phase 5 — logging setup tests."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.logging_config import get_logger  # noqa: E402


def test_logger_emits_structured_record(capsys):
    logger = get_logger("test_module")
    logger.info("structured test message")

    captured = capsys.readouterr().out
    assert "INFO" in captured
    assert "skilltree.test_module" in captured
    assert "structured test message" in captured


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
