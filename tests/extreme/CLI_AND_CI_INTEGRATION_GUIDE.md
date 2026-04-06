# CLI and CI/CD Integration Guide

## Overview

This guide covers the Command-Line Interface (CLI) for the Extreme Testing Framework and its integration with CI/CD pipelines (GitHub Actions and GitLab CI).

## CLI Usage

### Test Execution

The CLI provides comprehensive options for running extreme tests with selective execution capabilities.

#### Basic Usage

```bash
# Run all tests (default)
python -m tests.extreme.cli

# Explicitly run test command
python -m tests.extreme.cli test
```

#### Selective Test Execution

**By Category:**
```bash
# Run specific categories
python -m tests.extreme.cli test --category stress
python -m tests.extreme.cli test --category chaos --category adversarial

# Available categories: stress, chaos, adversarial, boundary, performance, property
```

**By Requirement:**
```bash
# Run tests for specific requirements
python -m tests.extreme.cli test --requirement 1.1
python -m tests.extreme.cli test --requirement 1.1 --requirement 2.3 --requirement 72.4
```

**Fast Tests (CI Mode):**
```bash
# Run only fast tests (property, boundary, adversarial)
python -m tests.extreme.cli test --fast

# This automatically:
# - Filters to fast test categories
# - Sets 10-minute timeout
# - Suitable for CI quick checks
```

#### Execution Options

**Verbose Output:**
```bash
python -m tests.extreme.cli test --verbose
```

**Fail-Fast Mode:**
```bash
# Stop on first failure
python -m tests.extreme.cli test --fail-fast
```

**Concurrency Control:**
```bash
# Set number of concurrent workers (default: 4)
python -m tests.extreme.cli test --concurrency 8
```

**Timeout Configuration:**
```bash
# Set timeout in seconds (default: 3600)
python -m tests.extreme.cli test --timeout 7200
```

**Output Directory:**
```bash
# Specify output directory (default: test_outputs/extreme)
python -m tests.extreme.cli test --output-dir custom_output/
```

#### Report Generation

**Control Report Formats:**
```bash
# Disable specific report formats
python -m tests.extreme.cli test --no-html
python -m tests.extreme.cli test --no-json
python -m tests.extreme.cli test --no-junit

# All reports disabled
python -m tests.extreme.cli test --no-html --no-json --no-junit
```

**With Coverage:**
```bash
# Run tests with code coverage measurement
python -m tests.extreme.cli test --with-coverage
```

### Test Data Generation

The CLI provides a powerful test data generation command for creating diverse test scenarios.

#### Generate Policy Documents

```bash
# Generate synthetic policy documents
python -m tests.extreme.cli generate-data --type policy --count 10 --pages 20

# Output: test_data/policy_1.txt, policy_2.txt, ...
```

#### Generate Malicious PDFs

```bash
# Generate malicious PDFs for security testing
python -m tests.extreme.cli generate-data --type malicious-pdf --count 5 --attack-type javascript

# Attack types: javascript, malformed, recursive, large_object
python -m tests.extreme.cli generate-data --type malicious-pdf --attack-type malformed
```

#### Generate Gap Policies

```bash
# Generate policies with intentional gaps
python -m tests.extreme.cli generate-data --type gap-policy --count 3 \
  --gaps ID.AM-1 ID.AM-2 PR.DS-1

# Output: test_data/gap_policy_1.txt with specified gaps
```

#### Generate Extreme Structures

```bash
# Generate documents with extreme structural properties
python -m tests.extreme.cli generate-data --type extreme-structure --count 5 \
  --structure no_headings

# Structure types:
# - no_headings: Document with no section markers
# - deep_nesting: 100+ levels of nested structure
# - inconsistent_hierarchy: Inconsistent heading hierarchy
# - only_tables: Document with only tables, no prose
# - many_headings: 1,000+ headings
# - many_sections: 1,000+ sections
```

#### Generate Multilingual Documents

```bash
# Generate documents with diverse character sets
python -m tests.extreme.cli generate-data --type multilingual --count 3 \
  --languages chinese arabic cyrillic

# Output: test_data/multilingual_1.txt with mixed languages
```

