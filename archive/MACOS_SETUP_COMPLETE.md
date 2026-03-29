# macOS Setup - Complete Guide

Everything you need to get started with the Offline Policy Gap Analyzer on macOS.

## 🚀 Quick Start (Choose One)

### Option 1: Automated Setup (Recommended)
```bash
chmod +x setup_mac.sh && ./setup_mac.sh
```

### Option 2: Manual Setup
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

## 📦 What You Get

After setup, you'll have:

### Scripts
- **setup_mac.sh** - One-command setup script
- **activate.sh** - Activate environment (run this first!)
- **policy-analyzer.sh** - Launcher (no activation needed)
- **test_installation.sh** - Test everything works
- **examples.sh** - View usage examples

### Commands
- **policy-analyzer** - Main CLI command
- All subcommands: analyze, list-models, info, validate-config, watch, etc.

### Documentation
- **MACOS_QUICK_START.md** - 5-minute quick start
- **SETUP_MAC_README.md** - Detailed setup guide
- **CLI_QUICK_REFERENCE.md** - Command reference
- **docs/CLI_GUIDE.md** - Complete guide (15+ pages)

## 🎯 Three Ways to Use

### Method 1: With Activation (Traditional)
```bash
# Activate environment
source activate.sh

# Use commands
policy-analyzer analyze policy.pdf --domain isms
policy-analyzer info
policy-analyzer list-models

# Deactivate when done
deactivate
```

### Method 2: With Launcher (Easy)
```bash
# No activation needed!
./policy-analyzer.sh analyze policy.pdf --domain isms
./policy-analyzer.sh info
./policy-analyzer.sh list-models
```

### Method 3: Direct (After Install)
```bash
# If you installed with pip install -e .
# and added to PATH
policy-analyzer analyze policy.pdf --domain isms
```

## 📋 Complete Setup Checklist

- [ ] Run `./setup_mac.sh`
- [ ] Wait for setup to complete
- [ ] Run `source activate.sh`
- [ ] Run `./test_installation.sh`
- [ ] Run `policy-analyzer info`
- [ ] Try dry run: `policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --dry-run`
- [ ] Run real analysis: `policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms`
- [ ] Check outputs in `outputs/` directory
- [ ] Install shell completion: `policy-analyzer completion bash --install`
- [ ] Read `MACOS_QUICK_START.md`

## 🔧 System Requirements

### Required
- macOS (any recent version)
- Python 3.8 or higher
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

### Optional but Recommended
- Ollama (for local LLM)
- Homebrew (for easy installation)

## 📚 Documentation Structure

```
Documentation/
├── INSTALL_MACOS.md              # One-line install
├── MACOS_QUICK_START.md          # 5-minute quick start
├── SETUP_MAC_README.md           # Detailed setup guide
├── CLI_QUICK_START.md            # CLI quick start
├── CLI_QUICK_REFERENCE.md        # Command reference
├── INSTALL_CLI.md                # CLI installation
├── docs/CLI_GUIDE.md             # Complete guide (15+ pages)
└── CLI_RECOMMENDED_ENHANCEMENTS_COMPLETE.md  # All features
```

## 🎓 Learning Path

### Day 1: Setup and Basics
1. Run `./setup_mac.sh`
2. Read `MACOS_QUICK_START.md`
3. Run `./test_installation.sh`
4. Try analyzing a test policy

### Day 2: Learn Commands
1. Read `CLI_QUICK_REFERENCE.md`
2. Try all commands
3. Experiment with options
4. Install shell completion

### Day 3: Advanced Features
1. Read `docs/CLI_GUIDE.md`
2. Try dry run mode
3. Try watch mode
4. Create custom configs

### Day 4: Production Use
1. Analyze your own policies
2. Set up automation
3. Integrate with workflows
4. Optimize settings

## 🛠️ Common Tasks

### First Time Setup
```bash
./setup_mac.sh
source activate.sh
./test_installation.sh
```

### Daily Usage
```bash
source activate.sh
policy-analyzer analyze policy.pdf --domain isms
deactivate
```

### Batch Processing
```bash
source activate.sh
for policy in *.pdf; do
    policy-analyzer analyze "$policy" --domain isms --quiet
done
deactivate
```

### Watch Mode
```bash
source activate.sh
policy-analyzer watch ./policies --domain isms --recursive
# Press Ctrl+C to stop
```

### Configuration
```bash
source activate.sh
policy-analyzer init-config my-config.yaml
# Edit my-config.yaml
policy-analyzer validate-config my-config.yaml
policy-analyzer analyze policy.pdf --config my-config.yaml
```

## 🐛 Troubleshooting

### Setup Issues

**Python not found:**
```bash
brew install python@3.11
```

