#!/bin/bash
# Install dependencies in stages to avoid resolution issues

echo "Installing dependencies in stages..."
echo ""

# Make sure venv is activated
source venv/bin/activate

# Stage 1: Core utilities
echo "Stage 1: Core utilities..."
pip install click rich tabulate watchdog pyyaml jsonschema psutil chardet

# Stage 2: Document processing
echo "Stage 2: Document processing..."
pip install PyMuPDF pdfplumber python-docx

# Stage 3: Data processing
echo "Stage 3: Data processing..."
pip install numpy pandas

# Stage 4: Testing (optional, skip if issues)
echo "Stage 4: Testing libraries..."
pip install hypothesis pytest || echo "Skipping test libraries"

# Stage 5: Other utilities
echo "Stage 5: Other utilities..."
pip install rank-bm25

# Done
echo ""
echo "✅ Core dependencies installed!"
echo ""
echo "Note: Some ML libraries (sentence-transformers, chromadb, langchain) were skipped"
echo "They can be installed later if needed for full functionality"
echo ""
echo "You can now use the CLI with:"
echo "  python -m cli.main --help"
