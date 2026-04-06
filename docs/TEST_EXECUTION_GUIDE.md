# Test Execution Guide

## Overview

This guide provides comprehensive instructions for running tests in the Offline Policy Gap Analyzer, interpreting test reports, and managing test baselines.

## Quick Start

### Run All Tests

```bash
# Run complete test suite (4 hours)
python -m tests.extreme.cli test

# Run with verbose output
python -m tests.extreme.cli test --verbose
```

### Run Fast Tests

```bash
# Run only fast tests (30 minutes)
python -m tests.extreme.cli test --fast

# Fast tests include: property, boundary, adversarial
```

## Running Specific Test Categories

### By Category

```bash
# Run stress tests only
python -m tests.extreme.cli test --category stress

# Run multiple categories
python -m tests.extreme.cli test --category stress --category chaos

# Available categories:
# - stress: Maximum load scenarios
# - chaos: Fault injection
# - adversarial: Security testing
# - boundary: Edge cases
# - performance: Performance profiling
# - property: Property-based tests
```

### By Requirement

```bash
# Run tests for specific requirement
python -m tests.extreme.cli test --requirement 1.1

# Run tests for multiple requirements
python -m tests.extreme.cli test --requirement 1.1 --requirement 2.3 --requirement 72.4
```

### Category Details

#### Stress Tests
**Duration**: ~2 hours  
**Purpose**: Validate system under maximum load

```bash
python -m tests.extreme.cli test --category stress
```

**Tests Include**:
- 100-page document processing
- 500,000-word documents
- 10,000+ chunks after segmentation
- 5+ concurrent analyses
- Resource leak detection (100+ sequential runs)
- Breaking point identification

**Expected Results**:
- All tests pass or fail gracefully
- No crashes or data corruption
- Resource usage within limits
- Breaking points documented

#### Chaos Tests
**Duration**: ~2 hours  
**Purpose**: Validate error handling under failures

```bash
python -m tests.extreme.cli test --category chaos
```

**Tests Include**:
- Disk full scenarios
- Memory exhaustion
- Model file corruption
- Process interruptions (SIGINT, SIGTERM, SIGKILL)
- File system permission errors
- Configuration chaos (50+ invalid configs)

**Expected Results**:
- Graceful degradation
- Descriptive error messages
- Proper cleanup after failures
- No data corruption

#### Adversarial Tests
**Duration**: ~30 minutes  
**Purpose**: Validate security boundaries

```bash
python -m tests.extreme.cli test --category adversarial
```

**Tests Include**:
- Malicious PDFs (20+ samples)
- Buffer overflow attempts
- Encoding attacks
- Path traversal attempts
- Prompt injection attacks
- Chunking boundary attacks

**Expected Results**:
- Malicious inputs rejected or sanitized
- No crashes or exploits
- Input validation working
- Security boundaries enforced

#### Boundary Tests
**Duration**: ~30 minutes  
**Purpose**: Validate edge cases

```bash
python -m tests.extreme.cli test --category boundary
```

**Tests Include**:
- Empty and whitespace-only documents
- Structural anomalies (no headings, 100+ nesting)
- Coverage boundaries (0 gaps, 49 gaps)
- Encoding diversity (10+ languages)
- Similarity score boundaries
- Extreme parameters

**Expected Results**:
- Edge cases handled gracefully
- Descriptive error messages
- No crashes on extreme inputs
- Boundary conditions validated

#### Performance Tests
**Duration**: ~2 hours  
**Purpose**: Measure performance characteristics

```bash
python -m tests.extreme.cli test --category performance
```

**Tests Include**:
- Document size scaling (1-100 pages)
- Chunk count scaling (10-10,000 chunks)
- LLM context scaling (100-10,000 tokens)
- Bottleneck identification
- Baseline establishment
- Degradation curve generation

**Expected Results**:
- Performance baselines established
- Bottlenecks identified
- Degradation curves generated
- No exponential scaling

