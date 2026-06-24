"""Deterministic proficiency scoring for detected technologies.

Phase 33: Proficiency scorer

Provides a purely mathematical, deterministic scoring algorithm that evaluates
technology proficiency based on concrete repository signals without any LLM calls.
"""

from __future__ import annotations

from typing import Any


# Technology-to-extension mapping for file count scoring
_TECH_EXTENSIONS: dict[str, list[str]] = {
    "python": [".py", ".pyw"],
    "javascript": [".js", ".jsx", ".mjs", ".cjs"],
    "typescript": [".ts", ".tsx"],
    "react": [".jsx", ".tsx"],
    "vue": [".vue"],
    "angular": [".ts", ".html"],
    "java": [".java"],
    "go": [".go"],
    "rust": [".rs"],
    "ruby": [".rb"],
    "php": [".php"],
    "c": [".c", ".h"],
    "c++": [".cpp", ".cc", ".hpp"],
    "c#": [".cs"],
    "swift": [".swift"],
    "kotlin": [".kt"],
    "scala": [".scala"],
    "html": [".html", ".htm"],
    "css": [".css"],
    "scss": [".scss", ".sass"],
    "sql": [".sql"],
    "shell": [".sh", ".bash", ".zsh"],
}


def _count_matching_files(tech: str, file_tree: list[str]) -> int:
    """Count files in the repository that match the technology's extensions."""
    tech_lower = tech.lower()
    extensions = _TECH_EXTENSIONS.get(tech_lower, [])

    if not extensions:
        return 0

    count = 0
    for path in file_tree:
        path_lower = path.lower()
        for ext in extensions:
            if path_lower.endswith(ext):
                count += 1
                break

    return count


def _is_in_dependencies(tech: str, dependencies: dict[str, list[str]]) -> bool:
    """Check if technology appears in any dependency manifest."""
    tech_lower = tech.lower().strip()

    for ecosystem, packages in dependencies.items():
        if not isinstance(packages, list):
            continue

        for package in packages:
            if isinstance(package, str) and package.lower().strip() == tech_lower:
                return True

    return False


def _calculate_complexity_score(repo_summary: dict[str, Any]) -> int:
    """Calculate repository complexity score based on file count and structure."""
    file_count = repo_summary.get("file_count", 0)
    top_level_dirs = repo_summary.get("top_level_dirs", [])

    # File count scoring (0-10 points)
    if file_count >= 200:
        file_score = 10
    elif file_count >= 100:
        file_score = 7
    elif file_count >= 50:
        file_score = 5
    elif file_count >= 20:
        file_score = 3
    else:
        file_score = 1

    # Directory structure scoring (0-5 points)
    dir_count = len(top_level_dirs) if isinstance(top_level_dirs, list) else 0
    if dir_count >= 10:
        dir_score = 5
    elif dir_count >= 5:
        dir_score = 3
    elif dir_count >= 3:
        dir_score = 2
    else:
        dir_score = 1

    return file_score + dir_score


def _get_language_percentage(tech: str, languages: dict[str, float]) -> float:
    """Get the percentage share of a language if the tech matches a language."""
    tech_lower = tech.lower()

    # Map technologies to language names
    tech_to_lang = {
        "python": "python",
        "javascript": "javascript",
        "typescript": "typescript",
        "java": "java",
        "go": "go",
        "rust": "rust",
        "ruby": "ruby",
        "php": "php",
        "c": "c",
        "c++": "c++",
        "c#": "c#",
        "swift": "swift",
        "kotlin": "kotlin",
        "scala": "scala",
    }

    lang_name = tech_to_lang.get(tech_lower)
    if not lang_name:
        return 0.0

    # Case-insensitive language lookup
    for lang, percentage in languages.items():
        if lang.lower() == lang_name:
            return percentage

    return 0.0


