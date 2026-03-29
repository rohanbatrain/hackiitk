#!/bin/bash
# Launcher script for policy-analyzer
# This script automatically activates the venv and runs policy-analyzer

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if venv exists
if [ ! -d "$SCRIPT_DIR/venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "Please run setup first: ./setup_mac.sh"
    exit 1
fi

# Activate virtual environment
source "$SCRIPT_DIR/venv/bin/activate"

# Check if Ollama is running (only if ollama command exists)
if command -v ollama &> /dev/null; then
    if ! pgrep -x "ollama" > /dev/null; then
        echo "⚠️  Starting Ollama..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
    fi
fi

# Run policy-analyzer with all arguments
policy-analyzer "$@"

# Capture exit code
EXIT_CODE=$?

# Deactivate virtual environment
deactivate

# Exit with the same code as policy-analyzer
exit $EXIT_CODE
