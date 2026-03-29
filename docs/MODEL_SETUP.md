# Model Setup Guide

This guide explains how to download and verify models for the Offline Policy Gap Analyzer.

## Overview

The system requires three types of models for offline operation:
1. **Embedding Model**: Converts text to dense vectors for semantic search
2. **Reranker Model**: Improves retrieval precision through cross-encoding
3. **LLM Model**: Performs gap analysis and policy revision generation

## Quick Start

### Download All Models (Recommended)

```bash
python scripts/setup_models.py --all
```

This downloads:
- Embedding model: `all-MiniLM-L6-v2` (~90 MB)
- Reranker model: `ms-marco-MiniLM-L-6-v2` (~80 MB)
- Default LLM: `Qwen2.5-3B-Instruct` (~2 GB)

### Check Model Status

```bash
python scripts/setup_models.py --status
```

This shows which models are installed and which are missing.

## Selective Downloads

### Download Only Embedding and Reranker

```bash
python scripts/setup_models.py --embedding --reranker
```

### Download Specific LLM Model

```bash
# Qwen2.5-3B (recommended, 2 GB)
python scripts/setup_models.py --llm qwen2.5-3b

# Phi-3.5-mini (2.3 GB)
python scripts/setup_models.py --llm phi-3.5

# Mistral-7B (4.1 GB)
python scripts/setup_models.py --llm mistral-7b

# Qwen3-8B (4.7 GB, best quality)
python scripts/setup_models.py --llm qwen3-8b
```

## Model Details

### Embedding Model: all-MiniLM-L6-v2
- **Size**: ~90 MB
- **Dimensions**: 384
- **Purpose**: Converts text chunks to vectors for semantic search
- **Storage**: `models/embeddings/all-MiniLM-L6-v2/`

### Reranker Model: ms-marco-MiniLM-L-6-v2
- **Size**: ~80 MB
- **Purpose**: Reranks retrieval results for improved precision
- **Storage**: `models/reranker/ms-marco-MiniLM-L-6-v2/`

### LLM Models

| Model | Size | RAM Required | Context Window | Best For |
|-------|------|--------------|----------------|----------|
| Qwen2.5-3B | 2 GB | 8 GB | 32k tokens | Default, fast |
| Phi-3.5-mini | 2.3 GB | 8 GB | 128k tokens | Long policies |
| Mistral-7B | 4.1 GB | 16 GB | 32k tokens | Better quality |
| Qwen3-8B | 4.7 GB | 16 GB | 131k tokens | Best quality |

## Prerequisites

### For Embedding and Reranker Models

```bash
pip install sentence-transformers
```

### For LLM Models

Install Ollama:
- **macOS**: `brew install ollama`
- **Linux**: `curl -fsSL https://ollama.ai/install.sh | sh`
- **Windows**: Download from https://ollama.ai

Start Ollama service:
```bash
ollama serve
```

## Verification

After downloading, verify all models are present:

```bash
python scripts/setup_models.py --status
```

Expected output when all models are installed:
```
============================================================
MODEL STATUS
============================================================

Embedding Model: all-MiniLM-L6-v2
  Status: ✓ Installed
  Path: models/embeddings/all-MiniLM-L6-v2

Reranker Model: ms-marco-MiniLM-L-6-v2
  Status: ✓ Installed
  Path: models/reranker/ms-marco-MiniLM-L-6-v2

LLM Models:
  Qwen2.5-3B-Instruct: ✓ Installed
    Tag: qwen2.5:3b-instruct

============================================================

✓ All required models are installed
```

## Troubleshooting

### "sentence-transformers not installed"

```bash
pip install sentence-transformers
```

### "Ollama not found"

Install Ollama from https://ollama.ai, then restart your terminal.

### "Download timed out"

The script has a 30-minute timeout for LLM downloads. If your connection is slow:
1. Download models manually using Ollama CLI:
   ```bash
   ollama pull qwen2.5:3b-instruct
   ```
2. Run the setup script again to verify

### "Model verification failed"

This usually means the download was interrupted. Use `--force` to re-download:
```bash
python scripts/setup_models.py --embedding --force
```

## Storage Locations

All models are stored in the `models/` directory:

```
models/
├── embeddings/
│   └── all-MiniLM-L6-v2/
├── reranker/
│   └── ms-marco-MiniLM-L-6-v2/
└── llm/
    ├── qwen2.5-3b/
    ├── phi-3.5/
    ├── mistral-7b/
    └── qwen3-8b/
```

## Offline Operation

Once models are downloaded, the system operates completely offline:
- No internet connection required for analysis
- All models loaded from local disk
- No external API calls

## Next Steps

After setting up models:

1. **Build Reference Catalog**:
   ```bash
   python scripts/build_catalog.py
   ```

2. **Run Analysis**:
   ```bash
   python -m analysis.cli path/to/policy.pdf
   ```

## Requirements Validation

This setup process validates:
- **Requirement 1.6**: Verify all required resources exist before execution
- **Requirement 17.1**: Verify presence of required model files
- **Requirement 17.2**: Provide setup script to download models
- **Requirement 17.3**: Document exact model files required
- **Requirement 17.4**: Document storage locations
- **Requirement 17.5**: Provide exact download commands when models missing

## Property Tests

The setup script is validated by Property 2: Local Resource Verification

Run property tests:
```bash
python -m pytest tests/property/test_resource_verification.py -v
```

This ensures:
- All required resources are verified before execution
- Missing resources trigger descriptive errors
- Directory integrity is validated (not just existence)
- Verification is idempotent and consistent
