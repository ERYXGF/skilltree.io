"""
Anthropic tool definitions and handlers for the AI agent.

This module provides:
1. Tool schemas in Anthropic's JSON format for Claude to invoke
2. Python handler functions that execute the tool logic
"""

import json
from pathlib import Path
from typing import Any

from ..core.proficiency_scorer import score_multiple_skills


def load_tech_taxonomy() -> dict[str, dict[str, str]]:
    """Load the tech_taxonomy.json file."""
    taxonomy_path = Path(__file__).parent.parent / "data" / "tech_taxonomy.json"
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        return json.load(f)


# Anthropic tool schema for detect_stack
DETECT_STACK_TOOL = {
    "name": "detect_stack",
    "description": (
        "Detects technologies present in a repository by analyzing its dependencies "
        "and file extensions. Cross-references findings against the tech_taxonomy to "
        "return only verified, recognized technologies. Use this tool to extract a "
        "clean list of technologies from repository data without hallucinating."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "repo_summary": {
                "type": "object",
                "description": (
                    "Repository summary object containing 'dependencies' (dict mapping "
                    "ecosystem to package lists) and 'languages' (dict mapping language "
                    "names to percentage shares)."
                ),
                "properties": {
                    "dependencies": {
                        "type": "object",
                        "description": "Dependencies organized by ecosystem (e.g., {'python': ['fastapi', 'pytest'], 'javascript': ['react', 'vite']})",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "languages": {
                        "type": "object",
                        "description": "Language breakdown with percentage shares (e.g., {'Python': 65.5, 'JavaScript': 34.5})",
                        "additionalProperties": {"type": "number"}
                    }
                },
                "required": ["dependencies"]
            }
        },
        "required": ["repo_summary"]
    }
}


# Anthropic tool schema for map_to_jobs
MAP_TO_JOBS_TOOL = {
    "name": "map_to_jobs",
    "description": (
        "Maps a list of verified technologies to their corresponding job families. "
        "Takes the output from detect_stack and cross-references each technology "
        "against tech_taxonomy to determine which job roles match the developer's "
        "skill profile. Returns a deduplicated list of job families."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "technologies": {
                "type": "array",
                "description": "List of verified technology names (e.g., ['fastapi', 'react', 'scikit-learn'])",
                "items": {"type": "string"}
            }
        },
        "required": ["technologies"]
    }
}


