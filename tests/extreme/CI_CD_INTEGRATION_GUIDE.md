# CI/CD Integration Guide for Extreme Testing Framework

This guide provides comprehensive instructions for integrating the Extreme Testing Framework with various CI/CD platforms.

## Table of Contents

1. [Overview](#overview)
2. [GitHub Actions Integration](#github-actions-integration)
3. [GitLab CI Integration](#gitlab-ci-integration)
4. [Report Formats](#report-formats)
5. [Selective Test Execution](#selective-test-execution)
6. [Performance Optimization](#performance-optimization)
7. [Troubleshooting](#troubleshooting)

---

## Overview

The Extreme Testing Framework provides comprehensive testing capabilities with full CI/CD integration support:

- **Multiple Report Formats**: JUnit XML, HTML, JSON, GitHub Annotations
- **Selective Execution**: Run specific categories or requirements
- **Fast vs Full Suites**: Quick validation vs comprehensive testing
- **Artifact Management**: Automatic upload of test results and reports
- **Failure Tracking**: Breaking points and failure mode documentation

### Test Categories

- **Property Tests**: Property-based testing with Hypothesis (1000 examples)
- **Stress Tests**: Maximum load, concurrency, resource leaks
- **Chaos Tests**: Fault injection, disk full, memory exhaustion
- **Adversarial Tests**: Security testing, malicious inputs
- **Boundary Tests**: Edge cases, extreme inputs
- **Performance Tests**: Profiling, bottleneck identification
- **Component Tests**: Component-specific stress tests
- **Integration Tests**: End-to-end chaos scenarios

---

## GitHub Actions Integration

### Quick Start

The framework includes pre-configured GitHub Actions workflows:

- **`quick-tests.yml`**: Fast validation (30 minutes) - runs on every push
- **`extreme-tests.yml`**: Comprehensive testing (3-4 hours) - runs on main/develop
- **`nightly-comprehensive.yml`**: Full suite (8-12 hours) - runs nightly

### Workflow Files

Located in `.github/workflows/`:

```
.github/workflows/
├── quick-tests.yml              # Fast validation
├── extreme-tests.yml            # Comprehensive testing
├── nightly-comprehensive.yml    # Full nightly suite
└── README.md                    # Workflow documentation
```

### Manual Trigger

Trigger workflows manually with specific categories:

```bash
# Trigger extreme tests
gh workflow run extreme-tests.yml

# Trigger with specific category
gh workflow run extreme-tests.yml -f test_category=property

# Trigger nightly comprehensive
gh workflow run nightly-comprehensive.yml
```

### Viewing Results

```bash
# List recent runs
gh run list --workflow=extreme-tests.yml

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

### GitHub Annotations

The framework generates GitHub annotations for inline display of test failures:

```json
{
  "annotations": [
    {
      "path": "tests/extreme/engines/stress_tester.py",
      "start_line": 1,
      "end_line": 1,
      "annotation_level": "error",
      "message": "test_maximum_document_size: Memory exhaustion at 100 pages",
      "title": "FAIL: stress.test_maximum_document_size"
    }
  ]
}
```

Annotations are automatically displayed in:
- Pull request checks
- Commit status checks
- GitHub Actions summary

### Artifact Retention

| Artifact Type | Retention Period |
|---------------|------------------|
| Test results (XML) | 30 days |
| Coverage reports | 30 days |
| Performance baselines | 90 days |
| Nightly reports | 90 days |
| 24-hour stability | 90 days |

---

## GitLab CI Integration

### Quick Start

The framework includes a comprehensive GitLab CI configuration in `.gitlab-ci.yml`.

### Pipeline Stages

1. **quick-validation**: Fast tests on every push (30 minutes)
2. **extreme-testing**: Comprehensive tests on main/develop (3-4 hours)
3. **report**: Generate comprehensive reports

### Running Tests

#### Automatic Triggers

- **Every push**: Quick validation tests
- **Main/Develop branches**: Full extreme testing suite
- **Scheduled pipelines**: Nightly comprehensive tests
- **Manual triggers**: Specific category tests

#### Manual Execution

Set the `TEST_CATEGORY` variable to run specific categories:

```bash
# Via GitLab UI
# Pipeline > Run Pipeline > Variables
# Key: TEST_CATEGORY
# Value: stress

# Via GitLab CLI
gitlab-runner exec docker manual-category-test \
  --env TEST_CATEGORY=stress
```

### Test Reports

GitLab CI automatically processes JUnit XML reports:

```yaml
artifacts:
  reports:
    junit: test-results/*.xml
    coverage_report:
      coverage_format: cobertura
      path: coverage.xml
```

Reports are displayed in:
- Merge request widgets
- Pipeline test reports
- Coverage visualization

### Artifact Management

```yaml
artifacts:
  when: always
  paths:
    - test-results/
    - test_outputs/
    - htmlcov/
  expire_in: 30 days
```

### Parallel Execution

Property tests run in parallel across Python versions:

```yaml
parallel:
  matrix:
    - PYTHON_VERSION: ["3.11", "3.12"]
```

---

## Report Formats

### JUnit XML

Standard format for CI/CD integration:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Extreme Testing Framework" tests="150" failures="5" errors="2">
  <testsuite name="stress" tests="30" failures="2" errors="0">
    <testcase name="test_maximum_document_size" classname="stress" time="45.3">
      <failure message="Memory exhaustion">Memory usage exceeded 16GB</failure>
    </testcase>
  </testsuite>
</testsuites>
```

**Usage:**
- Automatic parsing by CI/CD platforms
- Test result visualization
- Failure tracking

### HTML Report

Comprehensive human-readable report:

- Executive summary with pass/fail metrics
- Category breakdown
- Requirement coverage (80 requirements)
- Breaking points with thresholds
- Failure modes with mitigations
- Performance baselines

**Location:** `test_outputs/extreme/test_report_YYYYMMDD_HHMMSS.html`

### JSON Report

Machine-readable format for automation:

```json
{
  "execution_date": "2024-01-15T10:30:00",
  "total_tests": 150,
  "passed": 143,
  "failed": 5,
  "errors": 2,
  "category_results": {...},
  "requirement_results": {...},
  "breaking_points": [...],
  "failure_modes": [...]
}
```

**Usage:**
- Automated analysis
- Trend tracking
- Integration with monitoring systems

### GitHub Annotations

Inline annotations for GitHub Actions:

```json
{
  "annotations": [...],
  "summary": {
    "total_tests": 150,
    "passed": 143,
    "failed": 5,
    "pass_rate": 95.3
  }
}
```

**Usage:**
- Inline display in pull requests
- Commit status checks
- GitHub Actions summary

---

## Selective Test Execution

### By Category

Run specific test categories:

```bash
# Single category
python -m tests.extreme.cli --categories stress

# Multiple categories
python -m tests.extreme.cli --categories stress chaos adversarial

# All categories
python -m tests.extreme.cli --categories all
```

**Available categories:**
- `stress`: Maximum load, concurrency, resource leaks
- `chaos`: Fault injection, disk full, memory exhaustion
- `adversarial`: Security testing, malicious inputs
- `boundary`: Edge cases, extreme inputs
- `performance`: Profiling, bottleneck identification
- `property`: Property-based testing

### By Requirement

Run tests for specific requirements:

```bash
# Single requirement
python -m tests.extreme.cli --requirements 1.1

# Multiple requirements
python -m tests.extreme.cli --requirements 1.1 1.2 2.1

# All requirements in a range
python -m tests.extreme.cli --requirements 1.1 1.2 1.3 1.4 1.5
```

### Fast vs Full Suites

#### Fast Suite (Quick Validation)

**Duration:** 30 minutes  
**Use case:** Development, pull requests

```bash
# Unit tests only (non-slow, non-property)
pytest tests/ -m "not slow and not property" -v

# Quick property tests (10 examples)
pytest tests/extreme/test_properties.py --hypothesis-profile=quick -v
```

#### Full Suite (Comprehensive Testing)

**Duration:** 3-4 hours  
**Use case:** Main branch, nightly builds

```bash
# All categories with full examples
python -m tests.extreme.cli --categories all --verbose
```

#### Nightly Suite (Maximum Coverage)

**Duration:** 8-12 hours  
**Use case:** Scheduled nightly runs

```bash
# Full suite with 24-hour continuous stress test
python -m tests.extreme.cli --categories all --verbose \
  --with-coverage --output-dir test_outputs/nightly/
```

---

## Performance Optimization

### Parallel Execution

Run tests in parallel to reduce execution time:

```bash
# Pytest parallel execution
pytest tests/extreme/ -n auto -v

# Specific number of workers
pytest tests/extreme/ -n 4 -v
```

### Resource Requirements

#### Minimum Requirements

- **CPU**: 2 cores
- **RAM**: 8 GB
- **Disk**: 20 GB
- **Duration**: 4-6 hours (full suite)

#### Recommended Requirements

- **CPU**: 8+ cores
- **RAM**: 16+ GB
- **Disk**: 100+ GB
- **Duration**: 2-3 hours (full suite)

### Caching

Cache dependencies to speed up CI/CD runs:

**GitHub Actions:**
```yaml
- uses: actions/setup-python@v5
  with:
    python-version: '3.11'
    cache: 'pip'
```

**GitLab CI:**
```yaml
cache:
  paths:
    - .cache/pip
    - .hypothesis/
```

### Hypothesis Profiles

Configure Hypothesis for different environments:

```python
# conftest.py
from hypothesis import settings, HealthCheck

# Quick profile for development
settings.register_profile("quick", max_examples=10, deadline=None)

# CI profile for continuous integration
settings.register_profile("ci", max_examples=100, deadline=None)

# Full profile for comprehensive testing
settings.register_profile("full", max_examples=1000, deadline=None,
                         suppress_health_check=[HealthCheck.too_slow])
```

**Usage:**
```bash
# Quick tests
pytest --hypothesis-profile=quick

# CI tests
pytest --hypothesis-profile=ci

# Full tests
pytest --hypothesis-profile=full
```

---

## Troubleshooting

### Common Issues

#### Tests Timing Out

**Symptoms:**
- Tests exceed timeout limits
- CI/CD jobs killed

**Solutions:**
1. Increase timeout in workflow file:
   ```yaml
   timeout-minutes: 240  # 4 hours
   ```

2. Use self-hosted runners with more resources

3. Reduce `max_examples` in property tests:
   ```python
   @settings(max_examples=100)  # Instead of 1000
   ```

4. Split tests into smaller batches

#### Out of Memory Errors

**Symptoms:**
- Tests crash with OOM errors
- System becomes unresponsive

**Solutions:**
1. Increase runner memory (16+ GB recommended)

2. Reduce concurrent test workers:
   ```bash
   python -m tests.extreme.cli --concurrency 2
   ```

3. Run tests sequentially:
   ```bash
   pytest tests/extreme/ -v  # No -n flag
   ```

4. Use resource limits:
   ```python
   import resource
   resource.setrlimit(resource.RLIMIT_AS, (8 * 1024**3, -1))  # 8GB limit
   ```

#### Artifact Upload Failures

**Symptoms:**
- Artifacts fail to upload
- "Artifact too large" errors

**Solutions:**
1. Check artifact size limits (10 GB per artifact for GitHub)

2. Compress large artifacts:
   ```bash
   tar -czf test_outputs.tar.gz test_outputs/
   ```

3. Use selective artifact uploads:
   ```yaml
   paths:
     - test_outputs/extreme/*.html
     - test_outputs/extreme/*.json
     # Exclude large files
   ```

4. Reduce artifact retention period:
   ```yaml
   expire_in: 7 days  # Instead of 30 days
   ```

#### Flaky Tests

**Symptoms:**
- Tests pass/fail inconsistently
- Different results on different runs

**Solutions:**
1. Use Hypothesis to identify flaky tests:
   ```python
   @settings(max_examples=1000, derandomize=True)
   ```

2. Add explicit timeouts:
   ```python
   @pytest.mark.timeout(300)  # 5 minutes
   ```

3. Increase tolerance for timing-sensitive tests:
   ```python
   assert duration < 10.0 * 1.1  # 10% tolerance
   ```

4. Use retry logic for network-dependent tests:
   ```python
   @pytest.mark.flaky(reruns=3, reruns_delay=2)
   ```

### Getting Help

For issues with CI/CD integration:

1. **Check workflow logs**: Review detailed logs in CI/CD platform
2. **Review artifacts**: Download and inspect test outputs
3. **Run locally**: Reproduce issues on local machine
4. **Check resources**: Verify runner has sufficient CPU/RAM/disk
5. **Update dependencies**: Ensure all packages are up to date

For test failures:

1. **Review test logs**: Check detailed error messages
2. **Check baselines**: Verify performance baselines are current
3. **Verify test data**: Ensure test data integrity
4. **Run specific tests**: Isolate failing tests
5. **Check requirements**: Verify all dependencies installed

---

## Best Practices

### Development Workflow

1. **Run quick tests locally** before pushing:
   ```bash
   pytest tests/ -m "not slow and not property" -v
   ```

2. **Use pre-commit hooks** for linting:
   ```bash
   pre-commit install
   ```

3. **Monitor CI/CD results** for trends

4. **Review performance baselines** regularly

5. **Update test data** when system changes

### CI/CD Configuration

1. **Use caching** to speed up builds

2. **Set appropriate timeouts** for each job

3. **Configure artifact retention** based on needs

4. **Use parallel execution** where possible

5. **Monitor resource usage** and adjust as needed

### Test Maintenance

1. **Keep workflows updated** with new test categories

2. **Document expected duration** for new tests

3. **Add appropriate pytest markers** (`@pytest.mark.slow`, `@pytest.mark.property`)

4. **Update baselines** when performance improves

5. **Review and update** failure mode catalog

---

## Examples

### Example 1: Quick Validation in Pull Request

```yaml
# .github/workflows/pr-validation.yml
name: PR Validation
on: pull_request

jobs:
  quick-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: pytest tests/ -m "not slow and not property" -v
```

### Example 2: Nightly Comprehensive Testing

```yaml
# .github/workflows/nightly.yml
name: Nightly Tests
on:
  schedule:
    - cron: '0 2 * * *'  # 2 AM daily

jobs:
  full-suite:
    runs-on: ubuntu-latest
    timeout-minutes: 720  # 12 hours
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: python -m tests.extreme.cli --categories all --verbose
      - uses: actions/upload-artifact@v4
        if: always()
        with:
          name: nightly-report
          path: test_outputs/extreme/
          retention-days: 90
```

### Example 3: Manual Category Testing

```yaml
# .github/workflows/manual-test.yml
name: Manual Test
on:
  workflow_dispatch:
    inputs:
      category:
        description: 'Test category'
        required: true
        type: choice
        options:
          - stress
          - chaos
          - adversarial
          - boundary
          - performance
          - property

jobs:
  category-test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: '3.11'
          cache: 'pip'
      - run: pip install -r requirements.txt
      - run: python -m tests.extreme.cli --categories ${{ inputs.category }} --verbose
```

---

## Summary

The Extreme Testing Framework provides comprehensive CI/CD integration with:

✅ **Multiple CI/CD platforms**: GitHub Actions, GitLab CI  
✅ **Multiple report formats**: JUnit XML, HTML, JSON, GitHub Annotations  
✅ **Selective execution**: By category, requirement, or full suite  
✅ **Fast and full suites**: Quick validation vs comprehensive testing  
✅ **Artifact management**: Automatic upload and retention  
✅ **Failure tracking**: Breaking points and failure modes  

For questions or issues, refer to the workflow documentation in `.github/workflows/README.md` or the main testing framework README in `tests/extreme/README.md`.
