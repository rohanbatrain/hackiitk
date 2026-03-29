#!/bin/bash
# Install dependencies with Python 3.11 (staged to avoid resolution issues)

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Installing Dependencies with Python 3.11                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Activate venv311
source venv311/bin/activate

# Verify Python version
echo "Python version: $(python --version)"
echo ""

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing dependencies in stages..."
echo ""

# Stage 1: PyTorch (CPU version)
echo "Stage 1/7: Installing PyTorch..."
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Stage 2: Sentence Transformers
echo ""
echo "Stage 2/7: Installing Sentence Transformers..."
pip install sentence-transformers

# Stage 3: ChromaDB
echo ""
echo "Stage 3/7: Installing ChromaDB..."
pip install chromadb

# Stage 4: LangChain
echo ""
echo "Stage 4/7: Installing LangChain..."
pip install langchain langchain-community ollama

# Stage 5: Document processing
echo ""
echo "Stage 5/7: Installing document processing libraries..."
pip install pypdf2 python-docx chardet markdown

# Stage 6: CLI tools
echo ""
echo "Stage 6/7: Installing CLI tools..."
pip install pyyaml click rich tabulate watchdog

# Stage 7: Install package
echo ""
echo "Stage 7/7: Installing policy-analyzer package..."
pip install -e .

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Installation Complete!                                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "Next steps:"
echo "  1. Download embedding model: python scripts/download_models.py --embedding"
echo "  2. Move model: mkdir -p models/embeddings && mv models/all-MiniLM-L6-v2 models/embeddings/ 2>/dev/null || true"
echo "  3. Test: ./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms"
echo ""
