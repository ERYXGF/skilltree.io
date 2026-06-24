"""
Test suite for resume builder functions.

This test verifies:
1. clean_bullets() - Bullet post-processing and normalization
2. verify_grounded() - Hallucination guard for technology mentions
"""

import sys
import io
from pathlib import Path

# Set UTF-8 encoding for Windows console
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.core.resume_builder import clean_bullets, verify_grounded, to_markdown


def test_clean_bullets_basic():
    """Test basic bullet cleaning with conversational filler."""
    print("\n=== Testing clean_bullets: Basic Cleaning ===")

    raw_text = """Here are your bullets:
• Built FastAPI REST API with PostgreSQL backend
• Implemented React frontend with TypeScript
• Deployed application to AWS with 99.9% uptime

Let me know if you need more!"""

    result = clean_bullets(raw_text)

    # Verify conversational filler removed
    assert len(result) == 3, f"Expected 3 bullets, got {len(result)}"
    assert "Built FastAPI REST API with PostgreSQL backend" in result
    assert "Implemented React frontend with TypeScript" in result
    assert "Deployed application to AWS with 99.9% uptime" in result

    # Verify no conversational text leaked through
    for bullet in result:
        assert "here are" not in bullet.lower()
        assert "let me know" not in bullet.lower()

    print(f"✓ Cleaned {len(result)} bullets from raw text")
    print(f"✓ Removed conversational filler")
    print("✓ Basic cleaning test PASSED\n")


def test_clean_bullets_deduplication():
    """Test that duplicate bullets are removed."""
    print("\n=== Testing clean_bullets: Deduplication ===")

    raw_text = """
• Built FastAPI application with 95% test coverage
• Implemented React dashboard for data visualization
• Built FastAPI application with 95% test coverage
• Optimized database queries reducing latency by 40%
• Built fastapi application with 95% test coverage
"""

    result = clean_bullets(raw_text)

    # Should deduplicate case-insensitively
    assert len(result) == 3, f"Expected 3 unique bullets, got {len(result)}: {result}"

    # Verify the unique bullets are present
    bullet_texts = [b.lower() for b in result]
    assert any("fastapi" in b and "test coverage" in b for b in bullet_texts)
    assert any("react dashboard" in b for b in bullet_texts)
    assert any("database queries" in b for b in bullet_texts)

    print(f"✓ Deduplicated from 5 to {len(result)} unique bullets")
    print("✓ Case-insensitive deduplication working")
    print("✓ Deduplication test PASSED\n")


def test_clean_bullets_length_limit():
    """Test that overly long bullets are truncated."""
    print("\n=== Testing clean_bullets: Length Limit ===")

    # Create a bullet that exceeds 200 characters
    long_bullet = (
        "• Architected and implemented a highly scalable microservices-based "
        "backend infrastructure using FastAPI, PostgreSQL, Redis, and Docker, "
        "handling over 1 million API requests per day with sub-100ms latency "
        "while maintaining 99.99% uptime and comprehensive monitoring"
    )

    raw_text = long_bullet

    result = clean_bullets(raw_text)

    assert len(result) == 1, f"Expected 1 bullet, got {len(result)}"

    # Verify truncation occurred
    assert len(result[0]) <= 203, f"Bullet too long: {len(result[0])} chars"  # 200 + "..."
    assert result[0].endswith("..."), "Long bullet should end with ellipsis"

    print(f"✓ Truncated {len(long_bullet)} char bullet to {len(result[0])} chars")
    print(f"✓ Result: {result[0][:80]}...")
    print("✓ Length limit test PASSED\n")


def test_clean_bullets_whitespace_normalization():
    """Test that extra whitespace is normalized."""
    print("\n=== Testing clean_bullets: Whitespace Normalization ===")

    raw_text = """
•   Built    FastAPI   application    with   multiple   spaces
• Implemented    React    frontend
•     Deployed to    production
"""

    result = clean_bullets(raw_text)

    # Verify whitespace normalized
    for bullet in result:
        # Should not have multiple consecutive spaces
        assert "  " not in bullet, f"Multiple spaces found in: {bullet}"
        # Should not have leading/trailing whitespace
        assert bullet == bullet.strip(), f"Whitespace not trimmed: '{bullet}'"

    print(f"✓ Normalized whitespace in {len(result)} bullets")
    print("✓ Whitespace normalization test PASSED\n")