#### Property Tests
**Duration**: ~30 minutes  
**Purpose**: Validate universal properties

```bash
python -m tests.extreme.cli test --category property
```

**Tests Include**:
- 1000+ examples per property
- Invariant testing
- Round-trip properties
- Metamorphic properties
- System invariants

**Expected Results**:
- All properties hold
- No counterexamples found
- Failing examples saved for regression

## Execution Options

### Concurrency Control

```bash
# Set number of concurrent workers (default: 4)
python -m tests.extreme.cli test --concurrency 8

# Reduce for memory-constrained environments
python -m tests.extreme.cli test --concurrency 2
```

### Timeout Configuration

```bash
# Set timeout in seconds (default: 3600)
python -m tests.extreme.cli test --timeout 7200

# For fast tests (10 minutes)
python -m tests.extreme.cli test --fast --timeout 600
```

### Fail-Fast Mode

```bash
# Stop on first failure
python -m tests.extreme.cli test --fail-fast

# Useful for quick validation
python -m tests.extreme.cli test --fast --fail-fast
```

### Output Directory

```bash
# Specify custom output directory
python -m tests.extreme.cli test --output-dir custom_output/

# Default: test_outputs/extreme/
```

### Report Formats

```bash
# Disable specific report formats
python -m tests.extreme.cli test --no-html
python -m tests.extreme.cli test --no-json
python -m tests.extreme.cli test --no-junit

# All reports disabled (minimal output)
python -m tests.extreme.cli test --no-html --no-json --no-junit
```

### With Coverage

```bash
# Run tests with code coverage measurement
python -m tests.extreme.cli test --with-coverage

# Coverage reports generated in: coverage_reports_demo/
```

## Interpreting Test Reports

### HTML Report

**Location**: `test_outputs/extreme/test_report.html`

**Sections**:

1. **Executive Summary**
   - Total tests: 702
   - Passed: 685
   - Failed: 17
   - Skipped: 73
   - Success rate: 97.7%
   - Execution time: 3h 45m

2. **Category Results**
   - Pass/fail counts per category
   - Execution time per category
   - Key findings per category

3. **Requirement Coverage**
   - 80 requirements validated
   - Pass/fail status per requirement
   - Traceability to tests

4. **Breaking Points**
   - Maximum viable values
   - Failure modes
   - Hardware requirements
   - Mitigation strategies

5. **Failure Modes**
   - Documented failure scenarios
   - Trigger conditions
   - Impact assessment
   - Mitigation recommendations

6. **Performance Baselines**
   - Baseline metrics
   - Regression detection
   - Performance trends

7. **Artifacts**
   - Links to detailed logs
   - Test outputs
   - Coverage reports

**Interpreting Results**:

✅ **PASS**: Test completed successfully, all assertions passed  
❌ **FAIL**: Test failed, assertions not met or unexpected error  
⏭️ **SKIP**: Test skipped (environment-specific or optional)  
⚠️ **ERROR**: Test encountered unexpected error during execution

### JSON Report

**Location**: `test_outputs/extreme/test_report.json`

**Structure**:
```json
{
  "execution_date": "2026-04-06T10:30:00Z",
  "total_tests": 702,
  "passed": 685,
  "failed": 17,
  "skipped": 73,
  "errors": 0,
  "duration_seconds": 13500,
  "category_results": {
    "stress": {
      "total": 150,
      "passed": 145,
      "failed": 5,
      "duration": 7200
    },
    ...
  },
  "requirement_results": {
    "1.1": {
      "status": "pass",
      "tests": ["test_maximum_document_size"],
      "duration": 120
    },
    ...
  },
  "breaking_points": [
    {
      "dimension": "document_size_pages",
      "maximum_viable_value": 100,
      "failure_mode": "memory_exhaustion",
      "metrics": {...}
    },
    ...
  ],
  "failure_modes": [
    {
      "failure_id": "FM-001",
      "category": "crash",
      "trigger": "Processing documents >100 pages",
      "impact": "System crashes with OOM error",
      "mitigation": "Implement chunked processing"
    },
    ...
  ],
  "performance_baselines": {
    "10_page_document": {
      "duration_seconds": 120,
      "memory_peak_mb": 500,
      "cpu_average_percent": 65
    },
    ...
  }
}
```

