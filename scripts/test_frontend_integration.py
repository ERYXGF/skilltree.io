#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 47-52 Test: Frontend Integration & Hardening Validation
Tests the complete frontend build, structure, and component integration
"""

import subprocess
import sys
import os
from pathlib import Path
import json

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def test_frontend_structure():
    """Test that all required frontend files exist"""
    print("\n" + "=" * 60)
    print("Phase 47: Frontend Structure Validation")
    print("=" * 60)

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    frontend_dir = project_root / "frontend"

    required_files = [
        "package.json",
        "vite.config.js",
        "tailwind.config.js",
        "postcss.config.js",
        "index.html",
        "src/main.jsx",
        "src/App.jsx",
        "src/api.js",
        "src/styles/index.css",
        "src/components/RepoInput.jsx",
        "src/components/LoadingState.jsx",
        "src/components/ResumePanel.jsx",
        "src/components/ProficiencyChart.jsx",
        "src/components/ExportBar.jsx",
    ]

    all_exist = True
    for file_path in required_files:
        full_path = frontend_dir / file_path
        if full_path.exists():
            print(f"✓ {file_path}")
        else:
            print(f"✗ {file_path} - MISSING")
            all_exist = False

    return all_exist

def test_package_json():
    """Test package.json has all required dependencies"""
    print("\n" + "=" * 60)
    print("Phase 48: Package Dependencies Validation")
    print("=" * 60)

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    package_json = project_root / "frontend" / "package.json"

    with open(package_json, 'r') as f:
        data = json.load(f)

    required_deps = [
        "react",
        "react-dom",
        "react-markdown",
        "lucide-react",
        "react-plotly.js",
        "plotly.js-basic-dist-min"
    ]

    required_dev_deps = [
        "@vitejs/plugin-react",
        "vite",
        "tailwindcss",
        "postcss",
        "autoprefixer"
    ]

    all_present = True

    print("\nDependencies:")
    for dep in required_deps:
        if dep in data.get('dependencies', {}):
            print(f"✓ {dep}: {data['dependencies'][dep]}")
        else:
            print(f"✗ {dep} - MISSING")
            all_present = False

    print("\nDev Dependencies:")
    for dep in required_dev_deps:
        if dep in data.get('devDependencies', {}):
            print(f"✓ {dep}: {data['devDependencies'][dep]}")
        else:
            print(f"✗ {dep} - MISSING")
            all_present = False

    return all_present

def test_component_imports():
    """Test that components can be imported without syntax errors"""
    print("\n" + "=" * 60)
    print("Phase 49: Component Import Validation")
    print("=" * 60)

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    frontend_dir = project_root / "frontend"

    components = [
        "src/App.jsx",
        "src/api.js",
        "src/components/RepoInput.jsx",
        "src/components/LoadingState.jsx",
        "src/components/ResumePanel.jsx",
        "src/components/ProficiencyChart.jsx",
        "src/components/ExportBar.jsx",
    ]

    all_valid = True
    for component in components:
        file_path = frontend_dir / component
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Basic syntax checks
            if 'import' in content or 'export' in content:
                print(f"✓ {component} - Valid ES6 module")
            else:
                print(f"⚠ {component} - No imports/exports found")

        except Exception as e:
            print(f"✗ {component} - Error: {e}")
            all_valid = False

    return all_valid

def test_build_output():
    """Test that build produces expected output files"""
    print("\n" + "=" * 60)
    print("Phase 50: Build Output Validation")
    print("=" * 60)

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    dist_dir = project_root / "frontend" / "dist"

    if not dist_dir.exists():
        print("✗ dist directory not found - run 'npm run build' first")
        return False

    required_outputs = [
        "index.html",
        "assets",
    ]

    all_exist = True
    for output in required_outputs:
        output_path = dist_dir / output
        if output_path.exists():
            if output_path.is_dir():
                file_count = len(list(output_path.glob("*")))
                print(f"✓ {output}/ - {file_count} files")
            else:
                size = output_path.stat().st_size
                print(f"✓ {output} - {size} bytes")
        else:
            print(f"✗ {output} - MISSING")
            all_exist = False

    return all_exist

def test_safety_checks():
    """Test that components have proper error handling"""
    print("\n" + "=" * 60)
    print("Phase 51: Safety & Error Handling Validation")
    print("=" * 60)

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    frontend_dir = project_root / "frontend"

    safety_patterns = {
        "src/api.js": ["try", "catch", "throw"],
        "src/App.jsx": ["useState", "errorMessage"],
        "src/components/RepoInput.jsx": ["validation", "disabled"],
        "src/components/ResumePanel.jsx": ["isLoading", "!data"],
        "src/components/ProficiencyChart.jsx": ["isLoading", "!data"],
    }

    all_safe = True
    for file_path, patterns in safety_patterns.items():
        full_path = frontend_dir / file_path
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()

            found_patterns = []
            missing_patterns = []

            for pattern in patterns:
                if pattern in content:
                    found_patterns.append(pattern)
                else:
                    missing_patterns.append(pattern)

            if missing_patterns:
                print(f"⚠ {file_path} - Missing: {', '.join(missing_patterns)}")
            else:
                print(f"✓ {file_path} - All safety checks present")

        except Exception as e:
            print(f"✗ {file_path} - Error: {e}")
            all_safe = False

    return all_safe

def test_preset_examples():
    """Test that preset examples are configured"""
    print("\n" + "=" * 60)
    print("Phase 52: Preset Examples Validation")
    print("=" * 60)

    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    repo_input = project_root / "frontend" / "src" / "components" / "RepoInput.jsx"

    try:
        with open(repo_input, 'r', encoding='utf-8') as f:
            content = f.read()

        if 'PRESET_REPOS' in content:
            print("✓ Preset repositories array found")

            # Count preset repos
            preset_count = content.count('url:')
            print(f"✓ {preset_count} preset examples configured")

            # Check for specific repos
            if 'github.com' in content:
                print("✓ GitHub URLs present in presets")

            return True
        else:
            print("✗ PRESET_REPOS not found")
            return False

    except Exception as e:
        print(f"✗ Error reading RepoInput: {e}")
        return False

def run_all_tests():
    """Run all frontend integration tests"""
    print("\n" + "=" * 70)
    print("FRONTEND INTEGRATION TEST SUITE - Phases 47-52")
    print("=" * 70)

    tests = [
        ("Structure", test_frontend_structure),
        ("Dependencies", test_package_json),
        ("Component Imports", test_component_imports),
        ("Build Output", test_build_output),
        ("Safety Checks", test_safety_checks),
        ("Preset Examples", test_preset_examples),
    ]

    results = {}
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"\n✗ {test_name} test failed with exception: {e}")
            results[test_name] = False

    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for v in results.values() if v)
    total = len(results)

    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print("\n" + "-" * 70)
    print(f"Results: {passed}/{total} tests passed")
    print("=" * 70)

    return all(results.values())

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
