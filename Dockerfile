# Multi-stage Dockerfile for Offline Policy Gap Analyzer Testing
# Optimized for CI/CD with pre-installed dependencies

# Stage 1: Base image with uv package manager
FROM python:3.11-slim as base

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager (10-100x faster than pip)
RUN curl -LsSf https://astral.sh/uv/install.sh | sh
ENV PATH="/root/.cargo/bin:${PATH}"

# Set working directory
WORKDIR /app

# Stage 2: Dependencies installation
FROM base as dependencies

# Copy dependency files
COPY requirements.txt requirements-frozen.txt constraints.txt ./

# Install dependencies using uv (with fallback to frozen requirements)
RUN uv pip install --system -r requirements-frozen.txt || \
    uv pip install --system --constraint constraints.txt -r requirements.txt || \
    pip install -r requirements-frozen.txt

# Verify critical dependencies
RUN python -c "import langchain; import chromadb; import sentence_transformers; print('✓ All dependencies installed')"

# Stage 3: Application with dependencies
FROM dependencies as application

# Copy application code
COPY . .

# Create output directories
RUN mkdir -p test_outputs/extreme test_outputs/coverage

# Set Python path
ENV PYTHONPATH=/app

# Verify test CLI works
RUN python -m tests.extreme.cli --help

# Default command runs fast tests
CMD ["python", "-m", "tests.extreme.cli", "test", "--fast", "--verbose"]

# Stage 4: CI-optimized image (smaller, faster)
FROM dependencies as ci

# Copy only necessary files for testing
COPY tests/ tests/
COPY analysis/ analysis/
COPY cli/ cli/
COPY ingestion/ ingestion/
COPY models/ models/
COPY orchestration/ orchestration/
COPY reference_builder/ reference_builder/
COPY reporting/ reporting/
COPY retrieval/ retrieval/
COPY revision/ revision/
COPY utils/ utils/
COPY vector_store/ vector_store/
COPY pyproject.toml .coveragerc ./

# Create output directories
RUN mkdir -p test_outputs/extreme test_outputs/coverage

# Set Python path
ENV PYTHONPATH=/app

# Healthcheck
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.exit(0)"

# Default command for CI
CMD ["python", "-m", "tests.extreme.cli", "test", "--fast", "--verbose"]
