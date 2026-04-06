# Coverage Measurement for Extreme Testing Framework

This document describes the coverage measurement infrastructure for the comprehensive testing framework.

## Overview

The coverage measurement system tracks code coverage across all test categories and generates comprehensive reports to identify untested code paths and ensure adequate test coverage.

**Requirements:** 80.1, 80.2, 80.3, 80.4, 80.5, 80.6

## Features

- **Automated Coverage Tracking**: Integrates with pytest-cov to measure coverage during test execution
- **Multi-Format Reports**: Generates HTML, JSON, and terminal reports
- **Component-Level Analysis**: Breaks down coverage by module/component
- **Threshold Verification**: Validates that coverage meets 90% threshold
- **Error Path Coverage**: Verifies that error handling paths are tested
- **Trend Tracking**: Monitors coverage changes over time
- **Untested Path Identification**: Lists specific lines not covered by tests

## Installation

Install the required dependencies:

```bash
pip install pytest-cov>=4.1.0
```

## Usage

### Running Tests with Coverage

#### Option 1: Using the CLI

```bash
# Run all tests with coverage
python -m tests.extreme.cli --with-coverage

# Run specific categories with coverage
python -m tests.extreme.cli --categories stress chaos --with-coverage
```

#### Option 2: Using the Standalone Script

```bash
# Run all tests with coverage
python tests/extreme/run_coverage.py

# Run specific categories
python tests/extreme/run_coverage.py --categories stress chaos

# Set custom threshold
python tests/extreme/run_coverage.py --threshold 95

# Pass additional pytest arguments
python tests/extreme/run_coverage.py --pytest-args "-v" "--tb=short"
```

#### Option 3: Using pytest Directly

```bash
# Run all tests with coverage
pytest --cov=. --cov-report=html --cov-report=json --cov-report=term-missing

# Run specific test directory
pytest tests/extreme/ --cov=. --cov-report=html

# Run with specific coverage config
pytest --cov=. --cov-config=.coveragerc
```

### Programmatic Usage

```python
from tests.extreme.coverage_analyzer import CoverageAnalyzer

# Create analyzer
analyzer = CoverageAnalyzer(
    source_dirs=['ingestion', 'retrieval', 'analysis'],
    output_dir='coverage_reports',
    baseline_dir='coverage_baselines'
)

# Run tests with coverage
exit_code, output = analyzer.run_tests_with_coverage(
    test_categories=['stress', 'chaos']
)

# Generate coverage report
coverage_report = analyzer.generate_coverage_report()

# Verify threshold
meets_threshold, low_coverage = analyzer.verify_coverage_threshold(
    coverage_report,
    threshold=90.0
)

# Generate summary
summary = analyzer.generate_coverage_summary(coverage_report)
print(summary)

# Save report
analyzer.save_coverage_report(coverage_report)
```

## Coverage Reports

### HTML Report

The HTML report provides an interactive view of coverage:

- **Location**: `coverage_reports/html/index.html`
- **Features**:
  - Color-coded line coverage
  - Branch coverage visualization
  - Sortable component list
  - Drill-down to file level

### JSON Report

The JSON report provides machine-readable coverage data:

- **Location**: `coverage_reports/coverage.json`
- **Contents**:
  - Per-file coverage metrics
  - Line-by-line execution data
  - Branch coverage information
  - Summary statistics

### Terminal Report

The terminal report provides a quick overview:

```
COVERAGE ANALYSIS SUMMARY
================================================================================
Timestamp: 2026-04-06 01:52:14
Total Coverage: 92.45%
Threshold Met (≥90%): ✓ YES
Error Paths Covered: ✓ YES

Component Coverage:
--------------------------------------------------------------------------------
  ✓ ingestion.document_parser                        95.23% (123/129)
  ✓ retrieval.hybrid_retriever                       93.45% (156/167)
  ✗ analysis.stage_a_detector                        87.12% (98/112)
  ✓ analysis.stage_b_reasoner                        91.34% (142/155)
  ...

Untested Paths (15):
--------------------------------------------------------------------------------
  - analysis.stage_a_detector:45
  - analysis.stage_a_detector:67
  - analysis.stage_a_detector:89
  ...

Coverage Trend (last 10 runs):
--------------------------------------------------------------------------------
  2026-04-05T10:30:00: 90.12%
  2026-04-05T14:45:00: 91.23%
  2026-04-06T01:52:14: 92.45%

Reports:
  HTML: coverage_reports/html/index.html
  JSON: coverage_reports/coverage.json
================================================================================
```

## Configuration

### .coveragerc

The `.coveragerc` file configures coverage measurement:

```ini
[run]
source = .
omit =
    */tests/*
    */test_*.py
    */__pycache__/*
    */venv/*
    */env/*
    setup.py

[report]
precision = 2
show_missing = True
skip_covered = False
exclude_lines =
    pragma: no cover
    def __repr__
    raise AssertionError
    raise NotImplementedError
    if __name__ == .__main__.:

[html]
directory = coverage_reports/html

[json]
output = coverage_reports/coverage.json
```

