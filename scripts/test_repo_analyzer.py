"""Phases 16–18 — repo_analyzer dependency and language helpers."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.repo_analyzer import (  # noqa: E402
    language_breakdown,
    max_folder_depth,
    parse_js_deps,
    parse_python_deps,
)

SAMPLE_REQUIREMENTS = """
# core stack
fastapi==0.110.0
uvicorn[standard]>=0.27.0
-r other.txt
-e git+https://github.com/org/pkg.git#egg=pkg
pandas[extras]==2.0.1
numpy>=1.24
"""

SAMPLE_PYPROJECT = """
[project]
name = "demo"
dependencies = [
  "requests>=2.31",
  "pydantic[email]==2.6.0",
  "httpx",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff"]

[tool.poetry.dependencies]
python = "^3.11"
black = "^24.0"
"""

SAMPLE_PACKAGE_JSON = {
    "name": "demo-app",
    "dependencies": {
        "react": "^18.2.0",
        "lodash": "^4.17.21",
    },
    "devDependencies": {
        "eslint": "^8.0.0",
        "react": "^18.2.0",
        "typescript": "^5.0.0",
    },
}

SAMPLE_FILE_TREE = [
    "src/main.py",
    "src/utils.py",
    "src/app.js",
    "src/app.test.js",
    "src/components/Widget.tsx",
    "README.md",
    "package.json",
    "unknown-file",
]


def test_parse_python_deps_from_requirements():
    deps = parse_python_deps(SAMPLE_REQUIREMENTS)
    assert deps == ["fastapi", "numpy", "pandas", "uvicorn"]


def test_parse_python_deps_from_pyproject():
    deps = parse_python_deps(SAMPLE_PYPROJECT)
    assert deps == ["black", "httpx", "pydantic", "pytest", "requests", "ruff"]


def test_parse_js_deps_merges_and_dedupes():
    deps = parse_js_deps(SAMPLE_PACKAGE_JSON)
    assert deps == ["eslint", "lodash", "react", "typescript"]


def test_parse_js_deps_accepts_json_string():
    import json

    deps = parse_js_deps(json.dumps(SAMPLE_PACKAGE_JSON))
    assert deps == ["eslint", "lodash", "react", "typescript"]


def test_language_breakdown_sums_to_one_hundred():
    breakdown = language_breakdown(SAMPLE_FILE_TREE)
    total = sum(breakdown.values())
    assert abs(total - 100.0) <= 0.1
    assert breakdown["Python"] == 25.0
    assert breakdown["JavaScript"] == 25.0
    assert breakdown["TypeScript"] == 12.5
    assert breakdown["Markdown"] == 12.5
    assert breakdown["JSON"] == 12.5
    assert breakdown["Other"] == 12.5


def test_max_folder_depth():
    assert max_folder_depth(SAMPLE_FILE_TREE) == 2
    assert max_folder_depth(["README.md", "app.py"]) == 0
    assert max_folder_depth([]) == 0


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