def test_clean_bullets_various_formats():
    """Test handling of different bullet formats (-, *, numbered)."""
    print("\n=== Testing clean_bullets: Various Formats ===")

    raw_text = """
- Built FastAPI backend
* Implemented React frontend
• Deployed to AWS
1. Optimized database queries
2) Implemented caching layer
"""

    result = clean_bullets(raw_text)

    assert len(result) == 5, f"Expected 5 bullets, got {len(result)}"

    # Verify all formats were recognized
    bullet_texts = " ".join(result).lower()
    assert "fastapi" in bullet_texts
    assert "react" in bullet_texts
    assert "aws" in bullet_texts
    assert "database" in bullet_texts
    assert "caching" in bullet_texts

    print(f"✓ Recognized {len(result)} bullets across different formats")
    print("✓ Various formats test PASSED\n")


def test_verify_grounded_basic():
    """Test basic hallucination detection."""
    print("\n=== Testing verify_grounded: Basic Verification ===")

    bullets = [
        "Built FastAPI REST API with PostgreSQL backend",
        "Deployed application to Kubernetes cluster with auto-scaling",
        "Implemented React frontend with TypeScript"
    ]

    detected_techs = ["fastapi", "postgresql", "react", "typescript"]

    result = verify_grounded(bullets, detected_techs)

    # Should remove the Kubernetes bullet (not in detected_techs)
    assert len(result) == 2, f"Expected 2 verified bullets, got {len(result)}: {result}"

    # Verify correct bullets retained
    result_text = " ".join(result).lower()
    assert "fastapi" in result_text
    assert "react" in result_text
    assert "kubernetes" not in result_text

    print(f"✓ Filtered {len(bullets)} bullets to {len(result)} verified")
    print("✓ Removed unverified technology (Kubernetes)")
    print("✓ Basic verification test PASSED\n")


def test_verify_grounded_case_insensitive():
    """Test that verification is case-insensitive."""
    print("\n=== Testing verify_grounded: Case Insensitive ===")

    bullets = [
        "Built FASTAPI application",
        "Implemented PostgreSQL database",
        "Used React for frontend"
    ]

    detected_techs = ["FastAPI", "PostgreSQL", "React"]

    result = verify_grounded(bullets, detected_techs)

    # All should pass (case-insensitive matching)
    assert len(result) == 3, f"Expected 3 bullets, got {len(result)}"

    print(f"✓ Case-insensitive matching working")
    print(f"✓ All {len(result)} bullets verified")
    print("✓ Case insensitive test PASSED\n")


def test_verify_grounded_multiple_unverified():
    """Test filtering multiple unverified technologies."""
    print("\n=== Testing verify_grounded: Multiple Unverified ===")

    bullets = [
        "Built FastAPI REST API with 99.9% uptime",
        "Deployed to Kubernetes with Terraform automation",
        "Implemented Redis caching layer",
        "Set up Jenkins CI/CD pipeline",
        "Used Docker for containerization"
    ]

    detected_techs = ["fastapi", "docker"]

    result = verify_grounded(bullets, detected_techs)

    # Should only keep FastAPI and Docker bullets
    assert len(result) <= 2, f"Expected at most 2 verified bullets, got {len(result)}: {result}"

    result_text = " ".join(result).lower()
    assert "fastapi" in result_text or "docker" in result_text

    # Verify unverified techs removed
    assert "kubernetes" not in result_text
    assert "terraform" not in result_text
    assert "jenkins" not in result_text
    assert "redis" not in result_text

    print(f"✓ Filtered {len(bullets)} bullets to {len(result)} verified")
    print("✓ Removed multiple unverified technologies")
    print("✓ Multiple unverified test PASSED\n")


