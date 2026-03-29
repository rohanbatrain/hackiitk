#!/bin/bash
# Setup script for Python 3.12 (fixes ChromaDB compatibility)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Policy Analyzer - Python 3.12 Setup                         ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if Python 3.12 is installed
if ! command -v python3.12 &> /dev/null; then
    echo "❌ Python 3.12 not found"
    echo ""
    echo "Installing Python 3.12 via Homebrew..."
    brew install python@3.12
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install Python 3.12"
        echo "Please install manually: brew install python@3.12"
        exit 1
    fi
fi

echo "✓ Python 3.12 found: $(python3.12 --version)"
echo ""

# Create venv with Python 3.12
echo "Creating virtual environment with Python 3.12..."
python3.12 -m venv venv312

if [ $? -ne 0 ]; then
    echo "❌ Failed to create virtual environment"
    exit 1
fi

echo "✓ Virtual environment created: venv312/"
echo ""

# Activate venv
echo "Activating virtual environment..."
source venv312/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip -q

# Install dependencies
echo "Installing dependencies (this may take a few minutes)..."
pip install -r requirements.txt -q

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    exit 1
fi

echo "✓ Dependencies installed"
echo ""

# Install package
echo "Installing policy-analyzer package..."
pip install -e . -q

if [ $? -ne 0 ]; then
    echo "❌ Failed to install package"
    exit 1
fi

echo "✓ Package installed"
echo ""

# Download embedding model if not exists
if [ ! -d "models/embeddings/all-MiniLM-L6-v2" ]; then
    echo "Downloading embedding model..."
    python scripts/download_models.py --embedding
    
    # Move to correct location if needed
    if [ -d "models/all-MiniLM-L6-v2" ] && [ ! -d "models/embeddings/all-MiniLM-L6-v2" ]; then
        mkdir -p models/embeddings
        mv models/all-MiniLM-L6-v2 models/embeddings/
        echo "✓ Model moved to correct location"
    fi
else
    echo "✓ Embedding model already exists"
fi

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "To use the tool:"
echo "  1. Activate: source venv312/bin/activate"
echo "  2. Run: ./pa --policy-path your_policy.pdf --domain isms"
echo ""
echo "Test it now:"
echo "  source venv312/bin/activate"
echo "  ./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms"
echo ""