**Use Cases**:
- Automated processing and analysis
- Custom reporting and dashboards
- Trend analysis over time
- CI/CD integration

### JUnit XML Report

**Location**: `test_outputs/extreme/test_report.xml`

**Format**: Standard JUnit XML

**Integration**:
- GitHub Actions (test results tab)
- GitLab CI (tests tab)
- Jenkins (test results)
- CircleCI (test summary)

**Example**:
```xml
<testsuites>
  <testsuite name="stress" tests="150" failures="5" skipped="0" time="7200">
    <testcase name="test_maximum_document_size" classname="stress" time="120">
      <system-out>Test output...</system-out>
    </testcase>
    <testcase name="test_concurrent_operations" classname="stress" time="300">
      <failure message="Assertion failed">Expected 5 operations to complete...</failure>
    </testcase>
    ...
  </testsuite>
  ...
</testsuites>
```

### Terminal Output

**Example**:
```
Extreme Testing Framework
=========================

Configuration:
  Categories: stress, chaos
  Concurrency: 4
  Timeout: 3600s
  Output: test_outputs/extreme/

Running Tests...
  [1/150] test_maximum_document_size ... PASS (120s)
  [2/150] test_concurrent_operations ... FAIL (300s)
    Error: Expected 5 operations to complete, got 4
  [3/150] test_resource_leaks ... PASS (450s)
  ...

Results:
  Total: 150
  Passed: 145 (96.7%)
  Failed: 5 (3.3%)
  Skipped: 0
  Duration: 2h 15m

Reports:
  HTML: test_outputs/extreme/test_report.html
  JSON: test_outputs/extreme/test_report.json
  JUnit: test_outputs/extreme/test_report.xml
```

## Updating Baselines

### When to Update

Update baselines when:
- Intentional performance improvements made
- Hardware configuration changes
- System behavior intentionally changed
- New features added that affect performance

**Do NOT update** when:
- Tests fail due to regressions
- Performance degrades unexpectedly
- Bugs are discovered

### How to Update

#### Performance Baselines

```bash
# 1. Run performance tests
python -m tests.extreme.cli test --category performance --verbose

# 2. Review results in test_outputs/extreme/test_report.html

# 3. If results are acceptable, update baselines
cp test_outputs/extreme/performance_metrics.json coverage_baselines/

# 4. Commit updated baselines
git add coverage_baselines/
git commit -m "Update performance baselines after optimization"
```

#### Oracle Test Cases

```bash
# 1. Analyze policy with current system
python -m cli.main analyze tests/extreme/oracles/oracle_001/policy.md

# 2. Review output in outputs/

# 3. If output is correct, update oracle expected results
# Edit: tests/extreme/oracles/oracle_001/expected.json

# 4. Commit updated oracle
git add tests/extreme/oracles/oracle_001/expected.json
git commit -m "Update oracle_001 after gap detection improvement"
```

### Baseline Files

**Location**: `coverage_baselines/`

**Files**:
- `performance_10page.json` - 10-page document baseline
- `performance_50page.json` - 50-page document baseline
- `performance_100page.json` - 100-page document baseline
- `memory_baseline.json` - Memory usage baseline
- `cpu_baseline.json` - CPU usage baseline

**Format**:
```json
{
  "baseline_name": "performance_10page",
  "date_established": "2026-04-06",
  "hardware": {
    "cpu": "Apple M1",
    "ram_gb": 16,
    "os": "macOS 14.0"
  },
  "metrics": {
    "duration_seconds": 120,
    "memory_peak_mb": 500,
    "memory_average_mb": 350,
    "cpu_peak_percent": 95,
    "cpu_average_percent": 65,
    "disk_read_mb": 50,
    "disk_write_mb": 25
  },
  "tolerance": 0.20
}
```

