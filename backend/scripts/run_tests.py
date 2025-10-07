#!/usr/bin/env python3
"""
Test runner script for the Meeting Coach project
"""
import subprocess
import sys
import os
import argparse

def run_tests(test_type="all", verbose=False, coverage=False, markers=None):
    """Run tests with specified parameters."""

    # Build pytest command
    cmd = ["python", "-m", "pytest"]

    # Add test paths based on type
    if test_type == "unit":
        cmd.append("tests/unit/")
    elif test_type == "integration":
        cmd.append("tests/integration/")
    elif test_type == "all":
        cmd.append("tests/")
    else:
        cmd.append(test_type)  # Custom path

    # Add markers if specified
    if markers:
        cmd.extend(["-m", markers])

    # Add verbosity
    if verbose:
        cmd.append("-v")
    else:
        cmd.append("-q")

    # Add coverage if requested
    if coverage:
        cmd.extend(["--cov=.", "--cov-report=term-missing", "--cov-report=html"])

    print(f"Running command: {' '.join(cmd)}")

    # Run the tests
    try:
        result = subprocess.run(cmd, cwd=os.path.dirname(__file__))
        return result.returncode
    except KeyboardInterrupt:
        print("\nTests interrupted by user")
        return 1
    except Exception as e:
        print(f"Error running tests: {e}")
        return 1

def main():
    parser = argparse.ArgumentParser(description="Run Meeting Coach tests")

    parser.add_argument(
        "test_type",
        nargs="?",
        default="all",
        choices=["all", "unit", "integration"],
        help="Type of tests to run (default: all)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output"
    )

    parser.add_argument(
        "-c", "--coverage",
        action="store_true",
        help="Run with coverage reporting"
    )

    parser.add_argument(
        "-m", "--markers",
        help="Run only tests with specific markers (e.g., 'not slow')"
    )

    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run only fast tests (excludes slow and requires_* markers)"
    )

    parser.add_argument(
        "--unit-only",
        action="store_true",
        help="Run only unit tests"
    )

    args = parser.parse_args()

    # Handle special flags
    if args.fast:
        args.markers = "not slow and not requires_ollama and not requires_audio"
    elif args.unit_only:
        args.test_type = "unit"

    # Run tests
    exit_code = run_tests(
        test_type=args.test_type,
        verbose=args.verbose,
        coverage=args.coverage,
        markers=args.markers
    )

    sys.exit(exit_code)

if __name__ == "__main__":
    main()
