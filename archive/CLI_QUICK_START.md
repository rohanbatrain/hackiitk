# CLI Quick Start Guide

Get started with the enhanced CLI in 5 minutes.

## 1. Install (2 minutes)

```bash
# Install dependencies
pip install click rich tabulate watchdog

# Or install all at once
pip install -r requirements.txt

# Install package (makes 'policy-analyzer' command available)
pip install -e .
```

## 2. Verify (30 seconds)

```bash
# Check version
policy-analyzer --version

# View system info
policy-analyzer info

# List available models
policy-analyzer list-models
```

## 3. First Analysis (2 minutes)

```bash
# Analyze a test policy
policy-analyzer analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

## 4. Try New Features (1 minute)

```bash
# Preview analysis (dry run)
policy-analyzer analyze policy.pdf --domain isms --dry-run

# Validate configuration
policy-analyzer init-config my-config.yaml
policy-analyzer validate-config my-config.yaml

# Install shell completion
policy-analyzer completion bash --install
```

## 5. Advanced Usage (optional)

```bash
# Watch directory for new policies
policy-analyzer watch ./policies --domain isms --recursive

# Analyze with custom config
policy-analyzer analyze policy.pdf --config my-config.yaml --verbose

# Batch processing
for policy in *.pdf; do
    policy-analyzer analyze "$policy" --domain isms --quiet
done
```

## Common Commands

```bash
# Basic analysis
policy-analyzer analyze policy.pdf --domain isms

# With options
policy-analyzer analyze policy.pdf \
    --domain isms \
    --config my-config.yaml \
    --output-dir ./results \
    --verbose

# Dry run (preview)
policy-analyzer analyze policy.pdf --dry-run

# Validate config
policy-analyzer validate-config config.yaml

# Watch directory
policy-analyzer watch ./policies --domain isms

# List models
policy-analyzer list-models

# System info
policy-analyzer info

# Generate config
policy-analyzer init-config config.yaml

# Shell completion
policy-analyzer completion bash --install
```

## Help

```bash
# General help
policy-analyzer --help

# Command help
policy-analyzer analyze --help
policy-analyzer watch --help
policy-analyzer validate-config --help
```

## Next Steps

1. Read `CLI_QUICK_REFERENCE.md` for command reference
2. Read `docs/CLI_GUIDE.md` for complete documentation
3. Try analyzing your own policies
4. Set up watch mode for automated processing
5. Integrate into your CI/CD pipeline

## Troubleshooting

### Command not found
```bash
pip install -e .
```

### Module not found
```bash
pip install -r requirements.txt
```

### Model not found
```bash
ollama pull qwen2.5:3b-instruct
```

## Documentation

- **Quick Reference**: `CLI_QUICK_REFERENCE.md`
- **Installation**: `INSTALL_CLI.md`
- **Complete Guide**: `docs/CLI_GUIDE.md`
- **Enhancements**: `CLI_RECOMMENDED_ENHANCEMENTS_COMPLETE.md`

---

**You're ready to go!** 🚀
