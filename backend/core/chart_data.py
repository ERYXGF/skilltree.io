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


def to_skill_tree_data(skills: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Transform skills into a skill tree graph structure for visualization.

    Phase 53: Animated skill-tree view

    Creates a DAG (Directed Acyclic Graph) showing skill prerequisites and
    progression paths, suitable for react-flow or d3 visualization.

    Args:
        skills: List of skill dictionaries, each containing:
                - technology: str (technology name)
                - score: int (0-100 proficiency score)
                - rationale: str (explanation)

    Returns:
        Dictionary with nodes and edges:
        {
            "nodes": [
                {
                    "id": "skill_name",
                    "label": "Skill Name",
                    "score": 85,
                    "level": 0,
                    "unlocked": true
                },
                ...
            ],
            "edges": [
                {
                    "source": "prerequisite_skill",
                    "target": "dependent_skill"
                },
                ...
            ]
        }

    Example:
        >>> skills = [
        ...     {"technology": "python", "score": 85, "rationale": "Test"},
        ...     {"technology": "fastapi", "score": 70, "rationale": "Test"}
        ... ]
        >>> tree = to_skill_tree_data(skills)
        >>> len(tree["nodes"]) >= 2
        True
    """
    import json
    from pathlib import Path

    # Load tech taxonomy
    taxonomy_path = Path(__file__).parent.parent / "data" / "tech_taxonomy.json"
    with open(taxonomy_path, "r", encoding="utf-8") as f:
        TECH_TAXONOMY = json.load(f)

    # Define skill prerequisites based on common tech progressions
    prerequisites = {
        # Frontend progression
        "CSS styling": [],
        "Frontend UI": ["CSS styling"],
        "State management": ["Frontend UI"],
        "Type-safe programming": ["Frontend UI"],
        "Full-stack framework": ["Frontend UI", "Backend runtime"],

        # Backend progression
        "Version control": [],
        "Backend runtime": ["Version control"],
        "API development": ["Backend runtime"],
        "Web framework": ["API development"],
        "Database ORM": ["API development"],
        "Database management": ["Database ORM"],
        "NoSQL database": ["API development"],

        # Data science progression
        "Numerical computing": [],
        "Data manipulation": ["Numerical computing"],
        "Data visualization": ["Data manipulation"],
        "Interactive computing": ["Data manipulation"],
        "ML modeling": ["Data manipulation", "Numerical computing"],
        "Deep learning": ["ML modeling"],

        # DevOps progression
        "Containerization": ["Version control"],
        "Container orchestration": ["Containerization"],
        "Infrastructure as code": ["Containerization"],
        "Cloud infrastructure": ["Containerization"],
        "CI/CD": ["Version control"],
        "Configuration management": ["CI/CD"],
        "Monitoring": ["Cloud infrastructure"],
        "Observability": ["Monitoring"],

        # Data engineering
        "Big data processing": ["Data manipulation"],
        "Workflow orchestration": ["Big data processing"],
        "Stream processing": ["Big data processing"],

        # Other skills
        "Testing": ["Version control"],
        "Build tooling": ["Frontend UI"],
        "Caching": ["API development"],
        "Search engine": ["Database management"],
        "Web server": ["API development"],
        "API design": ["API development"],
        "Task queuing": ["API development"],
    }

    # Map technologies to skill categories
    tech_to_skill = {}
    for tech, info in TECH_TAXONOMY.items():
        skill_name = info.get("skill", "")
        if skill_name:
            tech_to_skill[tech] = skill_name

    # Build skill map from input
    skill_map = {}
    for skill_data in skills:
        tech = skill_data.get("technology", "").lower()
        score = skill_data.get("score", 0)
        rationale = skill_data.get("rationale", "")

        # Get skill category
        skill_name = tech_to_skill.get(tech, tech.capitalize())

        # Store highest score if duplicate
        if skill_name not in skill_map or skill_map[skill_name]["score"] < score:
            skill_map[skill_name] = {
                "name": skill_name,
                "score": score,
                "rationale": rationale,
                "technology": tech
            }

    # Calculate skill levels (hierarchy depth)
    def calculate_level(skill_name: str, visited: set) -> int:
        if skill_name in visited:
            return 0  # Cycle protection

        prereqs = prerequisites.get(skill_name, [])
        if not prereqs:
            return 0

        visited.add(skill_name)
        max_prereq_level = max(
            (calculate_level(p, visited) for p in prereqs if p in skill_map),
            default=-1
        )
        visited.remove(skill_name)

        return max_prereq_level + 1

    # Build nodes
    nodes = []
    for skill_name, skill_info in skill_map.items():
        level = calculate_level(skill_name, set())

        node = {
            "id": skill_name.lower().replace(" ", "_"),
            "label": skill_name,
            "score": skill_info["score"],
            "level": level,
            "unlocked": skill_info["score"] > 0,
            "rationale": skill_info["rationale"],
            "technology": skill_info["technology"]
        }
        nodes.append(node)

    # Build edges (only between skills that exist in the input)
    edges = []
    for skill_name in skill_map:
        prereqs = prerequisites.get(skill_name, [])
        for prereq in prereqs:
            if prereq in skill_map:
                edge = {
                    "source": prereq.lower().replace(" ", "_"),
                    "target": skill_name.lower().replace(" ", "_")
                }
                edges.append(edge)

    return {
        "nodes": nodes,
        "edges": edges
    }
