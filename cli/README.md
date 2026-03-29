# Command-Line Interface

The Offline Policy Gap Analyzer provides a user-friendly command-line interface for analyzing organizational cybersecurity policies against NIST CSF 2.0 standards.

## Installation

After installing the package, the CLI is available as:

```bash
# Using the installed command
policy-analyzer --policy-path policy.pdf --domain isms

# Or running as a Python module
python -m cli.main --policy-path policy.pdf --domain isms

# Or using the project's __main__.py
python __main__.py --policy-path policy.pdf --domain isms
```

## Usage

### Basic Analysis

Analyze a policy document with auto-detected domain:

```bash
policy-analyzer --policy-path my_policy.pdf
```

### Specify Policy Domain

For better CSF prioritization, specify the policy domain:

```bash
policy-analyzer --policy-path isms_policy.pdf --domain isms
```

Supported domains:
- `isms` - Information Security Management System
- `risk_management` - Risk Management
- `patch_management` - Patch Management
- `data_privacy` - Data Privacy

### Custom Configuration

Use a custom configuration file:

```bash
policy-analyzer --policy-path policy.docx --config custom_config.yaml
```

### Specify Output Directory

Control where results are saved:

```bash
policy-analyzer --policy-path policy.txt --output-dir ./my_results
```

### Use Specific Model

Override the default LLM model:

```bash
policy-analyzer --policy-path policy.pdf --model mistral-7b
```

### Verbose Logging

Enable detailed logging for troubleshooting:

```bash
policy-analyzer --policy-path policy.pdf --verbose
```

## Command-Line Arguments

| Argument | Required | Description | Default |
|----------|----------|-------------|---------|
| `--policy-path` | Yes | Path to policy document (PDF/DOCX/TXT/MD) | - |
| `--config` | No | Path to configuration file | Built-in defaults |
| `--domain` | No | Policy domain for CSF prioritization | Auto-detect |
| `--output-dir` | No | Output directory for results | `./outputs/TIMESTAMP` |
| `--model` | No | LLM model name | From config or qwen2.5-3b |
| `--verbose` | No | Enable verbose logging | False |
| `--version` | No | Show version and exit | - |
| `--help` | No | Show help message and exit | - |

## Supported File Formats

- **PDF** (`.pdf`) - Text-based PDFs only (no OCR support)
- **Word** (`.docx`) - Microsoft Word documents
- **Text** (`.txt`, `.md`) - Plain text and Markdown files

## Output Files

The analyzer generates the following outputs in the specified output directory:

1. **gap_analysis_report.md** - Human-readable gap analysis report
2. **gap_analysis_report.json** - Machine-readable gap data
3. **revised_policy.md** - Improved policy text addressing gaps
4. **implementation_roadmap.md** - Prioritized action plan
5. **implementation_roadmap.json** - Machine-readable roadmap data
6. **audit_log.json** - Immutable audit trail

## Exit Codes

- `0` - Success
- `1` - General error (file not found, parsing failed, etc.)
- `130` - Interrupted by user (Ctrl+C)

## Examples

### Analyze ISMS Policy

```bash
policy-analyzer \
  --policy-path isms_policy.pdf \
  --domain isms \
  --output-dir ./isms_results
```

### Analyze with Custom Config

```bash
policy-analyzer \
  --policy-path risk_policy.docx \
  --domain risk_management \
  --config ./configs/strict_analysis.yaml \
  --verbose
```

### Quick Analysis with Defaults

```bash
policy-analyzer --policy-path policy.txt
```

## Progress Indicators

The CLI displays a progress bar during analysis:

```
[████████████████░░░░░░░░░░░░░░] 60% - Executing gap analysis...
```

## Error Handling

The CLI provides clear error messages for common issues:

- **File not found**: Displays path and exits with code 1
- **Unsupported format**: Lists supported formats and exits with code 1
- **Configuration error**: Shows configuration issue and exits with code 1
- **Analysis failure**: Logs detailed error and exits with code 1
- **Keyboard interrupt**: Cleans up gracefully and exits with code 130

## Keyboard Interrupts

Press `Ctrl+C` to interrupt analysis. The CLI will:
1. Display interruption message
2. Clean up resources
3. Exit with code 130

## Logging

Logs are written to:
- Console (INFO level by default, DEBUG with `--verbose`)
- Log file in output directory (all levels)

## Troubleshooting

### Models Not Found

If you see "Model files may not be downloaded", run:

```bash
python scripts/setup_models.py
```

### CIS Guide Missing

Ensure the CIS guide is available at:
```
data/cis_guide.pdf
```

Or configure the path in your config file.

### Memory Issues

For large policies or limited RAM:
1. Use a smaller model (e.g., qwen2.5-3b instead of mistral-7b)
2. Reduce chunk size in configuration
3. Close other applications

### Parsing Errors

For PDF parsing issues:
1. Ensure PDF is text-based (not scanned)
2. Try converting to DOCX or TXT
3. Check PDF is not corrupted

## Integration

The CLI can be integrated into scripts and workflows:

```bash
#!/bin/bash

# Analyze multiple policies
for policy in policies/*.pdf; do
  echo "Analyzing $policy..."
  policy-analyzer --policy-path "$policy" --domain isms
done
```

## Development

To run the CLI during development:

```bash
# From project root
python -m cli.main --policy-path test.pdf

# Or directly
python __main__.py --policy-path test.pdf
```

## See Also

- [Main README](../README.md) - Project overview
- [Configuration Guide](../docs/README.md) - Configuration options
- [Model Setup](../docs/MODEL_SETUP.md) - Model installation
