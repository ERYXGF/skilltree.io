"""Test skill tree data structure validation.

Phase 53: Animated skill-tree view
Tests that skill tree data forms a valid DAG (Directed Acyclic Graph) with no cycles.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, List, Set


def build_skill_tree(skills: List[Dict]) -> Dict[str, List[str]]:
    """
    Build a skill tree graph from detected skills.

    Args:
        skills: List of skill dicts with name and proficiency score

    Returns:
        Dict mapping skill names to their prerequisites
    """
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

    # Build graph with only skills that exist in the input
    skill_names = {s["name"] for s in skills}
    graph = {}

    for skill in skills:
        skill_name = skill["name"]
        # Get prerequisites that also exist in detected skills
        prereqs = prerequisites.get(skill_name, [])
        graph[skill_name] = [p for p in prereqs if p in skill_names]

    return graph


def has_cycle(graph: Dict[str, List[str]]) -> bool:
    """
    Detect if graph has cycles using DFS.

    Args:
        graph: Dict mapping nodes to their dependencies

    Returns:
        True if cycle detected, False otherwise
    """
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node: str) -> bool:
        color[node] = GRAY
        for neighbor in graph.get(node, []):
            if color.get(neighbor, WHITE) == GRAY:
                return True  # Back edge = cycle
            if color.get(neighbor, WHITE) == WHITE:
                if dfs(neighbor):
                    return True
        color[node] = BLACK
        return False

    for node in graph:
        if color[node] == WHITE:
            if dfs(node):
                return True
    return False


def calculate_skill_levels(graph: Dict[str, List[str]]) -> Dict[str, int]:
    """
    Calculate hierarchical level for each skill (for tree layout).
    Level 0 = foundational skills with no prerequisites.

    Args:
        graph: Dict mapping skills to their prerequisites

    Returns:
        Dict mapping skill names to their level (0-based)
    """
    levels = {}

    def get_level(skill: str, visited: Set[str]) -> int:
        if skill in levels:
            return levels[skill]
        if skill in visited:
            return 0  # Cycle protection

        prereqs = graph.get(skill, [])
        if not prereqs:
            levels[skill] = 0
            return 0

        visited.add(skill)
        max_prereq_level = max((get_level(p, visited) for p in prereqs), default=-1)
        visited.remove(skill)

        levels[skill] = max_prereq_level + 1
        return levels[skill]

    for skill in graph:
        get_level(skill, set())

    return levels


def test_empty_skills():
    """Test with no skills."""
    skills = []
    graph = build_skill_tree(skills)
    assert graph == {}
    assert not has_cycle(graph)
    print("[PASS] Empty skills test passed")


def test_single_skill():
    """Test with single skill."""
    skills = [{"name": "Version control", "score": 80}]
    graph = build_skill_tree(skills)
    assert "Version control" in graph
    assert graph["Version control"] == []
    assert not has_cycle(graph)
    print("[PASS] Single skill test passed")


def test_linear_progression():
    """Test linear skill progression (no branching)."""
    skills = [
        {"name": "Version control", "score": 90},
        {"name": "Backend runtime", "score": 80},
        {"name": "API development", "score": 70},
    ]
    graph = build_skill_tree(skills)

    assert graph["Version control"] == []
    assert graph["Backend runtime"] == ["Version control"]
    assert graph["API development"] == ["Backend runtime"]
    assert not has_cycle(graph)

    levels = calculate_skill_levels(graph)
    assert levels["Version control"] == 0
    assert levels["Backend runtime"] == 1
    assert levels["API development"] == 2
    print("[PASS] Linear progression test passed")


def test_branching_tree():
    """Test tree with multiple branches."""
    skills = [
        {"name": "Version control", "score": 90},
        {"name": "Backend runtime", "score": 80},
        {"name": "API development", "score": 75},
        {"name": "Database ORM", "score": 70},
        {"name": "Containerization", "score": 65},
    ]
    graph = build_skill_tree(skills)

    # Backend runtime and Containerization both depend on Version control
    assert "Version control" in graph["Backend runtime"]
    assert "Version control" in graph["Containerization"]

    # API development depends on Backend runtime
    assert "Backend runtime" in graph["API development"]

    # Database ORM depends on API development
    assert "API development" in graph["Database ORM"]

    assert not has_cycle(graph)
    print("[PASS] Branching tree test passed")


def test_complex_dag():
    """Test complex DAG with multiple paths."""
    skills = [
        {"name": "Numerical computing", "score": 90},
        {"name": "Data manipulation", "score": 85},
        {"name": "ML modeling", "score": 80},
        {"name": "Deep learning", "score": 75},
    ]
    graph = build_skill_tree(skills)

    # ML modeling depends on both Data manipulation and Numerical computing
    assert "Data manipulation" in graph["ML modeling"]
    assert "Numerical computing" in graph["ML modeling"]

    # Deep learning depends on ML modeling
    assert "ML modeling" in graph["Deep learning"]

    assert not has_cycle(graph)

    levels = calculate_skill_levels(graph)
    assert levels["Numerical computing"] == 0
    assert levels["Data manipulation"] == 1
    assert levels["ML modeling"] == 2
    assert levels["Deep learning"] == 3
    print("[PASS] Complex DAG test passed")


def test_no_cycle_in_full_stack():
    """Test full-stack developer skills (frontend + backend)."""
    skills = [
        {"name": "Version control", "score": 95},
        {"name": "CSS styling", "score": 85},
        {"name": "Frontend UI", "score": 90},
        {"name": "Backend runtime", "score": 88},
        {"name": "API development", "score": 85},
        {"name": "Full-stack framework", "score": 80},
    ]
    graph = build_skill_tree(skills)

    # Full-stack framework depends on both Frontend UI and Backend runtime
    assert "Frontend UI" in graph["Full-stack framework"]
    assert "Backend runtime" in graph["Full-stack framework"]

    assert not has_cycle(graph)
    print("[PASS] Full-stack skills test passed")


def test_skill_levels_hierarchy():
    """Test that skill levels form proper hierarchy."""
    skills = [
        {"name": "Version control", "score": 90},
        {"name": "Backend runtime", "score": 85},
        {"name": "API development", "score": 80},
        {"name": "Web framework", "score": 75},
        {"name": "Database ORM", "score": 70},
    ]
    graph = build_skill_tree(skills)
    levels = calculate_skill_levels(graph)

    # Verify monotonic progression
    assert levels["Version control"] < levels["Backend runtime"]
    assert levels["Backend runtime"] < levels["API development"]
    assert levels["API development"] < levels["Web framework"]
    assert levels["API development"] < levels["Database ORM"]

    print("[PASS] Skill levels hierarchy test passed")


def test_isolated_skills():
    """Test skills with no defined prerequisites."""
    skills = [
        {"name": "Version control", "score": 90},
        {"name": "Testing", "score": 85},
        {"name": "Unknown Skill", "score": 70},  # Not in prerequisites map
    ]
    graph = build_skill_tree(skills)

    # Unknown skills should have empty prerequisites
    assert graph["Unknown Skill"] == []
    assert not has_cycle(graph)
    print("[PASS] Isolated skills test passed")


def run_all_tests():
    """Run all skill tree validation tests."""
    print("\n" + "="*60)
    print("SKILL TREE DATA VALIDATION TESTS (Phase 53)")
    print("="*60 + "\n")

    test_empty_skills()
    test_single_skill()
    test_linear_progression()
    test_branching_tree()
    test_complex_dag()
    test_no_cycle_in_full_stack()
    test_skill_levels_hierarchy()
    test_isolated_skills()

    print("\n" + "="*60)
    print("[SUCCESS] ALL SKILL TREE TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
