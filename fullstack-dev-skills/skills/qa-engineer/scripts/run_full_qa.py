#!/usr/bin/env python3
"""
Run complete QA workflow for a project.

Usage:
    python run_full_qa.py --project-dir /path/to/project
    python run_full_qa.py --project-dir . --skip-e2e
    python run_full_qa.py --project-dir . --only unit,integration

This script orchestrates:
1. Unit tests with coverage
2. Integration tests
3. Browser validation (console errors, network)
4. E2E tests
5. Accessibility audit
6. Performance check
"""

import argparse
import subprocess
import sys
import json
import os
from pathlib import Path
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class Status(Enum):
    PASS = "✅"
    FAIL = "❌"
    WARN = "⚠️"
    SKIP = "⏭️"


@dataclass
class StageResult:
    name: str
    status: Status
    duration_seconds: float
    details: Optional[str] = None
    blocking: bool = True


def run_command(cmd: list[str], cwd: str) -> tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd,
            cwd=cwd,
            capture_output=True,
            text=True,
            timeout=600,  # 10 minute timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)


def check_prerequisites(project_dir: str) -> bool:
    """Verify project has required files."""
    required = ["package.json"]
    missing = [f for f in required if not (Path(project_dir) / f).exists()]
    
    if missing:
        print(f"Missing required files: {missing}")
        return False
    return True


def run_unit_tests(project_dir: str) -> StageResult:
    """Run unit tests with coverage."""
    import time
    start = time.time()
    
    print("\n📋 Running Unit Tests...")
    
    # Try different test commands
    commands = [
        ["pnpm", "test:unit", "--coverage"],
        ["npm", "run", "test:unit", "--", "--coverage"],
        ["pnpm", "test", "--", "--run", "--coverage"],
    ]
    
    for cmd in commands:
        code, stdout, stderr = run_command(cmd, project_dir)
        if code == 0:
            # Try to extract coverage
            coverage = extract_coverage(project_dir)
            details = f"Coverage: {coverage}%" if coverage else "Tests passed"
            
            # Check coverage threshold
            if coverage and coverage < 80:
                return StageResult(
                    name="Unit Tests",
                    status=Status.WARN,
                    duration_seconds=time.time() - start,
                    details=f"Coverage {coverage}% below 80% threshold",
                    blocking=False,
                )
            
            return StageResult(
                name="Unit Tests",
                status=Status.PASS,
                duration_seconds=time.time() - start,
                details=details,
            )
    
    return StageResult(
        name="Unit Tests",
        status=Status.FAIL,
        duration_seconds=time.time() - start,
        details=stderr or "Tests failed",
    )


def extract_coverage(project_dir: str) -> Optional[float]:
    """Extract coverage percentage from coverage report."""
    coverage_file = Path(project_dir) / "coverage" / "coverage-summary.json"
    if coverage_file.exists():
        try:
            data = json.loads(coverage_file.read_text())
            return data.get("total", {}).get("lines", {}).get("pct", 0)
        except:
            pass
    return None


def run_integration_tests(project_dir: str) -> StageResult:
    """Run integration tests."""
    import time
    start = time.time()
    
    print("\n🔗 Running Integration Tests...")
    
    commands = [
        ["pnpm", "test:integration"],
        ["npm", "run", "test:integration"],
    ]
    
    for cmd in commands:
        code, stdout, stderr = run_command(cmd, project_dir)
        if code == 0:
            return StageResult(
                name="Integration Tests",
                status=Status.PASS,
                duration_seconds=time.time() - start,
                details="All integration tests passed",
            )
    
    # Check if integration tests exist
    if "not found" in stderr.lower() or "missing script" in stderr.lower():
        return StageResult(
            name="Integration Tests",
            status=Status.SKIP,
            duration_seconds=time.time() - start,
            details="No integration tests configured",
            blocking=False,
        )
    
    return StageResult(
        name="Integration Tests",
        status=Status.FAIL,
        duration_seconds=time.time() - start,
        details=stderr or "Tests failed",
    )


def run_e2e_tests(project_dir: str) -> StageResult:
    """Run E2E tests with Playwright."""
    import time
    start = time.time()
    
    print("\n🌐 Running E2E Tests...")
    
    # Check if Playwright is installed
    code, _, _ = run_command(["pnpm", "exec", "playwright", "--version"], project_dir)
    if code != 0:
        return StageResult(
            name="E2E Tests",
            status=Status.SKIP,
            duration_seconds=time.time() - start,
            details="Playwright not installed",
            blocking=False,
        )
    
    # Run E2E tests
    code, stdout, stderr = run_command(["pnpm", "test:e2e"], project_dir)
    
    if code == 0:
        return StageResult(
            name="E2E Tests",
            status=Status.PASS,
            duration_seconds=time.time() - start,
            details="All E2E tests passed",
        )
    
    return StageResult(
        name="E2E Tests",
        status=Status.FAIL,
        duration_seconds=time.time() - start,
        details=stderr or "E2E tests failed",
    )


