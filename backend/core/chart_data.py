"""Chart data transformation for frontend visualization.

Phase 35: Chart data shaper

Transforms proficiency scores into optimized JSON payloads for react-plotly.js,
ensuring clean, clutter-free visualizations with proper sorting and formatting.
"""

from __future__ import annotations

from typing import Any


def to_plotly_payload(skills: list[dict[str, Any]], max_skills: int = 10) -> dict[str, Any]:
    """
    Transform skills array into a Plotly-compatible horizontal bar chart payload.

    Creates a clean, optimized data structure for react-plotly.js with:
    - Horizontal bar orientation
    - Skills sorted by score (highest first)
    - Hover text showing detailed rationale
    - Limited to top N skills to avoid chart clutter

    Args:
        skills: List of skill dictionaries, each containing:
                - technology: str (technology name)
                - score: int (0-100 proficiency score)
                - rationale: str (explanation of the score)
        max_skills: Maximum number of skills to include (default: 10)

    Returns:
        Dictionary with Plotly-compatible structure:
        {
            "data": [{
                "type": "bar",
                "orientation": "h",
                "x": [scores...],
                "y": [technologies...],
                "hovertext": [rationales...],
                "marker": {"color": "..."}
            }],
            "layout": {
                "title": "...",
                "xaxis": {...},
                "yaxis": {...},
                "margin": {...}
            }
        }

    Example:
        >>> skills = [
        ...     {"technology": "fastapi", "score": 85, "rationale": "FastAPI - in dependencies (+30)"},
        ...     {"technology": "react", "score": 72, "rationale": "React - in dependencies (+30)"},
        ...     {"technology": "pytest", "score": 60, "rationale": "Pytest - detected"}
        ... ]
        >>> payload = to_plotly_payload(skills, max_skills=10)
        >>> payload["data"][0]["type"]
        'bar'
        >>> payload["data"][0]["orientation"]
        'h'
    """
    # Handle empty input
    if not skills:
        return {
            "data": [{
                "type": "bar",
                "orientation": "h",
                "x": [],
                "y": [],
                "hovertext": [],
                "marker": {
                    "color": "rgba(55, 128, 191, 0.7)",
                    "line": {
                        "color": "rgba(55, 128, 191, 1.0)",
                        "width": 1
                    }
                }
            }],
            "layout": {
                "title": {
                    "text": "Technology Proficiency Scores",
                    "font": {"size": 18}
                },
                "xaxis": {
                    "title": "Proficiency Score (0-100)",
                    "range": [0, 100],
                    "gridcolor": "rgba(200, 200, 200, 0.3)"
                },
                "yaxis": {
                    "title": "",
                    "automargin": True
                },
                "margin": {
                    "l": 150,
                    "r": 50,
                    "t": 80,
                    "b": 50
                },
                "height": 400,
                "hovermode": "closest"
            }
        }

    # Sort skills by score descending (highest first)
    sorted_skills = sorted(skills, key=lambda s: s.get("score", 0), reverse=True)

    # Limit to max_skills to avoid clutter
    limited_skills = sorted_skills[:max_skills]

    # Extract data arrays
    technologies = []
    scores = []
    rationales = []

    for skill in limited_skills:
        tech = skill.get("technology", "Unknown")
        score = skill.get("score", 0)
        rationale = skill.get("rationale", "No details available")

        # Capitalize technology name for display
        tech_display = tech.capitalize()

        technologies.append(tech_display)
        scores.append(score)
        rationales.append(rationale)

    # Reverse arrays so highest score appears at top of horizontal bar chart
    technologies.reverse()
    scores.reverse()
    rationales.reverse()

    # Calculate dynamic height based on number of skills
    chart_height = max(400, len(limited_skills) * 50)

    # Build Plotly payload
    payload = {
        "data": [{
            "type": "bar",
            "orientation": "h",
            "x": scores,
            "y": technologies,
            "hovertext": rationales,
            "hoverinfo": "text+x",
            "marker": {
                "color": "rgba(55, 128, 191, 0.7)",
                "line": {
                    "color": "rgba(55, 128, 191, 1.0)",
                    "width": 1
                }
            },
            "text": scores,
            "textposition": "outside",
            "textfont": {
                "size": 12
            }
        }],
        "layout": {
            "title": {
                "text": "Technology Proficiency Scores",
                "font": {"size": 18}
            },
            "xaxis": {
                "title": "Proficiency Score (0-100)",
                "range": [0, 105],  # Slightly over 100 to show text labels
                "gridcolor": "rgba(200, 200, 200, 0.3)"
            },
            "yaxis": {
                "title": "",
                "automargin": True
            },
            "margin": {
                "l": 150,
                "r": 50,
                "t": 80,
                "b": 50
            },
            "height": chart_height,
            "hovermode": "closest",
            "showlegend": False
        }
    }

    return payload


def to_simple_chart_data(skills: list[dict[str, Any]], max_skills: int = 10) -> dict[str, list]:
    """
    Transform skills into a simplified chart data format.

    Provides a lightweight alternative to the full Plotly payload for
    simpler charting libraries or custom visualizations.

    Args:
        skills: List of skill dictionaries
        max_skills: Maximum number of skills to include

    Returns:
        Dictionary with arrays:
        {
            "labels": [technology names...],
            "scores": [score values...],
            "rationales": [rationale strings...]
        }

    Example:
        >>> skills = [{"technology": "python", "score": 85, "rationale": "Test"}]
        >>> data = to_simple_chart_data(skills)
        >>> data["labels"]
        ['Python']
        >>> data["scores"]
        [85]
    """
    if not skills:
        return {
            "labels": [],
            "scores": [],
            "rationales": []
        }

    # Sort by score descending
    sorted_skills = sorted(skills, key=lambda s: s.get("score", 0), reverse=True)
    limited_skills = sorted_skills[:max_skills]

    labels = []
    scores = []
    rationales = []

    for skill in limited_skills:
        tech = skill.get("technology", "Unknown")
        score = skill.get("score", 0)
        rationale = skill.get("rationale", "No details available")

        labels.append(tech.capitalize())
        scores.append(score)
        rationales.append(rationale)

    return {
        "labels": labels,
        "scores": scores,
        "rationales": rationales
    }
