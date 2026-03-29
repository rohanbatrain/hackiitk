# Realistic Solution: Python Version Issue

## The Situation

1. You have Python 3.14.3 (too new)
2. Python 3.12 has dependency resolution issues
3. ChromaDB doesn't work with Python 3.14

## The Real Problem

Your `requirements.txt` has a very complex dependency tree:
- langchain + chromadb + sentence-transformers + torch
- These have conflicting version requirements
- Pip can't resolve them efficiently

## Solutions (Ranked by Feasibility)

### Option 1: Use Python 3.11 (Most Reliable)

Python 3.11 is the most stable for this project:

```bash
# Install Python 3.11
brew install python@3.11

# Create venv
python3.11 -m venv venv311

# Activate
source venv311/bin/activate

# Install in stages to avoid resolution issues
pip install --upgrade pip

# Install core ML libraries first
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Install sentence transformers
pip install sentence-transformers

# Install chromadb (will work with Python 3.11)
pip install chromadb

# Install remaining dependencies one by one
pip install langchain langchain-community ollama
pip install pypdf2 python-docx chardet markdown
pip install pyyaml click rich tabulate watchdog

# Install package
pip install -e .
```

### Option 2: Simplify Dependencies

Remove problematic packages and use simpler alternatives:

1. Replace ChromaDB with FAISS (works with Python 3.14)
2. Simplify langchain dependencies
3. Use minimal requirements

This requires code changes.

### Option 3: Use Docker

Create a Docker container with Python 3.11 and all dependencies pre-installed.

### Option 4: Use Conda Instead of Pip

Conda handles complex dependencies better:

```bash
# Install miniconda
brew install miniconda

# Create environment with Python 3.11
conda create -n policy-analyzer python=3.11

# Activate
conda activate policy-analyzer

# Install dependencies
conda install pytorch torchvision torchaudio -c pytorch
pip install sentence-transformers chromadb langchain
pip install -r requirements.txt
pip install -e .
```

## Recommended: Try Python 3.11

```bash
# Check if you have Python 3.11
python3.11 --version

# If not, install it
brew install python@3.11

# Create venv
python3.11 -m venv venv311

# Activate
source venv311/bin/activate

# Verify version
python --version  # Should show 3.11.x

# Install dependencies in stages
pip install --upgrade pip

# Stage 1: PyTorch (CPU version, smaller)
pip install torch --index-url https://download.pytorch.org/whl/cpu

# Stage 2: Core ML
pip install sentence-transformers

# Stage 3: ChromaDB
pip install chromadb

# Stage 4: LangChain
pip install langchain langchain-community

# Stage 5: Ollama
pip install ollama

# Stage 6: Document processing
pip install pypdf2 python-docx chardet markdown

# Stage 7: CLI tools
pip install pyyaml click rich tabulate watchdog

# Stage 8: Install package
pip install -e .

# Download embedding model
python scripts/download_models.py --embedding

# Ensure model is in correct location
mkdir -p models/embeddings
mv models/all-MiniLM-L6-v2 models/embeddings/ 2>/dev/null || true

# Test
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

## Why Python 3.11?

- ✅ Stable and well-tested
- ✅ ChromaDB fully supports it
- ✅ All ML libraries work
- ✅ No dependency resolution issues
- ✅ Recommended by ChromaDB team

## About the Catalog Question

See `CATALOG_EXPLANATION.md` for a detailed explanation of why the catalog is correct as-is (49 NIST CSF controls from the CIS guide).

**TL;DR**: The catalog is the framework (standard), your policy files are what you analyze against that framework. Don't rebuild the catalog from your policies!

## Next Steps

1. Install Python 3.11: `brew install python@3.11`
2. Follow the staged installation above
3. Test with: `./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms`
4. Read `CATALOG_EXPLANATION.md` to understand the architecture

Good luck!
