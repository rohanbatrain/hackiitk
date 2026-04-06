#!/usr/bin/env python3
"""
Result aggregation script for GitHub Actions parallel test execution.
This script aggregates test results from multiple parallel test jobs.
"""

import json
from pathlib import Path
from datetime import datetime
from typing import Dict, Any


def aggregate_test_results(results_dir: Path) -> Dict[str, Any]:
    """
    Aggregate test results from all parallel test jobs.
    
    Args:
        results_dir: Path to directory containing test result artifacts
        
    Returns:
        Dictionary containing aggregated test results
    """
    # Initialize aggregated results structure
    all_results = {
        "execution_date": datetime.now().isoformat(),
        "total_tests": 0,
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "skipped": 0,
        "duration_seconds": 0.0,
        "pass_rate": 0.0,
        "parallel_jobs": 0,
        "categories": {}
    }
    
    # Handle missing artifacts gracefully (minimal dependency mode)
    if not results_dir.exists():
        print("⚠️ No test results found - all tests were skipped")
        print("ℹ️ This is expected when running with minimal dependencies")
        return all_results
    
    # Count parallel jobs from artifact directories
    artifact_dirs = [d for d in results_dir.iterdir() if d.is_dir() and "test-results-" in d.name]
    all_results["parallel_jobs"] = len(artifact_dirs)
    
    # Parse JSON result files from all categories
    for artifact_dir in artifact_dirs:
        category = artifact_dir.name.replace("test-results-", "")
        
        # Initialize category statistics
        if category not in all_results["categories"]:
            all_results["categories"][category] = {
                "total": 0,
                "passed": 0,
                "failed": 0,
                "errors": 0,
                "skipped": 0
            }
        
        # Process all JSON files in the artifact directory
        for json_file in artifact_dir.glob("**/*.json"):
            try:
                with open(json_file) as f:
                    data = json.load(f)
                
                # Validate JSON structure
                if "total_tests" in data:
                    # Calculate total_tests, passed, failed, errors, skipped across all categories
                    all_results["total_tests"] += data.get("total_tests", 0)
                    all_results["passed"] += data.get("passed", 0)
                    all_results["failed"] += data.get("failed", 0)
                    all_results["errors"] += data.get("errors", 0)
                    all_results["skipped"] += data.get("skipped", 0)
                    
                    # Calculate total duration_seconds across all categories
                    all_results["duration_seconds"] += data.get("duration_seconds", 0.0)
                    
                    # Generate per-category statistics with test counts
                    all_results["categories"][category]["total"] += data.get("total_tests", 0)
                    all_results["categories"][category]["passed"] += data.get("passed", 0)
                    all_results["categories"][category]["failed"] += data.get("failed", 0)
                    all_results["categories"][category]["errors"] += data.get("errors", 0)
                    all_results["categories"][category]["skipped"] += data.get("skipped", 0)
            
            except json.JSONDecodeError as e:
                # Handle malformed JSON with try-except and error logging
                print(f"⚠️ Error parsing JSON file {json_file}: {e}")
                continue
            except Exception as e:
                # Handle other errors gracefully
                print(f"⚠️ Error processing {json_file}: {e}")
                continue
    
    # Calculate pass_rate percentage from aggregated results
    if all_results["total_tests"] > 0:
        all_results["pass_rate"] = (all_results["passed"] / all_results["total_tests"]) * 100
    else:
        all_results["pass_rate"] = 0.0
    
    # Calculate per-category pass rates
    for category, stats in all_results["categories"].items():
        if stats["total"] > 0:
            stats["pass_rate"] = (stats["passed"] / stats["total"]) * 100
        else:
            stats["pass_rate"] = 0.0
    
    return all_results


def format_console_output(results: Dict[str, Any]) -> str:
    """
    Format aggregated results for console output.
    
    Args:
        results: Aggregated test results dictionary
        
    Returns:
        Formatted string for console output
    """
    lines = []
    lines.append("=" * 80)
    lines.append("PARALLEL TEST SUITE RESULTS")
    lines.append("=" * 80)
    lines.append(f"Parallel Jobs: {results['parallel_jobs']}")
    lines.append(f"Total Tests: {results['total_tests']}")
    lines.append(f"Passed: {results['passed']} ({results['pass_rate']:.1f}%)")
    lines.append(f"Failed: {results['failed']}")
    lines.append(f"Errors: {results['errors']}")
    lines.append(f"Skipped: {results['skipped']}")
    lines.append(f"Duration: {results['duration_seconds']/60:.1f} minutes")
    lines.append("")
    lines.append("Category Breakdown:")
    for cat, stats in sorted(results["categories"].items()):
        if stats["total"] > 0:
            lines.append(f"  {cat}: {stats['passed']}/{stats['total']} ({stats['pass_rate']:.1f}%)")
    lines.append("=" * 80)
    
    # Display success criteria status
    if results["total_tests"] == 0:
        lines.append("ℹ️  No tests executed (minimal dependency mode)")
    elif results["pass_rate"] >= 95:
        lines.append("✅ SUCCESS CRITERIA MET (≥95% pass rate)")
    else:
        lines.append(f"⚠️  SUCCESS CRITERIA NOT MET ({results['pass_rate']:.1f}% < 95%)")
    lines.append("=" * 80)
    
    return "\n".join(lines)


if __name__ == "__main__":
    import sys
    
    # Get results directory from command line or use default
    results_dir = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("all-test-results")
    
    # Aggregate results
    results = aggregate_test_results(results_dir)
    
    # Write aggregated results to JSON file
    with open("aggregated_results.json", "w") as f:
        json.dump(results, f, indent=2)
    
    # Display formatted console output
    print(format_console_output(results))
