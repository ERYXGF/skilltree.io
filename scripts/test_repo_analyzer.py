"""Phases 16–18 — repo_analyzer dependency and language helpers."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.repo_analyzer import (  # noqa: E402
    build_repo_summary,
    language_breakdown,
    max_folder_depth,
    parse_js_deps,
    parse_python_deps,
)
from backend.models.schemas import RepoSummary  # noqa: E402

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


def test_build_repo_summary_with_fixture_data():
    """Phase 19: Test build_repo_summary with mocked fixture data."""
    meta = {
        "repo_url": "https://github.com/test-owner/test-repo",
        "owner": "test-owner",
        "repo": "test-repo",
        "description": "A test repository for Phase 19",
        "stars": 42,
        "primary_language": "Python",
    }

    tree = [
        "src/main.py",
        "src/utils.py",
        "src/components/Widget.tsx",
        "tests/test_main.py",
        "README.md",
        "package.json",
    ]

    deps = {
        "python": ["fastapi", "pydantic", "pytest"],
        "javascript": ["react", "typescript"],
    }

    langs = {
        "Python": 50.0,
        "TypeScript": 16.7,
        "Markdown": 16.7,
        "JSON": 16.6,
    }

    summary = build_repo_summary(meta, tree, deps, langs)

    # Verify all required keys are present
    assert "repo_url" in summary
    assert "owner" in summary
    assert "repo" in summary
    assert "description" in summary
    assert "stars" in summary
    assert "primary_language" in summary
    assert "languages" in summary
    assert "dependencies" in summary
    assert "file_tree" in summary
    assert "file_count" in summary
    assert "top_level_dirs" in summary

    # Verify values
    assert summary["repo_url"] == "https://github.com/test-owner/test-repo"
    assert summary["owner"] == "test-owner"
    assert summary["repo"] == "test-repo"
    assert summary["description"] == "A test repository for Phase 19"
    assert summary["stars"] == 42
    assert summary["primary_language"] == "Python"
    assert summary["languages"] == langs
    assert summary["dependencies"] == deps
    assert summary["file_tree"] == tree
    assert summary["file_count"] == 6
    assert sorted(summary["top_level_dirs"]) == ["src", "tests"]


def test_build_repo_summary_validates_with_pydantic():
    """Phase 19: Round-trip validation through RepoSummary Pydantic model."""
    meta = {
        "repo_url": "https://github.com/owner/repo",
        "owner": "owner",
        "repo": "repo",
        "description": "Test description",
        "stars": 100,
        "primary_language": "JavaScript",
    }

    tree = ["index.js", "lib/utils.js", "test/test.js"]
    deps = {"javascript": ["express", "lodash"]}
    langs = {"JavaScript": 100.0}

    summary_dict = build_repo_summary(meta, tree, deps, langs)

    # This should not raise a validation error
    validated = RepoSummary.model_validate(summary_dict)

    # Verify the model can be serialized to JSON
    json_data = validated.model_dump()
    assert json_data["repo_url"] == "https://github.com/owner/repo"
    assert json_data["file_count"] == 3
    assert json_data["top_level_dirs"] == ["lib", "test"]


def test_build_repo_summary_handles_empty_tree():
    """Phase 19: Test build_repo_summary with empty file tree."""
    meta = {
        "repo_url": "https://github.com/empty/repo",
        "owner": "empty",
        "repo": "repo",
        "description": "",
        "stars": 0,
        "primary_language": "",
    }

    summary = build_repo_summary(meta, [], {}, {})

    assert summary["file_count"] == 0
    assert summary["top_level_dirs"] == []
    assert summary["file_tree"] == []

    # Should still validate
    validated = RepoSummary.model_validate(summary)
    assert validated.file_count == 0


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