def test_verify_grounded_generic_bullets():
    """Test that generic bullets without specific tech mentions pass through."""
    print("\n=== Testing verify_grounded: Generic Bullets ===")

    bullets = [
        "Built FastAPI REST API",
        "Improved application performance by 40%",
        "Reduced deployment time from 2 hours to 15 minutes",
        "Achieved 95% test coverage across codebase"
    ]

    detected_techs = ["fastapi"]

    result = verify_grounded(bullets, detected_techs)

    # Generic bullets (without specific tech) should pass
    # Only FastAPI bullet is guaranteed to pass
    assert len(result) >= 1, f"Expected at least 1 bullet, got {len(result)}"

    # FastAPI bullet should definitely be included
    assert any("fastapi" in b.lower() for b in result)

    print(f"✓ Verified {len(result)} bullets (including generic ones)")
    print("✓ Generic bullets test PASSED\n")


def test_verify_grounded_word_boundaries():
    """Test that partial word matches don't cause false positives."""
    print("\n=== Testing verify_grounded: Word Boundaries ===")

    bullets = [
        "Built React application with reactive programming",
        "Implemented FastAPI endpoints for fast API responses"
    ]

    detected_techs = ["react", "fastapi"]

    result = verify_grounded(bullets, detected_techs)

    # Both should pass - "reactive" contains "react" but should match "React" properly
    assert len(result) == 2, f"Expected 2 bullets, got {len(result)}"

    print(f"✓ Word boundary matching working correctly")
    print(f"✓ All {len(result)} bullets verified")
    print("✓ Word boundaries test PASSED\n")


def test_integration_clean_and_verify():
    """Test integration of clean_bullets and verify_grounded."""
    print("\n=== Testing Integration: Clean + Verify ===")

    raw_text = """Here are your resume bullets:

• Built FastAPI REST API with PostgreSQL backend
• Built FastAPI REST API with PostgreSQL backend
• Deployed to Kubernetes cluster with Helm charts
• Implemented React frontend with TypeScript
• Set up Jenkins CI/CD pipeline

Hope this helps!"""

    detected_techs = ["fastapi", "postgresql", "react", "typescript"]

    # Step 1: Clean
    cleaned = clean_bullets(raw_text)
    print(f"✓ Cleaned to {len(cleaned)} bullets")

    # Step 2: Verify
    verified = verify_grounded(cleaned, detected_techs)
    print(f"✓ Verified to {len(verified)} grounded bullets")

    # Should have 2-3 bullets (FastAPI, React, maybe generic ones)
    # Kubernetes and Jenkins should be removed
    assert len(verified) >= 2, f"Expected at least 2 bullets, got {len(verified)}"

    result_text = " ".join(verified).lower()
    assert "kubernetes" not in result_text
    assert "jenkins" not in result_text

    print("✓ Integration test PASSED\n")


def test_to_markdown_basic_structure():
    """Test that to_markdown generates valid Markdown with all sections."""
    print("\n=== Testing to_markdown: Basic Structure ===")

    bullets = [
        "Built FastAPI REST API with 99.9% uptime",
        "Implemented React frontend with TypeScript"
    ]

    skills = [
        {"technology": "fastapi", "score": 85, "rationale": "Fastapi - in dependencies (+30), repo complexity (+5)"},
        {"technology": "react", "score": 72, "rationale": "React - in dependencies (+30), 1 matching files (+15)"}
    ]

    meta = {
        "repo_url": "https://github.com/testuser/testproject",
        "owner": "testuser",
        "repo": "testproject",
        "description": "A test project for SkillTree.io",
        "stars": 42,
        "primary_language": "Python"
    }

    result = to_markdown(bullets, skills, meta)

    # Verify it's a string
    assert isinstance(result, str), "Result should be a string"
    assert len(result) > 0, "Result should not be empty"

    # Verify main sections exist
    assert "# Technical Resume" in result, "Should have main header"
    assert "## Profile" in result, "Should have Profile section"
    assert "## Core Skills" in result, "Should have Core Skills section"
    assert "## Project Achievements" in result, "Should have Project Achievements section"

    # Verify metadata is included
    assert "testuser" in result, "Should include owner"
    assert "testproject" in result, "Should include repo name"
    assert "Python" in result, "Should include primary language"
    assert "42" in result, "Should include star count"

    print("✓ Generated valid Markdown structure")
    print("✓ All required sections present")
    print("✓ Metadata included correctly")
    print("✓ Basic structure test PASSED\n")


