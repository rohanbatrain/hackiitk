# Orchestration Module

This module provides the `AnalysisPipeline` class that orchestrates the complete workflow of the Offline Policy Gap Analyzer using LangChain abstractions.

## Overview

The `AnalysisPipeline` coordinates all components from document parsing through gap analysis, policy revision, roadmap generation, and output creation. It implements a structured workflow with progress indicators, error handling, and audit logging.

## Components

### AnalysisPipeline

Main orchestration class that manages the complete analysis workflow.

**Key Features:**
- Resource initialization and management
- Progress indicators for long-running operations
- Graceful error handling with detailed logging
- Audit trail generation for compliance
- Support for domain-specific prioritization
- Configurable parameters via PipelineConfig

**Workflow Steps:**
1. Parse policy document (PDF, DOCX, or TXT)
2. Load or build reference catalog from CIS guide
3. Chunk policy text with overlap
4. Embed policy chunks and store in vector database
5. Retrieve relevant CSF subcategories
6. Execute Stage A analysis (deterministic evidence detection)
7. Execute Stage B analysis (LLM reasoning for ambiguous cases)
8. Generate gap analysis report (markdown + JSON)
9. Generate revised policy document
10. Generate implementation roadmap (markdown + JSON)
11. Write all outputs to timestamped directory
12. Create immutable audit log entry

### PipelineConfig

Configuration dataclass for pipeline parameters.

**Parameters:**
- `chunk_size`: Maximum tokens per chunk (default: 512)
- `overlap`: Token overlap between chunks (default: 50)
- `top_k`: Number of retrieval results (default: 5)
- `temperature`: LLM temperature (default: 0.1)
- `max_tokens`: Maximum LLM generation tokens (default: 512)
- `model_name`: LLM model name
- `model_path`: Path to LLM model file
- `embedding_model_path`: Path to embedding model
- `vector_store_path`: Path to vector store persistence
- `catalog_path`: Path to reference catalog JSON
- `cis_guide_path`: Path to CIS guide PDF
- `output_dir`: Base output directory
- `audit_dir`: Audit log directory

### AnalysisResult

Result object containing all analysis outputs.

**Attributes:**
- `gap_report`: GapAnalysisReport with identified gaps
- `revised_policy`: RevisedPolicy with improvements
- `roadmap`: ImplementationRoadmap with prioritized actions
- `output_directory`: Path to output files
- `duration_seconds`: Total analysis duration

## Usage

### Basic Usage

```python
from orchestration.analysis_pipeline import AnalysisPipeline

# Create pipeline with default configuration
pipeline = AnalysisPipeline()

# Execute analysis
result = pipeline.execute(
    policy_path="path/to/policy.pdf",
    domain="isms",  # Optional: isms, risk_management, patch_management, data_privacy
    output_dir="outputs"
)

# Access results
print(f"Gaps identified: {len(result.gap_report.gaps)}")
print(f"Outputs: {result.output_directory}")

# Cleanup
pipeline.cleanup()
```

### Custom Configuration

```python
from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig

# Create custom configuration
config = PipelineConfig({
    'chunk_size': 512,
    'overlap': 50,
    'top_k': 5,
    'temperature': 0.1,
    'model_name': 'qwen2.5-3b-instruct',
    'output_dir': 'my_outputs'
})

# Create pipeline with custom config
pipeline = AnalysisPipeline(config=config)

# Execute analysis
result = pipeline.execute(policy_path="policy.pdf")
```

### Reusing Initialized Pipeline

```python
# Initialize once
pipeline = AnalysisPipeline()
pipeline.initialize_resources()

# Analyze multiple policies
for policy_path in policy_files:
    result = pipeline.execute(policy_path=policy_path)
    print(f"Analyzed {policy_path}: {len(result.gap_report.gaps)} gaps")

# Cleanup when done
pipeline.cleanup()
```

## Output Structure

The pipeline creates a timestamped output directory for each analysis:

