# 🧪 Testing Infrastructure

## Quick Start

```bash
# Run fast tests (5 minutes)
python -m tests.extreme.cli test --fast

# Run specific category (30 minutes)
python -m tests.extreme.cli test --category property

# Run full suite locally (8-10 hours)
python -m tests.extreme.cli test
```

## CI/CD Status

[![Extreme Tests](https://github.com/rohanbatrain/hackiitk/actions/workflows/extreme-tests-simple-parallel.yml/badge.svg)](https://github.com/rohanbatrain/hackiitk/actions/workflows/extreme-tests-simple-parallel.yml)

**Automatic Testing:**
- ✅ Every push to main/develop
- ✅ Every pull request
- ✅ Weekly schedule (Sunday 2 AM UTC)

**Execution Time:** 30 minutes (8 parallel jobs)

## Test Suite Overview

| Category | Tests | Purpose |
|----------|-------|---------|
| Property | 202 | Universal correctness properties |
| Boundary | 100 | Edge cases and limits |
| Adversarial | 80 | Security testing |
| Stress | 150 | Maximum load scenarios |
| Chaos | 120 | Fault injection |
| Performance | 50 | Performance profiling |
| Unit | 200+ | Component testing |
| Integration | 100+ | End-to-end testing |
| **Total** | **1055+** | **Comprehensive validation** |

## Documentation

- **Quick Start:** [PARALLEL_TESTING_QUICKSTART.md](PARALLEL_TESTING_QUICKSTART.md)
- **Full Guide:** [.github/workflows/README_PARALLEL_TESTING.md](.github/workflows/README_PARALLEL_TESTING.md)
- **Production Status:** [PRODUCTION_READY.md](PRODUCTION_READY.md)
- **Deployment Summary:** [DEPLOYMENT_SUMMARY.md](DEPLOYMENT_SUMMARY.md)

## Metrics

- **Code Coverage:** 92%
- **Requirement Coverage:** 100% (80/80)
- **Test Pass Rate:** 97.7% (target: ≥95%)
- **Execution Time:** 30 min (was: 8-10 hours)
- **Parallelization:** 16-20x faster

## GitHub Actions

**View test results:** [Actions Tab](https://github.com/rohanbatrain/hackiitk/actions)

**Trigger manually:**
```bash
gh workflow run extreme-tests-simple-parallel.yml
```

## Cost

**GitHub Actions Usage:** ~340 min/month (17% of free tier)

**Breakdown:**
- Fast tests (PRs): 100 min/month
- Weekly full suite: 240 min/month
- **Total:** Well within free tier (2000 min/month)

## Status

✅ **PRODUCTION READY**

All workflows deployed and operational.
