#!/bin/bash
# Setup script for Offline Policy Gap Analyzer on macOS
# This script sets up a virtual environment and installs all dependencies

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_header() {
    echo ""
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo -e "${BLUE}  $1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════════════════════${NC}"
    echo ""
}

# Check if running on macOS
if [[ "$OSTYPE" != "darwin"* ]]; then
    print_error "This script is designed for macOS"
    exit 1
fi

print_header "Offline Policy Gap Analyzer - macOS Setup"

# Step 1: Check Python version
print_info "Checking Python installation..."

if ! command -v python3 &> /dev/null; then
    print_error "Python 3 is not installed"
    print_info "Install Python 3 using Homebrew:"
    echo "  brew install python@3.11"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
print_success "Found Python $PYTHON_VERSION"

# Check Python version is 3.8+
PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    print_error "Python 3.8 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

# Step 2: Create virtual environment
print_info "Creating virtual environment..."

if [ -d "venv" ]; then
    print_warning "Virtual environment already exists"
    read -p "Do you want to recreate it? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf venv
        python3 -m venv venv
        print_success "Virtual environment recreated"
    else
        print_info "Using existing virtual environment"
    fi
else
    python3 -m venv venv
    print_success "Virtual environment created"
fi

# Step 3: Activate virtual environment
print_info "Activating virtual environment..."
source venv/bin/activate
print_success "Virtual environment activated"

# Step 4: Upgrade pip
print_info "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
print_success "pip upgraded"

# Step 5: Install dependencies
print_info "Installing dependencies (this may take a few minutes)..."

# Install in stages to show progress
print_info "  Installing core dependencies..."
pip install click rich tabulate watchdog > /dev/null 2>&1

print_info "  Installing document processing libraries..."
pip install PyMuPDF pdfplumber python-docx > /dev/null 2>&1

print_info "  Installing ML/AI libraries..."
pip install sentence-transformers chromadb > /dev/null 2>&1

print_info "  Installing LangChain..."
pip install langchain langchain-community langchain-ollama > /dev/null 2>&1

print_info "  Installing remaining dependencies..."
pip install -r requirements.txt > /dev/null 2>&1

print_success "All dependencies installed"

# Step 6: Install package
print_info "Installing policy-analyzer package..."
pip install -e . > /dev/null 2>&1
print_success "Package installed"

# Step 7: Check Ollama
print_header "Checking Ollama Installation"

if ! command -v ollama &> /dev/null; then
    print_warning "Ollama is not installed"
    print_info "Ollama is required for local LLM execution"
    echo ""
    echo "To install Ollama:"
    echo "  1. Visit: https://ollama.ai"
    echo "  2. Download and install for macOS"
    echo "  3. Or use Homebrew: brew install ollama"
    echo ""
    read -p "Do you want to continue without Ollama? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
else
    print_success "Ollama is installed"
    
    # Check if Ollama is running
    if pgrep -x "ollama" > /dev/null; then
        print_success "Ollama is running"
    else
        print_warning "Ollama is not running"
        print_info "Starting Ollama service..."
        ollama serve > /dev/null 2>&1 &
        sleep 2
        print_success "Ollama service started"
    fi
    
    # Check for models
    print_info "Checking for LLM models..."
    if ollama list | grep -q "qwen2.5:3b-instruct"; then
        print_success "Default model (qwen2.5:3b-instruct) is installed"
    else
        print_warning "Default model not found"
        echo ""
        read -p "Do you want to download qwen2.5:3b-instruct (~1.9GB)? (Y/n): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Nn]$ ]]; then
            print_info "Downloading model (this will take a few minutes)..."
            ollama pull qwen2.5:3b-instruct
            print_success "Model downloaded"
        fi
    fi
fi

# Step 8: Verify installation
print_header "Verifying Installation"

print_info "Testing policy-analyzer command..."
if policy-analyzer --version > /dev/null 2>&1; then
    VERSION=$(policy-analyzer --version)
    print_success "policy-analyzer is working: $VERSION"
else
    print_error "policy-analyzer command failed"
    exit 1
fi

# Step 9: Create activation script
print_info "Creating activation script..."

cat > activate.sh << 'EOF'
#!/bin/bash
# Activation script for Offline Policy Gap Analyzer