```
outputs/
└── policy_name_20240115_143022/
    ├── gap_analysis_report.md
    ├── gap_analysis_report.json
    ├── revised_policy.md
    ├── implementation_roadmap.md
    └── implementation_roadmap.json
```

Audit logs are stored separately:

```
audit_logs/
├── audit_20240115_143022_123456.json
└── audit_20240115_150033_789012.json
```

## Error Handling

The pipeline implements graceful error handling:

- **Initialization errors**: Missing models or resources → descriptive error with instructions
- **Parsing errors**: Corrupted files → logged and reported
- **Analysis errors**: LLM failures → retry with exponential backoff (up to 3 attempts)
- **Output errors**: File write failures → attempt alternate directory

All errors are logged with timestamps, component context, and stack traces for debugging.

## Progress Indicators

The pipeline provides progress indicators for long-running operations:

```
Starting analysis pipeline for: policy.pdf
Domain: isms
Initializing pipeline resources...
Step 1/9: Parsing policy document...
Parsed 25 pages, 45000 characters
Step 2/9: Chunking policy text...
Created 89 chunks
Step 3/9: Embedding policy chunks...
Policy chunks embedded
Step 4/9: Retrieving relevant CSF subcategories...
Step 5/9: Executing two-stage gap analysis...
Gap analysis complete: 12 gaps identified
Step 6/9: Generating revised policy...
Revised policy generated: 12 revisions
Step 7/9: Generating implementation roadmap...
Roadmap generated: 5 immediate, 4 near-term, 3 medium-term actions
Step 8/9: Writing outputs...
Outputs written to: outputs/policy_20240115_143022
Step 9/9: Creating audit log...
Audit log created
Analysis pipeline complete in 245.67 seconds
```

## Integration with LangChain

The pipeline uses LangChain abstractions for:

- **Document loaders**: PyMuPDF and pdfplumber for PDF parsing
- **Text splitters**: RecursiveCharacterTextSplitter for chunking
- **Retrievers**: Hybrid retriever combining dense and sparse search
- **LLM chains**: Structured prompting for gap analysis and policy revision

## Testing

Integration tests are provided in `tests/integration/test_complete_pipeline.py`:

```bash
# Run integration tests
pytest tests/integration/test_complete_pipeline.py -v

# Run with specific markers
pytest tests/integration/test_complete_pipeline.py -m integration -v
```

## Example Script

A complete example script is provided in `examples/run_analysis.py`:

```bash
# Analyze policy with default settings
python examples/run_analysis.py path/to/policy.pdf

# Analyze with domain prioritization
python examples/run_analysis.py path/to/policy.pdf --domain isms

# Analyze with custom output directory
python examples/run_analysis.py path/to/policy.pdf --output-dir my_results

# Analyze with custom configuration
python examples/run_analysis.py path/to/policy.pdf --config config.yaml
```

## Requirements

**Validates: Requirements 7.9, 8.8**

- Requirement 7.9: LangChain orchestration for retrieval pipeline
- Requirement 8.8: LangChain orchestration for LLM interactions

## Architecture

The pipeline follows a layered architecture:

1. **Input Layer**: Document parsing and validation
2. **Processing Layer**: Chunking, embedding, and storage
3. **Retrieval Layer**: Hybrid search with reranking
4. **Analysis Layer**: Two-stage gap analysis (Stage A + Stage B)
5. **Generation Layer**: Policy revision and roadmap generation
6. **Output Layer**: File writing and audit logging

Each layer is isolated with clear interfaces, enabling independent testing and future enhancements.

## Future Enhancements

Potential improvements documented in the design:

- **Agentic RAG**: Multi-agent workflows with Planner, Retriever, and Critic agents
- **Iterative self-correction**: Feedback loops for improved accuracy
- **Enhanced precision**: Internal auditing patterns for quality assurance
- **Parallel processing**: Concurrent analysis of multiple policies
- **Streaming outputs**: Real-time progress updates and partial results

## License

See LICENSE file in project root.
