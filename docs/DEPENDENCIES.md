# Dependencies

This document lists all dependencies required for the Offline Policy Gap Analyzer, including Python packages, models, and system requirements.

## Python Dependencies

### Core Requirements

The system requires Python 3.11+ (3.11 or 3.12 recommended). Python 3.14+ has compatibility issues with ChromaDB.

### Document Processing

| Package | Version | Purpose | Size |
|---------|---------|---------|------|
| PyMuPDF | >=1.23.0 | Primary PDF parser with layout preservation | ~50MB |
| pdfplumber | >=0.10.0 | Fallback PDF parser for complex tables | ~5MB |
| python-docx | >=1.0.0 | Microsoft Word document parsing | ~2MB |

**PyMuPDF** (fitz) is the primary PDF parser, chosen for speed and layout-aware extraction. **pdfplumber** serves as a fallback for documents with complex tabular data requiring character-level coordinate access.

### Embeddings and Vector Storage

| Package | Version | Purpose | Size |
|---------|---------|---------|------|
| sentence-transformers | >=2.2.0 | Local embedding model framework | ~100MB |
| chromadb | >=0.5.0 | Vector database for similarity search | ~50MB |

**sentence-transformers** provides the framework for loading and running local embedding models. **ChromaDB** offers Python-native vector storage with local persistence.

### LLM and RAG Orchestration

| Package | Version | Purpose | Size |
|---------|---------|---------|------|
| langchain | >=0.1.0 | RAG pipeline orchestration framework | ~20MB |
| langchain-community | >=0.1.0 | Community integrations for LangChain | ~15MB |
| langchain-ollama | >=0.1.0 | Ollama integration for LangChain | ~5MB |

**LangChain** provides abstractions for document loaders, text splitters, retrievers, and LLM chains, enabling modular RAG pipeline construction.

### Local LLM Runtime

| Package | Version | Purpose | Size | Notes |
|---------|---------|---------|------|-------|
| llama-cpp-python | >=0.2.0 | Python bindings for llama.cpp | ~50MB | Advanced users, requires compilation |
| ollama-python | >=0.1.0 | Python client for Ollama | ~5MB | Recommended, easier setup |

**Choose one or both**: Ollama is recommended for ease of use. llama.cpp provides more control but requires compilation.

### Sparse Retrieval

| Package | Version | Purpose | Size |
|---------|---------|---------|------|
| rank-bm25 | >=0.2.0 | BM25 keyword-based retrieval | ~1MB |

**rank-bm25** implements the BM25 algorithm for sparse keyword matching in hybrid retrieval.

### Configuration and Utilities

| Package | Version | Purpose | Size |
|---------|---------|---------|------|
| pyyaml | >=6.0 | YAML configuration file parsing | ~5MB |
| jsonschema | >=4.17.0 | JSON schema validation | ~2MB |
| numpy | >=1.24.0 | Numerical operations for embeddings | ~50MB |
| psutil | >=5.9.0 | System resource monitoring | ~5MB |

### Testing

| Package | Version | Purpose | Size |
|---------|---------|---------|------|
| hypothesis | >=6.90.0 | Property-based testing framework | ~10MB |
| pytest | >=7.4.0 | Unit and integration testing | ~5MB |

**hypothesis** enables the 49 property-based tests that validate universal correctness properties across the system.

## Model Dependencies

### Embedding Model

**Model**: `sentence-transformers/all-MiniLM-L6-v2`
- **Size**: ~90MB
- **Dimensions**: 384
- **Purpose**: Generate dense vector embeddings for semantic search
- **Performance**: ~100 chunks/minute on CPU
- **Download**: Automatic via `scripts/download_models.py`

This model is chosen for optimal speed/accuracy tradeoff on CPU-only hardware.

### Cross-Encoder Reranking Model

**Model**: `cross-encoder/ms-marco-MiniLM-L-6-v2`
- **Size**: ~90MB
- **Purpose**: Rerank hybrid retrieval results for precision
- **Performance**: ~50 pairs/second on CPU
- **Download**: Automatic via `scripts/download_models.py`

Cross-encoder reranking improves retrieval precision by 15-20% in RAG benchmarks.

### LLM Models (Choose One)

#### Option 1: Qwen2.5-3B-Instruct (Default)

- **Size**: ~2GB (4-bit quantized GGUF)
- **Context Window**: 32k tokens
- **RAM Required**: 8GB minimum
- **Performance**: ~10-15 tokens/second on CPU
- **Best For**: Consumer laptops, faster analysis
- **Download**: `scripts/download_models.py --model qwen2.5-3b`

#### Option 2: Phi-3.5-mini-Instruct

- **Size**: ~2.5GB (4-bit quantized GGUF)
- **Context Window**: 128k tokens
- **RAM Required**: 8GB minimum
- **Performance**: ~8-12 tokens/second on CPU
- **Best For**: Long policy documents
- **Download**: `scripts/download_models.py --model phi-3.5-mini`