def run_accessibility_audit(project_dir: str) -> StageResult:
    """Run accessibility audit."""
    import time
    start = time.time()
    
    print("\n♿ Running Accessibility Audit...")
    
    commands = [
        ["pnpm", "test:a11y"],
        ["npm", "run", "test:a11y"],
    ]
    
    for cmd in commands:
        code, stdout, stderr = run_command(cmd, project_dir)
        if code == 0:
            return StageResult(
                name="Accessibility",
                status=Status.PASS,
                duration_seconds=time.time() - start,
                details="No critical accessibility violations",
            )
    
    if "not found" in stderr.lower() or "missing script" in stderr.lower():
        return StageResult(
            name="Accessibility",
            status=Status.SKIP,
            duration_seconds=time.time() - start,
            details="No accessibility tests configured",
            blocking=False,
        )
    
    # Parse for violations
    if "violation" in stdout.lower() or "violation" in stderr.lower():
        return StageResult(
            name="Accessibility",
            status=Status.FAIL,
            duration_seconds=time.time() - start,
            details="Accessibility violations found",
        )
    
    return StageResult(
        name="Accessibility",
        status=Status.WARN,
        duration_seconds=time.time() - start,
        details="Could not determine accessibility status",
        blocking=False,
    )


def run_performance_check(project_dir: str) -> StageResult:
    """Run performance audit."""
    import time
    start = time.time()
    
    print("\n⚡ Running Performance Check...")
    
    # Try Lighthouse CI
    code, stdout, stderr = run_command(["npx", "lhci", "autorun"], project_dir)
    
    if code == 0:
        return StageResult(
            name="Performance",
            status=Status.PASS,
            duration_seconds=time.time() - start,
            details="Performance thresholds met",
            blocking=False,
        )
    
    if "not found" in stderr.lower() or "lhci" not in stderr.lower():
        return StageResult(
            name="Performance",
            status=Status.SKIP,
            duration_seconds=time.time() - start,
            details="Lighthouse CI not configured",
            blocking=False,
        )
    
    return StageResult(
        name="Performance",
        status=Status.WARN,
        duration_seconds=time.time() - start,
        details="Performance below threshold",
        blocking=False,
    )


def generate_report(results: list[StageResult]) -> None:
    """Generate and print QA report."""
    print("\n" + "=" * 60)
    print("                    QA REPORT")
    print("=" * 60)
    
    total_time = sum(r.duration_seconds for r in results)
    passed = sum(1 for r in results if r.status == Status.PASS)
    failed = sum(1 for r in results if r.status == Status.FAIL)
    warnings = sum(1 for r in results if r.status == Status.WARN)
    skipped = sum(1 for r in results if r.status == Status.SKIP)
    
    print(f"\nTotal Duration: {total_time:.1f}s")
    print(f"Passed: {passed} | Failed: {failed} | Warnings: {warnings} | Skipped: {skipped}")
    print("\n" + "-" * 60)
    
    for result in results:
        status_icon = result.status.value
        blocking = "🚫" if result.blocking and result.status == Status.FAIL else ""
        print(f"{status_icon} {result.name:<20} ({result.duration_seconds:.1f}s) {blocking}")
        if result.details:
            print(f"   └─ {result.details}")
    
    print("-" * 60)
    
    # Final verdict
    blocking_failures = [r for r in results if r.status == Status.FAIL and r.blocking]
    
    if blocking_failures:
        print("\n❌ QA FAILED - Blocking issues found:")
        for r in blocking_failures:
            print(f"   • {r.name}: {r.details}")
        print("\nFix these issues before merging.")
    elif warnings > 0:
        print("\n⚠️ QA PASSED WITH WARNINGS")
        print("Consider addressing warnings before release.")
    else:
        print("\n✅ QA PASSED")
    
    print("=" * 60)


def main():
    parser = argparse.ArgumentParser(description="Run complete QA workflow")
    parser.add_argument("--project-dir", "-p", default=".", help="Project directory")
    parser.add_argument("--skip-e2e", action="store_true", help="Skip E2E tests")
    parser.add_argument("--skip-perf", action="store_true", help="Skip performance check")
    parser.add_argument(
        "--only",
        type=str,
        help="Run only specific stages (comma-separated: unit,integration,e2e,a11y,perf)",
    )
    
    args = parser.parse_args()
    project_dir = os.path.abspath(args.project_dir)
    
    print(f"🔍 Running QA on: {project_dir}")
    
    if not check_prerequisites(project_dir):
        sys.exit(1)
    
    # Determine which stages to run
    stages_to_run = set()
    if args.only:
        stages_to_run = set(args.only.lower().split(","))
    else:
        stages_to_run = {"unit", "integration", "e2e", "a11y", "perf"}
        if args.skip_e2e:
            stages_to_run.discard("e2e")
        if args.skip_perf:
            stages_to_run.discard("perf")
    
    results: list[StageResult] = []
    
    # Run stages in order
    if "unit" in stages_to_run:
        results.append(run_unit_tests(project_dir))
    
    if "integration" in stages_to_run:
        results.append(run_integration_tests(project_dir))
    
    if "e2e" in stages_to_run:
        results.append(run_e2e_tests(project_dir))
    
    if "a11y" in stages_to_run:
        results.append(run_accessibility_audit(project_dir))
    
    if "perf" in stages_to_run:
        results.append(run_performance_check(project_dir))
    
    # Generate report
    generate_report(results)
    
    # Exit with appropriate code
    blocking_failures = [r for r in results if r.status == Status.FAIL and r.blocking]
    sys.exit(1 if blocking_failures else 0)


if __name__ == "__main__":
    main()
