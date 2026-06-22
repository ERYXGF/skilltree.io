"""Deterministic repository analysis helpers.

Phases 16–18: dependency parsing and language/structure signals.

``max_folder_depth(file_tree)`` returns the deepest directory nesting among
paths in *file_tree* (0 for flat files at repo root). Use alongside
``language_breakdown`` when summarizing repo structure.
"""

from __future__ import annotations

import json
import re
import tomllib
from pathlib import PurePosixPath
from typing import Any

_VERSION_OPS = ("===", "==", ">=", "<=", "!=", "~=", ">", "<")
_PKG_HEAD_RE = re.compile(
    r"^([a-zA-Z0-9][\w.-]*)(?:\[[^\]]*\])?",
    re.ASCII,
)

_EXTENSION_TO_LANGUAGE: dict[str, str] = {
    ".py": "Python",
    ".pyw": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".mjs": "JavaScript",
    ".cjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".go": "Go",
    ".rs": "Rust",
    ".rb": "Ruby",
    ".php": "PHP",
    ".c": "C",
    ".h": "C",
    ".cpp": "C++",
    ".cc": "C++",
    ".hpp": "C++",
    ".cs": "C#",
    ".swift": "Swift",
    ".kt": "Kotlin",
    ".scala": "Scala",
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".sass": "SCSS",
    ".less": "LESS",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".toml": "TOML",
    ".xml": "XML",
    ".sql": "SQL",
    ".sh": "Shell",
    ".bash": "Shell",
    ".zsh": "Shell",
    ".ps1": "PowerShell",
    ".vue": "Vue",
    ".svelte": "Svelte",
}


def _strip_inline_comment(line: str) -> str:
    for sep in (" #", "\t#"):
        if sep in line:
            return line.split(sep, 1)[0].strip()
    return line.strip()


def _normalize_requirement_token(token: str) -> str | None:
    token = _strip_inline_comment(token)
    if not token or token.startswith("#"):
        return None
    if token.startswith("-"):
        return None

    name_part = token.split(";", 1)[0].strip()
    match = _PKG_HEAD_RE.match(name_part)
    if not match:
        return None

    name = match.group(1).lower().replace("_", "-")
    return name


def _parse_requirements_lines(text: str) -> list[str]:
    deps: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith(("-r", "--requirement", "-e", "--editable")):
            continue
        normalized = _normalize_requirement_token(line)
        if normalized:
            deps.append(normalized)
    return deps


def _parse_pyproject_deps(text: str) -> list[str]:
    data = tomllib.loads(text)
    deps: list[str] = []

    project = data.get("project", {})
    for entry in project.get("dependencies", []):
        if isinstance(entry, str):
            normalized = _normalize_requirement_token(entry)
            if normalized:
                deps.append(normalized)

    optional = project.get("optional-dependencies", {})
    if isinstance(optional, dict):
        for group_deps in optional.values():
            if not isinstance(group_deps, list):
                continue
            for entry in group_deps:
                if isinstance(entry, str):
                    normalized = _normalize_requirement_token(entry)
                    if normalized:
                        deps.append(normalized)

    poetry = data.get("tool", {}).get("poetry", {})
    poetry_deps = poetry.get("dependencies", {})
    if isinstance(poetry_deps, dict):
        for name in poetry_deps:
            if name.lower() == "python":
                continue
            deps.append(name.lower().replace("_", "-"))

    return deps


def _looks_like_pyproject(text: str) -> bool:
    stripped = text.lstrip()
    return stripped.startswith("[") and (
        "[project]" in text or "[tool.poetry]" in text
    )


def parse_python_deps(text: str) -> list[str]:
    """Parse Python dependencies from requirements.txt or pyproject.toml text."""
    if _looks_like_pyproject(text):
        deps = _parse_pyproject_deps(text)
    else:
        deps = _parse_requirements_lines(text)

    return sorted(set(deps))


def parse_js_deps(package_json: dict[str, Any] | str) -> list[str]:
    """Parse JavaScript package names from a package.json object or JSON string."""
    if isinstance(package_json, str):
        data = json.loads(package_json)
    else:
        data = package_json

    names: set[str] = set()
    for section in ("dependencies", "devDependencies"):
        entries = data.get(section, {})
        if isinstance(entries, dict):
            names.update(entries.keys())

    return sorted(names)


def max_folder_depth(file_tree: list[str]) -> int:
    """Return the maximum directory nesting depth across *file_tree* paths."""
    if not file_tree:
        return 0

    depths: list[int] = []
    for path in file_tree:
        normalized = path.replace("\\", "/").strip("/")
        if not normalized:
            continue
        parts = [part for part in normalized.split("/") if part]
        depths.append(max(len(parts) - 1, 0))

    return max(depths) if depths else 0


def _language_counts(file_tree: list[str]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for path in file_tree:
        suffix = PurePosixPath(path.replace("\\", "/")).suffix.lower()
        language = _EXTENSION_TO_LANGUAGE.get(suffix, "Other")
        counts[language] = counts.get(language, 0) + 1
    return counts


def _to_percentages(counts: dict[str, int]) -> dict[str, float]:
    total = sum(counts.values())
    if total == 0:
        return {}

    raw = {language: (count / total) * 100 for language, count in counts.items()}
    rounded = {language: round(share, 1) for language, share in raw.items()}

    drift = round(100.0 - sum(rounded.values()), 1)
    if drift and rounded:
        largest = max(rounded, key=rounded.get)
        rounded[largest] = round(rounded[largest] + drift, 1)

    return rounded


def language_breakdown(file_tree: list[str]) -> dict[str, float]:
    """Map file extensions in *file_tree* to language percentage shares."""
    return _to_percentages(_language_counts(file_tree))


# Phase 19: build_repo_summary
