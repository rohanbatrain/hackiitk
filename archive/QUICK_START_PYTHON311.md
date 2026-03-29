# Quick Start with Python 3.11

## Current Status

✅ Python 3.11.15 installed
✅ venv311 created
🔄 Dependencies installing (run `./install_python311.sh`)

## After Installation Completes

### Step 1: Activate venv
```bash
source venv311/bin/activate
```

### Step 2: Download embedding model
```bash
python scripts/download_models.py --embedding
```

### Step 3: Move model to correct location
```bash
mkdir -p models/embeddings
mv models/all-MiniLM-L6-v2 models/embeddings/ 2>/dev/null || true
```

### Step 4: Test the analyzer
```bash
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

## If Installation Script is Still Running

Just wait for it to complete. It's installing:
1. PyTorch (large, takes time)
2. Sentence Transformers
3. ChromaDB
4. LangChain
5. Document processing libraries
6. CLI tools
7. Policy analyzer package

## Quick Commands

```bash
# Check if installation is done
ps aux | grep install_python311

# Activate venv
source venv311/bin/activate

# Check Python version
python --version  # Should show 3.11.15

# Run the analyzer
./pa --help
```

## About the Catalog

The catalog is CORRECT as-is:
- Contains 49 NIST CSF 2.0 controls
- Built from CIS guide PDF
- Your policy files in `data/policies/` are for ANALYSIS, not for building the catalog

Read `CATALOG_EXPLANATION.md` for full details.

## Troubleshooting

### If installation fails
Try installing packages one by one:
```bash
source venv311/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install sentence-transformers
pip install chromadb
pip install langchain langchain-community ollama
pip install pypdf2 python-docx chardet markdown
pip install pyyaml click rich tabulate watchdog
pip install -e .
```

### If ChromaDB still doesn't work
Check Python version:
```bash
python --version  # Must be 3.11.x
```

## Next Steps After Setup

1. Test with dummy policy
2. Analyze your own policies in `data/policies/`
3. Review gap reports
4. Implement recommendations

You're almost there!
