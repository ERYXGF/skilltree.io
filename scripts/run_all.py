"""Phase 10 — discover and run every scripts/test_*.py file.
Phase 20 — includes Part B ingestion tests.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent

# Foundation-phase tests (Phases 1–10)
FOUNDATION_TESTS = [
    "test_repo_layout.py",
    "test_requirements.py",
    "test_imports.py",
    "test_config.py",
    "test_logging.py",
    "test_schemas.py",
    "test_database.py",
    "test_main_routes.py",
]

# Part B ingestion tests (Phases 14–20)
PART_B_TESTS = [
    "test_url_parser.py",
    "test_github_client.py",
    "test_repo_analyzer.py",
    "test_main_routes.py",  # Re-run with new ingestion tests
]


def _run_test(script_name: str) -> tuple[str, bool, str]:
    path = SCRIPTS_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    return script_name, result.returncode == 0, output


def main() -> int:
    print("SkillTree.io — Master Test Runner\n")
    print("=" * 60)
    print("PART A: Foundation Tests (Phases 1–10)")
    print("=" * 60)
    print(f"{'TEST':<32} {'RESULT':<8}")
    print("-" * 60)

    all_failures: list[str] = []

    # Run foundation tests
    for script in FOUNDATION_TESTS:
        name, passed, output = _run_test(script)
        status = "PASS" if passed else "FAIL"
        print(f"{name:<32} {status:<8}")
        if not passed:
            all_failures.append(f"Foundation: {name}")
            if output:
                print(output)
                print()

    foundation_passed = len(FOUNDATION_TESTS) - len([f for f in all_failures if f.startswith("Foundation:")])
    print("-" * 60)
    print(f"Foundation: {foundation_passed}/{len(FOUNDATION_TESTS)} passed\n")

    # Run Part B tests
    print("=" * 60)
    print("PART B: Ingestion Tests (Phases 14–20)")
    print("=" * 60)
    print(f"{'TEST':<32} {'RESULT':<8}")
    print("-" * 60)

    # Use set to avoid running test_main_routes.py twice
    part_b_unique = []
    seen = set()
    for script in PART_B_TESTS:
        if script not in seen:
            part_b_unique.append(script)
            seen.add(script)

    for script in part_b_unique:
        name, passed, output = _run_test(script)
        status = "PASS" if passed else "FAIL"
        print(f"{name:<32} {status:<8}")
        if not passed:
            all_failures.append(f"Part B: {name}")
            if output:
                print(output)
                print()

    part_b_passed = len(part_b_unique) - len([f for f in all_failures if f.startswith("Part B:")])
    print("-" * 60)
    print(f"Part B: {part_b_passed}/{len(part_b_unique)} passed\n")

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_tests = len(FOUNDATION_TESTS) + len(part_b_unique)
    total_passed = foundation_passed + part_b_passed
    print(f"Total: {total_passed}/{total_tests} tests passed")

    if all_failures:
        print(f"\nFailed tests ({len(all_failures)}):")
        for failure in all_failures:
            print(f"  - {failure}")
        return 1

    print("\nAll tests passed successfully!")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
