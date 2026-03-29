# CLI Quick Reference Card

## Installation

```bash
# Install dependencies
pip install click rich tabulate

# Install package
pip install -e .

# Verify
policy-analyzer --version
```

## Basic Commands

```bash
# Analyze a policy
policy-analyzer analyze policy.pdf --domain isms

# List models
policy-analyzer list-models

# System info
policy-analyzer info

# Generate config
policy-analyzer init-config config.yaml

# Help
policy-analyzer --help
```

## Analyze Command

```bash
policy-analyzer analyze POLICY_FILE [OPTIONS]

Options:
  -d, --domain DOMAIN      isms | risk_management | patch_management | data_privacy
  -c, --config PATH        Configuration file (YAML/JSON)
  -o, --output-dir PATH    Output directory
  -m, --model TEXT         LLM model name
  -v, --verbose            Detailed logging
  -q, --quiet              Minimal output
```

## Examples

```bash
# Basic
policy-analyzer analyze policy.pdf --domain isms

# With config
policy-analyzer analyze policy.pdf --config my-config.yaml

# Custom output
policy-analyzer analyze policy.pdf -o ./results

# Different model
policy-analyzer analyze policy.pdf -m phi3.5:3.8b

# Verbose
policy-analyzer analyze policy.pdf --verbose

# Quiet (automation)
policy-analyzer analyze policy.pdf --quiet

# All options
policy-analyzer analyze policy.pdf \
    --domain isms \
    --config config.yaml \
    --output-dir ./results \
    --model qwen2.5:3b-instruct \
    --verbose
```

## List Models Command

```bash
# Table format (default)
policy-analyzer list-models

# JSON format
policy-analyzer list-models --format json

# List format
policy-analyzer list-models --format list
```

## Init Config Command

```bash
# YAML (default)
policy-analyzer init-config config.yaml

# JSON
policy-analyzer init-config config.json --format json
```

## Supported Domains

| Domain | Description |
|--------|-------------|
| `isms` | Information Security Management System |
| `risk_management` | Risk Management |
| `patch_management` | Patch Management |
| `data_privacy` | Data Privacy |

## Supported Formats

- PDF (`.pdf`) - Text-based only
- Word (`.docx`)
- Text (`.txt`, `.md`)

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Error |
| 130 | Interrupted (Ctrl+C) |

## Common Workflows

### First Time Use
```bash
policy-analyzer info
policy-analyzer list-models
policy-analyzer analyze policy.pdf --domain isms
```

### With Custom Config
```bash
policy-analyzer init-config my-config.yaml
# Edit my-config.yaml
policy-analyzer analyze policy.pdf --config my-config.yaml
```

### Batch Processing
```bash
for policy in *.pdf; do
    policy-analyzer analyze "$policy" --domain isms --quiet
done
```

### CI/CD
```bash
policy-analyzer analyze policy.pdf --domain isms --quiet
if [ $? -eq 0 ]; then echo "Pass"; else echo "Fail"; fi
```

## Troubleshooting

### Command not found
```bash
pip install -e .
# or use: python -m cli.main
```

### Module not found
```bash
pip install click rich tabulate
```

### Model not found
```bash
ollama pull qwen2.5:3b-instruct
```

### Ollama not running
```bash
ollama serve
```

## Documentation

- **Complete Guide**: `docs/CLI_GUIDE.md`
- **Installation**: `INSTALL_CLI.md`
- **Overview**: `CLI_PRODUCTION_READY.md`
- **Technical**: `CLI_ENHANCEMENT_SUMMARY.md`

## Getting Help

```bash
policy-analyzer --help
policy-analyzer analyze --help
policy-analyzer list-models --help
policy-analyzer info --help
policy-analyzer init-config --help
```

## Alternative Usage

```bash
# Without installation
python -m cli.main analyze policy.pdf --domain isms

# Direct execution
python cli/main.py analyze policy.pdf --domain isms
```
