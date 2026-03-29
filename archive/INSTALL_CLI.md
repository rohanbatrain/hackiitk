# Installing the Enhanced CLI

Quick guide to install and use the production-ready CLI.

## Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Ollama (for LLM models)

## Installation Steps

### 1. Install Python Dependencies

```bash
# Install the new CLI dependencies
pip install click>=8.1.0 rich>=13.0.0 tabulate>=0.9.0

# Or install all requirements at once
pip install -r requirements.txt
```

**Note:** If you get an error about system packages on macOS, you may need to use a virtual environment:

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Then install
pip install -r requirements.txt
```

### 2. Install the Package (Recommended)

```bash
# Install in development mode (from project root)
pip install -e .
```

This makes the `policy-analyzer` command available globally.

### 3. Verify Installation

```bash
# Check version
policy-analyzer --version

# View help
policy-analyzer --help

# System info
policy-analyzer info
```

## Quick Start

### 1. Check System

```bash
# View system information
policy-analyzer info

# List available models
policy-analyzer list-models
```

### 2. Generate Configuration (Optional)

```bash
# Create default config
policy-analyzer init-config my-config.yaml

# Edit if needed
nano my-config.yaml
```

### 3. Analyze a Policy

```bash
# Basic analysis
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms

# With custom config
policy-analyzer analyze policy.pdf --config my-config.yaml

# With all options
policy-analyzer analyze policy.pdf \
    --domain isms \
    --config my-config.yaml \
    --output-dir ./results \
    --model qwen2.5:3b-instruct \
    --verbose
```

## Usage Examples

### Analyze Different Policy Types

```bash
# ISMS policy
policy-analyzer analyze isms_policy.pdf --domain isms

# Risk management policy
policy-analyzer analyze risk_policy.docx --domain risk_management

# Patch management policy
policy-analyzer analyze patch_policy.txt --domain patch_management

# Data privacy policy
policy-analyzer analyze privacy_policy.md --domain data_privacy
```

### Different Output Modes

```bash
# Normal output (default)
policy-analyzer analyze policy.pdf --domain isms

# Verbose (detailed logging)
policy-analyzer analyze policy.pdf --domain isms --verbose

# Quiet (minimal output, for automation)
policy-analyzer analyze policy.pdf --domain isms --quiet
```

### Utility Commands

```bash
# List available models
policy-analyzer list-models

# List models as JSON
policy-analyzer list-models --format json

# Show system information
policy-analyzer info

# Generate configuration file
policy-analyzer init-config config.yaml
```

## Troubleshooting

### Issue: Command not found

**Error:**
```
policy-analyzer: command not found
```

**Solution:**
```bash
# Make sure you installed the package
pip install -e .

# Or use the module form
python -m cli.main analyze policy.pdf --domain isms
```

### Issue: Module not found

**Error:**
```
ModuleNotFoundError: No module named 'click'
```

**Solution:**
```bash
# Install dependencies
pip install click rich tabulate

# Or all at once
pip install -r requirements.txt
```

### Issue: Ollama not found

**Error:**
```
❌ Ollama command not found
```

**Solution:**
```bash
# Install Ollama
# macOS
brew install ollama

# Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Then pull a model
ollama pull qwen2.5:3b-instruct
```

### Issue: Model not found

**Error:**
```
❌ Model Not Found: Model 'qwen2.5:3b-instruct' not found
```

**Solution:**
```bash
# Make sure Ollama is running
ollama serve

# In another terminal, pull the model
ollama pull qwen2.5:3b-instruct

# Verify
ollama list
```

## Alternative Usage (Without Installation)

If you don't want to install the package, you can still use the CLI:

```bash
# Run as module
python -m cli.main analyze policy.pdf --domain isms

# Or run directly
python cli/main.py analyze policy.pdf --domain isms
```

## Next Steps

1. Read the complete CLI guide: `docs/CLI_GUIDE.md`
2. Try analyzing the dummy policies in `tests/fixtures/dummy_policies/`
3. Generate a config file and customize parameters
4. Integrate into your workflow (scripts, CI/CD, etc.)

## Getting Help

```bash
# General help
policy-analyzer --help

# Command-specific help
policy-analyzer analyze --help
policy-analyzer list-models --help
policy-analyzer info --help
policy-analyzer init-config --help
```

## Documentation

- **CLI Guide**: `docs/CLI_GUIDE.md` - Complete documentation
- **Enhancement Summary**: `CLI_ENHANCEMENT_SUMMARY.md` - Technical details
- **Production Ready**: `CLI_PRODUCTION_READY.md` - Overview
- **Main README**: `README.md` - Project overview

## Support

For issues or questions:
- Check `docs/TROUBLESHOOTING.md`
- Review `docs/CLI_GUIDE.md`
- Check GitHub issues (if applicable)
