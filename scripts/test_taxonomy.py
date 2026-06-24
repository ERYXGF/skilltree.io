"""
Test script for tech taxonomy and job descriptions data files.
Phase 22 & 23 validation.
"""

import json
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_path))

# Set UTF-8 encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')


def test_tech_taxonomy():
    """Test that tech_taxonomy.json is valid and properly structured."""
    print("Testing tech_taxonomy.json...")

    taxonomy_path = backend_path / "data" / "tech_taxonomy.json"

    # Load the file
    try:
        with open(taxonomy_path, 'r', encoding='utf-8') as f:
            taxonomy = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON in tech_taxonomy.json: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ FAILED: tech_taxonomy.json not found at {taxonomy_path}")
        return False

    # Validate structure
    if not isinstance(taxonomy, dict):
        print("❌ FAILED: tech_taxonomy.json must be a JSON object")
        return False

    if len(taxonomy) == 0:
        print("❌ FAILED: tech_taxonomy.json is empty")
        return False

    # Validate each entry
    for tech, data in taxonomy.items():
        if not isinstance(data, dict):
            print(f"❌ FAILED: Entry '{tech}' is not an object")
            return False

        # Check for exactly the required keys
        if set(data.keys()) != {"skill", "job_family"}:
            print(f"❌ FAILED: Entry '{tech}' must have exactly 'skill' and 'job_family' keys")
            print(f"   Found keys: {list(data.keys())}")
            return False

        # Check that values are strings
        if not isinstance(data["skill"], str):
            print(f"❌ FAILED: Entry '{tech}' has non-string 'skill' value")
            return False

        if not isinstance(data["job_family"], str):
            print(f"❌ FAILED: Entry '{tech}' has non-string 'job_family' value")
            return False

        # Check that values are not empty
        if not data["skill"].strip():
            print(f"❌ FAILED: Entry '{tech}' has empty 'skill' value")
            return False

        if not data["job_family"].strip():
            print(f"❌ FAILED: Entry '{tech}' has empty 'job_family' value")
            return False

    print(f"✅ PASSED: tech_taxonomy.json is valid with {len(taxonomy)} entries")
    return True


def test_job_descriptions():
    """Test that job_descriptions.json covers all job families from taxonomy."""
    print("\nTesting job_descriptions.json...")

    taxonomy_path = backend_path / "data" / "tech_taxonomy.json"
    jd_path = backend_path / "data" / "job_descriptions.json"

    # Load taxonomy
    try:
        with open(taxonomy_path, 'r', encoding='utf-8') as f:
            taxonomy = json.load(f)
    except Exception as e:
        print(f"❌ FAILED: Could not load tech_taxonomy.json: {e}")
        return False

    # Load job descriptions
    try:
        with open(jd_path, 'r', encoding='utf-8') as f:
            job_descriptions = json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ FAILED: Invalid JSON in job_descriptions.json: {e}")
        return False
    except FileNotFoundError:
        print(f"❌ FAILED: job_descriptions.json not found at {jd_path}")
        return False

    # Extract all unique job families from taxonomy
    job_families = set()
    for tech, data in taxonomy.items():
        job_families.add(data["job_family"])

    print(f"Found {len(job_families)} unique job families in taxonomy:")
    for family in sorted(job_families):
        print(f"  - {family}")

    # Check that all job families exist in job_descriptions.json
    missing_families = []
    for family in job_families:
        if family not in job_descriptions:
            missing_families.append(family)

    if missing_families:
        print(f"\n❌ FAILED: Missing job families in job_descriptions.json:")
        for family in sorted(missing_families):
            print(f"  - {family}")
        return False

    print(f"\n✅ PASSED: All {len(job_families)} job families are covered in job_descriptions.json")
    return True


def main():
    """Run all tests."""
    print("=" * 60)
    print("Phase 22 & 23: Tech Taxonomy and Job Descriptions Tests")
    print("=" * 60)

    results = []

    # Phase 22 test
    results.append(test_tech_taxonomy())

    # Phase 23 test (only if Phase 22 passed)
    if results[0]:
        results.append(test_job_descriptions())
    else:
        print("\n⚠️  Skipping job_descriptions test due to taxonomy test failure")

    print("\n" + "=" * 60)
    if all(results):
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    else:
        print("❌ SOME TESTS FAILED")
        print("=" * 60)
        return 1


if __name__ == "__main__":
    sys.exit(main())
