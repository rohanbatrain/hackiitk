# GitHub CI/CD Quick Start Guide

## Overview

This guide helps you quickly get started with the GitHub CI/CD workflows for the extreme testing suite.

## Workflows at a Glance

| Workflow | When It Runs | Duration | Purpose |
|----------|--------------|----------|---------|
| **Quick Tests** | Every push/PR | 30 min | Fast validation |
| **Extreme Tests** | Push to main/develop, daily | 3-4 hours | Comprehensive testing |
| **Nightly Comprehensive** | Daily at 1 AM UTC | 8-12 hours | Full suite + long-running tests |

## Quick Start

### 1. Automatic Execution

Workflows run automatically:
- **Quick Tests:** On every push and pull request
- **Extreme Tests:** On push to main/develop branches
- **Nightly Comprehensive:** Every night at 1 AM UTC

No action needed - just push your code!

### 2. Manual Execution

Trigger workflows manually using GitHub CLI:

```bash
# Install GitHub CLI (if not already installed)
brew install gh  # macOS
# or visit: https://cli.github.com/

# Authenticate
gh auth login

# Trigger extreme tests
gh workflow run extreme-tests.yml

# Trigger with specific category
gh workflow run extreme-tests.yml -f test_category=property

# Trigger nightly comprehensive
gh workflow run nightly-comprehensive.yml
```

Or use the GitHub web interface:
1. Go to **Actions** tab
2. Select workflow from left sidebar
3. Click **Run workflow** button
4. Choose branch and options
5. Click **Run workflow**

### 3. View Results

```bash
# List recent workflow runs
gh run list

# List runs for specific workflow
gh run list --workflow=extreme-tests.yml

# View specific run details
gh run view <run-id>

# Watch run in real-time
gh run watch <run-id>

# Download artifacts
gh run download <run-id>
```

Or use the GitHub web interface:
1. Go to **Actions** tab
2. Click on workflow run
3. View job details and logs
4. Download artifacts from **Artifacts** section

## Workflow Details

### Quick Tests (30 minutes)

**What it does:**
- Runs unit tests (non-slow, non-property)
- Runs quick property tests (10 examples)
- Checks code formatting and linting
- Generates coverage reports

**When to use:**
- During active development
- Before creating a pull request
- For fast feedback on changes

**Artifacts:**
- Test results (JUnit XML)
- Coverage reports (XML, HTML)

### Extreme Tests (3-4 hours)

**What it does:**
- Runs all test categories in parallel:
  - Property tests (1000 examples)
  - Stress tests
  - Chaos tests
  - Adversarial tests
  - Boundary tests
  - Performance tests
  - Component tests
  - Integration tests
- Generates comprehensive report
- Publishes test results

**When to use:**
- Before merging to main
- After significant changes
- For comprehensive validation

**Artifacts:**
- Test results for all categories
- Coverage reports
- Performance baselines
- Comprehensive test report

### Nightly Comprehensive (8-12 hours)

**What it does:**
- Runs full test suite (8-10 hours)
- Runs 24-hour continuous stress test
- Runs model comparison tests
- Creates GitHub issue on failure

**When to use:**
- Automatic nightly runs
- Manual trigger for deep validation
- Before major releases

**Artifacts:**
- Full test suite results (90-day retention)
- 24-hour stability report (90-day retention)
- Model comparison results (90-day retention)
- Annual summary (365-day retention)

## Common Tasks

### Run Property Tests Locally

```bash
# Quick validation (10 examples, ~1 minute)
pytest tests/extreme/test_properties.py --hypothesis-profile=quick -v

# Full validation (1000 examples, ~2 hours)
pytest tests/extreme/test_properties.py -v

# Specific property class
pytest tests/extreme/test_properties.py::TestResourceLeakProperty -v
```

### Run Specific Test Category

```bash
# Trigger extreme tests with specific category
gh workflow run extreme-tests.yml -f test_category=stress
gh workflow run extreme-tests.yml -f test_category=chaos
gh workflow run extreme-tests.yml -f test_category=property
```

### Download Test Results

```bash
# List recent runs
gh run list --workflow=extreme-tests.yml --limit 5

# Download artifacts from specific run
gh run download <run-id>

# Download specific artifact
gh run download <run-id> -n property-test-results-3.11
```

### Check Test Status

```bash
# View run status
gh run view <run-id>

# View run logs
gh run view <run-id> --log

# View specific job logs
gh run view <run-id> --job=<job-id> --log
```

## Understanding Test Results

### Pass/Fail Criteria

**Quick Tests:**
- All unit tests must pass
- Property tests (10 examples) must pass
- Linting checks should pass (warnings allowed)

**Extreme Tests:**
- ≥95% test pass rate required
- Critical tests must pass
- Non-critical tests can fail (continue-on-error)

**Nightly Comprehensive:**
- ≥80% pass rate required
- Creates GitHub issue if below threshold
- Tracks trends over time

### Artifacts

**Test Results (JUnit XML):**
- Standard test result format
- Viewable in GitHub Actions UI
- Can be imported into test management tools

**Coverage Reports:**
- XML format for Codecov integration
- HTML format for detailed viewing
- Shows code coverage by file and line

