# Docker Quick Start Guide

## TL;DR

```bash
# Pull and run tests
docker pull ghcr.io/rohanbatrain/hackiitk:latest
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest

# Or build locally
docker build --target ci -t hackiitk:ci .
docker run --rm hackiitk:ci
```

## Why Docker?

The project has complex dependencies (langchain, chromadb, sentence-transformers) that cause `pip` to fail with "resolution-too-deep" errors. Docker solves this by:

1. ✅ Pre-installing all dependencies using `uv` (10-100x faster than pip)
2. ✅ Guaranteeing consistent environment across local and CI
3. ✅ Reducing CI setup time from 5 minutes to 5 seconds
4. ✅ Eliminating dependency resolution issues

## Quick Commands

### Run Tests

```bash
# Fast tests (3 minutes)
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest

# Specific category
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -m tests.extreme.cli test --category boundary --fast

# All tests (25 minutes)
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -m tests.extreme.cli test --verbose

# Save test outputs
docker run --rm -v $(pwd)/test_outputs:/app/test_outputs \
  ghcr.io/rohanbatrain/hackiitk:latest
```

### Build Locally

```bash
# CI image (recommended for testing)
docker build --target ci -t hackiitk:ci .

# Full image (includes all code)
docker build --target application -t hackiitk:full .

# With cache from registry
docker build --target ci \
  --cache-from ghcr.io/rohanbatrain/hackiitk:latest \
  -t hackiitk:ci .
```

### Development

```bash
# Interactive shell
docker run --rm -it ghcr.io/rohanbatrain/hackiitk:latest bash

# Mount code for live updates
docker run --rm -it \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/tests:/app/tests \
  ghcr.io/rohanbatrain/hackiitk:latest bash
```

## Using the Build Script

```bash
# Build and test CI image
./scripts/docker-build-test.sh ci

# Build and test full image
./scripts/docker-build-test.sh full

# Build and test both
./scripts/docker-build-test.sh all

# Push to registry (requires authentication)
./scripts/docker-build-test.sh push

# Clean up old images
./scripts/docker-build-test.sh clean
```

## GitHub Actions Integration

The workflows automatically use the pre-built Docker image:

```yaml
# .github/workflows/extreme-tests-simple-parallel.yml
jobs:
  test-suite:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/rohanbatrain/hackiitk:latest
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
```

## Performance Comparison

| Method | Setup Time | Success Rate | Notes |
|--------|------------|--------------|-------|
| pip | ❌ Fails | 0% | resolution-too-deep error |
| pip (frozen) | ~5 min | 80% | Missing transitive deps |
| uv | ~30 sec | 95% | Much faster, better resolution |
| Docker | ~5 sec | 100% | Pre-built, guaranteed to work |

## Troubleshooting

### Pull fails
```bash
# Login to GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin
```

### Build fails
```bash
# Clear cache and rebuild
docker builder prune -a
docker build --no-cache --target ci -t hackiitk:ci .
```

### Tests fail
```bash
# Check dependencies
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -c "import langchain; import chromadb; print('OK')"

# Run with verbose output
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -m tests.extreme.cli test --category property --verbose
```

## Next Steps

- **Full Guide:** See `DOCKER_GUIDE.md` for comprehensive documentation
- **CI/CD:** Check `.github/workflows/docker-build-push.yml` for automated builds
- **Development:** Use `docker-compose.yml` for local development (coming soon)

## Resources

- **Docker Hub:** https://hub.docker.com/
- **GitHub Container Registry:** https://ghcr.io
- **UV Package Manager:** https://github.com/astral-sh/uv
- **Dockerfile:** See `Dockerfile` in project root
