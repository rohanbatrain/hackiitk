# Parallel Testing Strategy for Extreme Test Suite

## Overview

The extreme test suite contains 1055+ tests that would take 8-10 hours to run sequentially. We've implemented three levels of parallelization to dramatically reduce execution time:

1. **Standard Parallel** (`extreme-tests-parallel.yml`) - ~30 minutes wall time
2. **Ultra Parallel** (`extreme-tests-ultra-parallel.yml`) - ~15-20 minutes wall time
3. **Fast Tests** (on every PR) - ~5 minutes wall time

## Workflow Comparison

| Workflow | Jobs | Wall Time | When to Use | Cost |
|----------|------|-----------|-------------|------|
| `extreme-tests.yml` | 4-5 | ~2 hours | Weekly, manual | Low |
| `extreme-tests-parallel.yml` | 16 | ~30 min | Weekly, releases | Medium |
| `extreme-tests-ultra-parallel.yml` | 50+ | ~15 min | Critical releases | High |
| Fast tests only | 3 | ~5 min | Every PR | Very Low |

## Standard Parallel Workflow

**File:** `.github/workflows/extreme-tests-parallel.yml`

**Strategy:** Splits tests by test engine (16 parallel jobs)

**Jobs:**
- 3 fast test jobs (property, boundary, adversarial)
- 3 stress test jobs (max load, concurrent, resource leaks)
- 6 chaos test jobs (disk, memory, model, interruption, permissions, vector store)
- 4 performance test jobs (document, chunk, LLM, bottlenecks)

**Execution:**
```bash
# Triggered automatically on schedule
# Or manually via GitHub UI

# Manual trigger:
gh workflow run extreme-tests-parallel.yml
```

**Benefits:**
- Reduces 8-10 hours to ~30 minutes
- Organized by test category
- Easy to identify failing categories
- Moderate GitHub Actions cost

## Ultra Parallel Workflow

**File:** `.github/workflows/extreme-tests-ultra-parallel.yml`

**Strategy:** Dynamically generates matrix of test chunks (50+ parallel jobs)

**Features:**
- Automatically discovers all tests
- Groups tests into small chunks (5-10 tests per job)
- Runs up to 50 jobs in parallel (configurable)
- Aggregates results from all jobs

**Execution:**
```bash
# Manual trigger with custom parallelism
gh workflow run extreme-tests-ultra-parallel.yml \
  -f max_parallel=100

# Default (50 parallel jobs)
gh workflow run extreme-tests-ultra-parallel.yml
```

**Benefits:**
- Reduces 8-10 hours to ~15-20 minutes
- Maximum parallelization
- Fastest possible execution
- Higher GitHub Actions cost

**Configuration:**
```yaml
# Adjust max_parallel in workflow dispatch
max_parallel: 50  # Default
max_parallel: 100 # Maximum speed (higher cost)
max_parallel: 25  # Cost-conscious
```

## Fast Tests (PR Validation)

**Runs on:** Every push and pull request

**Duration:** ~5 minutes

**Tests:**
- Property tests (100% pass rate)
- Boundary tests (85.7% pass rate)
- Adversarial tests (security validation)

**Purpose:** Quick validation before merging

## Parallelization Strategy

### Test Categories and Timing

| Category | Sequential Time | Parallel Jobs | Wall Time |
|----------|----------------|---------------|-----------|
| Property | 30 min | 1 | 30 min |
| Boundary | 30 min | 1 | 30 min |
| Adversarial | 30 min | 1 | 30 min |
| Stress | 2 hours | 3 | 40 min |
| Chaos | 2 hours | 6 | 20 min |
| Performance | 2 hours | 4 | 30 min |
| **Total** | **8-10 hours** | **16 jobs** | **~30 min** |

### Ultra Parallel Breakdown

With 50 parallel jobs:
- Each job runs 5-10 tests
- Average job duration: 15-20 minutes
- Wall time: ~20 minutes (longest job)
- Total compute time: ~8 hours (distributed)

## GitHub Actions Configuration

### Runner Types

**Standard runners** (ubuntu-latest):
- 2 cores, 7GB RAM
- Good for: property, boundary, adversarial tests
- Cost: Included in free tier

**Large runners** (ubuntu-latest-8-cores):
- 8 cores, 32GB RAM
- Good for: stress, performance tests
- Cost: Premium (requires GitHub Team/Enterprise)

### Cost Optimization

**Free Tier Strategy:**
```yaml
# Use standard runners only
runs-on: ubuntu-latest

# Limit parallelism
max-parallel: 20

# Run full suite weekly only
schedule:
  - cron: '0 2 * * 0'  # Sunday 2 AM
```

**Premium Strategy:**
```yaml
# Use large runners for heavy tests
runs-on: ubuntu-latest-8-cores

# Maximum parallelism
max-parallel: 100

# Run on every release
on:
  release:
    types: [published]
```

## Usage Examples