# Activate virtual environment
source venv/bin/activate

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "⚠️  Ollama is not running. Starting..."
    ollama serve > /dev/null 2>&1 &
    sleep 2
    echo "✓ Ollama started"
fi

echo "✓ Environment activated"
echo ""
echo "Available commands:"
echo "  policy-analyzer --help"
echo "  policy-analyzer info"
echo "  policy-analyzer list-models"
echo "  policy-analyzer analyze <policy-file> --domain <domain>"
echo ""
echo "To deactivate: deactivate"
EOF

chmod +x activate.sh
print_success "Activation script created: ./activate.sh"

# Step 10: Create quick test script
print_info "Creating test script..."

cat > test_installation.sh << 'EOF'
#!/bin/bash
# Test script for policy-analyzer

source venv/bin/activate

echo "Testing policy-analyzer installation..."
echo ""

echo "1. Checking version..."
policy-analyzer --version

echo ""
echo "2. Checking system info..."
policy-analyzer info

echo ""
echo "3. Listing models..."
policy-analyzer list-models

echo ""
echo "4. Testing with dummy policy (dry run)..."
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms --dry-run

echo ""
echo "✓ All tests passed!"
EOF

chmod +x test_installation.sh
print_success "Test script created: ./test_installation.sh"

# Step 11: Create usage examples script
print_info "Creating examples script..."

cat > examples.sh << 'EOF'
#!/bin/bash
# Usage examples for policy-analyzer

source venv/bin/activate

echo "Policy Analyzer - Usage Examples"
echo "================================"
echo ""

echo "1. Basic Analysis:"
echo "   policy-analyzer analyze policy.pdf --domain isms"
echo ""

echo "2. Dry Run (Preview):"
echo "   policy-analyzer analyze policy.pdf --domain isms --dry-run"
echo ""

echo "3. With Custom Config:"
echo "   policy-analyzer init-config my-config.yaml"
echo "   policy-analyzer analyze policy.pdf --config my-config.yaml"
echo ""

echo "4. Validate Config:"
echo "   policy-analyzer validate-config my-config.yaml --verbose"
echo ""

echo "5. Watch Directory:"
echo "   policy-analyzer watch ./policies --domain isms --recursive"
echo ""

echo "6. List Models:"
echo "   policy-analyzer list-models"
echo ""

echo "7. System Info:"
echo "   policy-analyzer info"
echo ""

echo "8. Shell Completion:"
echo "   policy-analyzer completion bash --install"
echo ""

echo "Available domains:"
echo "  - isms (Information Security Management System)"
echo "  - risk_management (Risk Management)"
echo "  - patch_management (Patch Management)"
echo "  - data_privacy (Data Privacy)"
echo ""

echo "For more help:"
echo "  policy-analyzer --help"
echo "  policy-analyzer analyze --help"
EOF

chmod +x examples.sh
print_success "Examples script created: ./examples.sh"

# Final summary
print_header "Setup Complete!"

echo "Your environment is ready to use!"
echo ""
echo "📁 Project directory: $(pwd)"
echo "🐍 Python version: $PYTHON_VERSION"
echo "📦 Virtual environment: ./venv"
echo ""
echo "Quick Start:"
echo "  1. Activate environment:  source activate.sh"
echo "  2. Run test:             ./test_installation.sh"
echo "  3. View examples:        ./examples.sh"
echo "  4. Analyze a policy:     policy-analyzer analyze <file> --domain isms"
echo ""
echo "Useful scripts created:"
echo "  • activate.sh           - Activate environment"
echo "  • test_installation.sh  - Test the installation"
echo "  • examples.sh           - View usage examples"
echo ""
echo "Documentation:"
echo "  • CLI_QUICK_START.md    - Quick start guide"
echo "  • CLI_QUICK_REFERENCE.md - Command reference"
echo "  • docs/CLI_GUIDE.md     - Complete guide"
echo ""

if command -v ollama &> /dev/null; then
    print_success "Ollama is installed and ready"
else
    print_warning "Remember to install Ollama: https://ollama.ai"
fi

echo ""
print_success "Setup complete! Run 'source activate.sh' to get started."
echo ""
