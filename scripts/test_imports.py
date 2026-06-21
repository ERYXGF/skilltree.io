"""Phase 3 — verify backend packages import cleanly."""

import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

PACKAGES = [
    "backend",
    "backend.core",
    "backend.agent",
    "backend.models",
]


def test_packages_import():
    for package in PACKAGES:
        importlib.import_module(package)


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
