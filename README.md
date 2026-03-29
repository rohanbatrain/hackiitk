# Policy Analyzer - NIST CSF 2.0 Gap Analysis Tool

Analyze policy documents against NIST Cybersecurity Framework 2.0 to identify compliance gaps.

## Quick Start

### 1. Run Setup
```bash
./setup.sh
```

This will:
- Install Python 3.11 (if needed)
- Create virtual environment
- Install all dependencies
- Download embedding models
- Verify installation

### 2. Activate Environment
```bash
source venv311/bin/activate
```

### 3. Test with Sample Policy
```bash
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

### 4. Analyze Your Own Policy
```bash
./pa --policy-path data/policies/Information-Security-Policy.md --domain isms
```

## Available Commands

```bash
# Show help
./pa --help

# Analyze with specific domain
./pa --policy-path policy.pdf --domain isms
./pa --policy-path policy.pdf --domain risk_management
./pa --policy-path policy.pdf --domain data_privacy
./pa --policy-path policy.pdf --domain patch_management

# Specify output directory
./pa --policy-path policy.pdf --output-dir ./my_results

# Use specific Ollama model
./pa --policy-path policy.pdf --model phi3.5:3.8b

# Verbose mode
./pa --policy-path policy.pdf --verbose
```

## Supported Domains

- `isms` - Information Security Management System
- `risk_management` - Risk Management
- `patch_management` - Patch Management
- `data_privacy` - Data Privacy

## Supported File Formats

- PDF (`.pdf`) - Text-based PDFs
- Word (`.docx`) - Microsoft Word documents
- Text (`.txt`) - Plain text files
- Markdown (`.md`) - Markdown files

## Output Files

After analysis, you'll find in `outputs/TIMESTAMP/`:
- `gap_analysis.json` - Detailed gap report
- `revised_policy.md` - Policy with improvements
- `implementation_roadmap.md` - Step-by-step action plan
- `audit_log.json` - Complete audit trail

## Architecture

```
Reference Catalog (49 NIST CSF 2.0 controls)
    ↓
ANALYZES
    ↓
Your Policy Document
    ↓
PRODUCES
    ↓
Gap Analysis + Recommendations
```

The tool compares your policy against the 49 NIST CSF 2.0 controls to identify what's missing or needs improvement.

## Requirements

- macOS (Apple Silicon or Intel)
- Python 3.11+
- Ollama with models (qwen2.5:3b-instruct or phi3.5:3.8b)
- 8GB RAM minimum

## Troubleshooting

### Setup fails
```bash
# Try manual installation
source venv311/bin/activate
pip install torch sentence-transformers chromadb langchain
pip install pypdf2 python-docx pyyaml click rich
pip install -e .
```

### ChromaDB errors
Make sure you're using Python 3.11 (not 3.14):
```bash
python --version  # Should show 3.11.x
```

### Model not found
```bash
python scripts/download_models.py --embedding
mkdir -p models/embeddings
mv models/all-MiniLM-L6-v2 models/embeddings/
```

### Ollama not found
Install Ollama and pull a model:
```bash
brew install ollama
ollama pull qwen2.5:3b-instruct
```

## Project Structure

```
.
├── setup.sh                    # Main setup script
├── pa                          # CLI wrapper
├── data/
│   ├── cis_guide.pdf          # NIST CSF 2.0 source
│   ├── reference_catalog.json # 49 CSF controls
│   └── policies/              # Sample policy templates
├── tests/fixtures/
│   └── dummy_policies/        # Test policies
├── models/embeddings/         # ML models
└── outputs/                   # Analysis results
```

## Documentation

- `CATALOG_EXPLANATION.md` - Understanding the reference catalog
- `START_HERE.md` - Quick start guide
- `SETUP_README.md` - Detailed setup instructions

## License

MIT

## Support

For issues or questions, check the documentation files or create an issue.
