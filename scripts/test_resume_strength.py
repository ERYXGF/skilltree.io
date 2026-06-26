"""Phase 57 - Test resume strength scoring.

Tests the resume_strength function that scores resume quality based on:
- Quantified bullets (with numbers)
- Action verb starts
- Skill diversity
- Bullet length optimization
- Technical depth
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.core.resume_builder import resume_strength


def test_resume_strength_basic():
    """Test basic resume strength scoring."""
    bullets = [
        "Built FastAPI REST API with 99.9% uptime",
        "Implemented React frontend with TypeScript",
        "Deployed to AWS with Docker containers"
    ]

    skills = [
        {"technology": "fastapi", "score": 85},
        {"technology": "react", "score": 75},
        {"technology": "typescript", "score": 70},
        {"technology": "docker", "score": 65},
        {"technology": "aws", "score": 60}
    ]

    result = resume_strength(bullets, skills)

    assert "score" in result
    assert "tips" in result
    assert isinstance(result["score"], int)
    assert 0 <= result["score"] <= 100
    assert isinstance(result["tips"], list)

    print(f"[PASS] Basic resume strength: {result['score']}/100")


def test_quantified_bullets_increase_score():
    """Test that quantified bullets (with numbers) increase the score."""
    # Resume without numbers
    bullets_no_numbers = [
        "Built a REST API",
        "Implemented frontend features",
        "Deployed to cloud"
    ]

    # Resume with numbers
    bullets_with_numbers = [
        "Built REST API serving 1M+ requests daily",
        "Implemented 15+ frontend features",
        "Deployed to cloud with 99.9% uptime"
    ]

    skills = [{"technology": "python", "score": 80}]

    score_without = resume_strength(bullets_no_numbers, skills)["score"]
    score_with = resume_strength(bullets_with_numbers, skills)["score"]

    assert score_with > score_without, "Quantified bullets should increase score"
    print(f"[PASS] Quantified bullets increase score: {score_without} -> {score_with}")


def test_action_verbs_increase_score():
    """Test that bullets starting with action verbs increase the score."""
    # Weak bullets (no action verbs)
    bullets_weak = [
        "Responsible for API development",
        "Worked on frontend features",
        "Involved in deployment"
    ]

    # Strong bullets (action verbs)
    bullets_strong = [
        "Developed REST API with FastAPI",
        "Implemented responsive frontend",
        "Deployed microservices to AWS"
    ]

    skills = [{"technology": "python", "score": 80}]

    score_weak = resume_strength(bullets_weak, skills)["score"]
    score_strong = resume_strength(bullets_strong, skills)["score"]

    assert score_strong > score_weak, "Action verbs should increase score"
    print(f"[PASS] Action verbs increase score: {score_weak} -> {score_strong}")


def test_skill_diversity_bonus():
    """Test that diverse skills increase the score."""
    bullets = ["Built full-stack application"]

    # Few skills
    skills_few = [
        {"technology": "python", "score": 80}
    ]

    # Many diverse skills
    skills_many = [
        {"technology": "python", "score": 80},
        {"technology": "react", "score": 75},
        {"technology": "postgresql", "score": 70},
        {"technology": "docker", "score": 65},
        {"technology": "aws", "score": 60}
    ]

    score_few = resume_strength(bullets, skills_few)["score"]
    score_many = resume_strength(bullets, skills_many)["score"]

    assert score_many > score_few, "Skill diversity should increase score"
    print(f"[PASS] Skill diversity increases score: {score_few} -> {score_many}")


def test_optimal_bullet_length():
    """Test that optimal bullet length (60-120 chars) increases score."""
    skills = [{"technology": "python", "score": 80}]

    # Too short
    bullets_short = ["Built API"]

    # Optimal length
    bullets_optimal = [
        "Built scalable REST API using FastAPI framework with comprehensive test coverage"
    ]

    # Too long
    bullets_long = [
        "Built a highly scalable and performant REST API using the FastAPI framework with comprehensive test coverage including unit tests, integration tests, and end-to-end tests, deployed to AWS with Docker containers and monitored with CloudWatch"
    ]

    score_short = resume_strength(bullets_short, skills)["score"]
    score_optimal = resume_strength(bullets_optimal, skills)["score"]
    score_long = resume_strength(bullets_long, skills)["score"]

    assert score_optimal >= score_short, "Optimal length should be better than too short"
    assert score_optimal >= score_long, "Optimal length should be better than too long"
    print(f"[PASS] Optimal bullet length: short={score_short}, optimal={score_optimal}, long={score_long}")


def test_technical_depth_bonus():
    """Test that advanced/high-scoring skills increase the score."""
    bullets = ["Built application"]

    # Low proficiency skills
    skills_low = [
        {"technology": "html", "score": 30},
        {"technology": "css", "score": 35}
    ]

    # High proficiency skills
    skills_high = [
        {"technology": "kubernetes", "score": 85},
        {"technology": "tensorflow", "score": 90}
    ]

    score_low = resume_strength(bullets, skills_low)["score"]
    score_high = resume_strength(bullets, skills_high)["score"]

    assert score_high > score_low, "Advanced skills should increase score"
    print(f"[PASS] Technical depth increases score: {score_low} -> {score_high}")


def test_tips_provided():
    """Test that helpful tips are provided for improvement."""
    # Weak resume
    bullets = ["Did some work"]
    skills = [{"technology": "python", "score": 50}]

    result = resume_strength(bullets, skills)

    assert len(result["tips"]) > 0, "Should provide improvement tips"
    assert any("quantif" in tip.lower() for tip in result["tips"]), "Should suggest quantification"

    print(f"[PASS] Provides {len(result['tips'])} improvement tips")


def test_perfect_resume():
    """Test a near-perfect resume gets high score."""
    bullets = [
        "Architected microservices platform serving 10M+ daily users with 99.99% uptime",
        "Optimized database queries reducing response time by 60% and saving $50K annually",
        "Implemented CI/CD pipeline deploying 100+ releases per month with zero downtime",
        "Led team of 5 engineers delivering 20+ features across 3 major product releases"
    ]

    skills = [
        {"technology": "kubernetes", "score": 90},
        {"technology": "postgresql", "score": 85},
        {"technology": "python", "score": 88},
        {"technology": "react", "score": 82},
        {"technology": "docker", "score": 87},
        {"technology": "aws", "score": 85}
    ]

    result = resume_strength(bullets, skills)

    assert result["score"] >= 80, f"Perfect resume should score high, got {result['score']}"
    print(f"[PASS] Perfect resume scores high: {result['score']}/100")


def main() -> int:
    """Run all resume strength tests."""
    print("=" * 60)
    print("Phase 57 - Resume Strength Score Tests")
    print("=" * 60)

    try:
        test_resume_strength_basic()
        test_quantified_bullets_increase_score()
        test_action_verbs_increase_score()
        test_skill_diversity_bonus()
        test_optimal_bullet_length()
        test_technical_depth_bonus()
        test_tips_provided()
        test_perfect_resume()

        print("=" * 60)
        print("[SUCCESS] All resume strength tests passed!")
        print("=" * 60)
        return 0

    except AssertionError as e:
        print(f"\n[FAIL] Test failed: {e}")
        return 1
    except Exception as e:
        print(f"\n[ERROR] Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
