# GitHub CI/CD Workflows for Extreme Testing

This directory contains GitHub Actions workflows for running the comprehensive extreme testing suite on CI/CD infrastructure.

## Workflows

### 1. Quick Tests (`quick-tests.yml`)

**Trigger:** Every push and pull request  
**Duration:** ~30 minutes  
**Purpose:** Fast validation for development

- Runs unit tests (non-slow, non-property)
- Runs quick property tests (10 examples)
- Linting and formatting checks
- Code coverage reporting

**Use case:** Quick feedback during development

### 2. Extreme Testing Suite (`extreme-tests.yml`)

**Trigger:** Push to main/develop, PRs, daily schedule, manual  
**Duration:** ~3-4 hours  
**Purpose:** Comprehensive testing across all categories

**Jobs:**
- **Property Tests** (2 hours): 1000 examples per property, Python 3.11 & 3.12
- **Stress Tests** (3 hours): Maximum load, concurrency, resource leaks
- **Chaos Tests** (3 hours): Fault injection, disk full, memory exhaustion
- **Adversarial Tests** (2 hours): Security testing, malicious inputs
- **Boundary Tests** (2 hours): Edge cases, extreme inputs
- **Performance Tests** (3 hours): Profiling, bottleneck identification
- **Component Tests** (3 hours): Component-specific stress tests
- **Integration Tests** (4 hours): End-to-end chaos scenarios

**Artifacts:**
- Test results (JUnit XML)
- Coverage reports (XML, HTML)
- Performance baselines
- Test logs

### 3. Nightly Comprehensive Tests (`nightly-comprehensive.yml`)

**Trigger:** Daily at 1 AM UTC, manual  
**Duration:** 8-12 hours  
**Purpose:** Full test suite execution with long-running tests

**Jobs:**
- **Full Test Suite** (8-10 hours): All tests with maximum examples
- **24-Hour Continuous Stress** (25 hours): Stability testing
- **Model Comparison** (4 hours): Test all supported models

**Features:**
- Automatic issue creation on failure
- 90-day artifact retention for reports
- Performance baseline tracking
- Stability analysis

## Running Tests Manually

### Trigger a specific workflow

```bash
# Trigger extreme tests
gh workflow run extreme-tests.yml

# Trigger with specific category
gh workflow run extreme-tests.yml -f test_category=property

# Trigger nightly comprehensive
gh workflow run nightly-comprehensive.yml
```

### View workflow status

```bash
# List recent runs
gh run list --workflow=extreme-tests.yml

# View specific run
gh run view <run-id>

# Download artifacts
gh run download <run-id>
```

## Test Categories

### Property-Based Tests
- Resource leak detection
- Data integrity under concurrency
- Cleanup after failures
- Error message completeness
- Input sanitization
- Metamorphic properties
- Performance scaling
- System invariants

### Stress Tests
- Maximum document size (100 pages, 500k words)
- Concurrent operations (5+ simultaneous)
- Resource leak detection (100+ iterations)
- Reference catalog scale (1000+ subcategories)

### Chaos Tests
- Disk full scenarios
- Memory exhaustion
- Model corruption
- Process interruption (SIGINT, SIGTERM, SIGKILL)
- Permission errors
- Configuration chaos

### Adversarial Tests
- Malicious PDFs (20+ samples)
- Buffer overflow attempts
- Encoding attacks
- Path traversal
- Prompt injection (15+ patterns)

### Boundary Tests
- Empty documents
- Structural anomalies
- Coverage boundaries
- Encoding diversity (10+ languages)
- Similarity score boundaries

### Performance Tests
- Document size scaling (1-100 pages)
- Chunk count scaling (10-10,000 chunks)
- LLM context scaling (100-10,000 tokens)
- Bottleneck identification
- Baseline establishment

## Artifact Retention

| Artifact Type | Retention Period |
|---------------|------------------|
| Test results (XML) | 30 days |
| Coverage reports | 30 days |
| Performance baselines | 90 days |
| Nightly reports | 90 days |
| 24-hour stability | 90 days |
| Annual summaries | 365 days |

## Monitoring and Alerts

### Automatic Issue Creation

The nightly comprehensive workflow automatically creates GitHub issues when:
- Pass rate drops below 80%
- 24-hour stability test fails
- Critical test failures occur

Issues are labeled with:
- `test-failure`
- `automated`

### Notifications

Configure GitHub notifications for:
- Workflow failures
- New issues created by workflows
- Artifact uploads

## Configuration

### Hypothesis Settings

Property tests use aggressive settings:
```python
@settings(
    max_examples=1000,
    deadline=None,
    suppress_health_check=[HealthCheck.too_slow]
)
```

For quick tests, use the `quick` profile:
```bash
pytest --hypothesis-profile=quick
```

### Timeouts

| Job | Timeout |
|-----|---------|
| Quick tests | 30 minutes |
| Property tests | 120 minutes |
| Stress tests | 180 minutes |
| Chaos tests | 180 minutes |
| Full suite | 720 minutes (12 hours) |
| 24-hour continuous | 1500 minutes (25 hours) |

## Resource Requirements

### GitHub Actions Runners

- **Standard runner:** 2-core CPU, 7 GB RAM, 14 GB SSD
- **Recommended for extreme tests:** Use self-hosted runners with:
  - 8+ core CPU
  - 16+ GB RAM
  - 100+ GB SSD

### Self-Hosted Runners

To use self-hosted runners for heavy tests:

1. Add runner labels to workflow:
```yaml
runs-on: [self-hosted, linux, x64, high-memory]
```

2. Configure runner with required resources
3. Install dependencies on runner

## Troubleshooting

### Tests timing out

- Increase timeout in workflow file
- Use self-hosted runners with more resources
- Reduce `max_examples` in property tests

### Out of memory errors

- Increase runner memory
- Reduce concurrent test workers
- Split tests into smaller batches

### Artifact upload failures

- Check artifact size limits (10 GB per artifact)
- Compress large artifacts
- Use selective artifact uploads

## Best Practices

1. **Run quick tests locally** before pushing
2. **Monitor nightly results** for trends
3. **Review performance baselines** regularly
4. **Update test data** when system changes
5. **Keep workflows updated** with new test categories

## Local Testing

Before pushing, run tests locally:

```bash
# Quick validation
pytest tests/ -m "not slow and not property" -v

# Property tests (quick profile)
pytest tests/extreme/test_properties.py --hypothesis-profile=quick -v

# Specific category
pytest tests/extreme/engines/test_stress.py -v

# Full suite (8-10 hours)
python -m tests.extreme.runner --categories all
```

## Contributing

When adding new tests:

1. Add appropriate pytest markers (`@pytest.mark.slow`, `@pytest.mark.property`)
2. Update workflow files if new categories added
3. Document expected duration
4. Test locally before pushing
5. Update this README

## Support

For issues with CI/CD workflows:
- Check workflow logs in GitHub Actions
- Review artifact contents
- Check runner capacity
- Verify dependencies are installed

For test failures:
- Review test logs
- Check performance baselines
- Verify test data integrity
- Run tests locally to reproduce