#### Generate Oracle Test Cases

```bash
# Generate oracle test cases with expected results template
python -m tests.extreme.cli generate-data --type oracle --count 5 --pages 10

# Output structure:
# test_data/oracle_1/
#   ├── policy.txt
#   └── expected.json (template - update after analysis)
```

#### Custom Output Directory

```bash
# Specify custom output directory
python -m tests.extreme.cli generate-data --type policy --output custom_test_data/
```

## CI/CD Integration

### GitHub Actions

The framework provides comprehensive GitHub Actions workflows for automated testing.

#### Workflow File

Location: `.github/workflows/extreme-tests.yml`

#### Trigger Conditions

**Automatic Triggers:**
- Push to `main` or `develop` branches → Fast tests
- Pull requests to `main` or `develop` → Fast tests
- Weekly schedule (Sunday 2 AM UTC) → Full suite

**Manual Triggers:**
- Workflow dispatch with category selection
- Options: all, fast, stress, chaos, adversarial, boundary, performance, property

#### Jobs

**1. Fast Tests (Every Push/PR)**
- Runs: property, boundary, adversarial tests
- Timeout: 30 minutes
- Fail-fast: enabled
- Publishes: JUnit XML results

**2. Stress Tests (Schedule/Manual)**
- Runs: stress category
- Timeout: 2 hours
- Allows failure: yes
- Uploads: test results and artifacts

**3. Chaos Tests (Schedule/Manual)**
- Runs: chaos category
- Timeout: 2 hours
- Allows failure: yes
- Uploads: test results and artifacts

**4. Performance Tests (Schedule/Manual)**
- Runs: performance category
- Timeout: 2 hours
- Allows failure: yes
- Uploads: test results and performance baselines

**5. Full Suite (Schedule/Manual)**
- Runs: all categories with coverage
- Timeout: 4 hours
- Allows failure: yes
- Uploads: test results, coverage reports
- Comments PR with results summary

#### Artifacts

All jobs upload artifacts:
- HTML reports: `test_outputs/extreme/*.html`
- JSON reports: `test_outputs/extreme/*.json`
- JUnit XML: `test_outputs/extreme/*.xml`
- Coverage reports: `coverage_reports_demo/*.html`
- Performance baselines: `coverage_baselines/*.json`

#### Manual Workflow Dispatch

```yaml
# Trigger from GitHub UI:
# Actions → Extreme Testing Suite → Run workflow
# Select branch and test category
```

### GitLab CI

The framework provides comprehensive GitLab CI configuration for automated testing.

#### Configuration File

Location: `.gitlab-ci-extreme.yml`

To use, either:
1. Rename to `.gitlab-ci.yml`, or
2. Include in existing `.gitlab-ci.yml`:
   ```yaml
   include:
     - local: '.gitlab-ci-extreme.yml'
   ```

#### Pipeline Stages

1. `fast-tests`: Quick validation tests
2. `stress-tests`: Maximum load tests
3. `chaos-tests`: Fault injection tests
4. `performance-tests`: Performance profiling
5. `full-suite`: Complete test suite with coverage

#### Trigger Rules

**Fast Tests:**
- Every push
- Every merge request
- Manual with `TEST_CATEGORY=fast`

**Stress/Chaos/Performance Tests:**
- Scheduled pipelines
- Manual trigger with `TEST_CATEGORY=<category>`
- Included in `TEST_CATEGORY=all`

**Full Suite:**
- Scheduled pipelines
- Manual trigger with `TEST_CATEGORY=all`

#### Pipeline Variables

Set in GitLab CI/CD settings:

```bash
TEST_CATEGORY=fast      # Run specific category
TEST_CATEGORY=all       # Run full suite
PYTHON_VERSION=3.11     # Python version (default: 3.11)
```

#### Manual Job Triggers

**Generate Test Data:**
```yaml
# Available as manual job in .pre stage
# Generates:
# - 10 policy documents (20 pages each)
# - 5 malicious PDFs (JavaScript attack)
# - 5 oracle test cases
```

#### Artifacts and Reports

