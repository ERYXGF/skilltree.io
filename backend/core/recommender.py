"""Skill recommendation system for career development.

Phase 55: "Next skill to unlock" recommender

Analyzes detected skills vs target role requirements to suggest
the most valuable skills to learn next, with prioritization based on:
- Relevance to target role
- Prerequisite completion
- Market demand
- Learning path progression
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def suggest_next(
    detected_skills: list[str],
    target_role: str,
    max_recommendations: int = 5
) -> list[dict[str, Any]]:
    """
    Suggest next skills to learn based on detected skills and target role.

    Performs gap analysis by comparing detected skills against role requirements
    and recommends high-value skills that build on existing knowledge.

    Args:
        detected_skills: List of technology names already detected
        target_role: Target job role (e.g., "Backend Engineer", "Data Scientist")
        max_recommendations: Maximum number of recommendations to return

    Returns:
        List of recommendation dictionaries, each containing:
        - skill: str (technology/skill name)
        - reason: str (why this skill is recommended)
        - priority: int (0-100, higher = more important)

    Example:
        >>> suggest_next(["python", "git"], "Backend Engineer")
        [
            {
                "skill": "FastAPI",
                "reason": "Essential API framework for Python backend development",
                "priority": 95
            },
            ...
        ]
    """
    # Load taxonomy
    data_dir = Path(__file__).parent.parent / "data"

    with open(data_dir / "tech_taxonomy.json", "r", encoding="utf-8") as f:
        taxonomy = json.load(f)

    # Normalize inputs
    detected_lower = {skill.lower() for skill in detected_skills}

    # Define role-specific skill requirements
    role_skills = {
        "Backend Engineer": {
            "required": ["API development", "Database management", "Backend runtime", "Version control"],
            "preferred": ["Caching", "Task queuing", "Testing", "Containerization"]
        },
        "Frontend Engineer": {
            "required": ["Frontend UI", "CSS styling", "Build tooling", "Version control"],
            "preferred": ["State management", "Type-safe programming", "Testing"]
        },
        "Data Scientist": {
            "required": ["Data manipulation", "Numerical computing", "Data visualization", "ML modeling"],
            "preferred": ["Deep learning", "Interactive computing", "Big data processing"]
        },
        "DevOps Engineer": {
            "required": ["Containerization", "CI/CD", "Cloud infrastructure", "Version control"],
            "preferred": ["Container orchestration", "Infrastructure as code", "Monitoring", "Configuration management"]
        },
        "Full Stack Engineer": {
            "required": ["Frontend UI", "Backend runtime", "API development", "Database management"],
            "preferred": ["Full-stack framework", "Containerization", "Testing"]
        },
        "ML Engineer": {
            "required": ["Deep learning", "ML modeling", "Data manipulation"],
            "preferred": ["Big data processing", "Containerization", "Cloud infrastructure"]
        },
        "Data Engineer": {
            "required": ["Big data processing", "Workflow orchestration", "Data manipulation"],
            "preferred": ["Stream processing", "Cloud infrastructure", "Containerization"]
        }
    }

    # Get requirements for target role
    role_reqs = role_skills.get(target_role, role_skills["Backend Engineer"])
    required_skills = role_reqs["required"]
    preferred_skills = role_reqs["preferred"]

    # Define skill prerequisites and progressions
    skill_progressions = {
        # Backend progression
        "Version control": [],
        "Backend runtime": ["Version control"],
        "API development": ["Backend runtime"],
        "Web framework": ["API development"],
        "Database ORM": ["API development"],
        "Database management": ["Database ORM"],

        # Frontend progression
        "CSS styling": [],
        "Frontend UI": ["CSS styling"],
        "State management": ["Frontend UI"],
        "Type-safe programming": ["Frontend UI"],

        # Data science progression
        "Numerical computing": [],
        "Data manipulation": ["Numerical computing"],
        "Data visualization": ["Data manipulation"],
        "ML modeling": ["Data manipulation", "Numerical computing"],
        "Deep learning": ["ML modeling"],

        # DevOps progression
        "Containerization": ["Version control"],
        "Container orchestration": ["Containerization"],
        "Infrastructure as code": ["Containerization"],
        "Cloud infrastructure": ["Containerization"],
        "CI/CD": ["Version control"],

        # Testing
        "Testing": ["Version control"],
    }

    # Map technologies to skill categories
    tech_to_skill = {}
    skill_to_techs = {}

    for tech, info in taxonomy.items():
        skill_name = info.get("skill", "")
        if skill_name:
            tech_to_skill[tech.lower()] = skill_name
            if skill_name not in skill_to_techs:
                skill_to_techs[skill_name] = []
            skill_to_techs[skill_name].append(tech)

    # Determine which skill categories are already covered
    covered_skills = set()
    for detected in detected_lower:
        if detected in tech_to_skill:
            covered_skills.add(tech_to_skill[detected])

    # Build recommendations
    recommendations = []

    # Check prerequisites completion for each skill
    def prerequisites_met(skill_name: str) -> bool:
        prereqs = skill_progressions.get(skill_name, [])
        return all(prereq in covered_skills for prereq in prereqs)

    # Recommend skills from role requirements
    for skill_category in required_skills + preferred_skills:
        # Skip if already covered
        if skill_category in covered_skills:
            continue

        # Check if prerequisites are met
        if not prerequisites_met(skill_category):
            continue

        # Find specific technologies in this category
        techs_in_category = skill_to_techs.get(skill_category, [])

        for tech in techs_in_category:
            if tech.lower() not in detected_lower:
                # Calculate priority
                priority = 70  # Base priority

                # Higher priority for required skills
                if skill_category in required_skills:
                    priority += 20

                # Bonus for popular technologies
                popular_techs = ["react", "python", "docker", "kubernetes", "postgresql",
                                "fastapi", "typescript", "aws", "redis", "jest"]
                if tech.lower() in popular_techs:
                    priority += 10

                # Create recommendation
                reason = f"Essential {skill_category.lower()} skill for {target_role}"
                if skill_category in preferred_skills:
                    reason = f"Preferred {skill_category.lower()} skill for {target_role}"

                recommendations.append({
                    "skill": tech.capitalize(),
                    "reason": reason,
                    "priority": min(100, priority)
                })

    # If no role-specific recommendations, suggest foundational skills
    if not recommendations:
        foundational = {
            "Backend Engineer": [
                ("Python", "Versatile language for backend development", 90),
                ("FastAPI", "Modern Python API framework", 85),
                ("PostgreSQL", "Robust relational database", 80),
                ("Docker", "Essential containerization tool", 85),
                ("Git", "Version control foundation", 95),
            ],
            "Frontend Engineer": [
                ("React", "Popular UI framework", 90),
                ("TypeScript", "Type-safe JavaScript", 85),
                ("Tailwind", "Modern CSS framework", 75),
                ("Jest", "JavaScript testing framework", 70),
                ("Git", "Version control foundation", 95),
            ],
            "Data Scientist": [
                ("Python", "Primary data science language", 95),
                ("Pandas", "Data manipulation library", 90),
                ("NumPy", "Numerical computing foundation", 85),
                ("Scikit-learn", "Machine learning library", 85),
                ("Jupyter", "Interactive computing environment", 80),
            ],
            "DevOps Engineer": [
                ("Docker", "Containerization platform", 95),
                ("Kubernetes", "Container orchestration", 90),
                ("Terraform", "Infrastructure as code", 85),
                ("AWS", "Cloud platform", 85),
                ("Git", "Version control foundation", 95),
            ],
            "Full Stack Engineer": [
                ("React", "Frontend framework", 85),
                ("Node.js", "JavaScript runtime", 85),
                ("PostgreSQL", "Database management", 80),
                ("Docker", "Containerization", 80),
                ("Git", "Version control", 95),
            ],
        }

        default_skills = foundational.get(target_role, foundational["Backend Engineer"])

        for skill, reason, priority in default_skills:
            if skill.lower() not in detected_lower:
                recommendations.append({
                    "skill": skill,
                    "reason": reason,
                    "priority": priority
                })

    # Sort by priority (highest first) and limit
    recommendations.sort(key=lambda x: x["priority"], reverse=True)
    recommendations = recommendations[:max_recommendations]

    return recommendations