def score_skill(tech: str, repo_summary: dict[str, Any]) -> dict[str, Any]:
    """Calculate a deterministic proficiency score for a technology.

    Scoring algorithm:
    - Base score: 20 points (for detection)
    - Dependency presence: +30 points (listed in package manifest)
    - File count match: +15 points (files with matching extensions)
    - Language dominance: +20 points (if language >30% of codebase)
    - Repository complexity: +15 points (based on file count and structure)

    Total possible: 100 points

    Args:
        tech: Technology name (e.g., "fastapi", "react", "python")
        repo_summary: Repository summary dictionary containing:
            - dependencies: Dict mapping ecosystem to package lists
            - languages: Dict mapping language names to percentage shares
            - file_tree: List of file paths
            - file_count: Total number of files
            - top_level_dirs: List of top-level directory names

    Returns:
        Dictionary with keys:
            - technology: str (the input technology name)
            - score: int (0-100, capped)
            - rationale: str (one-line explanation of scoring)

    Example:
        >>> summary = {
        ...     "dependencies": {"python": ["fastapi", "pytest"]},
        ...     "languages": {"Python": 75.5, "JavaScript": 24.5},
        ...     "file_tree": ["main.py", "test.py", "app.js"],
        ...     "file_count": 45,
        ...     "top_level_dirs": ["src", "tests", "docs"]
        ... }
        >>> score_skill("fastapi", summary)
        {
            'technology': 'fastapi',
            'score': 78,
            'rationale': 'In dependencies (+30), 2 matching files (+15), complex repo (+8), Python dominant (+20)'
        }
    """
    # Initialize score and rationale components
    score = 20  # Base score for any detected technology
    rationale_parts = ["detected"]

    # Extract repo data
    dependencies = repo_summary.get("dependencies", {})
    languages = repo_summary.get("languages", {})
    file_tree = repo_summary.get("file_tree", [])

    # Check if in dependencies (+30 points)
    if _is_in_dependencies(tech, dependencies):
        score += 30
        rationale_parts.append("in dependencies (+30)")

    # Count matching files (+15 points if any found)
    matching_files = _count_matching_files(tech, file_tree)
    if matching_files > 0:
        score += 15
        rationale_parts.append(f"{matching_files} matching files (+15)")

    # Check language dominance (+20 points if >30%)
    lang_percentage = _get_language_percentage(tech, languages)
    if lang_percentage > 30:
        score += 20
        rationale_parts.append(f"{lang_percentage:.1f}% of codebase (+20)")

    # Repository complexity (+0 to +15 points)
    complexity_score = _calculate_complexity_score(repo_summary)
    if complexity_score > 0:
        score += complexity_score
        rationale_parts.append(f"repo complexity (+{complexity_score})")

    # Cap at 100
    final_score = min(score, 100)

    # Build rationale string
    if len(rationale_parts) == 1:
        rationale = f"{tech.capitalize()} - {rationale_parts[0]}"
    else:
        rationale = f"{tech.capitalize()} - {', '.join(rationale_parts[1:])}"

    return {
        "technology": tech,
        "score": final_score,
        "rationale": rationale
    }


def score_multiple_skills(
    technologies: list[str],
    repo_summary: dict[str, Any]
) -> list[dict[str, Any]]:
    """Score multiple technologies and return sorted by score (highest first).

    Args:
        technologies: List of technology names to score
        repo_summary: Repository summary dictionary

    Returns:
        List of score dictionaries sorted by score descending

    Example:
        >>> score_multiple_skills(["fastapi", "react", "pytest"], summary)
        [
            {'technology': 'fastapi', 'score': 85, 'rationale': '...'},
            {'technology': 'pytest', 'score': 72, 'rationale': '...'},
            {'technology': 'react', 'score': 45, 'rationale': '...'}
        ]
    """
    scored = [score_skill(tech, repo_summary) for tech in technologies]

    # Sort by score descending (highest first)
    scored.sort(key=lambda x: x["score"], reverse=True)

    return scored
