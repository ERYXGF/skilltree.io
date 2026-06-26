"""Phase 60 - Test shareable result link functionality.

Tests the share link system that allows users to:
- Generate short unique IDs for analysis results
- Store analysis results with IDs in database
- Retrieve analysis results by ID
- Track view counts (optional)
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.models.database import (
    save_shared_result,
    get_shared_result,
    generate_share_id
)


def test_generate_share_id():
    """Test that share IDs are generated correctly."""
    share_id = generate_share_id()

    assert isinstance(share_id, str)
    assert len(share_id) == 8, f"Share ID should be 8 chars, got {len(share_id)}"
    assert share_id.isalnum(), "Share ID should be alphanumeric"

    # Generate multiple IDs to check uniqueness
    ids = [generate_share_id() for _ in range(10)]
    assert len(set(ids)) == len(ids), "Share IDs should be unique"

    print(f"[PASS] Generated share ID: {share_id}")


def test_save_and_retrieve_shared_result():
    """Test saving and retrieving a shared result."""
    # Sample analysis result
    result_data = {
        "repo_url": "https://github.com/test/repo",
        "resume_markdown": "# Test Resume",
        "bullets": [{"text": "Built something", "category": "general"}],
        "skills": [{"skill": "python", "score": 85, "rationale": "Test"}],
        "chart_data": {"x": [1, 2, 3], "y": [4, 5, 6]},
        "skill_tree": {"nodes": [], "edges": []}
    }

    # Save the result
    share_id = save_shared_result(result_data)

    assert isinstance(share_id, str)
    assert len(share_id) == 8

    # Retrieve the result
    retrieved = get_shared_result(share_id)

    assert retrieved is not None, "Should retrieve saved result"
    assert retrieved["repo_url"] == result_data["repo_url"]
    assert retrieved["resume_markdown"] == result_data["resume_markdown"]
    assert len(retrieved["bullets"]) == len(result_data["bullets"])
    assert len(retrieved["skills"]) == len(result_data["skills"])

    print(f"[PASS] Save and retrieve round-trip successful: {share_id}")


def test_retrieve_nonexistent_share_id():
    """Test that retrieving a nonexistent share ID returns None."""
    result = get_shared_result("NOTEXIST")

    assert result is None, "Should return None for nonexistent share ID"

    print("[PASS] Nonexistent share ID returns None")


def test_share_id_uniqueness():
    """Test that each save generates a unique share ID."""
    result_data = {
        "repo_url": "https://github.com/test/repo",
        "resume_markdown": "# Test",
        "bullets": [],
        "skills": [],
        "chart_data": {},
        "skill_tree": {}
    }

    # Save multiple times
    ids = []
    for i in range(5):
        share_id = save_shared_result({**result_data, "repo_url": f"https://github.com/test/repo{i}"})
        ids.append(share_id)

    # All IDs should be unique
    assert len(set(ids)) == len(ids), "Each save should generate unique ID"

    print(f"[PASS] Generated {len(ids)} unique share IDs")


def test_share_id_persistence():
    """Test that shared results persist across retrievals."""
    result_data = {
        "repo_url": "https://github.com/test/persistence",
        "resume_markdown": "# Persistence Test",
        "bullets": [],
        "skills": [],
        "chart_data": {},
        "skill_tree": {}
    }

    # Save result
    share_id = save_shared_result(result_data)

    # Retrieve multiple times
    first_retrieval = get_shared_result(share_id)
    second_retrieval = get_shared_result(share_id)

    assert first_retrieval is not None
    assert second_retrieval is not None
    assert first_retrieval["repo_url"] == second_retrieval["repo_url"]

    print("[PASS] Shared results persist across multiple retrievals")


def test_complete_analysis_data():
    """Test that all analysis fields are preserved in shared results."""
    result_data = {
        "repo_url": "https://github.com/facebook/react",
        "resume_markdown": "# React Developer Resume\n\n## Skills\n- React: 95/100",
        "bullets": [
            {"text": "Built component library", "category": "frontend"},
            {"text": "Optimized rendering performance", "category": "performance"}
        ],
        "skills": [
            {"skill": "react", "score": 95, "rationale": "Core library"},
            {"skill": "javascript", "score": 90, "rationale": "Primary language"}
        ],
        "chart_data": {
            "data": [{"x": ["React", "JavaScript"], "y": [95, 90], "type": "bar"}],
            "layout": {"title": "Skills"}
        },
        "skill_tree": {
            "nodes": [
                {"id": "react", "label": "React", "score": 95},
                {"id": "javascript", "label": "JavaScript", "score": 90}
            ],
            "edges": [{"source": "javascript", "target": "react"}]
        }
    }

    share_id = save_shared_result(result_data)
    retrieved = get_shared_result(share_id)

    # Verify all fields are present
    assert "repo_url" in retrieved
    assert "resume_markdown" in retrieved
    assert "bullets" in retrieved
    assert "skills" in retrieved
    assert "chart_data" in retrieved
    assert "skill_tree" in retrieved

    # Verify nested data integrity
    assert len(retrieved["bullets"]) == 2
    assert len(retrieved["skills"]) == 2
    assert retrieved["bullets"][0]["text"] == "Built component library"
    assert retrieved["skills"][0]["skill"] == "react"

    print("[PASS] Complete analysis data preserved in shared result")


def main() -> int:
    """Run all share link tests."""
    print("=" * 60)
    print("Phase 60 - Shareable Result Link Tests")
    print("=" * 60)

    try:
        test_generate_share_id()
        test_save_and_retrieve_shared_result()
        test_retrieve_nonexistent_share_id()
        test_share_id_uniqueness()
        test_share_id_persistence()
        test_complete_analysis_data()

        print("=" * 60)
        print("[SUCCESS] All share link tests passed!")
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