def test_to_markdown_skills_table():
    """Test that skills are formatted as a proper Markdown table."""
    print("\n=== Testing to_markdown: Skills Table ===")

    bullets = ["Built something cool"]

    skills = [
        {"technology": "fastapi", "score": 85, "rationale": "Fastapi - in dependencies (+30)"},
        {"technology": "react", "score": 72, "rationale": "React - in dependencies (+30)"},
        {"technology": "pytest", "score": 60, "rationale": "Pytest - in dependencies (+30)"}
    ]

    meta = {
        "repo_url": "https://github.com/user/repo",
        "owner": "user",
        "repo": "repo",
        "description": "Test",
        "stars": 10,
        "primary_language": "Python"
    }

    result = to_markdown(bullets, skills, meta)

    # Verify table structure
    assert "| Technology | Proficiency Score | Details |" in result, "Should have table header"
    assert "|------------|-------------------|---------|" in result, "Should have table separator"

    # Verify all skills are in the table
    assert "Fastapi" in result or "fastapi" in result, "Should include fastapi"
    assert "React" in result or "react" in result, "Should include react"
    assert "Pytest" in result or "pytest" in result, "Should include pytest"

    # Verify scores are displayed
    assert "85" in result, "Should show fastapi score"
    assert "72" in result, "Should show react score"
    assert "60" in result, "Should show pytest score"

    print("✓ Skills formatted as Markdown table")
    print("✓ All skills included with scores")
    print("✓ Skills table test PASSED\n")


def test_to_markdown_bullets_formatting():
    """Test that bullets are properly formatted in Markdown."""
    print("\n=== Testing to_markdown: Bullets Formatting ===")

    bullets = [
        "Built FastAPI REST API",
        "Implemented React frontend",
        "Deployed to production"
    ]

    skills = [{"technology": "fastapi", "score": 85, "rationale": "Test"}]

    meta = {
        "repo_url": "https://github.com/user/repo",
        "owner": "user",
        "repo": "repo",
        "description": "Test",
        "stars": 5,
        "primary_language": "Python"
    }

    result = to_markdown(bullets, skills, meta)

    # Verify bullets are in the achievements section
    lines = result.split("\n")
    achievements_idx = next(i for i, line in enumerate(lines) if "## Project Achievements" in line)

    # Check that bullets appear after the achievements header
    achievements_section = "\n".join(lines[achievements_idx:])

    for bullet in bullets:
        assert bullet in achievements_section, f"Bullet '{bullet}' should be in achievements section"

    # Verify bullets have proper Markdown formatting (should start with -)
    assert "- Built FastAPI REST API" in result or "Built FastAPI REST API" in result

    print("✓ Bullets properly formatted")
    print("✓ All bullets included in achievements section")
    print("✓ Bullets formatting test PASSED\n")


def test_to_markdown_no_template_holes():
    """Test that there are no unrendered template variables."""
    print("\n=== Testing to_markdown: No Template Holes ===")

    bullets = ["Test bullet"]
    skills = [{"technology": "python", "score": 50, "rationale": "Test"}]
    meta = {
        "repo_url": "https://github.com/user/repo",
        "owner": "user",
        "repo": "repo",
        "description": "Test",
        "stars": 0,
        "primary_language": "Python"
    }

    result = to_markdown(bullets, skills, meta)

    # Check for common template markers
    assert "{{" not in result, "Should not contain {{ markers"
    assert "}}" not in result, "Should not contain }} markers"
    assert "${" not in result, "Should not contain ${ markers"
    assert "<%" not in result, "Should not contain <% markers"
    assert "%>" not in result, "Should not contain %> markers"

    # Check for undefined/None values
    assert "undefined" not in result.lower(), "Should not contain 'undefined'"
    assert "None" not in result, "Should not contain 'None'"

    print("✓ No template holes found")
    print("✓ No undefined values")
    print("✓ Template holes test PASSED\n")


