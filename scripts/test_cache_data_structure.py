#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test script to verify cache data structure matches frontend expectations
"""

import json
import sys
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from backend.models.schemas import AnalyzeResponse, SkillScore, ResumeBullet

def test_cache_structure():
    """Test that cached data structure is compatible with frontend"""

    print("=" * 60)
    print("Testing Cache Data Structure")
    print("=" * 60)

    # Simulate what gets cached
    mock_skills = [
        SkillScore(skill="Python", score=85, rationale="Heavy usage"),
        SkillScore(skill="JavaScript", score=75, rationale="Frontend code"),
        SkillScore(skill="React", score=70, rationale="UI framework"),
    ]

    mock_bullets = [
        ResumeBullet(text="Built scalable backend", category="general"),
        ResumeBullet(text="Implemented REST API", category="general"),
    ]

    # Create response as it would be cached
    response_data = {
        "repo_url": "https://github.com/test/repo",
        "resume_markdown": "# Test Resume\n\nSample content",
        "bullets": [bullet.model_dump() for bullet in mock_bullets],
        "skills": [skill.model_dump() for skill in mock_skills],
        "chart_data": {"data": [], "layout": {}},
    }

    print("\n1. Testing AnalyzeResponse validation...")
    try:
        response = AnalyzeResponse(**response_data)
        print("   ✓ Response validates correctly")
    except Exception as e:
        print(f"   ✗ Validation failed: {e}")
        return False

    print("\n2. Checking skills structure...")
    print(f"   Skills count: {len(response.skills)}")
    for skill in response.skills:
        print(f"   - {skill.skill}: {skill.score}% (has 'skill' and 'score' fields)")

    print("\n3. Verifying frontend compatibility...")
    # Frontend expects: skill.skill, skill.score
    try:
        for skill in response.skills:
            name = skill.skill  # Frontend uses skill.skill
            score = skill.score  # Frontend uses skill.score
            print(f"   ✓ Can access: skill='{name}', score={score}")
    except AttributeError as e:
        print(f"   ✗ Frontend incompatibility: {e}")
        return False

    print("\n4. Testing JSON serialization (cache storage)...")
    try:
        json_str = json.dumps(response_data, indent=2)
        print("   ✓ Serializes to JSON correctly")

        # Test deserialization
        loaded = json.loads(json_str)
        response_from_cache = AnalyzeResponse(**loaded)
        print("   ✓ Deserializes from JSON correctly")

        # Verify skills are accessible
        first_skill = response_from_cache.skills[0]
        print(f"   ✓ First skill from cache: {first_skill.skill} = {first_skill.score}%")

    except Exception as e:
        print(f"   ✗ Serialization failed: {e}")
        return False

    print("\n" + "=" * 60)
    print("✅ All cache structure tests passed!")
    print("=" * 60)
    print("\nFrontend should now correctly handle:")
    print("  - First request: Fresh data from backend")
    print("  - Second request: Cached data with same structure")
    print("  - Both use: skill.skill and skill.score")

    return True

if __name__ == "__main__":
    success = test_cache_structure()
    sys.exit(0 if success else 1)