# Anthropic tool schema for score_skills
SCORE_SKILLS_TOOL = {
    "name": "score_skills",
    "description": (
        "Calculates proficiency scores (0-100) for detected technologies based on "
        "repository analysis. Evaluates factors like file counts, dependency usage, "
        "and code patterns to estimate skill level. Returns a list of skills with "
        "scores and rationale, sorted by score (highest first)."
    ),
    "input_schema": {
        "type": "object",
        "properties": {
            "technologies": {
                "type": "array",
                "description": "List of verified technology names to score",
                "items": {"type": "string"}
            },
            "repo_summary": {
                "type": "object",
                "description": (
                    "Repository summary containing dependencies, languages, and file counts "
                    "for scoring analysis"
                ),
                "properties": {
                    "dependencies": {
                        "type": "object",
                        "description": "Dependencies organized by ecosystem",
                        "additionalProperties": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "languages": {
                        "type": "object",
                        "description": "Language breakdown with percentage shares",
                        "additionalProperties": {"type": "number"}
                    },
                    "file_count": {
                        "type": "integer",
                        "description": "Total number of files in repository"
                    }
                },
                "required": ["dependencies"]
            }
        },
        "required": ["technologies", "repo_summary"]
    }
}


# All available tools (legacy list for backward compatibility)
TOOLS = [DETECT_STACK_TOOL]


# Centralized tool registry
TOOL_SCHEMAS = [
    DETECT_STACK_TOOL,
    MAP_TO_JOBS_TOOL,
    SCORE_SKILLS_TOOL
]


def detect_stack_handler(repo_summary: dict[str, Any]) -> list[str]:
    """
    Handler for the detect_stack tool.

    Analyzes repository dependencies and cross-references them against tech_taxonomy.json
    to return a verified list of detected technologies.

    Args:
        repo_summary: Dictionary containing:
            - dependencies: Dict mapping ecosystem names to lists of package names
            - languages: (optional) Dict mapping language names to percentage shares

    Returns:
        List of detected technology names that exist in tech_taxonomy.json

    Example:
        >>> summary = {
        ...     "dependencies": {
        ...         "python": ["fastapi", "pytest", "unknown-package"],
        ...         "javascript": ["react", "vite"]
        ...     }
        ... }
        >>> detect_stack_handler(summary)
        ['fastapi', 'pytest', 'react', 'vite']
    """
    # Load the tech taxonomy
    taxonomy = load_tech_taxonomy()

    # Normalize taxonomy keys to lowercase for case-insensitive matching
    taxonomy_lower = {key.lower(): key for key in taxonomy.keys()}

    detected_techs: set[str] = set()

    # Extract dependencies from all ecosystems
    dependencies = repo_summary.get("dependencies", {})

    for ecosystem, packages in dependencies.items():
        if not isinstance(packages, list):
            continue

        for package in packages:
            if not isinstance(package, str):
                continue

            # Normalize package name for matching
            package_lower = package.lower().strip()

            # Check if this package exists in our taxonomy
            if package_lower in taxonomy_lower:
                # Use the canonical name from taxonomy
                detected_techs.add(taxonomy_lower[package_lower])

    # Also check for language-based technologies (e.g., "typescript", "node.js")
    languages = repo_summary.get("languages", {})
    if isinstance(languages, dict):
        for language in languages.keys():
            language_lower = language.lower().strip()
            if language_lower in taxonomy_lower:
                detected_techs.add(taxonomy_lower[language_lower])

    # Return sorted list for consistency
    return sorted(detected_techs)


def map_to_jobs_handler(technologies: list[str]) -> list[str]:
    """
    Handler for the map_to_jobs tool.

    Maps verified technologies to their corresponding job families by looking up
    each technology in tech_taxonomy.json and extracting the job_family field.

    Args:
        technologies: List of verified technology names (e.g., ['fastapi', 'react'])

    Returns:
        Deduplicated, sorted list of job family names

    Example:
        >>> map_to_jobs_handler(['fastapi', 'scikit-learn', 'pytest'])
        ['Backend Engineer', 'Data Scientist']
    """
    # Load the tech taxonomy
    taxonomy = load_tech_taxonomy()

    # Normalize taxonomy keys to lowercase for case-insensitive matching
    taxonomy_lower = {key.lower(): key for key in taxonomy.keys()}

    job_families: set[str] = set()

    for tech in technologies:
        if not isinstance(tech, str):
            continue

        tech_lower = tech.lower().strip()

        # Look up the technology in taxonomy
        if tech_lower in taxonomy_lower:
            canonical_name = taxonomy_lower[tech_lower]
            tech_data = taxonomy[canonical_name]

            # Extract job_family
            if "job_family" in tech_data:
                job_families.add(tech_data["job_family"])

    # Return sorted list for consistency
    return sorted(job_families)


def score_skills_handler(technologies: list[str], repo_summary: dict[str, Any]) -> list[dict[str, Any]]:
    """
    Handler for the score_skills tool.

    Calculates proficiency scores (0-100) for each technology based on repository
    analysis using the production proficiency_scorer module.

    Args:
        technologies: List of verified technology names to score
        repo_summary: Repository summary containing dependencies, languages, file counts

    Returns:
        List of skill dictionaries sorted by score (highest first), each containing:
        - technology: str (technology name)
        - score: int (0-100)
        - rationale: str (brief explanation of the score)

    Example:
        >>> score_skills_handler(['fastapi', 'react'], {...})
        [
            {'technology': 'fastapi', 'score': 85, 'rationale': 'Fastapi - in dependencies (+30), repo complexity (+5)'},
            {'technology': 'react', 'score': 72, 'rationale': 'React - in dependencies (+30), 1 matching files (+15)'}
        ]
    """
    # Use the production proficiency scorer
    return score_multiple_skills(technologies, repo_summary)


def dispatch(name: str, arguments: dict[str, Any], repo_summary: dict[str, Any] | None = None) -> Any:
    """
    Centralized tool dispatch entry point.

    Routes tool execution to the appropriate handler based on tool name.
    Provides a clean, unified interface for invoking any registered tool.

    Args:
        name: Name of the tool to invoke
        arguments: Tool-specific arguments
        repo_summary: Optional repository summary (required for some tools)

    Returns:
        Result from the tool handler

    Raises:
        ValueError: If tool name is not recognized

    Example:
        >>> dispatch("detect_stack", {"repo_summary": {...}})
        ['fastapi', 'react']
        >>> dispatch("map_to_jobs", {"technologies": ['fastapi']})
        ['Backend Engineer']
    """
    if name == "detect_stack":
        return detect_stack_handler(arguments["repo_summary"])
    elif name == "map_to_jobs":
        return map_to_jobs_handler(arguments["technologies"])
    elif name == "score_skills":
        return score_skills_handler(
            arguments["technologies"],
            arguments["repo_summary"]
        )
    else:
        raise ValueError(f"Unknown tool: {name}")


def handle_tool_use(tool_name: str, tool_input: dict[str, Any]) -> Any:
    """
    Route tool calls to their appropriate handlers (legacy interface).

    Args:
        tool_name: Name of the tool to invoke
        tool_input: Input parameters for the tool

    Returns:
        Result from the tool handler

    Raises:
        ValueError: If tool_name is not recognized

    Note:
        This function is maintained for backward compatibility.
        New code should use dispatch() instead.
    """
    return dispatch(tool_name, tool_input)