All jobs produce:
- Test results: HTML, JSON, JUnit XML
- JUnit reports: Integrated with GitLab UI
- Coverage reports: Cobertura format
- Performance baselines: JSON files

Artifacts expire after 1 week (configurable).

## CI-Friendly Report Formats

### JUnit XML

Generated automatically for CI integration:
- Location: `test_outputs/extreme/*.xml`
- Format: Standard JUnit XML
- Integration: GitHub Actions, GitLab CI, Jenkins, etc.

### GitHub Annotations

Generated for GitHub Actions:
- Location: `test_outputs/extreme/github_annotations.txt`
- Format: GitHub workflow commands
- Displays: Inline annotations on files

### JSON Reports

Machine-readable format:
- Location: `test_outputs/extreme/test_report.json`
- Contains: Complete test results, metrics, breaking points
- Usage: Custom reporting, dashboards, analysis

## Best Practices

### For Development

```bash
# Quick validation before commit
python -m tests.extreme.cli test --fast --fail-fast

# Test specific changes
python -m tests.extreme.cli test --category boundary --requirement 15.1

# Generate test data for manual testing
python -m tests.extreme.cli generate-data --type policy --count 5
```

### For CI/CD

**GitHub Actions:**
- Fast tests on every PR (30 min)
- Full suite weekly (4 hours)
- Manual triggers for specific categories

**GitLab CI:**
- Fast tests on every push/MR (30 min)
- Scheduled full suite (4 hours)
- Manual jobs for test data generation

### For Performance Testing

```bash
# Establish baselines
python -m tests.extreme.cli test --category performance --verbose

# Compare against baselines
python -m tests.extreme.cli test --category performance --with-coverage

# Baselines stored in: coverage_baselines/
```

### For Security Testing

```bash
# Generate malicious test data
python -m tests.extreme.cli generate-data --type malicious-pdf --count 20 \
  --attack-type javascript

# Run adversarial tests
python -m tests.extreme.cli test --category adversarial --verbose
```

## Troubleshooting

### Tests Timeout

```bash
# Increase timeout
python -m tests.extreme.cli test --timeout 7200

# Or run specific categories
python -m tests.extreme.cli test --category property --category boundary
```

### Out of Memory

```bash
# Reduce concurrency
python -m tests.extreme.cli test --concurrency 2

# Or run fast tests only
python -m tests.extreme.cli test --fast
```

### CI Pipeline Failures

**GitHub Actions:**
- Check workflow logs in Actions tab
- Download artifacts for detailed reports
- Review JUnit XML for specific failures

**GitLab CI:**
- Check pipeline logs in CI/CD → Pipelines
- Download artifacts from job page
- Review JUnit reports in Tests tab

## Requirements Validation

This CLI implementation validates:

- **Requirement 72.4**: Selective test execution by category and requirement
- **Requirement 72.7**: CI/CD integration support with GitHub Actions and GitLab CI
- **Requirement 75.6**: Test data generation CLI for custom test cases

## Examples

### Complete Workflow

```bash
# 1. Generate test data
python -m tests.extreme.cli generate-data --type policy --count 10
python -m tests.extreme.cli generate-data --type malicious-pdf --count 5

# 2. Run fast tests locally
python -m tests.extreme.cli test --fast --verbose

# 3. Run specific category
python -m tests.extreme.cli test --category stress --verbose

# 4. Run with coverage
python -m tests.extreme.cli test --with-coverage

# 5. Generate oracle test cases
python -m tests.extreme.cli generate-data --type oracle --count 5
```

### CI Integration

**GitHub Actions:**
```yaml
# .github/workflows/custom.yml
- name: Run extreme tests
  run: python -m tests.extreme.cli test --fast --fail-fast
```

**GitLab CI:**
```yaml
# .gitlab-ci.yml
test:
  script:
    - python -m tests.extreme.cli test --fast --fail-fast
```

## Support

For issues or questions:
1. Check test outputs in `test_outputs/extreme/`
2. Review HTML reports for detailed diagnostics
3. Check CI/CD logs for pipeline failures
4. Consult `tests/extreme/README.md` for framework details
