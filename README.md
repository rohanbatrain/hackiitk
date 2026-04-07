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

## 📦 Automated Cross-Platform Releases

This repository includes an automated GitHub release workflow at `/.github/workflows/release.yml`

### What it does
- Builds release artifacts on **Linux**, **macOS**, and **Windows**
- Runs release-focused validation for install, startup, CLI, update, and uninstall flows
- Builds Python distribution artifacts (`sdist` + `wheel`)
- Builds standalone executables using PyInstaller
- Publishes all artifacts plus SHA256 checksums to GitHub Releases

### How to trigger
- Automatic: push a semantic version tag, e.g. `v1.2.3`
- Manual: run the **Cross-Platform Release** workflow with `release_tag`

### Included release artifacts
- Source distribution (`.tar.gz`)
- Wheel (`.whl`)
- Linux standalone bundle (`.tar.gz`)
- macOS standalone bundle (`.tar.gz`)
- Windows standalone bundle (`.zip`)

## 🖥️ Electron Desktop Application

A production-oriented Electron desktop application lives in `desktop/` with:

- Secure IPC boundaries (`main` + `preload` + typed contracts)
- Onboarding, runtime, model management, task execution, and settings screens
- Local Ollama runtime/process integration and model lifecycle actions
- Cross-platform installer packaging (`electron-builder`)
- Release split/assembly tooling to keep every released file below 2 GiB

See:
- [Desktop README](desktop/README.md)
- [Desktop Architecture and Operations](docs/ELECTRON_DESKTOP_APP.md)

## 🏗️ Architecture

```
ingestion/          # Document parsing & chunking
reference_builder/  # NIST CSF 2.0 catalog
retrieval/          # Hybrid retrieval (vector + sparse + reranking)
analysis/           # Gap analysis (Stage A + Stage B)
revision/           # Policy revision engine
reporting/          # Output generation & audit logging
orchestration/      # LangChain pipeline orchestration
tests/              # Comprehensive test suite
  ├── unit/         # Unit tests
  ├── integration/  # Integration tests
  ├── property/     # Property-based tests
  └── extreme/      # Stress, chaos, adversarial tests
```

## 📝 Documentation

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
