"""Phase 10 — discover and run every scripts/test_*.py file.
Phase 20 — includes Part B ingestion tests.
Phase 35 — includes Part D scoring & resume assembly tests.
Phase 52 — includes Part E frontend integration tests.
Phase 55 — includes Part F stretch features tests.
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

# Part D scoring & resume assembly tests (Phases 33–35)
PART_D_TESTS = [
    "test_proficiency_scorer.py",
    "test_resume_builder.py",
    "test_chart_data.py",
]

# Part E frontend integration tests (Phases 36–52)
PART_E_TESTS = [
    "test_frontend_build.py",
    "test_frontend_integration.py",
]

# Part F stretch features tests (Phases 53–80)
PART_F_TESTS = [
    "test_skilltree_data.py",
    "test_xp_levels.py",
    "test_recommender.py",
    "test_api_contract.py",
    "test_resume_strength.py",
    "test_share.py",
]


def _run_test(script_name: str) -> tuple[str, bool, str]:
    path = SCRIPTS_DIR / script_name
    result = subprocess.run(
        [sys.executable, str(path)],
        cwd=ROOT,
        capture_output=True,
        text=True,
        encoding='utf-8',
        errors='replace',
    )
    stdout = result.stdout or ""
    stderr = result.stderr or ""
    output = (stdout + stderr).strip()
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
                try:
                    print(output)
                except UnicodeEncodeError:
                    print(output.encode('ascii', 'replace').decode('ascii'))
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
                try:
                    print(output)
                except UnicodeEncodeError:
                    print(output.encode('ascii', 'replace').decode('ascii'))
                print()

    part_b_passed = len(part_b_unique) - len([f for f in all_failures if f.startswith("Part B:")])
    print("-" * 60)
    print(f"Part B: {part_b_passed}/{len(part_b_unique)} passed\n")

    # Run Part D tests
    print("=" * 60)
    print("PART D: Scoring & Resume Assembly (Phases 33–35)")
    print("=" * 60)
    print(f"{'TEST':<32} {'RESULT':<8}")
    print("-" * 60)

    for script in PART_D_TESTS:
        name, passed, output = _run_test(script)
        status = "PASS" if passed else "FAIL"
        print(f"{name:<32} {status:<8}")
        if not passed:
            all_failures.append(f"Part D: {name}")
            if output:
                try:
                    print(output)
                except UnicodeEncodeError:
                    print(output.encode('ascii', 'replace').decode('ascii'))
                print()

    part_d_passed = len(PART_D_TESTS) - len([f for f in all_failures if f.startswith("Part D:")])
    print("-" * 60)
    print(f"Part D: {part_d_passed}/{len(PART_D_TESTS)} passed\n")

    # Run Part E tests
    print("=" * 60)
    print("PART E: Frontend Integration (Phases 36–52)")
    print("=" * 60)
    print(f"{'TEST':<32} {'RESULT':<8}")
    print("-" * 60)

    for script in PART_E_TESTS:
        name, passed, output = _run_test(script)
        status = "PASS" if passed else "FAIL"
        print(f"{name:<32} {status:<8}")
        if not passed:
            all_failures.append(f"Part E: {name}")
            if output:
                try:
                    print(output)
                except UnicodeEncodeError:
                    print(output.encode('ascii', 'replace').decode('ascii'))
                print()

    part_e_passed = len(PART_E_TESTS) - len([f for f in all_failures if f.startswith("Part E:")])
    print("-" * 60)
    print(f"Part E: {part_e_passed}/{len(PART_E_TESTS)} passed\n")

    # Run Part F tests
    print("=" * 60)
    print("PART F: Stretch Features (Phases 53–80)")
    print("=" * 60)
    print(f"{'TEST':<32} {'RESULT':<8}")
    print("-" * 60)

    for script in PART_F_TESTS:
        name, passed, output = _run_test(script)
        status = "PASS" if passed else "FAIL"
        print(f"{name:<32} {status:<8}")
        if not passed:
            all_failures.append(f"Part F: {name}")
            if output:
                try:
                    print(output)
                except UnicodeEncodeError:
                    print(output.encode('ascii', 'replace').decode('ascii'))
                print()

    part_f_passed = len(PART_F_TESTS) - len([f for f in all_failures if f.startswith("Part F:")])
    print("-" * 60)
    print(f"Part F: {part_f_passed}/{len(PART_F_TESTS)} passed\n")

    # Summary
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    total_tests = len(FOUNDATION_TESTS) + len(part_b_unique) + len(PART_D_TESTS) + len(PART_E_TESTS) + len(PART_F_TESTS)
    total_passed = foundation_passed + part_b_passed + part_d_passed + part_e_passed + part_f_passed
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
