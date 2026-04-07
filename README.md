# Offline Policy Gap Analyzer

An AI-powered system for analyzing policy documents and detecting gaps against compliance frameworks.

## Quick Start

```bash
# Setup
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# Run analysis
python -m cli.main analyze path/to/policy.pdf
```

## Documentation

- [Setup Guide](docs/guides/SETUP_README.md)
- [CLI Guide](docs/CLI_GUIDE.md)
- [Architecture](docs/ARCHITECTURE.md)
- [Testing Guide](docs/TESTING_FRAMEWORK.md)
- [API Documentation](docs/API.md)

## Project Structure

```
├── analysis/          # Core analysis engine
├── cli/              # Command-line interface
├── data/             # Reference data and policies
├── docs/             # Documentation
├── ingestion/        # Document parsing
├── models/           # Data models and schemas
├── retrieval/        # Vector store and retrieval
├── reporting/        # Report generation
├── scripts/          # Utility scripts
├── tests/            # Test suite
└── utils/            # Shared utilities
```

## Features

- PDF/DOCX policy document parsing
- AI-powered gap detection
- Compliance framework mapping (CIS, NIST)
- Detailed gap reports with remediation roadmaps
- Offline operation with local LLMs

## License

See [LICENSE](LICENSE) file for details.