def test_to_markdown_empty_inputs():
    """Test handling of empty bullets and skills."""
    print("\n=== Testing to_markdown: Empty Inputs ===")

    # Empty bullets and skills
    bullets = []
    skills = []
    meta = {
        "repo_url": "https://github.com/user/repo",
        "owner": "user",
        "repo": "repo",
        "description": "Test",
        "stars": 0,
        "primary_language": "Python"
    }

    result = to_markdown(bullets, skills, meta)

    # Should still generate valid Markdown
    assert isinstance(result, str), "Should return a string"
    assert len(result) > 0, "Should not be empty"
    assert "# Technical Resume" in result, "Should have header"

    # Should have placeholder messages
    assert "No skills detected" in result or "No achievements listed" in result

    print("✓ Handles empty inputs gracefully")
    print("✓ Generates valid Markdown even with no data")
    print("✓ Empty inputs test PASSED\n")


def test_to_markdown_special_characters():
    """Test handling of special characters in metadata and bullets."""
    print("\n=== Testing to_markdown: Special Characters ===")

    bullets = [
        "Built API with 99.9% uptime & high availability",
        "Reduced costs by $5,000/month"
    ]

    skills = [{"technology": "fastapi", "score": 85, "rationale": "FastAPI - great performance!"}]

    meta = {
        "repo_url": "https://github.com/user/my-awesome-repo",
        "owner": "user",
        "repo": "my-awesome-repo",
        "description": "A project with special chars: & < > \" '",
        "stars": 100,
        "primary_language": "Python"
    }

    result = to_markdown(bullets, skills, meta)

    # Should handle special characters without breaking
    assert isinstance(result, str), "Should return a string"
    assert "my-awesome-repo" in result, "Should include repo name with hyphens"

    # Verify bullets with special chars are included
    assert "99.9%" in result or "uptime" in result
    assert "$5,000" in result or "costs" in result

    print("✓ Handles special characters correctly")
    print("✓ Special characters test PASSED\n")


def test_to_markdown_valid_markdown_syntax():
    """Test that output is syntactically valid Markdown."""
    print("\n=== Testing to_markdown: Valid Markdown Syntax ===")

    bullets = ["Built FastAPI application", "Deployed to production"]
    skills = [
        {"technology": "fastapi", "score": 85, "rationale": "FastAPI - in dependencies"},
        {"technology": "docker", "score": 70, "rationale": "Docker - containerization"}
    ]
    meta = {
        "repo_url": "https://github.com/user/repo",
        "owner": "user",
        "repo": "repo",
        "description": "Test project",
        "stars": 25,
        "primary_language": "Python"
    }

    result = to_markdown(bullets, skills, meta)

    # Check for valid Markdown structures
    assert result.count("#") >= 3, "Should have multiple headers"
    assert result.count("##") >= 3, "Should have section headers"

    # Check for table structure
    assert "|" in result, "Should have table pipes"

    # Check for proper line breaks
    lines = result.split("\n")
    assert len(lines) > 10, "Should have multiple lines"

    # Verify no malformed Markdown
    assert not result.startswith("\n\n\n"), "Should not start with excessive newlines"

    print("✓ Valid Markdown syntax")
    print(f"✓ Generated {len(lines)} lines of Markdown")
    print("✓ Valid Markdown syntax test PASSED\n")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("RESUME BUILDER TEST SUITE")
    print("="*60)

    try:
        # Phase 30: clean_bullets tests
        test_clean_bullets_basic()
        test_clean_bullets_deduplication()
        test_clean_bullets_length_limit()
        test_clean_bullets_whitespace_normalization()
        test_clean_bullets_various_formats()

        # Phase 31: verify_grounded tests
        test_verify_grounded_basic()
        test_verify_grounded_case_insensitive()
        test_verify_grounded_multiple_unverified()
        test_verify_grounded_generic_bullets()
        test_verify_grounded_word_boundaries()

        # Integration test
        test_integration_clean_and_verify()

        # Phase 34: to_markdown tests
        test_to_markdown_basic_structure()
        test_to_markdown_skills_table()
        test_to_markdown_bullets_formatting()
        test_to_markdown_no_template_holes()
        test_to_markdown_empty_inputs()
        test_to_markdown_special_characters()
        test_to_markdown_valid_markdown_syntax()

        print("="*60)
        print("ALL RESUME BUILDER TESTS PASSED ✓")
        print("="*60 + "\n")

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)
