# 🚀 Quick Start Guide

Your Policy Analyzer is ready to use!

## Using the Tool

### Option 1: Simple Wrapper (Recommended)
```bash
# Activate virtual environment
source venv/bin/activate

# Run analysis (warnings suppressed)
./pa --policy-path your_policy.pdf --domain isms
```

### Option 2: Direct Python
```bash
# Activate virtual environment
source venv/bin/activate

# Run with warnings suppressed
PYTHONWARNINGS="ignore" python -m cli.main --policy-path your_policy.pdf --domain isms
```

## Quick Examples

### Analyze an ISMS policy
```bash
./pa --policy-path isms_policy.pdf --domain isms
```

### Analyze a privacy policy
```bash
./pa --policy-path privacy_policy.pdf --domain data_privacy
```

### Auto-detect domain
```bash
./pa --policy-path policy.pdf
```

### Specify output directory
```bash
./pa --policy-path policy.pdf --output-dir ./my_results
```

### Use specific Ollama model
```bash
./pa --policy-path policy.pdf --model qwen2.5:3b-instruct
```

## Available Domains
- `isms` - Information Security Management System
- `risk_management` - Risk Management  
- `patch_management` - Patch Management
- `data_privacy` - Data Privacy

## Supported File Formats
- PDF (`.pdf`) - Text-based PDFs
- Word (`.docx`) - Microsoft Word documents
- Text (`.txt`, `.md`) - Plain text and Markdown

## Your Ollama Models
You have these models installed:
- `qwen2.5:3b-instruct` (1.9 GB)
- `phi3.5:3.8b` (2.2 GB)

## Getting Help
```bash
./pa --help
```

## Troubleshooting

### If you see "command not found: pa"
```bash
chmod +x pa
```

### If virtual environment is not activated
```bash
source venv/bin/activate
```

### To check if everything is working
```bash
./pa --version
```

## What the Tool Does

1. **Parses** your policy document
2. **Analyzes** it against NIST CSF 2.0 framework
3. **Identifies** compliance gaps
4. **Generates** outputs:
   - Gap analysis report (JSON)
   - Revised policy with improvements
   - Implementation roadmap
   - Audit log

## Output Location
Results are saved to: `./outputs/TIMESTAMP/`

---

**That's it!** You're ready to analyze policies. 🎉