### Run Fast Tests (Every PR)

Automatic - no action needed. Runs on every push/PR.

### Run Full Suite Weekly

Automatic - configured in workflow schedule.

### Manual Full Suite Run

```bash
# Standard parallel (30 min)
gh workflow run extreme-tests-parallel.yml

# Ultra parallel (15 min)
gh workflow run extreme-tests-ultra-parallel.yml

# With custom parallelism
gh workflow run extreme-tests-ultra-parallel.yml \
  -f max_parallel=75
```

### Run Specific Category

```bash
# Stress tests only
gh workflow run extreme-tests-parallel.yml \
  -f test_mode=stress-only

# Performance tests only
gh workflow run extreme-tests-parallel.yml \
  -f test_mode=performance-only
```

### Run Before Release

```bash
# Full validation with maximum speed
gh workflow run extreme-tests-ultra-parallel.yml \
  -f max_parallel=100

# Wait for completion
gh run watch

# Check results
gh run view --log
```

## Result Aggregation

All parallel workflows aggregate results automatically:

1. **Individual job results** uploaded as artifacts
2. **Aggregation job** combines all results
3. **Summary posted** to PR or workflow summary
4. **Success criteria checked** (≥95% pass rate)

### Viewing Results

**GitHub UI:**
1. Go to Actions tab
2. Select workflow run
3. View "Aggregate Test Results" job
4. Download "aggregated-test-results" artifact

**CLI:**
```bash
# List recent runs
gh run list --workflow=extreme-tests-ultra-parallel.yml

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

### Result Format

```json
{
  "execution_date": "2026-04-06T17:06:52",
  "total_tests": 1055,
  "passed": 1030,
  "failed": 20,
  "errors": 5,
  "pass_rate": 97.6,
  "duration_seconds": 1200,
  "parallel_jobs": 50,
  "categories": {
    "property": {"total": 202, "passed": 202},
    "boundary": {"total": 100, "passed": 95},
    "adversarial": {"total": 80, "passed": 75},
    "stress": {"total": 150, "passed": 145},
    "chaos": {"total": 120, "passed": 115},
    "performance": {"total": 50, "passed": 48}
  }
}
```

## Troubleshooting

### Jobs Timing Out

**Problem:** Individual jobs exceed timeout

**Solution:**
```yaml
# Increase timeout for specific categories
timeout-minutes: 90  # Default is 60

# Or split into smaller chunks
chunk_size: 3  # Reduce from 5
```

### Rate Limiting

**Problem:** Too many parallel jobs

**Solution:**
```yaml
# Reduce max_parallel
max-parallel: 25  # Down from 50

# Or stagger job starts
strategy:
  max-parallel: 25
  fail-fast: false
```

### Artifact Upload Failures

**Problem:** Too many artifacts

**Solution:**
```yaml
# Combine artifacts per category
- name: Upload results
  uses: actions/upload-artifact@v3
  with:
    name: test-results-${{ matrix.category }}  # Not per chunk
    path: test_outputs/extreme/*
```

### Cost Concerns

**Problem:** High GitHub Actions minutes usage

**Solution:**
1. Use standard runners only
2. Reduce max_parallel to 20
3. Run full suite weekly only
4. Use fast tests for PR validation

## Best Practices

### For Development

- Run fast tests locally before pushing
- Let CI run fast tests on PR
- Manually trigger full suite before merging major changes

### For CI/CD

- Fast tests on every PR (5 min)
- Standard parallel on weekly schedule (30 min)
- Ultra parallel on releases (15 min)
- Cache dependencies aggressively

### For Cost Management

- Use free tier runners when possible
- Limit parallelism to 20-25 jobs
- Run full suite weekly, not on every push
- Archive old test results

## Monitoring and Metrics

### Key Metrics to Track

1. **Pass Rate:** Should be ≥95%
2. **Wall Time:** Target <30 minutes
3. **Cost:** GitHub Actions minutes used
4. **Flaky Tests:** Tests that fail intermittently

### Setting Up Alerts

```yaml
# Add to workflow
- name: Check pass rate
  run: |
    if [ $PASS_RATE -lt 95 ]; then
      echo "::error::Pass rate below threshold"
      # Send alert (Slack, email, etc.)
    fi
```

## Future Improvements

1. **Self-hosted runners** for unlimited parallelism
2. **Test result caching** to skip unchanged tests
3. **Intelligent test selection** based on code changes
4. **Performance regression detection** with baselines
5. **Flaky test detection** and automatic retry

## Summary

The parallel testing strategy reduces extreme test suite execution from 8-10 hours to 15-30 minutes by:

- Splitting tests into 16-50+ parallel jobs
- Using appropriate runner sizes
- Aggregating results automatically
- Providing flexible execution modes

Choose the workflow based on your needs:
- **Fast tests:** Every PR (5 min)
- **Standard parallel:** Weekly, releases (30 min)
- **Ultra parallel:** Critical releases (15 min)
