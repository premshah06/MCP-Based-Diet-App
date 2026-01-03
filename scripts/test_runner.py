#!/usr/bin/env python3
"""
Diet Coach MCP Test Runner
This script runs tests for both the FastAPI app and MCP server components.
It can run tests individually or all together with coverage reporting.
"""
import os
import sys
import subprocess
import argparse
from pathlib import Path
def run_command(cmd, cwd=None, description=""):
    """Run a command and return the result"""
    print(f"\n{'='*60}")
    print(f"Running: {description or cmd}")
    print(f"{'='*60}")
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            cwd=cwd,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error running command: {e}")
        return False
def install_dependencies(component_path):
    """Install test dependencies for a component"""
    requirements_file = component_path / "requirements.txt"
    test_requirements_file = component_path / "test_requirements.txt"
    success = True
    if requirements_file.exists():
        cmd = f"pip install -r {requirements_file}"
        success &= run_command(cmd, description=f"Installing main dependencies for {component_path.name}")
    if test_requirements_file.exists():
        cmd = f"pip install -r {test_requirements_file}"
        success &= run_command(cmd, description=f"Installing test dependencies for {component_path.name}")
    return success
def run_tests(component_path, test_args=""):
    """Run tests for a specific component"""
    cmd = f"python -m pytest {test_args}"
    return run_command(cmd, cwd=component_path, description=f"Running tests for {component_path.name}")
def run_linting(component_path):
    """Run linting for a component"""
    # Install flake8 if not present
    subprocess.run("pip install flake8", shell=True, capture_output=True)
    cmd = "flake8 --max-line-length=120 --ignore=E501,W503 *.py"
    return run_command(cmd, cwd=component_path, description=f"Running linting for {component_path.name}")
def main():
    parser = argparse.ArgumentParser(description="Diet Coach MCP Test Runner")
    parser.add_argument("--component", choices=["api", "mcp", "all"], default="all",
                       help="Which component to test (default: all)")
    parser.add_argument("--install-deps", action="store_true",
                       help="Install dependencies before running tests")
    parser.add_argument("--lint", action="store_true",
                       help="Run linting in addition to tests")
    parser.add_argument("--coverage", action="store_true",
                       help="Generate coverage reports")
    parser.add_argument("--verbose", "-v", action="store_true",
                       help="Verbose output")
    parser.add_argument("--fast", action="store_true",
                       help="Skip slow tests")
    parser.add_argument("--test-pattern", type=str,
                       help="Run specific test pattern (e.g., test_tdee)")
    args = parser.parse_args()
    # Define component paths
    project_root = Path(__file__).parent
    api_path = project_root / "apps" / "diet-api"
    mcp_path = project_root / "apps" / "diet-mcp"
    # Determine which components to test
    components = []
    if args.component in ["api", "all"]:
        components.append(("FastAPI App", api_path))
    if args.component in ["mcp", "all"]:
        components.append(("MCP Server", mcp_path))
    overall_success = True
    for component_name, component_path in components:
        print(f"\n{'*'*80}")
        print(f"TESTING: {component_name}")
        print(f"PATH: {component_path}")
        print(f"{'*'*80}")
        if not component_path.exists():
            print(f"ERROR: Component path does not exist: {component_path}")
            overall_success = False
            continue
        # Install dependencies if requested
        if args.install_deps:
            if not install_dependencies(component_path):
                print(f"ERROR: Failed to install dependencies for {component_name}")
                overall_success = False
                continue
        # Run linting if requested
        if args.lint:
            if not run_linting(component_path):
                print(f"WARNING: Linting failed for {component_name}")
                # Don't fail overall for linting issues
        # Prepare test arguments
        test_args = []
        if args.verbose:
            test_args.append("-v")
        if args.fast:
            test_args.append('-m "not slow"')
        if args.test_pattern:
            test_args.append(f"-k {args.test_pattern}")
        if args.coverage:
            test_args.extend([
                "--cov-report=term-missing",
                "--cov-report=html:htmlcov"
            ])
        # Run tests
        test_args_str = " ".join(test_args)
        if not run_tests(component_path, test_args_str):
            print(f"ERROR: Tests failed for {component_name}")
            overall_success = False
        else:
            print(f"SUCCESS: All tests passed for {component_name}")
    # Summary
    print(f"\n{'='*80}")
    if overall_success:
        print("🎉 ALL TESTS PASSED!")
        print("✅ The Diet Coach MCP application is ready for deployment.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please fix the failing tests before deployment.")
    print(f"{'='*80}")
    # Coverage reports
    if args.coverage:
        print("\n📊 Coverage reports generated:")
        for component_name, component_path in components:
            coverage_path = component_path / "htmlcov" / "index.html"
            if coverage_path.exists():
                print(f"  {component_name}: {coverage_path.absolute()}")
    return 0 if overall_success else 1
if __name__ == "__main__":
    sys.exit(main())
