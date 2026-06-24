"""
Test suite for backend/agent/prompts.py

Validates that prompt constants are properly defined and contain
essential structural keywords for guiding AI behavior.
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from agent.prompts import SYSTEM_PROMPT, BULLET_INSTRUCTIONS

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_system_prompt_exists():
    """Test that SYSTEM_PROMPT is defined and non-empty."""
    assert SYSTEM_PROMPT, "SYSTEM_PROMPT must be defined"
    assert isinstance(SYSTEM_PROMPT, str), "SYSTEM_PROMPT must be a string"
    assert len(SYSTEM_PROMPT) > 0, "SYSTEM_PROMPT must not be empty"
    print("✓ SYSTEM_PROMPT exists and is non-empty")


def test_system_prompt_contains_tool_guidance():
    """Test that SYSTEM_PROMPT contains guidance about tool usage."""
    assert "tool" in SYSTEM_PROMPT.lower(), "SYSTEM_PROMPT must mention 'tool'"
    assert "detect_stack" in SYSTEM_PROMPT.lower(), "SYSTEM_PROMPT must reference detect_stack tool"
    print("✓ SYSTEM_PROMPT contains tool usage guidance")


def test_system_prompt_contains_role_definition():
    """Test that SYSTEM_PROMPT defines the AI's role clearly."""
    prompt_lower = SYSTEM_PROMPT.lower()
    assert any(word in prompt_lower for word in ["resume", "architect", "expert"]), \
        "SYSTEM_PROMPT must define the AI's role"
    print("✓ SYSTEM_PROMPT contains clear role definition")


def test_bullet_instructions_exists():
    """Test that BULLET_INSTRUCTIONS is defined and non-empty."""
    assert BULLET_INSTRUCTIONS, "BULLET_INSTRUCTIONS must be defined"
    assert isinstance(BULLET_INSTRUCTIONS, str), "BULLET_INSTRUCTIONS must be a string"
    assert len(BULLET_INSTRUCTIONS) > 0, "BULLET_INSTRUCTIONS must not be empty"
    print("✓ BULLET_INSTRUCTIONS exists and is non-empty")


def test_bullet_instructions_contains_action_verb_guidance():
    """Test that BULLET_INSTRUCTIONS mandates strong action verbs."""
    instructions_lower = BULLET_INSTRUCTIONS.lower()
    assert "action verb" in instructions_lower, "BULLET_INSTRUCTIONS must mention 'action verb'"
    print("✓ BULLET_INSTRUCTIONS contains action verb guidance")


def test_bullet_instructions_contains_quantification_guidance():
    """Test that BULLET_INSTRUCTIONS requires quantified metrics."""
    instructions_lower = BULLET_INSTRUCTIONS.lower()
    assert any(word in instructions_lower for word in ["quantif", "metric", "measur"]), \
        "BULLET_INSTRUCTIONS must require quantification"
    print("✓ BULLET_INSTRUCTIONS contains quantification guidance")


def test_bullet_instructions_forbids_generic_language():
    """Test that BULLET_INSTRUCTIONS explicitly forbids generic AI fluff."""
    instructions_lower = BULLET_INSTRUCTIONS.lower()
    # Check that it mentions forbidden terms
    assert "leveraged" in instructions_lower or "utilized" in instructions_lower, \
        "BULLET_INSTRUCTIONS must list forbidden generic terms"
    assert "forbidden" in instructions_lower or "avoid" in instructions_lower or "✗" in BULLET_INSTRUCTIONS, \
        "BULLET_INSTRUCTIONS must explicitly forbid certain phrases"
    print("✓ BULLET_INSTRUCTIONS forbids generic AI language")


def test_prompts_are_substantial():
    """Test that prompts are substantial enough to provide meaningful guidance."""
    assert len(SYSTEM_PROMPT) > 200, "SYSTEM_PROMPT should be substantial (>200 chars)"
    assert len(BULLET_INSTRUCTIONS) > 500, "BULLET_INSTRUCTIONS should be comprehensive (>500 chars)"
    print("✓ Prompts are substantial and comprehensive")


def test_prompts_contain_examples():
    """Test that BULLET_INSTRUCTIONS contains examples for clarity."""
    # Look for example indicators
    assert any(indicator in BULLET_INSTRUCTIONS.lower() for indicator in ["example", "✓", "✗", "good:", "bad:"]), \
        "BULLET_INSTRUCTIONS should contain examples"
    print("✓ BULLET_INSTRUCTIONS contains examples")


def main():
    """Run all prompt tests."""
    print("\n" + "="*60)
    print("Testing Phase 24: Prompt Library")
    print("="*60 + "\n")

    tests = [
        test_system_prompt_exists,
        test_system_prompt_contains_tool_guidance,
        test_system_prompt_contains_role_definition,
        test_bullet_instructions_exists,
        test_bullet_instructions_contains_action_verb_guidance,
        test_bullet_instructions_contains_quantification_guidance,
        test_bullet_instructions_forbids_generic_language,
        test_prompts_are_substantial,
        test_prompts_contain_examples,
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ {test.__name__} failed: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ {test.__name__} error: {e}")
            failed += 1

    print("\n" + "="*60)
    print(f"Results: {passed} passed, {failed} failed")
    print("="*60 + "\n")

    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