**Performance Baselines:**
- JSON format with metrics
- Used for regression detection
- Tracks performance over time

## Troubleshooting

### Workflow Not Running

**Check:**
1. Workflow file syntax (YAML validation)
2. Branch name matches trigger conditions
3. GitHub Actions enabled for repository
4. Workflow permissions configured

**Fix:**
```bash
# Validate workflow file
gh workflow view extreme-tests.yml

# Check workflow status
gh workflow list

# Enable workflow if disabled
gh workflow enable extreme-tests.yml
```

### Tests Failing

**Check:**
1. Test logs in GitHub Actions UI
2. Artifact downloads for detailed results
3. Recent code changes that might cause failures

**Fix:**
```bash
# View failure logs
gh run view <run-id> --log-failed

# Download artifacts for analysis
gh run download <run-id>

# Run tests locally to reproduce
pytest tests/extreme/test_properties.py -v --tb=short
```

### Timeout Issues

**Symptoms:**
- Jobs timing out before completion
- Tests not finishing within time limit

**Solutions:**
1. Increase timeout in workflow file
2. Use self-hosted runners with more resources
3. Reduce test examples (for property tests)
4. Split tests into smaller batches

### Out of Memory

**Symptoms:**
- Jobs failing with OOM errors
- Tests crashing during execution

**Solutions:**
1. Use runners with more memory
2. Reduce concurrent test workers
3. Reduce test data size
4. Add memory limits to tests

## Best Practices

### Before Pushing

1. **Run quick tests locally:**
   ```bash
   pytest tests/ -m "not slow and not property" -v
   ```

2. **Run quick property tests:**
   ```bash
   pytest tests/extreme/test_properties.py --hypothesis-profile=quick -v
   ```

3. **Check linting:**
   ```bash
   flake8 . --count --select=E9,F63,F7,F82 --show-source
   black --check .
   ```

### During Development

1. **Monitor quick test results** on every push
2. **Review coverage reports** to ensure adequate testing
3. **Fix failures immediately** to maintain green builds

### Before Merging

1. **Wait for extreme tests** to complete
2. **Review comprehensive test report**
3. **Check performance baselines** for regressions
4. **Verify all critical tests pass**

### After Merging

1. **Monitor nightly comprehensive results**
2. **Review any created issues**
3. **Track performance trends**
4. **Update baselines if needed**

## Configuration

### Hypothesis Settings

**Quick Profile (CI):**
```python
# Set via environment variable
HYPOTHESIS_PROFILE=quick
# Uses max_examples=10
```

**Full Profile (default):**
```python
@settings(
    max_examples=1000,
    deadline=None
)
```

### Workflow Timeouts

| Job | Default Timeout | Adjustable |
|-----|----------------|------------|
| Quick tests | 30 min | Yes |
| Property tests | 120 min | Yes |
| Stress tests | 180 min | Yes |
| Full suite | 720 min (12 hours) | Yes |
| 24-hour continuous | 1500 min (25 hours) | Yes |

To adjust timeouts, edit the workflow file:
```yaml
jobs:
  my-job:
    timeout-minutes: 240  # 4 hours
```

## Getting Help

### Documentation

- **Workflow README:** `.github/workflows/README.md`
- **Property Tests Summary:** `tests/extreme/PROPERTY_TESTS_AND_CI_SUMMARY.md`
- **Task Completion Summary:** `TASK_29_COMPLETION_SUMMARY.md`

### GitHub Actions Docs

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/reference/workflow-syntax-for-github-actions)
- [GitHub CLI](https://cli.github.com/manual/)

### Support

For issues with:
- **Workflows:** Check workflow logs and artifacts
- **Tests:** Run locally to reproduce
- **CI/CD:** Review GitHub Actions documentation
- **Property Tests:** Check Hypothesis documentation

## Quick Reference

### Essential Commands

```bash
# Trigger workflow
gh workflow run extreme-tests.yml

# View status
gh run list --workflow=extreme-tests.yml

# Watch run
gh run watch

# Download results
gh run download <run-id>

# View logs
gh run view <run-id> --log
```

### Essential Files

- `.github/workflows/quick-tests.yml` - Fast validation
- `.github/workflows/extreme-tests.yml` - Comprehensive testing
- `.github/workflows/nightly-comprehensive.yml` - Long-running tests
- `tests/extreme/test_properties.py` - Property-based tests

### Essential Links

- **Actions Tab:** `https://github.com/<owner>/<repo>/actions`
- **Workflow Runs:** `https://github.com/<owner>/<repo>/actions/workflows/<workflow>.yml`
- **Artifacts:** Available in each workflow run

## Summary

The GitHub CI/CD infrastructure provides:

✅ **Automatic testing** on every push/PR  
✅ **Comprehensive coverage** across all test categories  
✅ **Heavy testing** offloaded to GitHub runners  
✅ **Long-running tests** (24-hour continuous)  
✅ **Flexible execution** (automatic, scheduled, manual)  
✅ **Detailed reporting** with artifacts and metrics  
✅ **Monitoring and alerts** with automatic issue creation  

Start using it today by simply pushing your code - the workflows will run automatically!
