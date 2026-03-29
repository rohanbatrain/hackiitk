#!/bin/bash
# Install only essential packages to get the tool working

echo "Installing essential packages..."

source venv311/bin/activate

# Install packages one by one with progress
echo "1/8: Installing sentence-transformers..."
pip install sentence-transformers -q

echo "2/8: Installing chromadb..."
pip install chromadb -q

echo "3/8: Installing langchain..."
pip install langchain langchain-community -q

echo "4/8: Installing ollama..."
pip install ollama -q

echo "5/8: Installing document processing..."
pip install pypdf2 python-docx chardet markdown -q

echo "6/8: Installing CLI tools..."
pip install click rich tabulate watchdog -q

echo "7/8: Installing remaining dependencies..."
pip install -r requirements.txt --no-deps -q 2>/dev/null || true

echo "8/8: Installing package..."
pip install -e . -q

echo ""
echo "✅ Installation complete!"
echo ""
echo "Next: python scripts/download_models.py --embedding"
