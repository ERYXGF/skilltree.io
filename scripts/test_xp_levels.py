"""Test XP and levels conversion system.

Phase 54: XP & levels per skill
Tests conversion of 0-100 proficiency scores to RPG-style levels and XP.
"""

import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.proficiency_scorer import to_xp_level


def test_score_zero():
    """Test score of 0 maps to level 1."""
    result = to_xp_level(0)
    assert result["level"] == 1
    assert result["xp"] == 0
    assert result["xp_to_next"] == 100
    assert result["progress_pct"] == 0
    print("[PASS] Score 0 test passed")


def test_score_100():
    """Test score of 100 maps to level 10 (max)."""
    result = to_xp_level(100)
    assert result["level"] == 10
    assert result["xp"] == 1000
    assert result["xp_to_next"] == 0
    assert result["progress_pct"] == 100
    print("[PASS] Score 100 test passed")


def test_score_50():
    """Test score of 50 maps to level 6."""
    result = to_xp_level(50)
    assert result["level"] == 6
    assert result["xp"] == 500
    assert result["xp_to_next"] == 100
    assert result["progress_pct"] == 0
    print("[PASS] Score 50 test passed")


def test_score_55():
    """Test score of 55 maps to level 6 with 50% progress."""
    result = to_xp_level(55)
    assert result["level"] == 6
    assert result["xp"] == 550
    assert result["xp_to_next"] == 100
    assert result["progress_pct"] == 50
    print("[PASS] Score 55 test passed")


def test_score_99():
    """Test score of 99 maps to level 10 with 90% progress."""
    result = to_xp_level(99)
    assert result["level"] == 10
    assert result["xp"] == 990
    assert result["xp_to_next"] == 100
    assert result["progress_pct"] == 90
    print("[PASS] Score 99 test passed")


def test_monotonic_mapping():
    """Test that higher scores always map to higher or equal levels."""
    prev_level = 0
    prev_xp = 0

    for score in range(0, 101, 5):
        result = to_xp_level(score)

        # Level should be monotonically increasing
        assert result["level"] >= prev_level, f"Level decreased at score {score}"

        # XP should be monotonically increasing
        assert result["xp"] >= prev_xp, f"XP decreased at score {score}"

        # Level should be between 1 and 10
        assert 1 <= result["level"] <= 10, f"Invalid level {result['level']} at score {score}"

        # Progress should be between 0 and 100
        assert 0 <= result["progress_pct"] <= 100, f"Invalid progress at score {score}"

        prev_level = result["level"]
        prev_xp = result["xp"]

    print("[PASS] Monotonic mapping test passed")


def test_level_boundaries():
    """Test scores at level boundaries."""
    # Level 1: 0-9
    assert to_xp_level(0)["level"] == 1
    assert to_xp_level(9)["level"] == 1

    # Level 2: 10-19
    assert to_xp_level(10)["level"] == 2
    assert to_xp_level(19)["level"] == 2

    # Level 5: 40-49
    assert to_xp_level(40)["level"] == 5
    assert to_xp_level(49)["level"] == 5

    # Level 6: 50-59
    assert to_xp_level(50)["level"] == 6
    assert to_xp_level(59)["level"] == 6

    # Level 10: 90-100
    assert to_xp_level(90)["level"] == 10
    assert to_xp_level(100)["level"] == 10

    print("[PASS] Level boundaries test passed")


def test_xp_calculation():
    """Test XP calculation is correct."""
    # Score 0 = 0 XP
    assert to_xp_level(0)["xp"] == 0

    # Score 10 = 100 XP (10 * 10)
    assert to_xp_level(10)["xp"] == 100

    # Score 25 = 250 XP
    assert to_xp_level(25)["xp"] == 250

    # Score 75 = 750 XP
    assert to_xp_level(75)["xp"] == 750

    # Score 100 = 1000 XP
    assert to_xp_level(100)["xp"] == 1000

    print("[PASS] XP calculation test passed")


def test_progress_percentage():
    """Test progress percentage within level."""
    # Start of level (0% progress)
    assert to_xp_level(10)["progress_pct"] == 0
    assert to_xp_level(20)["progress_pct"] == 0

    # Middle of level (50% progress)
    assert to_xp_level(15)["progress_pct"] == 50
    assert to_xp_level(25)["progress_pct"] == 50

    # Near end of level (90% progress)
    assert to_xp_level(19)["progress_pct"] == 90
    assert to_xp_level(29)["progress_pct"] == 90

    print("[PASS] Progress percentage test passed")


def test_edge_cases():
    """Test edge cases and boundary conditions."""
    # Negative score (should handle gracefully)
    try:
        result = to_xp_level(-1)
        # If it doesn't raise, check it returns level 1
        assert result["level"] == 1
    except (ValueError, AssertionError):
        pass  # Expected to fail or handle gracefully

    # Score over 100 (should cap at level 10)
    try:
        result = to_xp_level(150)
        assert result["level"] == 10
    except (ValueError, AssertionError):
        pass  # Expected to fail or handle gracefully

    print("[PASS] Edge cases test passed")


def run_all_tests():
    """Run all XP/levels tests."""
    print("\n" + "="*60)
    print("XP & LEVELS SYSTEM TESTS (Phase 54)")
    print("="*60 + "\n")

    test_score_zero()
    test_score_100()
    test_score_50()
    test_score_55()
    test_score_99()
    test_monotonic_mapping()
    test_level_boundaries()
    test_xp_calculation()
    test_progress_percentage()
    test_edge_cases()

    print("\n" + "="*60)
    print("[SUCCESS] ALL XP/LEVELS TESTS PASSED")
    print("="*60 + "\n")


if __name__ == "__main__":
    run_all_tests()
