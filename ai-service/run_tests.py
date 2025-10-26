#!/usr/bin/env python3
"""
Comprehensive test runner for VirtPLC AI Service
"""
import sys
import subprocess
import argparse
from pathlib import Path


def run_tests(test_type="all", verbose=False, coverage=False):
    """Run tests with specified configuration"""

    base_cmd = [sys.executable, "-m", "pytest"]

    if test_type == "unit":
        base_cmd.extend(["-m", "unit"])
    elif test_type == "integration":
        base_cmd.extend(["-m", "integration"])
    elif test_type == "performance":
        base_cmd.extend(["-m", "performance"])
    elif test_type == "config":
        base_cmd.extend(["tests/test_config.py"])
    elif test_type == "mcp":
        base_cmd.extend(["tests/test_mcp_client.py"])
    elif test_type == "timebase":
        base_cmd.extend(["tests/test_timebase_client.py"])
    elif test_type == "main":
        base_cmd.extend(["tests/test_main.py"])

    if verbose:
        base_cmd.append("-v")

    if coverage:
        base_cmd.extend([
            "--cov=src",
            "--cov-report=html",
            "--cov-report=term-missing",
            "--cov-fail-under=80"
        ])

    # Add test directory
    if test_type == "all":
        base_cmd.append("tests/")

    print(f"Running command: {' '.join(base_cmd)}")

    try:
        result = subprocess.run(base_cmd, cwd=Path(__file__).parent)
        return result.returncode == 0
    except Exception as e:
        print(f"Test execution failed: {e}")
        return False


def run_linting():
    """Run code linting checks"""
    print("Running linting checks...")

    try:
        # Check imports
        result = subprocess.run([
            sys.executable, "-c",
            "import src.config; import src.services.mcp_client; import src.services.timebase_client; import src.main"
        ], cwd=Path(__file__).parent)

        if result.returncode == 0:
            print("✓ All imports successful")
            return True
        else:
            print("✗ Import errors detected")
            return False
    except Exception as e:
        print(f"Linting failed: {e}")
        return False


def run_type_checking():
    """Run type checking with mypy (if available)"""
    print("Running type checking...")

    try:
        result = subprocess.run([
            sys.executable, "-c", "import mypy"
        ], capture_output=True)

        if result.returncode == 0:
            # mypy is available
            mypy_result = subprocess.run([
                sys.executable, "-m", "mypy", "src/"
            ], cwd=Path(__file__).parent)

            if mypy_result.returncode == 0:
                print("✓ Type checking passed")
                return True
            else:
                print("✗ Type checking failed")
                return False
        else:
            print("⚠ mypy not available, skipping type checking")
            return True
    except Exception as e:
        print(f"Type checking failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="VirtPLC AI Service Test Runner")
    parser.add_argument(
        "--type",
        choices=["all", "unit", "integration", "performance", "config", "mcp", "timebase", "main"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Generate coverage report"
    )
    parser.add_argument(
        "--lint",
        action="store_true",
        help="Run linting checks"
    )
    parser.add_argument(
        "--types",
        action="store_true",
        help="Run type checking"
    )

    args = parser.parse_args()

    print("VirtPLC AI Service - Comprehensive Test Suite")
    print("=" * 50)

    success = True

    if args.lint:
        success &= run_linting()

    if args.types:
        success &= run_type_checking()

    # Run tests
    success &= run_tests(args.type, args.verbose, args.coverage)

    print("\n" + "=" * 50)
    if success:
        print("✓ All tests passed!")
        sys.exit(0)
    else:
        print("✗ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()