"""Phase 56 - Test API contract for target_role parameter.

Validates that the /analyze endpoint accepts an optional target_role parameter
and that it flows through the system correctly.
"""

from __future__ import annotations

import sys
from pathlib import Path

# Add project root to path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from backend.models.schemas import AnalyzeRequest


def test_analyze_request_accepts_target_role():
    """Test that AnalyzeRequest schema accepts optional target_role parameter."""
    # Test without target_role (should work)
    request1 = AnalyzeRequest(repo_url="https://github.com/user/repo")
    assert request1.repo_url == "https://github.com/user/repo"
    assert request1.target_role is None

    # Test with target_role (should work)
    request2 = AnalyzeRequest(
        repo_url="https://github.com/user/repo",
        target_role="Backend Engineer"
    )
    assert request2.repo_url == "https://github.com/user/repo"
    assert request2.target_role == "Backend Engineer"

    print("[PASS] AnalyzeRequest accepts optional target_role parameter")


def test_valid_target_roles():
    """Test that valid target roles are accepted."""
    valid_roles = [
        "Backend Engineer",
        "Frontend Engineer",
        "Data Scientist",
        "ML Engineer",
        "Full Stack Engineer",
        "DevOps Engineer",
        "Data Engineer",
    ]

    for role in valid_roles:
        request = AnalyzeRequest(
            repo_url="https://github.com/user/repo",
            target_role=role
        )
        assert request.target_role == role

    print(f"[PASS] All {len(valid_roles)} valid target roles accepted")


def test_target_role_optional():
    """Test that target_role is truly optional."""
    # Should work without target_role
    request = AnalyzeRequest(repo_url="https://github.com/user/repo")
    assert hasattr(request, 'target_role')
    assert request.target_role is None

    print("[PASS] target_role is optional (defaults to None)")


def main() -> int:
    """Run all API contract tests."""
    print("=" * 60)
    print("Phase 56 - API Contract Tests (target_role parameter)")
    print("=" * 60)

    try:
        test_analyze_request_accepts_target_role()
        test_valid_target_roles()
        test_target_role_optional()

        print("=" * 60)
        print("[SUCCESS] All API contract tests passed!")
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