#### Option 3: Mistral-7B-Instruct

- **Size**: ~4GB (4-bit quantized GGUF)
- **Context Window**: 32k tokens
- **RAM Required**: 16GB minimum
- **Performance**: ~5-8 tokens/second on CPU
- **Best For**: Higher quality analysis, more RAM available
- **Download**: `scripts/download_models.py --model mistral-7b`

#### Option 4: Qwen3-8B-Instruct

- **Size**: ~4.5GB (4-bit quantized GGUF)
- **Context Window**: 131k tokens
- **RAM Required**: 16GB minimum
- **Performance**: ~5-8 tokens/second on CPU
- **Best For**: Very long policies, maximum context
- **Download**: `scripts/download_models.py --model qwen3-8b`

### Model Storage Locations

All models are stored locally in the `models/` directory:

```
models/
├── embeddings/
│   └── all-MiniLM-L6-v2/
├── reranker/
│   └── ms-marco-MiniLM-L-6-v2/
└── llm/
    ├── qwen2.5-3b-instruct.gguf
    ├── phi-3.5-mini-instruct.gguf
    ├── mistral-7b-instruct.gguf
    └── qwen3-8b-instruct.gguf
```

## Reference Data

### CIS MS-ISAC NIST CSF 2.0 Policy Template Guide

- **File**: `context/CIS_NIST_CSF_2.0_Policy_Template_Guide.pdf`
- **Size**: ~5MB
- **Purpose**: Reference baseline for gap analysis
- **Contains**: 49 NIST CSF 2.0 subcategory mappings with policy templates
- **Source**: CIS MS-ISAC (2024)

This guide is parsed during initialization to build the structured Reference Catalog.

## System Requirements

### Operating System

- **Linux**: Recommended (best performance)
- **macOS**: Fully supported
- **Windows**: Supported (may require WSL for some features)

### Hardware

#### Minimum Configuration

- **CPU**: x86_64 processor (Intel/AMD)
- **RAM**: 8GB for 3B parameter models
- **Disk**: 10GB free space
- **GPU**: Not required (CPU-only operation)

#### Recommended Configuration

- **CPU**: 4+ cores for parallel processing
- **RAM**: 16GB for 7B parameter models
- **Disk**: 20GB free space for multiple models
- **GPU**: Not required

### Network

- **Internet**: Required only for initial model download
- **Offline Operation**: All analysis runs without network connectivity

## Optional Dependencies

### Alternative Vector Stores

**FAISS** (Facebook AI Similarity Search)
- **Package**: `faiss-cpu>=1.7.0`
- **Purpose**: Alternative to ChromaDB for larger catalogs (>10k chunks)
- **Performance**: Faster similarity search on large datasets
- **Installation**: `pip install faiss-cpu`

### Development Tools

**Sphinx** (API Documentation)
- **Package**: `sphinx>=7.0.0`
- **Purpose**: Generate API documentation
- **Installation**: `pip install sphinx sphinx-rtd-theme`

**pdoc** (Alternative Documentation)
- **Package**: `pdoc>=14.0.0`
- **Purpose**: Lightweight API documentation
- **Installation**: `pip install pdoc`

## Installation

### Standard Installation

```bash
# Install all required dependencies
pip install -r requirements.txt

# Or install as editable package
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"
```

### Model Download

```bash
# Download all models (requires internet)
python scripts/download_models.py --all

# Download specific model
python scripts/download_models.py --model qwen2.5-3b

# Verify model integrity
python scripts/download_models.py --verify
```

## Dependency Management

### Version Pinning

All dependencies use minimum version constraints (`>=`) to allow compatible updates while ensuring required features are available.

For production deployments, consider pinning exact versions:

```bash
# Generate pinned requirements
pip freeze > requirements-pinned.txt
```

### Compatibility Notes

- **Python 3.14+**: ChromaDB has known compatibility issues. Use Python 3.11 or 3.12.
- **Apple Silicon (M1/M2)**: All dependencies support ARM64 architecture.
- **Windows**: llama-cpp-python may require Visual Studio Build Tools for compilation.

## Troubleshooting

### Common Issues

**ChromaDB Installation Fails**
```bash
# Try installing with specific version
pip install chromadb==0.5.0

# Or use conda
conda install -c conda-forge chromadb
```

**llama-cpp-python Compilation Errors**
```bash
# Use pre-built wheels
pip install llama-cpp-python --extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu

# Or use Ollama instead (no compilation required)
pip install ollama-python
```

**Model Download Fails**
```bash
# Download manually from Hugging Face
# See docs/MODEL_SETUP.md for manual download instructions
```

See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for complete troubleshooting guide.
