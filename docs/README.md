# Offline Policy Gap Analyzer

## Overview

The Offline Policy Gap Analyzer is a local LLM-powered system that analyzes organizational cybersecurity policies against NIST CSF 2.0 standards using the CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024) as the reference baseline. The system identifies gaps, generates revised policy text, and creates prioritized improvement roadmaps while operating entirely offline on consumer-grade hardware without any cloud dependencies.

## Features

- **Complete Offline Operation**: All processing occurs locally without network calls
- **Multi-Format Support**: Parse PDF, DOCX, and TXT policy documents
- **Hybrid RAG**: Combines semantic similarity with keyword matching for precision
- **Two-Stage Analysis**: Deterministic evidence detection + constrained LLM reasoning
- **Policy Revision**: Generate improved policy text with human-review warnings
- **Implementation Roadmaps**: Prioritized action plans aligned with NIST CSF
- **Consumer Hardware**: Runs on laptops with 8-16GB RAM without GPU

## Architecture

### Core Components

1. **Document Ingestion** (`ingestion/`): Parse policy documents from PDF/DOCX/TXT
2. **Reference Builder** (`reference_builder/`): Structure CIS guide into queryable catalog
3. **Retrieval** (`retrieval/`): Hybrid search combining dense + sparse methods
4. **Analysis** (`analysis/`): Two-stage gap analysis engine
5. **Revision** (`revision/`): Policy improvement text generation
6. **Reporting** (`reporting/`): Gap reports and roadmap generation
7. **Models** (`models/`): Data structures and schemas

### Two-Stage Analysis Architecture

**Stage A: Deterministic Evidence Detection**
- Lexical overlap scoring (keyword matching)
- Semantic similarity scoring (embedding distance)
- Section heuristics (policy structure analysis)
- Classification: Covered / Partially Covered / Missing / Ambiguous

**Stage B: Constrained LLM Reasoning**
- Processes only Ambiguous/Missing cases from Stage A
- Strict output schemas to prevent hallucination
- Explains gaps and suggests specific fixes

## Installation

### Prerequisites

- Python 3.9 or higher
- 8GB RAM minimum (for 3B models), 16GB recommended (for 7B models)
- 10GB disk space for models and dependencies

### Setup Steps

1. **Clone the repository**:
```bash
git clone <repository-url>
cd offline-policy-gap-analyzer
```

2. **Create virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -e .
```

4. **Download models** (while internet is available):
```bash
# Download embedding model
python scripts/download_models.py --embedding

# Download LLM (choose one)
python scripts/download_models.py --llm qwen2.5-3b-instruct
# OR
python scripts/download_models.py --llm phi-3.5-mini
```

5. **Prepare reference catalog**:
```bash
# Place CIS guide PDF in data/cis_guide.pdf
python scripts/build_catalog.py
```

## Configuration

Edit `config.yaml` to customize:

- **Chunking**: `chunk_size`, `overlap`
- **Retrieval**: `top_k`, `rerank_top_k`
- **LLM**: `temperature`, `max_tokens`, `model_name`
- **Analysis**: Coverage thresholds, severity mapping
- **Domain**: Policy type prioritization

## Usage

### Basic Analysis

```bash
policy-analyzer analyze --input path/to/policy.pdf --domain isms
```

### Specify Configuration

```bash
policy-analyzer analyze --input policy.pdf --config custom_config.yaml
```

### Output Structure

```
outputs/20240115_103000/
├── gap_analysis_report.md
├── gap_analysis_report.json
├── revised_policy.md
├── implementation_roadmap.md
├── implementation_roadmap.json
└── analyzer.log
```

## Supported Policy Domains

- **ISMS**: Information Security Management System policies
- **Risk Management**: Risk assessment and management policies
- **Patch Management**: Vulnerability and patch management policies
- **Data Privacy**: Data protection and privacy policies

## Model Options

### Embedding Models
- **all-MiniLM-L6-v2** (default): 384-dim, fast, CPU-optimized

### LLM Models
- **Qwen2.5-3B-Instruct** (default): 8GB RAM, 131k context
- **Phi-3.5-mini**: 8GB RAM, efficient
- **Mistral-7B**: 16GB RAM, higher quality
- **Qwen3-8B**: 16GB RAM, 131k context

All models use 4-bit quantization (GGUF format) for consumer hardware.

## Testing

### Run Unit Tests
```bash
pytest tests/unit/
```

### Run Property-Based Tests
```bash
pytest tests/property/ --hypothesis-seed=12345
```

### Run Integration Tests
```bash
pytest tests/integration/
```

## Known Limitations

1. **OCR Not Supported**: Scanned PDFs without text layer are rejected
2. **Privacy Framework Scope**: NIST CSF addresses cybersecurity aspects only; complete privacy compliance may require additional frameworks
3. **Document Size**: Maximum 100 pages per policy document
4. **Manual Review Required**: All AI-generated policy revisions must be reviewed by qualified legal counsel and compliance officers

## Troubleshooting

### Model Not Found
```
Error: Model file not found at ./models/qwen2.5-3b-instruct-q4_k_m.gguf
Solution: Run python scripts/download_models.py --llm qwen2.5-3b-instruct
```

### Memory Overflow
```
Error: Memory usage exceeded 90% threshold
Solution: Use a smaller model (3B instead of 7B) or reduce chunk_size in config.yaml
```

### Empty Retrieval Results
```
Warning: No relevant CSF subcategories found
Solution: Check that reference_catalog.json exists and contains 49 subcategories
```

## Future Enhancements

The system architecture is designed to evolve toward:

1. **Agentic RAG**: Multi-agent workflows (Planner, Retriever, Critic agents)
2. **Self-Correction**: Iterative refinement with internal auditing
3. **Enhanced Precision**: Advanced retrieval strategies and prompt engineering
4. **Multi-Framework Support**: Extend beyond NIST CSF to ISO 27001, SOC 2, etc.

## License

MIT License - See LICENSE file for details

## Compliance Warning

**IMPORTANT**: This system generates AI-assisted policy analysis and revisions. The CIS MS-ISAC templates are advisory and may not reflect the most recent applicable standards or your organization's specific legal, regulatory, or operational requirements. All outputs MUST be reviewed, validated, and approved by qualified legal counsel, compliance officers, and security leadership before adoption.

## Support

For issues, questions, or contributions, please refer to the project repository.
