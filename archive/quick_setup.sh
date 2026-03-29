#!/bin/bash
# Quick setup script - simpler version

echo "🚀 Quick Setup for Policy Analyzer"
echo ""

# Create venv
echo "1. Creating virtual environment..."
python3 -m venv venv

# Activate
echo "2. Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "3. Upgrading pip..."
pip install --upgrade pip

# Install all dependencies from requirements.txt
echo "4. Installing dependencies (this will take a few minutes)..."
pip install -r requirements.txt

# Install package
echo "5. Installing policy-analyzer..."
pip install -e .

echo ""
echo "✅ Setup complete!"
echo ""
echo "To use the tool:"
echo "  1. Activate: source venv/bin/activate"
echo "  2. Run: python -m cli.main --help"
echo ""
