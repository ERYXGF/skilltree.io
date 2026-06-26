"""Test skill recommender system.

Phase 55: "Next skill to unlock" recommender
Tests gap analysis and skill recommendations based on target roles.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.recommender import suggest_next


def test_empty_skills():
    """Test with no detected skills."""
    detected = []
    target_role = "Backend Engineer"

    recommendations = suggest_next(detected, target_role)

    # Should recommend foundational skills
    assert len(recommendations) > 0
    assert all("skill" in r for r in recommendations)
    assert all("reason" in r for r in recommendations)
    assert all("priority" in r for r in recommendations)

    print("[PASS] Empty skills test passed")


def test_backend_engineer_gaps():
    """Test recommendations for backend engineer with some skills."""
    detected = ["python", "git"]
    target_role = "Backend Engineer"

    recommendations = suggest_next(detected, target_role)

    # Should recommend backend-specific skills
    assert len(recommendations) > 0

    # Check that recommendations are relevant
    skill_names = [r["skill"].lower() for r in recommendations]

    # Should recommend API frameworks, databases, etc.
    backend_skills = ["fastapi", "django", "flask", "postgresql", "redis", "docker"]
    has_backend_recommendation = any(skill in " ".join(skill_names).lower() for skill in backend_skills)
    assert has_backend_recommendation, f"Expected backend skills in {skill_names}"

    print("[PASS] Backend engineer gaps test passed")


def test_frontend_engineer_gaps():
    """Test recommendations for frontend engineer."""
    detected = ["javascript", "html", "css"]
    target_role = "Frontend Engineer"

    recommendations = suggest_next(detected, target_role)

    assert len(recommendations) > 0

    # Should recommend frontend frameworks
    skill_names = [r["skill"].lower() for r in recommendations]
    frontend_skills = ["react", "vue", "angular", "typescript", "tailwind"]
    has_frontend_recommendation = any(skill in " ".join(skill_names).lower() for skill in frontend_skills)
    assert has_frontend_recommendation, f"Expected frontend skills in {skill_names}"

    print("[PASS] Frontend engineer gaps test passed")


def test_data_scientist_gaps():
    """Test recommendations for data scientist."""
    detected = ["python", "numpy"]
    target_role = "Data Scientist"

    recommendations = suggest_next(detected, target_role)

    assert len(recommendations) > 0

    # Should recommend data science tools
    skill_names = [r["skill"].lower() for r in recommendations]
    ds_skills = ["pandas", "scikit-learn", "matplotlib", "jupyter", "tensorflow"]
    has_ds_recommendation = any(skill in " ".join(skill_names).lower() for skill in ds_skills)
    assert has_ds_recommendation, f"Expected data science skills in {skill_names}"

    print("[PASS] Data scientist gaps test passed")


def test_priority_ordering():
    """Test that recommendations are ordered by priority."""
    detected = ["python"]
    target_role = "Backend Engineer"

    recommendations = suggest_next(detected, target_role)

    # Check priority is monotonically decreasing or equal
    priorities = [r["priority"] for r in recommendations]
    for i in range(len(priorities) - 1):
        assert priorities[i] >= priorities[i + 1], "Priorities should be in descending order"

    print("[PASS] Priority ordering test passed")


def test_recommendation_structure():
    """Test that each recommendation has required fields."""
    detected = ["python", "fastapi"]
    target_role = "Backend Engineer"

    recommendations = suggest_next(detected, target_role)

    assert len(recommendations) > 0

    for rec in recommendations:
        # Check required fields
        assert "skill" in rec, "Missing 'skill' field"
        assert "reason" in rec, "Missing 'reason' field"
        assert "priority" in rec, "Missing 'priority' field"

        # Check types
        assert isinstance(rec["skill"], str), "skill should be string"
        assert isinstance(rec["reason"], str), "reason should be string"
        assert isinstance(rec["priority"], (int, float)), "priority should be numeric"

        # Check non-empty
        assert len(rec["skill"]) > 0, "skill should not be empty"
        assert len(rec["reason"]) > 0, "reason should not be empty"
        assert rec["priority"] >= 0, "priority should be non-negative"

    print("[PASS] Recommendation structure test passed")


def test_no_duplicate_detected_skills():
    """Test that recommendations don't include already detected skills."""
    detected = ["python", "fastapi", "postgresql"]
    target_role = "Backend Engineer"

    recommendations = suggest_next(detected, target_role)

    # Recommendations should not include skills already detected
    recommended_skills = [r["skill"].lower() for r in recommendations]
    detected_lower = [s.lower() for s in detected]

    for skill in recommended_skills:
        assert skill not in detected_lower, f"Recommended skill '{skill}' is already detected"

    print("[PASS] No duplicate detected skills test passed")


def test_devops_engineer_gaps():
    """Test recommendations for DevOps engineer."""
    detected = ["git", "python"]
    target_role = "DevOps Engineer"

    recommendations = suggest_next(detected, target_role)

    assert len(recommendations) > 0

    # Should recommend DevOps tools
    skill_names = [r["skill"].lower() for r in recommendations]
    devops_skills = ["docker", "kubernetes", "terraform", "ansible", "aws", "jenkins"]
    has_devops_recommendation = any(skill in " ".join(skill_names).lower() for skill in devops_skills)
    assert has_devops_recommendation, f"Expected DevOps skills in {skill_names}"

    print("[PASS] DevOps engineer gaps test passed")


def test_max_recommendations():
    """Test that recommendations are limited to reasonable number."""
    detected = ["python"]
    target_role = "Backend Engineer"

    recommendations = suggest_next(detected, target_role, max_recommendations=5)

    # Should respect max limit
    assert len(recommendations) <= 5, "Should not exceed max recommendations"

    print("[PASS] Max recommendations test passed")


def run_all_tests():
    """Run all recommender tests."""
    print("\n" + "="*60)
    print("SKILL RECOMMENDER TESTS (Phase 55)")
    print("="*60 + "\n")

    test_empty_skills()
    test_backend_engineer_gaps()
    test_frontend_engineer_gaps()
    test_data_scientist_gaps()
    test_priority_ordering()
    test_recommendation_structure()
    test_no_duplicate_detected_skills()
    test_devops_engineer_gaps()
    test_max_recommendations()

    print("\n" + "="*60)
    print("[SUCCESS] ALL RECOMMENDER TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
