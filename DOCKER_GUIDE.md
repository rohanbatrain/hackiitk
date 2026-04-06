# Docker Guide for Offline Policy Gap Analyzer

## Overview

This project uses Docker to ensure consistent dependency resolution and faster CI/CD execution. The Docker image includes all dependencies pre-installed using the `uv` package manager (10-100x faster than pip).

## Quick Start

### Pull Pre-built Image

```bash
# Pull the latest CI-optimized image
docker pull ghcr.io/rohanbatrain/hackiitk:latest

# Pull the full application image
docker pull ghcr.io/rohanbatrain/hackiitk:latest-full
```

### Run Tests in Docker

```bash
# Run fast tests (default)
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest

# Run specific category
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -m tests.extreme.cli test --category property --fast

# Run all tests
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -m tests.extreme.cli test --verbose

# Run with volume mount for test outputs
docker run --rm -v $(pwd)/test_outputs:/app/test_outputs \
  ghcr.io/rohanbatrain/hackiitk:latest \
  python -m tests.extreme.cli test --fast
```

## Building Locally

### Build CI Image (Smaller, Faster)

```bash
# Build CI-optimized image
docker build --target ci -t hackiitk:ci .

# Run tests
docker run --rm hackiitk:ci
```

### Build Full Application Image

```bash
# Build full image with all code
docker build --target application -t hackiitk:full .

# Run interactive shell
docker run --rm -it hackiitk:full bash
```

### Build with Cache

```bash
# Use BuildKit for better caching
DOCKER_BUILDKIT=1 docker build --target ci -t hackiitk:ci .

# Use cache from registry
docker build --target ci \
  --cache-from ghcr.io/rohanbatrain/hackiitk:latest \
  -t hackiitk:ci .
```

## Multi-Stage Build Architecture

The Dockerfile uses a multi-stage build for optimization:

### Stage 1: Base
- Python 3.11 slim image
- System dependencies (git, curl, build-essential)
- UV package manager installation

### Stage 2: Dependencies
- Installs all Python dependencies using uv
- Tries frozen requirements first (fastest)
- Falls back to constrained requirements if needed
- Verifies critical dependencies (langchain, chromadb, sentence-transformers)

### Stage 3: Application
- Copies full application code
- Creates output directories
- Sets up Python path
- Default command runs fast tests

### Stage 4: CI (Optimized)
- Copies only necessary files for testing
- Smaller image size (~500MB vs ~1GB)
- Faster startup time
- Optimized for CI/CD pipelines

## Image Tags

- `latest` - Latest CI-optimized image from main branch
- `latest-full` - Latest full application image from main branch
- `main` - Main branch CI image
- `develop` - Develop branch CI image
- `pr-<number>` - Pull request images
- `main-<sha>` - Specific commit from main branch

## GitHub Actions Integration

### Using Pre-built Container

```yaml
jobs:
  test:
    runs-on: ubuntu-latest
    container:
      image: ghcr.io/rohanbatrain/hackiitk:latest
      credentials:
        username: ${{ github.actor }}
        password: ${{ secrets.GITHUB_TOKEN }}
    
    steps:
    - uses: actions/checkout@v4
    - name: Run tests
      run: python -m tests.extreme.cli test --fast
```

### Building in Workflow

```yaml
jobs:
  build-and-test:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: docker build --target ci -t test-image .
    
    - name: Run tests
      run: docker run --rm test-image
```

## Development Workflow

### Local Development with Docker

```bash
# Build development image
docker build --target application -t hackiitk:dev .

# Run with code mounted (for live updates)
docker run --rm -it \
  -v $(pwd)/src:/app/src \
  -v $(pwd)/tests:/app/tests \
  -v $(pwd)/test_outputs:/app/test_outputs \
  hackiitk:dev bash

# Inside container, run tests
python -m tests.extreme.cli test --category property --verbose
```

### Debugging

```bash
# Run with interactive shell
docker run --rm -it ghcr.io/rohanbatrain/hackiitk:latest bash

# Check installed packages
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest pip list

# Verify dependencies
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -c "import langchain; import chromadb; print('OK')"
```

## Performance Comparison

### Dependency Installation Time

| Method | Time | Success Rate |
|--------|------|--------------|
| pip (requirements.txt) | ❌ Fails | 0% (resolution-too-deep) |
| pip (frozen) | ~5 minutes | 80% (missing transitive deps) |
| uv (frozen) | ~30 seconds | 95% |
| Docker (pre-built) | ~5 seconds | 100% |

### CI/CD Execution Time

| Approach | Setup Time | Test Time | Total |
|----------|------------|-----------|-------|
| No Docker (pip) | ~5 min | ❌ Fails | ❌ |
| No Docker (uv) | ~30 sec | ~25 min | ~26 min |
| Docker (pre-built) | ~5 sec | ~25 min | ~25 min |
| Docker (parallel 8x) | ~5 sec | ~3 min | ~3 min |

## Troubleshooting

### Image Pull Fails

```bash
# Authenticate with GitHub Container Registry
echo $GITHUB_TOKEN | docker login ghcr.io -u USERNAME --password-stdin

# Or use personal access token
docker login ghcr.io -u USERNAME
```

### Build Fails

```bash
# Clear Docker cache
docker builder prune -a

# Build without cache
docker build --no-cache --target ci -t hackiitk:ci .

# Check build logs
docker build --progress=plain --target ci -t hackiitk:ci .
```

### Tests Fail in Container

```bash
# Check Python version
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest python --version

# Check installed packages
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest pip list | grep langchain

# Run with verbose output
docker run --rm ghcr.io/rohanbatrain/hackiitk:latest \
  python -m tests.extreme.cli test --category property --verbose
```

### Container Registry Issues

```bash
# Check if image exists
docker manifest inspect ghcr.io/rohanbatrain/hackiitk:latest

# Pull specific tag
docker pull ghcr.io/rohanbatrain/hackiitk:main

# List available tags (requires GitHub CLI)
gh api /user/packages/container/hackiitk/versions
```

## Best Practices

1. **Use CI-optimized image for testing** - Smaller, faster, sufficient for tests
2. **Use full image for development** - Includes all code and tools
3. **Mount volumes for outputs** - Preserve test results and reports
4. **Use BuildKit** - Faster builds with better caching
5. **Tag images properly** - Use semantic versioning for releases
6. **Clean up regularly** - Remove old images to save space

## Security

### Image Scanning

```bash
# Scan for vulnerabilities (requires Docker Scout)
docker scout cves ghcr.io/rohanbatrain/hackiitk:latest

# Or use Trivy
trivy image ghcr.io/rohanbatrain/hackiitk:latest
```

### Minimal Base Image

The Dockerfile uses `python:3.11-slim` to minimize attack surface:
- Smaller image size (~150MB base vs ~900MB full Python)
- Fewer packages = fewer vulnerabilities
- Faster downloads and startup

## Resources

- **Docker Hub:** https://hub.docker.com/
- **GitHub Container Registry:** https://ghcr.io
- **UV Package Manager:** https://github.com/astral-sh/uv
- **Docker BuildKit:** https://docs.docker.com/build/buildkit/

## Support

For issues with Docker setup:
1. Check this guide first
2. Review GitHub Actions logs
3. Open an issue with `docker` label
4. Include Docker version: `docker --version`
