#!/bin/bash
# Policy Analyzer - Complete Setup Script
# Handles Python 3.11 installation, dependencies, and model download

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  Policy Analyzer - Complete Setup                           ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Step 1: Check/Install Python 3.11
echo "Step 1: Checking Python 3.11..."
if ! command -v python3.11 &> /dev/null; then
    log_warn "Python 3.11 not found. Installing..."
    if command -v brew &> /dev/null; then
        brew install python@3.11 || { log_error "Failed to install Python 3.11"; exit 1; }
    else
        log_error "Homebrew not found. Install from https://brew.sh"
        exit 1
    fi
fi
log_info "Python 3.11 found: $(python3.11 --version)"

# Step 2: Create/Activate venv
echo ""
echo "Step 2: Setting up virtual environment..."
if [ -d "venv311" ]; then
    log_warn "venv311 exists. Removing and recreating for clean install..."
    rm -rf venv311
fi

python3.11 -m venv venv311 || { log_error "Failed to create venv"; exit 1; }
log_info "Virtual environment created"

source venv311/bin/activate || { log_error "Failed to activate venv"; exit 1; }
log_info "Virtual environment activated"

# Step 3: Upgrade pip
echo ""
echo "Step 3: Upgrading pip..."
pip install --upgrade pip setuptools wheel -q
log_info "Pip upgraded"

# Step 4: Install dependencies with version constraints
echo ""
echo "Step 4: Installing dependencies (this may take 5-10 minutes)..."

install_package() {
    local package=$1
    local name=$2
    echo "  Installing $name..."
    if pip install $package 2>&1 | grep -q "Successfully installed"; then
        log_info "$name installed"
        return 0
    else
        log_warn "$name: retrying..."
        if pip install --no-cache-dir $package; then
            log_info "$name installed (retry successful)"
            return 0
        else
            log_error "$name installation failed (continuing anyway)"
            return 1
        fi
    fi
}

# Critical: Install NumPy < 2.0 first (ChromaDB compatibility)
install_package "numpy<2.0" "NumPy (< 2.0 for ChromaDB)" || { log_error "NumPy installation failed"; exit 1; }

# Install core dependencies in order
install_package "pyyaml" "PyYAML" || true
install_package "click" "Click" || true
install_package "rich" "Rich" || true
install_package "tabulate" "Tabulate" || true
install_package "psutil" "psutil" || true
install_package "chardet" "chardet" || true
install_package "python-docx" "python-docx" || true
install_package "PyMuPDF" "PyMuPDF" || true
install_package "pdfplumber" "pdfplumber" || true
install_package "markdown" "markdown" || true
install_package "watchdog" "watchdog" || true
install_package "jsonschema" "jsonschema" || true
install_package "rank-bm25" "rank-bm25" || true

# Install ML/AI dependencies
install_package "torch --index-url https://download.pytorch.org/whl/cpu" "PyTorch (CPU)" || true
install_package "sentence-transformers" "Sentence Transformers" || true
install_package "chromadb" "ChromaDB" || true
install_package "langchain" "LangChain" || true
install_package "langchain-community" "LangChain Community" || true
install_package "langchain-ollama" "LangChain Ollama" || true
install_package "ollama" "Ollama Python" || true

# Install testing dependencies
install_package "hypothesis" "Hypothesis" || true
install_package "pytest" "pytest" || true

# Step 5: Install package
echo ""
echo "Step 5: Installing Policy Analyzer package..."
pip install -e . || { log_error "Package installation failed"; exit 1; }
log_info "Package installed"

# Step 6: Download embedding model
echo ""
echo "Step 6: Setting up embedding model..."
mkdir -p models/embeddings

if [ ! -d "models/embeddings/all-MiniLM-L6-v2" ]; then
    log_info "Downloading embedding model..."
    if python scripts/download_models.py --embedding 2>&1 | grep -q "successfully"; then
        log_info "Embedding model downloaded"
        # Move to correct location if needed
        if [ -d "models/all-MiniLM-L6-v2" ] && [ ! -d "models/embeddings/all-MiniLM-L6-v2" ]; then
            mv models/all-MiniLM-L6-v2 models/embeddings/ 2>/dev/null || true
            log_info "Model moved to correct location"
        fi
    else
        log_warn "Model download script failed, trying manual download..."
        python -c "from sentence_transformers import SentenceTransformer; model = SentenceTransformer('all-MiniLM-L6-v2'); model.save('models/embeddings/all-MiniLM-L6-v2')" 2>/dev/null && log_info "Model downloaded manually" || log_warn "Manual download failed - you may need to download it later"
    fi
else
    log_info "Embedding model already exists"
fi

# Step 7: Download CIS guide if missing
echo ""
echo "Step 7: Checking CIS guide..."
if [ ! -f "data/cis_guide.pdf" ]; then
    log_warn "CIS guide not found. You need to download it manually from:"
    echo "  https://www.cisecurity.org/-/media/project/cisecurity/cisecurity/data/media/files/uploads/2024/08/cis-ms-isac-nist-cybersecurity-framework-policy-template-guide-2024.pdf"
    echo "  Save it as: data/cis_guide.pdf"
else
    log_info "CIS guide found"
fi

# Step 8: Verify installation
echo ""
echo "Step 8: Verifying installation..."
VERIFY_RESULT=$(python -c "
import sys
try:
    import yaml
    import click
    import chromadb
    import sentence_transformers
    import langchain
    print('SUCCESS')
except Exception as e:
    print(f'FAILED: {e}')
    sys.exit(1)
" 2>&1)

if echo "$VERIFY_RESULT" | grep -q "SUCCESS"; then
    log_info "All core dependencies verified"
else
    log_error "Verification failed: $VERIFY_RESULT"
    exit 1
fi

# Final summary
echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Setup Complete!                                          ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "To use the tool:"
echo "  1. Activate: source venv311/bin/activate"
echo "  2. Run: ./pa --policy-path your_policy.pdf --domain isms"
echo ""
echo "Test it now:"
echo "  ./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms"
echo ""
echo "Note: The catalog is correct (49 NIST CSF controls)."
echo "      Your policy files in data/policies/ are for ANALYSIS."
echo ""