**Permission denied:**
```bash
chmod +x setup_mac.sh
```

**Virtual environment issues:**
```bash
rm -rf venv
./setup_mac.sh
```

### Runtime Issues

**Command not found:**
```bash
source activate.sh
# or
./policy-analyzer.sh --help
```

**Ollama not running:**
```bash
ollama serve &
# or
source activate.sh  # Auto-starts Ollama
```

**Model not found:**
```bash
ollama pull qwen2.5:3b-instruct
```

**Import errors:**
```bash
source activate.sh
pip install -r requirements.txt
```

## 📊 What Gets Installed

### Python Packages (~500MB)
- CLI: click, rich, tabulate, watchdog
- Documents: PyMuPDF, pdfplumber, python-docx
- ML/AI: sentence-transformers, chromadb
- LLM: langchain, ollama-python
- Testing: hypothesis, pytest
- Utils: pyyaml, jsonschema, psutil

### Ollama Models (~2-8GB)
- qwen2.5:3b-instruct (1.9 GB) - Default, fast
- phi3.5:3.8b (2.2 GB) - Optional, balanced
- mistral:7b (4.1 GB) - Optional, accurate

### Total Disk Space
- Python packages: ~500 MB
- Virtual environment: ~1 GB
- Default model: ~2 GB
- **Total: ~3.5 GB**

## 🔄 Updating

### Update Code
```bash
source activate.sh
git pull  # If using git
pip install -e .
```

### Update Dependencies
```bash
source activate.sh
pip install --upgrade -r requirements.txt
```

### Update Models
```bash
ollama pull qwen2.5:3b-instruct
```

## 🗑️ Uninstalling

### Remove Everything
```bash
# Remove virtual environment
rm -rf venv

# Remove helper scripts
rm activate.sh test_installation.sh examples.sh policy-analyzer.sh

# Remove outputs
rm -rf outputs/

# Remove Ollama models (optional)
ollama rm qwen2.5:3b-instruct
```

### Keep Code, Remove Environment
```bash
rm -rf venv
rm activate.sh test_installation.sh examples.sh
```

## 💡 Pro Tips

1. **Use the launcher script** for one-off commands
   ```bash
   ./policy-analyzer.sh analyze policy.pdf --domain isms
   ```

2. **Install shell completion** for faster typing
   ```bash
   policy-analyzer completion bash --install
   ```

3. **Always dry run first** to preview
   ```bash
   policy-analyzer analyze policy.pdf --dry-run
   ```

4. **Validate configs** before using
   ```bash
   policy-analyzer validate-config config.yaml
   ```

5. **Use watch mode** for automation
   ```bash
   policy-analyzer watch ./policies --domain isms
   ```

6. **Check system** before analyzing
   ```bash
   policy-analyzer info
   ```

7. **Use quiet mode** in scripts
   ```bash
   policy-analyzer analyze policy.pdf --quiet
   ```

8. **Create aliases** for common commands
   ```bash
   echo 'alias pa="source ~/offline-policy-analyzer/activate.sh"' >> ~/.bashrc
   echo 'alias analyze="policy-analyzer analyze"' >> ~/.bashrc
   ```

## 🎯 Next Steps

After setup:

1. ✅ Run `source activate.sh`
2. ✅ Run `./test_installation.sh`
3. ✅ Read `MACOS_QUICK_START.md`
4. ✅ Try analyzing a test policy
5. ✅ Read `CLI_QUICK_REFERENCE.md`
6. ✅ Install shell completion
7. ✅ Analyze your own policies
8. ✅ Set up automation

## 📞 Getting Help

### Documentation
- Quick start: `MACOS_QUICK_START.md`
- Commands: `CLI_QUICK_REFERENCE.md`
- Complete guide: `docs/CLI_GUIDE.md`
- Troubleshooting: `docs/TROUBLESHOOTING.md`

### Command Help
```bash
policy-analyzer --help
policy-analyzer analyze --help
policy-analyzer watch --help
```

### Examples
```bash
./examples.sh
```

### System Info
```bash
policy-analyzer info
```

## ✅ Verification

After setup, verify everything works:

```bash
# 1. Activate
source activate.sh

# 2. Check version
policy-analyzer --version

# 3. Check system
policy-analyzer info

# 4. List models
policy-analyzer list-models

# 5. Dry run test
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --dry-run

# 6. Real test
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms

# 7. Check outputs
ls -la outputs/
```

If all steps work, you're ready to go! 🎉

## 🚀 You're Ready!

Your macOS setup is complete. Start analyzing policies with:

```bash
source activate.sh
policy-analyzer analyze your-policy.pdf --domain isms
```

Or use the launcher:

```bash
./policy-analyzer.sh analyze your-policy.pdf --domain isms
```

**Happy analyzing!** 🎉
