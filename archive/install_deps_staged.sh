#!/bin/bash
# Staged dependency installation to avoid resolution-too-deep error

echo "Installing dependencies in stages..."

# Stage 1: Core dependencies
echo "Stage 1: Core dependencies..."
pip install --no-deps \
    sentence-transformers \
    chromadb \
    langchain \
    langchain-community \
    ollama

# Stage 2: ML/AI libraries
echo "Stage 2: ML/AI libraries..."
pip install \
    torch \
    transformers \
    numpy \
    scikit-learn

# Stage 3: Document processing
echo "Stage 3: Document processing..."
pip install \
    pypdf2 \
    python-docx \
    chardet \
    markdown

# Stage 4: Remaining dependencies
echo "Stage 4: Remaining dependencies..."
pip install \
    pyyaml \
    pydantic \
    click \
    rich \
    tabulate \
    watchdog

# Stage 5: Install missing dependencies from requirements
echo "Stage 5: Resolving remaining dependencies..."
pip install -r requirements.txt --no-deps 2>/dev/null || true

echo "✓ Dependencies installed"
