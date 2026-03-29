# CLI Guide - Offline Policy Gap Analyzer

Complete guide to using the production-ready command-line interface.

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Commands](#commands)
- [Options](#options)
- [Examples](#examples)
- [Configuration](#configuration)
- [Exit Codes](#exit-codes)
- [Troubleshooting](#troubleshooting)

## Installation

### Install from Source

```bash
# Clone the repository
git clone https://github.com/yourusername/offline-policy-analyzer.git
cd offline-policy-analyzer

# Install dependencies
pip install -r requirements.txt

# Install the package
pip install -e .
```

After installation, the `policy-analyzer` command will be available globally.

### Verify Installation

```bash
policy-analyzer --version
policy-analyzer info
```

## Quick Start

```bash
# Analyze a policy document
policy-analyzer analyze policy.pdf --domain isms

# Get help
policy-analyzer --help
policy-analyzer analyze --help
```

## Commands

### `analyze` - Analyze a Policy Document

Perform NIST CSF 2.0 compliance gap analysis on a policy document.

```bash
policy-analyzer analyze POLICY_FILE [OPTIONS]
```

**Arguments:**
- `POLICY_FILE` - Path to policy document (PDF, DOCX, TXT, or MD)

**Options:**
- `--domain, -d` - Policy domain (isms, risk_management, patch_management, data_privacy)
- `--config, -c` - Path to configuration file (YAML/JSON)
- `--output-dir, -o` - Output directory for results
- `--model, -m` - LLM model name (default: qwen2.5:3b-instruct)
- `--verbose, -v` - Enable verbose logging
- `--quiet, -q` - Suppress non-essential output

**Examples:**

```bash
# Basic analysis
policy-analyzer analyze isms_policy.pdf --domain isms

# With custom configuration
policy-analyzer analyze policy.docx --config my-config.yaml

# Specify output directory and model
policy-analyzer analyze policy.txt -o ./results -m phi3.5:3.8b

# Verbose mode for debugging
policy-analyzer analyze policy.pdf --domain isms --verbose

# Quiet mode for automation
policy-analyzer analyze policy.pdf --quiet
```

### `list-models` - List Available Models

Display available LLM models from Ollama.

```bash
policy-analyzer list-models [OPTIONS]
```

**Options:**
- `--format, -f` - Output format (table, list, json)

**Examples:**

```bash
# Table format (default)
policy-analyzer list-models

# List format (model names only)
policy-analyzer list-models --format list

# JSON format for scripting
policy-analyzer list-models --format json
```

### `info` - Display System Information

Show system information, dependencies, and configuration.

```bash
policy-analyzer info
```

Displays:
- Python version
- Platform information
- CPU and RAM
- Installed dependencies
- Supported file formats
- Supported policy domains

### `init-config` - Generate Configuration File

Create a default configuration file.

```bash
policy-analyzer init-config [OUTPUT_PATH] [OPTIONS]
```

**Arguments:**
- `OUTPUT_PATH` - Path for configuration file (default: config.yaml)

**Options:**
- `--format, -f` - File format (yaml, json)

**Examples:**

```bash
# Create default YAML config
policy-analyzer init-config

# Create JSON config
policy-analyzer init-config config.json --format json

# Custom path
policy-analyzer init-config configs/production.yaml
```

## Options

### Global Options

Available for all commands:

- `--version` - Show version and exit
- `--help` - Show help message and exit

### Analysis Options

#### Domain Selection

The `--domain` option prioritizes specific CSF subcategories:

- `isms` - Information Security Management System
  - Prioritizes: GV (Govern) function subcategories
  
- `risk_management` - Risk Management
  - Prioritizes: GV.RM, GV.OV, ID.RA subcategories
  
- `patch_management` - Patch Management
  - Prioritizes: ID.RA, PR.DS, PR.PS subcategories
  
- `data_privacy` - Data Privacy
  - Prioritizes: PR.AA, PR.DS, PR.AT subcategories
  - Note: NIST CSF 2.0 is not a complete privacy framework

If not specified, the system attempts to auto-detect the domain.

#### Model Selection

The `--model` option specifies which LLM to use:

```bash
# Use Qwen 2.5 3B (default, fastest)
policy-analyzer analyze policy.pdf -m qwen2.5:3b-instruct

# Use Phi 3.5 3.8B (balanced)
policy-analyzer analyze policy.pdf -m phi3.5:3.8b

# Use Mistral 7B (most accurate, requires 16GB RAM)
policy-analyzer analyze policy.pdf -m mistral:7b
```

**Recommended Models:**
- **8GB RAM**: qwen2.5:3b-instruct, phi3.5:3.8b
- **16GB RAM**: mistral:7b, qwen3:8b

#### Output Directory

The `--output-dir` option specifies where to save results:

```bash
# Default: ./outputs/TIMESTAMP
policy-analyzer analyze policy.pdf

# Custom directory
policy-analyzer analyze policy.pdf -o ./my-results

# Absolute path
policy-analyzer analyze policy.pdf -o /path/to/results
```

Output structure:
```
output-dir/
├── gap_analysis_report.md
├── gap_analysis_report.json
├── revised_policy.md
├── implementation_roadmap.md
├── implementation_roadmap.json
└── audit_log.json
```

#### Verbosity Control

Control output verbosity:

```bash
# Normal output (default)
policy-analyzer analyze policy.pdf

# Verbose (detailed logging)
policy-analyzer analyze policy.pdf --verbose

# Quiet (minimal output, for automation)
policy-analyzer analyze policy.pdf --quiet
```

## Examples

### Basic Workflows

#### 1. First-Time Analysis

```bash
# Check system info
policy-analyzer info

# List available models
policy-analyzer list-models

# Analyze policy
policy-analyzer analyze isms_policy.pdf --domain isms
```

#### 2. Custom Configuration

```bash
# Generate config file
policy-analyzer init-config my-config.yaml

# Edit config file (adjust parameters)
nano my-config.yaml

# Run analysis with custom config
policy-analyzer analyze policy.pdf --config my-config.yaml
```

#### 3. Batch Processing

```bash
#!/bin/bash
# Analyze multiple policies

for policy in policies/*.pdf; do
    echo "Analyzing $policy..."
    policy-analyzer analyze "$policy" \
        --domain isms \
        --output-dir "results/$(basename $policy .pdf)" \
        --quiet
done
```

#### 4. CI/CD Integration

```bash
# Run in CI pipeline
policy-analyzer analyze policy.pdf \
    --domain isms \
    --output-dir ./artifacts \
    --quiet

# Check exit code
if [ $? -eq 0 ]; then
    echo "Analysis passed"
else
    echo "Analysis failed"
    exit 1
fi
```

### Advanced Usage

#### Custom Model Configuration

```yaml
# config.yaml
chunk_size: 512
overlap: 50
top_k: 5
temperature: 0.1
max_tokens: 512
model_name: phi3.5:3.8b

severity_thresholds:
  critical: 0.9
  high: 0.7
  medium: 0.5
  low: 0.3
```

```bash
policy-analyzer analyze policy.pdf --config config.yaml
```

#### Different File Formats

```bash
# PDF document
policy-analyzer analyze policy.pdf --domain isms

# Word document
policy-analyzer analyze policy.docx --domain risk_management

# Markdown file
policy-analyzer analyze policy.md --domain patch_management

# Plain text
policy-analyzer analyze policy.txt --domain data_privacy
```

## Configuration

### Configuration File Format

Configuration files can be YAML or JSON:

**YAML Example:**

```yaml
# Analysis parameters
chunk_size: 512          # Text chunk size in tokens
overlap: 50              # Overlap between chunks
top_k: 5                 # Number of retrieval results
temperature: 0.1         # LLM temperature (0.0-1.0)
max_tokens: 512          # Max tokens per LLM response
model_name: qwen2.5:3b-instruct

# Severity thresholds
severity_thresholds:
  critical: 0.9
  high: 0.7
  medium: 0.5
  low: 0.3

# CSF function priority (optional)
csf_function_priority:
  - GV  # Govern
  - ID  # Identify
  - PR  # Protect
  - DE  # Detect
  - RS  # Respond
  - RC  # Recover
```

**JSON Example:**

```json
{
  "chunk_size": 512,
  "overlap": 50,
  "top_k": 5,
  "temperature": 0.1,
  "max_tokens": 512,
  "model_name": "qwen2.5:3b-instruct",
  "severity_thresholds": {
    "critical": 0.9,
    "high": 0.7,
    "medium": 0.5,
    "low": 0.3
  }
}
```

### Configuration Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `chunk_size` | int | 512 | Text chunk size in tokens |
| `overlap` | int | 50 | Overlap between consecutive chunks |
| `top_k` | int | 5 | Number of retrieval results |
| `temperature` | float | 0.1 | LLM temperature (0.0 = deterministic, 1.0 = creative) |
| `max_tokens` | int | 512 | Maximum tokens per LLM response |
| `model_name` | string | qwen2.5:3b-instruct | LLM model name |
| `severity_thresholds` | dict | See above | Thresholds for gap severity classification |

## Exit Codes

The CLI uses standard exit codes:

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | General error (file not found, parsing error, etc.) |
| 2 | Command-line usage error |
| 130 | Interrupted by user (Ctrl+C) |

**Example usage in scripts:**

```bash
policy-analyzer analyze policy.pdf --domain isms
EXIT_CODE=$?

if [ $EXIT_CODE -eq 0 ]; then
    echo "Success"
elif [ $EXIT_CODE -eq 1 ]; then
    echo "Analysis failed"
elif [ $EXIT_CODE -eq 130 ]; then
    echo "Interrupted"
fi
```

## Troubleshooting

### Common Issues

#### 1. Model Not Found

**Error:**
```
❌ Model Not Found: Model 'qwen2.5:3b-instruct' not found
```

**Solution:**
```bash
# Install the model with Ollama
ollama pull qwen2.5:3b-instruct

# Verify installation
ollama list
```

#### 2. Ollama Not Running

**Error:**
```
❌ Error listing models: Connection refused
```

**Solution:**
```bash
# Start Ollama service
ollama serve

# Or on macOS with Homebrew
brew services start ollama
```

#### 3. Unsupported File Format

**Error:**
```
❌ Unsupported format '.doc'
```

**Solution:**
- Convert to supported format (PDF, DOCX, TXT, MD)
- For .doc files, save as .docx in Microsoft Word

#### 4. OCR Required

**Error:**
```
❌ OCR Required: This PDF appears to be scanned
```

**Solution:**
- This tool only supports text-based PDFs
- Use OCR software to convert scanned PDFs to text
- Or manually extract text and save as .txt or .md

#### 5. Memory Issues

**Error:**
```
❌ Analysis Failed: Out of memory
```

**Solution:**
```bash
# Use a smaller model
policy-analyzer analyze policy.pdf -m qwen2.5:3b-instruct

# Reduce chunk size in config
echo "chunk_size: 256" > config.yaml
policy-analyzer analyze policy.pdf --config config.yaml
```

### Debug Mode

Enable verbose logging for troubleshooting:

```bash
policy-analyzer analyze policy.pdf --verbose
```

This shows:
- Detailed progress information
- Component initialization
- Error stack traces
- Performance metrics

### Getting Help

```bash
# General help
policy-analyzer --help

# Command-specific help
policy-analyzer analyze --help
policy-analyzer list-models --help
policy-analyzer info --help
policy-analyzer init-config --help
```

## Performance Tips

### 1. Model Selection

- **Fast analysis**: Use qwen2.5:3b-instruct (1.9 GB)
- **Balanced**: Use phi3.5:3.8b (2.2 GB)
- **Accurate**: Use mistral:7b (requires 16GB RAM)

### 2. Hardware Optimization

- **8GB RAM**: Stick to 3B models, close other applications
- **16GB RAM**: Can use 7B models comfortably
- **CPU**: More cores = faster embedding generation

### 3. Document Size

- **Optimal**: 10-30 pages
- **Maximum**: 100 pages (enforced limit)
- **Large documents**: Consider splitting into sections

### 4. Batch Processing

For multiple policies:

```bash
# Sequential (safer)
for policy in *.pdf; do
    policy-analyzer analyze "$policy" --quiet
done

# Parallel (faster, requires more RAM)
ls *.pdf | xargs -P 4 -I {} policy-analyzer analyze {} --quiet
```

## Integration Examples

### Python Script

```python
import subprocess
import json

result = subprocess.run(
    ['policy-analyzer', 'analyze', 'policy.pdf', '--domain', 'isms'],
    capture_output=True,
    text=True
)

if result.returncode == 0:
    print("Analysis successful")
else:
    print(f"Analysis failed: {result.stderr}")
```

### GitHub Actions

```yaml
name: Policy Analysis

on: [push]

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install -e .
      
      - name: Install Ollama
        run: |
          curl -fsSL https://ollama.ai/install.sh | sh
          ollama pull qwen2.5:3b-instruct
      
      - name: Analyze policy
        run: |
          policy-analyzer analyze policy.pdf --domain isms --output-dir ./results
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: analysis-results
          path: ./results
```

### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Ollama
RUN curl -fsSL https://ollama.ai/install.sh | sh

# Copy application
COPY . .
RUN pip install -e .

# Pull default model
RUN ollama pull qwen2.5:3b-instruct

ENTRYPOINT ["policy-analyzer"]
```

## Best Practices

1. **Always specify domain** for better CSF prioritization
2. **Use configuration files** for consistent analysis
3. **Enable verbose mode** when debugging
4. **Use quiet mode** in automation/CI
5. **Check exit codes** in scripts
6. **Review audit logs** for compliance tracking
7. **Keep models updated** with `ollama pull`
8. **Monitor memory usage** with large documents

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/yourusername/offline-policy-analyzer/issues
- Documentation: https://github.com/yourusername/offline-policy-analyzer/docs
- Examples: See `examples/` directory