## Common Scenarios

### Pre-Commit Validation

```bash
# Quick validation before commit (5 minutes)
python -m tests.extreme.cli test --fast --fail-fast --verbose
```

### Pull Request Validation

```bash
# Comprehensive validation for PR (30 minutes)
python -m tests.extreme.cli test --category property --category boundary --category adversarial
```

### Release Validation

```bash
# Full suite with coverage (4 hours)
python -m tests.extreme.cli test --with-coverage --verbose
```

### Performance Regression Check

```bash
# Run performance tests and compare to baselines
python -m tests.extreme.cli test --category performance --verbose

# Check for >20% degradation in test_outputs/extreme/test_report.html
```

### Security Audit

```bash
# Run adversarial tests with verbose output
python -m tests.extreme.cli test --category adversarial --verbose

# Review security findings in test_outputs/extreme/test_report.html
```

### Stress Testing New Feature

```bash
# Run stress tests for specific requirement
python -m tests.extreme.cli test --category stress --requirement 1.1 --verbose
```

## Troubleshooting

### Test Failures

**Symptom**: Tests fail unexpectedly

**Diagnosis**:
1. Check HTML report for failure details
2. Review test logs in `test_outputs/extreme/logs/`
3. Check for environment issues (disk space, memory)

**Solutions**:
- Fix code if regression detected
- Update test if behavior intentionally changed
- Update baseline if performance improved
- Skip test if environment-specific

### Timeouts

**Symptom**: Tests timeout before completion

**Solutions**:
```bash
# Increase timeout
python -m tests.extreme.cli test --timeout 7200

# Reduce concurrency
python -m tests.extreme.cli test --concurrency 2

# Run specific category
python -m tests.extreme.cli test --category property
```

### Out of Memory

**Symptom**: Tests crash with OOM error

**Solutions**:
```bash
# Reduce concurrency
python -m tests.extreme.cli test --concurrency 1

# Run fast tests only
python -m tests.extreme.cli test --fast

# Skip stress tests
python -m tests.extreme.cli test --category property --category boundary
```

### Disk Space Issues

**Symptom**: Tests fail with disk full errors

**Solutions**:
1. Clean up old test outputs: `rm -rf test_outputs/extreme/old_*`
2. Clean up synthetic documents: `rm -rf tests/synthetic/*.md`
3. Clean up coverage reports: `rm -rf coverage_reports_demo/`
4. Increase disk space

### CI Pipeline Failures

**GitHub Actions**:
1. Check workflow logs in Actions tab
2. Download artifacts for detailed reports
3. Review JUnit XML for specific failures
4. Check for environment-specific issues

**GitLab CI**:
1. Check pipeline logs in CI/CD → Pipelines
2. Download artifacts from job page
3. Review JUnit reports in Tests tab
4. Check for environment-specific issues

## Best Practices

### For Development

1. **Run fast tests before every commit**
2. **Run full category after major changes**
3. **Update baselines after intentional improvements**
4. **Document new failure modes discovered**

### For CI/CD

1. **Fast tests on every PR** (30 min)
2. **Full suite weekly** (4 hours)
3. **Performance tests on release branches**
4. **Security tests on security-related changes**

### For Performance

1. **Establish baselines on target hardware**
2. **Run performance tests regularly**
3. **Alert on >20% degradation**
4. **Track trends over time**

### For Security

1. **Run adversarial tests regularly**
2. **Update attack patterns as threats evolve**
3. **Validate all input sanitization**
4. **Document security findings**

## References

- [Testing Framework Documentation](TESTING_FRAMEWORK.md)
- [CLI and CI Integration Guide](../tests/extreme/CLI_AND_CI_INTEGRATION_GUIDE.md)
- [Breaking Points Catalog](../tests/extreme/BREAKING_POINTS.md)
- [Failure Modes Catalog](../tests/extreme/FAILURE_MODES.md)