## Coverage Metrics

### Component-Level Metrics

For each component, the following metrics are tracked:

- **Total Statements**: Number of executable statements
- **Covered Statements**: Number of statements executed during tests
- **Missing Statements**: Number of statements not executed
- **Coverage Percent**: Percentage of statements covered
- **Missing Lines**: Specific line numbers not covered
- **Uncovered Branches**: Branch points not fully tested

### Overall Metrics

- **Total Coverage**: Aggregate coverage across all components
- **Threshold Status**: Whether coverage meets 90% threshold
- **Error Path Coverage**: Whether error handling is tested
- **Untested Paths**: List of specific untested code locations

## Coverage Threshold

The system enforces a **90% coverage threshold** (Requirement 80.4):

- Tests must cover at least 90% of all statements
- Components below threshold are flagged
- Error handling paths must be covered (Requirement 80.5)
- Threshold verification fails if any component is below 90%

## Coverage Trends

Coverage trends are tracked over time (Requirement 80.6):

- Each test run records coverage percentage
- Trends are stored in `coverage_baselines/coverage_trends.json`
- Last 100 runs are retained
- Trends help identify coverage regressions

## Identifying Untested Paths

The system identifies specific untested code paths (Requirement 80.2):

- Lists module name and line number for each untested path
- Prioritizes error handling paths
- Helps focus testing efforts on gaps

## Integration with CI/CD

### GitHub Actions Example

```yaml
name: Coverage

on: [push, pull_request]

jobs:
  coverage:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest-cov
      - name: Run tests with coverage
        run: python tests/extreme/run_coverage.py
      - name: Upload coverage reports
        uses: actions/upload-artifact@v2
        with:
          name: coverage-reports
          path: coverage_reports/
```

### GitLab CI Example

```yaml
coverage:
  stage: test
  script:
    - pip install -r requirements.txt
    - pip install pytest-cov
    - python tests/extreme/run_coverage.py
  artifacts:
    paths:
      - coverage_reports/
    reports:
      coverage_report:
        coverage_format: cobertura
        path: coverage_reports/coverage.xml
```

## Troubleshooting

### Coverage Data Not Found

If you see "Coverage data not found", ensure:

1. Tests were run with `--cov` flag
2. `.coverage` file exists in output directory
3. Coverage JSON was generated

### Low Coverage Warnings

If coverage is below 90%:

1. Check which components are below threshold
2. Review untested paths list
3. Add tests for missing coverage
4. Verify error handling paths are tested

### Coverage Trend Not Updating

If trends aren't updating:

1. Check `coverage_baselines/coverage_trends.json` exists
2. Verify write permissions on baseline directory
3. Ensure coverage report generation completed

## Best Practices

1. **Run coverage regularly**: Include in CI/CD pipeline
2. **Review untested paths**: Focus on high-priority code
3. **Test error paths**: Ensure exception handlers are covered
4. **Track trends**: Monitor coverage over time
5. **Set realistic thresholds**: 90% is a good target
6. **Document exclusions**: Use `pragma: no cover` sparingly

## API Reference

### CoverageAnalyzer

Main class for coverage measurement and analysis.

#### Methods

- `run_tests_with_coverage(test_categories, pytest_args)`: Run tests with coverage
- `generate_coverage_report()`: Generate comprehensive coverage report
- `verify_coverage_threshold(report, threshold)`: Verify coverage meets threshold
- `generate_coverage_summary(report)`: Generate human-readable summary
- `save_coverage_report(report, filename)`: Save summary to file

### CoverageMetrics

Data class for component-level coverage metrics.

#### Attributes

- `module_name`: Name of the module
- `total_statements`: Total executable statements
- `covered_statements`: Statements executed during tests
- `missing_statements`: Statements not executed
- `coverage_percent`: Coverage percentage
- `missing_lines`: List of uncovered line numbers
- `is_adequate`: Whether coverage meets 90% threshold

### CoverageReport

Data class for comprehensive coverage report.

#### Attributes

- `timestamp`: Report generation time
- `total_coverage_percent`: Overall coverage percentage
- `component_coverage`: Dict of component metrics
- `untested_paths`: List of untested code locations
- `error_paths_covered`: Whether error handling is tested
- `coverage_trend`: Historical coverage data
- `html_report_path`: Path to HTML report
- `json_report_path`: Path to JSON report

#### Methods

- `meets_threshold(threshold)`: Check if coverage meets threshold
- `get_low_coverage_components(threshold)`: Get components below threshold

## Requirements Mapping

- **80.1**: Coverage measurement infrastructure with pytest-cov
- **80.2**: Identification of untested code paths
- **80.3**: HTML and JSON coverage report generation
- **80.4**: Verification of ≥90% coverage threshold
- **80.5**: Verification of error handling path coverage
- **80.6**: Coverage trend tracking over time

## See Also

- [pytest-cov documentation](https://pytest-cov.readthedocs.io/)
- [Coverage.py documentation](https://coverage.readthedocs.io/)
- [Extreme Testing Framework README](README.md)
