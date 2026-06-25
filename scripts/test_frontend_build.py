#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Phase 36 Test: Validate frontend build process
Tests that the Vite build completes successfully with exit code 0
"""

import subprocess
import sys
import os
from pathlib import Path

# Force UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def test_frontend_build():
    """Test that npm run build executes successfully in the frontend directory"""

    # Get the project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    frontend_dir = project_root / "frontend"

    print("=" * 60)
    print("Phase 36 Test: Frontend Build Validation")
    print("=" * 60)

    # Check if frontend directory exists
    if not frontend_dir.exists():
        print(f"❌ ERROR: Frontend directory not found at {frontend_dir}")
        return False

    print(f"✓ Frontend directory found: {frontend_dir}")

    # Check if package.json exists
    package_json = frontend_dir / "package.json"
    if not package_json.exists():
        print(f"❌ ERROR: package.json not found at {package_json}")
        return False

    print(f"✓ package.json found")

    # Check if node_modules exists, if not suggest npm install
    node_modules = frontend_dir / "node_modules"
    if not node_modules.exists():
        print("\n⚠️  WARNING: node_modules not found")
        print("   Please run 'npm install' in the frontend directory first")
        print(f"   Command: cd {frontend_dir} && npm install")
        return False

    print(f"✓ node_modules found")

    # Run npm run build
    print("\n" + "-" * 60)
    print("Running: npm run build")
    print("-" * 60 + "\n")

    try:
        # Use shell=True on Windows to find npm in PATH
        if sys.platform == 'win32':
            result = subprocess.run(
                "npm run build",
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                shell=True,
                timeout=120  # 2 minute timeout
            )
        else:
            result = subprocess.run(
                ["npm", "run", "build"],
                cwd=str(frontend_dir),
                capture_output=True,
                text=True,
                timeout=120  # 2 minute timeout
            )

        # Print stdout
        if result.stdout:
            print(result.stdout)

        # Print stderr if there are errors
        if result.stderr and result.returncode != 0:
            print("STDERR:", result.stderr, file=sys.stderr)

        # Check exit code
        if result.returncode == 0:
            print("\n" + "=" * 60)
            print("✅ SUCCESS: Frontend build completed successfully!")
            print(f"   Exit code: {result.returncode}")

            # Check if dist directory was created
            dist_dir = frontend_dir / "dist"
            if dist_dir.exists():
                print(f"✓ Build output directory created: {dist_dir}")

                # List some key files
                index_html = dist_dir / "index.html"
                if index_html.exists():
                    print(f"✓ index.html generated")

                assets_dir = dist_dir / "assets"
                if assets_dir.exists():
                    asset_count = len(list(assets_dir.glob("*")))
                    print(f"✓ Assets directory created with {asset_count} files")

            print("=" * 60)
            return True
        else:
            print("\n" + "=" * 60)
            print(f"❌ FAILURE: Build failed with exit code {result.returncode}")
            print("=" * 60)
            return False

    except subprocess.TimeoutExpired:
        print("\n❌ ERROR: Build process timed out after 120 seconds")
        return False
    except FileNotFoundError:
        print("\n❌ ERROR: npm command not found. Please ensure Node.js is installed.")
        return False
    except Exception as e:
        print(f"\n❌ ERROR: Unexpected error during build: {e}")
        return False

if __name__ == "__main__":
    success = test_frontend_build()
    sys.exit(0 if success else 1)
