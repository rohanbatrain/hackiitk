# GitHub Actions Test Aggregation Scripts

## Overview

This directory contains scripts for aggregating test results from parallel GitHub Actions test jobs.

## Files

### aggregate_results.py

Python script that aggregates test results from multiple parallel test categories.

**Functions:**

- `aggregate_test_results(results_dir: Path) -> Dict[str, Any]`: Aggregates test results from all parallel test jobs
- `format_console_output(results: Dict[str, Any]) -> str`: Formats aggregated results for console output

**Usage:**

```bash
python3 aggregate_results.py [results_directory]
```

**Features:**

- Aggregates test counts (total, passed, failed, errors, skipped) across all categories
- Calculates overall and per-category pass rates
- Handles missing artifacts gracefully (minimal dependency mode)
- Handles malformed JSON files with error logging
- Generates production-ready console output with success criteria validation

### run_tests.sh

Bash script that executes pytest for specific test categories.

**Usage:**

```bash
./run_tests.sh <category> [output_dir]
```

**Categories:**
- property
- boundary
- adversarial
- stress
- chaos
- performance
- unit
- integration
- all (runs all categories)

## Testing

Unit tests for the aggregation logic are located in `tests/unit/test_result_aggregation.py`.

Run tests with:

```bash
python -m pytest tests/unit/test_result_aggregation.py -v
```

## Requirements

The aggregation script validates:
- Requirements 5.1-5.5: Result aggregation and calculation
- Requirements 6.1-6.5: Production-ready report generation
- Requirements 7.1-7.5: Success criteria validation
- Requirements 10.4: Error handling and resilience
- Requirements 14.1-14.5: Console output formatting
