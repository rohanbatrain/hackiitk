# macOS Setup Guide

Quick and easy setup for the Offline Policy Gap Analyzer on macOS.

## Prerequisites

- macOS (any recent version)
- Python 3.8+ (usually pre-installed, or install via Homebrew)
- Internet connection (for initial setup only)

## One-Command Setup

```bash
chmod +x setup_mac.sh && ./setup_mac.sh
```

That's it! The script will:
1. ✅ Check Python installation
2. ✅ Create virtual environment
3. ✅ Install all dependencies
4. ✅ Install the policy-analyzer package
5. ✅ Check/install Ollama
6. ✅ Download default LLM model
7. ✅ Create helper scripts
8. ✅ Verify installation

## After Setup

### Activate Environment

```bash
source activate.sh
```

This activates the virtual environment and starts Ollama if needed.

### Test Installation

```bash
./test_installation.sh
```

### View Examples

```bash
./examples.sh
```

### Analyze Your First Policy

```bash
# Activate environment first
source activate.sh

# Analyze a policy
policy-analyzer analyze your-policy.pdf --domain isms
```

## Quick Commands

```bash
# Activate environment
source activate.sh

# Get help
policy-analyzer --help

# System info
policy-analyzer info

# List models
policy-analyzer list-models

# Analyze policy
policy-analyzer analyze policy.pdf --domain isms

# Dry run (preview)
policy-analyzer analyze policy.pdf --domain isms --dry-run

# Watch directory
policy-analyzer watch ./policies --domain isms

# Deactivate when done
deactivate
```

## Helper Scripts Created

After running `setup_mac.sh`, you'll have:

1. **activate.sh** - Activate the environment
   ```bash
   source activate.sh
   ```

2. **test_installation.sh** - Test everything works
   ```bash
   ./test_installation.sh
   ```

3. **examples.sh** - View usage examples
   ```bash
   ./examples.sh
   ```

## Troubleshooting

### Python Not Found

```bash
# Install Python via Homebrew
brew install python@3.11
```

### Ollama Not Installed

```bash
# Install via Homebrew
brew install ollama

# Or download from
open https://ollama.ai
```

### Permission Denied

```bash
# Make script executable
chmod +x setup_mac.sh
```

### Virtual Environment Issues

```bash
# Remove and recreate
rm -rf venv
./setup_mac.sh
```

## Daily Usage

### Starting Your Work Session

```bash
# 1. Navigate to project directory
cd /path/to/offline-policy-analyzer

# 2. Activate environment
source activate.sh

# 3. Start analyzing
policy-analyzer analyze policy.pdf --domain isms
```

### Ending Your Work Session

```bash
# Deactivate virtual environment
deactivate
```

## Updating

To update the tool:

```bash
# Activate environment
source activate.sh

# Pull latest changes (if using git)
git pull

# Reinstall
pip install -e .
```

## Uninstalling

To completely remove:

```bash
# Remove virtual environment
rm -rf venv

# Remove helper scripts
rm activate.sh test_installation.sh examples.sh

# Remove Ollama models (optional)
ollama rm qwen2.5:3b-instruct
```

## What Gets Installed

### Python Packages
- click, rich, tabulate, watchdog (CLI)
- PyMuPDF, pdfplumber, python-docx (Document processing)
- sentence-transformers, chromadb (Embeddings)
- langchain, ollama (LLM integration)
- And more (see requirements.txt)

### Ollama Models
- qwen2.5:3b-instruct (~1.9 GB) - Default model
- Optional: phi3.5:3.8b, mistral:7b

### Helper Scripts
- activate.sh - Environment activation
- test_installation.sh - Installation test
- examples.sh - Usage examples

## File Structure After Setup

```
offline-policy-analyzer/
├── venv/                    # Virtual environment
├── activate.sh              # Activation script
├── test_installation.sh     # Test script
├── examples.sh              # Examples script
├── setup_mac.sh             # Setup script
├── requirements.txt         # Dependencies
├── cli/                     # CLI code
├── docs/                    # Documentation
└── tests/                   # Test files
```

## Next Steps

1. Read `CLI_QUICK_START.md` for quick start
2. Read `CLI_QUICK_REFERENCE.md` for commands
3. Read `docs/CLI_GUIDE.md` for complete guide
4. Try analyzing the dummy policies in `tests/fixtures/dummy_policies/`

## Support

For issues:
- Check `docs/TROUBLESHOOTING.md`
- Check `docs/CLI_GUIDE.md`
- Review error messages (they're helpful!)

## Tips

1. **Always activate first**: `source activate.sh`
2. **Use dry run**: Test with `--dry-run` first
3. **Validate configs**: Use `validate-config` before analysis
4. **Use tab completion**: Install with `policy-analyzer completion bash --install`
5. **Check system**: Run `policy-analyzer info` to verify setup

---

**Ready to analyze policies!** 🚀

Run `./setup_mac.sh` to get started.
