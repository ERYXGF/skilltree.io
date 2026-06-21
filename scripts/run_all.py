"""Phase 10 — discover and run every scripts/test_*.py file."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parent
ROOT = SCRIPTS_DIR.parent

# Foundation-phase tests (Phases 1–10). Later phases add more test_*.py files.
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
    print("SkillTree.io — foundation test board (Phases 1–10)\n")
    print(f"{'TEST':<28} {'RESULT':<8}")
    print("-" * 40)

    failures: list[str] = []
    for script in FOUNDATION_TESTS:
        name, passed, output = _run_test(script)
        status = "PASS" if passed else "FAIL"
        print(f"{name:<28} {status:<8}")
        if not passed:
            failures.append(name)
            if output:
                print(output)
                print()

    print("-" * 40)
    passed_count = len(FOUNDATION_TESTS) - len(failures)
    print(f"{passed_count}/{len(FOUNDATION_TESTS)} passed")

    if failures:
        print(f"Failed: {', '.join(failures)}")
        return 1

    print("All foundation tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
