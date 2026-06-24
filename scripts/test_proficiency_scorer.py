"""Test suite for Phase 33 - Proficiency scorer.

Validates that the deterministic scoring algorithm:
1. Produces identical outputs for identical inputs (100% deterministic)
2. Assigns higher scores for deeper usage signals
3. Never exceeds 100 or drops below 0
4. Generates proper rationale strings
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent
sys.path.insert(0, str(backend_path))

from backend.core.proficiency_scorer import score_skill, score_multiple_skills


# Use ASCII-compatible symbols for Windows compatibility
CHECK = "[PASS]"
CROSS = "[FAIL]"


def test_deterministic_scoring():
    """Test that identical inputs always produce identical outputs."""
    print("Testing deterministic scoring...")

    repo_summary = {
        "dependencies": {"python": ["fastapi", "pytest"]},
        "languages": {"Python": 75.5, "JavaScript": 24.5},
        "file_tree": ["main.py", "test.py", "app.js"],
        "file_count": 45,
        "top_level_dirs": ["src", "tests", "docs"]
    }

    # Score the same tech multiple times
    result1 = score_skill("fastapi", repo_summary)
    result2 = score_skill("fastapi", repo_summary)
    result3 = score_skill("fastapi", repo_summary)

    # All results should be identical
    assert result1 == result2 == result3, "Scoring is not deterministic!"
    assert result1["technology"] == "fastapi"
    assert isinstance(result1["score"], int)
    assert isinstance(result1["rationale"], str)

    print(f"  {CHECK} Deterministic: {result1}")


def test_score_boundaries():
    """Test that scores never exceed 100 or drop below 0."""
    print("Testing score boundaries...")

    # Minimal repo (should give low score)
    minimal_repo = {
        "dependencies": {},
        "languages": {},
        "file_tree": [],
        "file_count": 0,
        "top_level_dirs": []
    }

    result_min = score_skill("unknown-tech", minimal_repo)
    assert 0 <= result_min["score"] <= 100, f"Score out of bounds: {result_min['score']}"
    assert result_min["score"] >= 0, "Score should never be negative"
    print(f"  {CHECK} Minimal score: {result_min['score']}")

    # Maximal repo (should give high score but capped at 100)
    maximal_repo = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 95.0},
        "file_tree": ["main.py"] * 250,  # 250 Python files
        "file_count": 250,
        "top_level_dirs": ["src", "tests", "docs", "scripts", "config", "data", "models", "api", "utils", "core", "lib"]
    }

    result_max = score_skill("fastapi", maximal_repo)
    assert 0 <= result_max["score"] <= 100, f"Score out of bounds: {result_max['score']}"
    assert result_max["score"] <= 100, "Score should never exceed 100"
    print(f"  {CHECK} Maximal score (capped): {result_max['score']}")


def test_higher_usage_higher_score():
    """Test that deeper usage signals trigger higher scores."""
    print("Testing usage depth correlation...")

    # Low usage: not in dependencies, few files
    low_usage = {
        "dependencies": {},
        "languages": {"Python": 10.0},
        "file_tree": ["main.py"],
        "file_count": 5,
        "top_level_dirs": ["src"]
    }

    # Medium usage: in dependencies, moderate files
    medium_usage = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 45.0},
        "file_tree": ["main.py", "test.py", "api.py"],
        "file_count": 60,
        "top_level_dirs": ["src", "tests", "docs"]
    }

    # High usage: in dependencies, many files, dominant language
    high_usage = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 85.0},
        "file_tree": ["main.py"] * 50,
        "file_count": 150,
        "top_level_dirs": ["src", "tests", "docs", "scripts", "config", "data"]
    }

    score_low = score_skill("fastapi", low_usage)
    score_medium = score_skill("fastapi", medium_usage)
    score_high = score_skill("fastapi", high_usage)

    print(f"  Low usage score: {score_low['score']}")
    print(f"  Medium usage score: {score_medium['score']}")
    print(f"  High usage score: {score_high['score']}")

    assert score_low["score"] < score_medium["score"], "Medium usage should score higher than low"
    assert score_medium["score"] < score_high["score"], "High usage should score higher than medium"
    print(f"  {CHECK} Usage depth correlation verified")


def test_dependency_bonus():
    """Test that being in dependencies adds significant points."""
    print("Testing dependency bonus...")

    base_repo = {
        "dependencies": {},
        "languages": {"Python": 50.0},
        "file_tree": ["main.py", "test.py"],
        "file_count": 30,
        "top_level_dirs": ["src", "tests"]
    }

    with_dep_repo = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 50.0},
        "file_tree": ["main.py", "test.py"],
        "file_count": 30,
        "top_level_dirs": ["src", "tests"]
    }

    score_without = score_skill("fastapi", base_repo)
    score_with = score_skill("fastapi", with_dep_repo)

    print(f"  Without dependency: {score_without['score']}")
    print(f"  With dependency: {score_with['score']}")

    # Should have exactly 30 point difference (dependency bonus)
    assert score_with["score"] == score_without["score"] + 30, "Dependency bonus should be +30"
    assert "in dependencies" in score_with["rationale"], "Rationale should mention dependencies"
    print(f"  {CHECK} Dependency bonus verified (+30 points)")


def test_file_count_bonus():
    """Test that matching file extensions add points."""
    print("Testing file count bonus...")

    no_files = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {},
        "file_tree": [],
        "file_count": 0,
        "top_level_dirs": []
    }

    with_files = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {},
        "file_tree": ["main.py", "test.py", "api.py"],
        "file_count": 3,
        "top_level_dirs": []
    }

    score_no_files = score_skill("python", no_files)
    score_with_files = score_skill("python", with_files)

    print(f"  No matching files: {score_no_files['score']}")
    print(f"  With matching files: {score_with_files['score']}")

    assert score_with_files["score"] > score_no_files["score"], "Matching files should increase score"
    assert "matching files" in score_with_files["rationale"], "Rationale should mention file count"
    print(f"  {CHECK} File count bonus verified")


def test_language_dominance_bonus():
    """Test that dominant language usage adds points."""
    print("Testing language dominance bonus...")

    low_percentage = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 15.0, "JavaScript": 85.0},
        "file_tree": ["main.py"],
        "file_count": 10,
        "top_level_dirs": ["src"]
    }

    high_percentage = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 75.0, "JavaScript": 25.0},
        "file_tree": ["main.py"],
        "file_count": 10,
        "top_level_dirs": ["src"]
    }

    score_low = score_skill("python", low_percentage)
    score_high = score_skill("python", high_percentage)

    print(f"  Low percentage (15%): {score_low['score']}")
    print(f"  High percentage (75%): {score_high['score']}")

    # High percentage should get +20 bonus (threshold is >30%)
    assert score_high["score"] == score_low["score"] + 20, "Language dominance bonus should be +20"
    assert "codebase" in score_high["rationale"], "Rationale should mention codebase percentage"
    print(f"  {CHECK} Language dominance bonus verified (+20 points)")


def test_multiple_skills_sorting():
    """Test that score_multiple_skills returns sorted results."""
    print("Testing multiple skills sorting...")

    repo_summary = {
        "dependencies": {"python": ["fastapi", "pytest"], "javascript": ["react"]},
        "languages": {"Python": 70.0, "JavaScript": 30.0},
        "file_tree": ["main.py", "test.py", "app.jsx"],
        "file_count": 50,
        "top_level_dirs": ["src", "tests", "docs"]
    }

    technologies = ["fastapi", "pytest", "react"]
    results = score_multiple_skills(technologies, repo_summary)

    # Should return 3 results
    assert len(results) == 3, f"Expected 3 results, got {len(results)}"

    # Should be sorted by score descending
    scores = [r["score"] for r in results]
    assert scores == sorted(scores, reverse=True), "Results should be sorted by score (highest first)"

    print(f"  Sorted results:")
    for r in results:
        print(f"    {r['technology']}: {r['score']} - {r['rationale']}")

    print(f"  {CHECK} Multiple skills sorting verified")


def test_rationale_format():
    """Test that rationale strings are properly formatted."""
    print("Testing rationale format...")

    repo_summary = {
        "dependencies": {"python": ["fastapi"]},
        "languages": {"Python": 80.0},
        "file_tree": ["main.py", "test.py"],
        "file_count": 100,
        "top_level_dirs": ["src", "tests", "docs", "scripts"]
    }

    result = score_skill("fastapi", repo_summary)
    rationale = result["rationale"]

    # Should be a non-empty string
    assert isinstance(rationale, str), "Rationale should be a string"
    assert len(rationale) > 0, "Rationale should not be empty"

    # Should not have template holes or unrendered variables
    assert "{{" not in rationale, "Rationale should not contain template markers"
    assert "}}" not in rationale, "Rationale should not contain template markers"
    assert "None" not in rationale, "Rationale should not contain None values"

    print(f"  {CHECK} Rationale format: '{rationale}'")


def test_edge_cases():
    """Test edge cases and unusual inputs."""
    print("Testing edge cases...")

    # Empty repo summary
    empty_repo = {
        "dependencies": {},
        "languages": {},
        "file_tree": [],
        "file_count": 0,
        "top_level_dirs": []
    }

    result = score_skill("fastapi", empty_repo)
    assert 0 <= result["score"] <= 100, "Score should be valid even for empty repo"
    assert result["score"] >= 20, "Should at least get base score"
    print(f"  {CHECK} Empty repo: {result['score']}")

    # Missing optional fields
    minimal_repo = {
        "dependencies": {"python": ["fastapi"]}
    }

    result = score_skill("fastapi", minimal_repo)
    assert 0 <= result["score"] <= 100, "Score should be valid with minimal fields"
    print(f"  {CHECK} Minimal fields: {result['score']}")

    # Case sensitivity
    mixed_case_repo = {
        "dependencies": {"python": ["FastAPI"]},
        "languages": {"PYTHON": 50.0},
        "file_tree": ["Main.PY"],
        "file_count": 1,
        "top_level_dirs": []
    }

    result = score_skill("fastapi", mixed_case_repo)
    assert result["score"] > 20, "Should handle case-insensitive matching"
    print(f"  {CHECK} Case insensitive: {result['score']}")


def run_all_tests():
    """Run all test functions."""
    print("=" * 60)
    print("Phase 33 - Proficiency Scorer Test Suite")
    print("=" * 60)
    print()

    tests = [
        test_deterministic_scoring,
        test_score_boundaries,
        test_higher_usage_higher_score,
        test_dependency_bonus,
        test_file_count_bonus,
        test_language_dominance_bonus,
        test_multiple_skills_sorting,
        test_rationale_format,
        test_edge_cases,
    ]

    passed = 0
    failed = 0

    for test_func in tests:
        try:
            test_func()
            passed += 1
            print()
        except AssertionError as e:
            failed += 1
            print(f"  {CROSS} FAILED: {e}")
            print()
        except Exception as e:
            failed += 1
            print(f"  {CROSS} ERROR: {e}")
            print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed")
    print("=" * 60)

    if failed == 0:
        print(f"{CHECK} All tests passed!")
        return 0
    else:
        print(f"{CROSS} Some tests failed")
        return 1


if __name__ == "__main__":
    exit_code = run_all_tests()
    sys.exit(exit_code)
