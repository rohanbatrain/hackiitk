# macOS Quick Start - 5 Minutes to First Analysis

## Step 1: Run Setup (2 minutes)

Open Terminal and navigate to the project directory, then run:

```bash
chmod +x setup_mac.sh && ./setup_mac.sh
```

The script will guide you through everything. Just answer the prompts.

## Step 2: Activate Environment (5 seconds)

```bash
source activate.sh
```

You'll see:
```
✓ Ollama started
✓ Environment activated

Available commands:
  policy-analyzer --help
  policy-analyzer info
  ...
```

## Step 3: Test It (30 seconds)

```bash
./test_installation.sh
```

This runs a quick test to make sure everything works.

## Step 4: Analyze Your First Policy (2 minutes)

```bash
# Try with a test policy first (dry run)
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms --dry-run

# Now do a real analysis
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

## That's It! 🎉

You just analyzed your first policy!

## Daily Usage

### Every Time You Start

```bash
# Navigate to project
cd /path/to/offline-policy-analyzer

# Activate environment
source activate.sh
```

### Analyze Policies

```bash
# Basic analysis
policy-analyzer analyze your-policy.pdf --domain isms

# Preview first (recommended)
policy-analyzer analyze your-policy.pdf --domain isms --dry-run

# With custom config
policy-analyzer analyze your-policy.pdf --config my-config.yaml
```

### When You're Done

```bash
deactivate
```

## Alternative: Use the Launcher Script

Instead of activating manually, use the launcher:

```bash
# Make it executable (one time)
chmod +x policy-analyzer.sh

# Use it anytime (no activation needed!)
./policy-analyzer.sh analyze policy.pdf --domain isms
./policy-analyzer.sh info
./policy-analyzer.sh list-models
```

The launcher automatically:
- Activates the virtual environment
- Starts Ollama if needed
- Runs your command
- Deactivates when done

## Common Commands

```bash
# After activating (source activate.sh)

# Get help
policy-analyzer --help

# System info
policy-analyzer info

# List models
policy-analyzer list-models

# Analyze policy
policy-analyzer analyze policy.pdf --domain isms

# Dry run (preview)
policy-analyzer analyze policy.pdf --dry-run

# Validate config
policy-analyzer validate-config config.yaml

# Watch directory
policy-analyzer watch ./policies --domain isms

# Generate config
policy-analyzer init-config my-config.yaml
```

## Domains

Choose the domain that matches your policy:

- `isms` - Information Security Management System
- `risk_management` - Risk Management
- `patch_management` - Patch Management
- `data_privacy` - Data Privacy

## Tips

1. **Always activate first** (unless using launcher script)
   ```bash
   source activate.sh
   ```

2. **Use dry run to preview**
   ```bash
   policy-analyzer analyze policy.pdf --dry-run
   ```

3. **Validate configs before use**
   ```bash
   policy-analyzer validate-config config.yaml
   ```

4. **Install shell completion for faster typing**
   ```bash
   policy-analyzer completion bash --install
   source ~/.bash_completion.d/policy-analyzer
   ```

5. **Check system before analyzing**
   ```bash
   policy-analyzer info
   ```

## Troubleshooting

### "Command not found"

```bash
# Make sure you activated
source activate.sh

# Or use the launcher
./policy-analyzer.sh --help
```

### "Ollama not running"

```bash
# Start Ollama
ollama serve &

# Or let activate.sh do it
source activate.sh
```

### "Model not found"

```bash
# Download the model
ollama pull qwen2.5:3b-instruct
```

### "Virtual environment not found"

```bash
# Run setup again
./setup_mac.sh
```

## Next Steps

1. ✅ Setup complete
2. ✅ First analysis done
3. 📖 Read `CLI_QUICK_REFERENCE.md` for all commands
4. 📖 Read `docs/CLI_GUIDE.md` for complete guide
5. 🚀 Start analyzing your own policies!

## File Locations

After setup, you'll have:

```
offline-policy-analyzer/
├── venv/                    # Virtual environment (don't touch)
├── activate.sh              # Run this to activate
├── policy-analyzer.sh       # Or use this launcher
├── test_installation.sh     # Test script
├── examples.sh              # Examples
├── outputs/                 # Analysis results go here
└── ...
```

## Getting Help

```bash
# Command help
policy-analyzer --help
policy-analyzer analyze --help

# View examples
./examples.sh

# Read docs
cat CLI_QUICK_REFERENCE.md
open docs/CLI_GUIDE.md
```

## Workflow Example

Here's a typical workflow:

```bash
# 1. Start your session
cd ~/offline-policy-analyzer
source activate.sh

# 2. Check system
policy-analyzer info

# 3. Preview analysis
policy-analyzer analyze my-policy.pdf --domain isms --dry-run

# 4. Run analysis
policy-analyzer analyze my-policy.pdf --domain isms

# 5. Check results
ls -la outputs/

# 6. Analyze another
policy-analyzer analyze another-policy.pdf --domain risk_management

# 7. End session
deactivate
```

## Batch Processing

Analyze multiple policies:

```bash
source activate.sh

for policy in policies/*.pdf; do
    echo "Analyzing $policy..."
    policy-analyzer analyze "$policy" --domain isms --quiet
done

deactivate
```

## Watch Mode

Automatically analyze new policies:

```bash
source activate.sh

# Start watching
policy-analyzer watch ./incoming-policies --domain isms --recursive

# In another terminal, copy policies to ./incoming-policies/
# They'll be analyzed automatically!

# Press Ctrl+C to stop watching
```

---

**You're all set!** 🎉

Start with: `source activate.sh` then `policy-analyzer --help`
