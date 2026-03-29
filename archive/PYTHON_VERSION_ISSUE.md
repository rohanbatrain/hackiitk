# ⚠️ Python Version Compatibility Issue

## Problem

Your Policy Analyzer encountered a compatibility issue:

```
ChromaDB is not available: unable to infer type for attribute "chroma_server_nofile"
Note: ChromaDB requires Python < 3.14 due to Pydantic v1 compatibility issues.
```

## Root Cause

You're using **Python 3.14.3**, but ChromaDB (the vector database) requires **Python 3.11 or 3.12** due to Pydantic v1 compatibility issues.

## Solution Options

### Option 1: Use Python 3.12 (Recommended)

1. **Install Python 3.12** using Homebrew:
```bash
brew install python@3.12
```

2. **Create new virtual environment with Python 3.12**:
```bash
# Remove old venv
rm -rf venv

# Create new venv with Python 3.12
python3.12 -m venv venv

# Activate
source venv/bin/activate

# Verify version
python --version  # Should show Python 3.12.x

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

3. **Run the analyzer**:
```bash
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

### Option 2: Use Python 3.11

Same steps as Option 1, but use `python3.11` instead:
```bash
brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install -e .
```

### Option 3: Wait for ChromaDB Update

ChromaDB is working on Python 3.14 support. You can:
- Monitor: https://github.com/chroma-core/chroma/issues
- Wait for a compatible version
- Use Python 3.12 in the meantime

## Why This Happens

- **Python 3.14** was released recently (October 2024)
- **ChromaDB** uses Pydantic v1, which has compatibility issues with Python 3.14
- **Pydantic v2** works with Python 3.14, but ChromaDB hasn't migrated yet

## What's Already Working

✅ CIS guide downloaded (524 KB)
✅ Reference catalog built (49 subcategories)
✅ CLI wrapper configured
✅ All dependencies installed
✅ Ollama models ready

## Quick Check

To see which Python versions you have:
```bash
# Check available Python versions
ls -la /usr/local/bin/python* 2>/dev/null
ls -la /opt/homebrew/bin/python* 2>/dev/null

# Or use which
which python3.12
which python3.11
```

## After Switching Python Version

Once you recreate the venv with Python 3.12:

1. The CIS guide and catalog are already downloaded (no need to rebuild)
2. Just run: `./pa --policy-path your_policy.pdf --domain isms`
3. Everything should work!

## Need Help?

If you don't have Python 3.12 installed:
```bash
# Install with Homebrew
brew install python@3.12

# Verify installation
python3.12 --version
```

---

**TL;DR**: Use Python 3.12 instead of Python 3.14 for ChromaDB compatibility.
