# API Documentation

This document provides API documentation for the Offline Policy Gap Analyzer, including usage examples for each component and a developer guide for extending the system.

## Table of Contents

- [Overview](#overview)
- [Core Components](#core-components)
- [Usage Examples](#usage-examples)
- [Developer Guide](#developer-guide)
- [Generating Full API Documentation](#generating-full-api-documentation)

## Overview

The Offline Policy Gap Analyzer is organized into modular components that can be used independently or as part of the complete analysis pipeline.

### Component Organization

```
ingestion/          # Document parsing and chunking
reference_builder/  # Reference catalog construction
retrieval/          # Hybrid search and retrieval
analysis/           # Gap analysis and LLM runtime
revision/           # Policy revision generation
reporting/          # Output generation and audit logging
orchestration/      # Pipeline orchestration
models/             # Data structures and schemas
utils/              # Configuration, logging, error handling
```

## Core Components

### Document Parser

**Module**: `ingestion.document_parser`

**Purpose**: Extract text from policy documents while preserving structure.

**Key Classes**:
- `DocumentParser`: Main parser class with multi-format support

**Example**:
```python
from ingestion.document_parser import DocumentParser

# Initialize parser
parser = DocumentParser()

# Parse PDF document
parsed_doc = parser.parse("policy.pdf", file_type="pdf")

# Access extracted text
print(parsed_doc.text)
print(f"Pages: {parsed_doc.page_count}")

# Access structure
for heading in parsed_doc.structure.headings:
    print(f"Level {heading.level}: {heading.text}")
```

### Text Chunker

**Module**: `ingestion.text_chunker`

**Purpose**: Segment documents into embedding-compatible chunks.

**Key Classes**:
- `TextChunker`: Intelligent chunking with overlap and boundary preservation

**Example**:
```python
from ingestion.text_chunker import TextChunker

# Initialize chunker
chunker = TextChunker(chunk_size=512, overlap=50)

# Chunk document
chunks = chunker.chunk(parsed_doc.text, parsed_doc.structure)

# Access chunks
for chunk in chunks:
    print(f"Chunk {chunk.chunk_id}: {len(chunk.text)} chars")
    print(f"Section: {chunk.section_title}")
```

### Embedding Engine

**Module**: `retrieval.embedding_engine`

**Purpose**: Generate dense vector embeddings for semantic search.

**Key Classes**:
- `EmbeddingEngine`: Local sentence transformer wrapper

**Example**:
```python
from retrieval.embedding_engine import EmbeddingEngine

# Initialize engine
engine = EmbeddingEngine(model_path="models/embeddings/all-MiniLM-L6-v2")

# Embed single text
embedding = engine.embed_text("This is a policy statement")
print(f"Embedding shape: {embedding.shape}")  # (384,)

# Embed batch
texts = [chunk.text for chunk in chunks]
embeddings = engine.embed_batch(texts)
print(f"Batch shape: {embeddings.shape}")  # (n_chunks, 384)

# Verify offline operation
assert engine.verify_offline()
```

### Vector Store

**Module**: `retrieval.vector_store`

**Purpose**: Store and retrieve embeddings with metadata.

**Key Classes**:
- `VectorStore`: ChromaDB wrapper for local persistence

**Example**:
```python
from retrieval.vector_store import VectorStore

# Initialize store
store = VectorStore(persist_directory=".chroma")

# Add embeddings
store.add_embeddings(
    embeddings=embeddings,
    metadata=[{"chunk_id": c.chunk_id, "source": c.source_file} for c in chunks],
    collection="policy_embeddings"
)

# Similarity search
query_embedding = engine.embed_text("risk management")
results = store.similarity_search(
    query_embedding=query_embedding,
    collection="policy_embeddings",
    top_k=5
)

# Access results
for result in results:
    print(f"Score: {result.score}, Text: {result.text[:100]}")
```

### Reference Catalog

**Module**: `reference_builder.reference_catalog`

**Purpose**: Structure CIS guide into queryable knowledge base.

**Key Classes**:
- `ReferenceCatalog`: CSF subcategory catalog with persistence

**Example**:
```python
from reference_builder.reference_catalog import ReferenceCatalog

# Build from CIS guide
catalog = ReferenceCatalog(cis_guide_path="context/CIS_Guide.pdf")

# Query by ID
subcategory = catalog.get_subcategory("GV.RM-01")
print(f"{subcategory.subcategory_id}: {subcategory.description}")

# Query by function
govern_subcategories = catalog.get_by_function("Govern")
print(f"Govern subcategories: {len(govern_subcategories)}")

# Query by domain
isms_subcategories = catalog.get_by_domain("isms")
print(f"ISMS-relevant subcategories: {len(isms_subcategories)}")

# Persist for reuse
catalog.persist("context/reference_catalog.json")

# Load from file
catalog2 = ReferenceCatalog.load("context/reference_catalog.json")
```

### Hybrid Retriever

**Module**: `retrieval.hybrid_retriever`

**Purpose**: Combine semantic and keyword search with reranking.

**Key Classes**:
- `HybridRetriever`: Orchestrates dense + sparse + reranking

**Example**:
```python
from retrieval.hybrid_retriever import HybridRetriever

# Initialize retriever
retriever = HybridRetriever(
    vector_store=store,
    embedding_engine=engine,
    catalog=catalog
)

# Retrieve relevant subcategories
query = "The organization shall maintain an asset inventory"
results = retriever.retrieve(query_text=query, top_k=5)

# Access results
for result in results:
    print(f"Subcategory: {result.subcategory_id}")
    print(f"Relevance: {result.relevance_score:.3f}")
    print(f"Method: {result.retrieval_method}")
    print(f"Evidence: {result.evidence_spans[0][:100]}")
```

### LLM Runtime

**Module**: `analysis.llm_runtime`

**Purpose**: Execute quantized language models locally.

**Key Classes**:
- `LLMRuntime`: Local LLM inference wrapper

**Example**:
```python
from analysis.llm_runtime import LLMRuntime

# Initialize runtime
llm = LLMRuntime(
    model_path="models/llm/qwen2.5-3b-instruct.gguf",
    backend="ollama"
)

# Generate text
prompt = "Explain the importance of supply chain risk management."
response = llm.generate(
    prompt=prompt,
    max_tokens=256,
    temperature=0.1
)
print(response)

# Generate structured output
schema = {
    "type": "object",
    "properties": {
        "status": {"type": "string", "enum": ["missing", "partially_covered"]},
        "explanation": {"type": "string"}
    },
    "required": ["status", "explanation"]
}

structured_response = llm.generate_structured(prompt=prompt, schema=schema)
print(structured_response)

# Check memory usage
memory_pct = llm.check_memory()
print(f"Memory usage: {memory_pct:.1f}%")
```

### Gap Analysis Engine

**Module**: `analysis.gap_analysis_engine`

**Purpose**: Execute two-stage gap analysis.

**Key Classes**:
- `GapAnalysisEngine`: Orchestrates Stage A and Stage B

**Example**:
```python
from analysis.gap_analysis_engine import GapAnalysisEngine

# Initialize engine
engine = GapAnalysisEngine(
    retriever=retriever,
    llm=llm,
    catalog=catalog
)

# Analyze policy
report = engine.analyze(
    policy_chunks=chunks,
    domain="isms"
)

# Access results
print(f"Total gaps: {len(report.gaps)}")
print(f"Covered subcategories: {len(report.covered_subcategories)}")

# Filter by severity
critical_gaps = [g for g in report.gaps if g.severity == "critical"]
print(f"Critical gaps: {len(critical_gaps)}")

# Access gap details
for gap in critical_gaps:
    print(f"\n{gap.subcategory_id}: {gap.subcategory_description}")
    print(f"Status: {gap.status}")
    print(f"Explanation: {gap.gap_explanation}")
    print(f"Suggested fix: {gap.suggested_fix}")
```

### Policy Revision Engine

**Module**: `revision.policy_revision_engine`

**Purpose**: Generate improved policy text addressing gaps.

**Key Classes**:
- `PolicyRevisionEngine`: Policy improvement generator

**Example**:
```python
from revision.policy_revision_engine import PolicyRevisionEngine

# Initialize engine
revision_engine = PolicyRevisionEngine(llm=llm, catalog=catalog)

# Generate revised policy
revised_policy = revision_engine.revise(
    original_policy=parsed_doc,
    gaps=report.gaps
)

# Access revisions
print(f"Total revisions: {len(revised_policy.revisions)}")

for revision in revised_policy.revisions:
    print(f"\nSection: {revision.section}")
    print(f"Addresses: {revision.gap_addressed}")
    print(f"Type: {revision.revision_type}")
    print(f"Original: {revision.original_clause[:100]}")
    print(f"Revised: {revision.revised_clause[:100]}")

# Access complete revised text
print(revised_policy.revised_text)

# Verify warning included
assert "IMPORTANT: This revised policy was generated by an AI system" in revised_policy.warning
```

### Roadmap Generator

**Module**: `reporting.roadmap_generator`

**Purpose**: Create prioritized implementation plans.

**Key Classes**:
- `RoadmapGenerator`: Implementation roadmap creator

**Example**:
```python
from reporting.roadmap_generator import RoadmapGenerator

# Initialize generator
roadmap_gen = RoadmapGenerator(catalog=catalog)

# Generate roadmap
roadmap = roadmap_gen.generate(gaps=report.gaps)

# Access actions by timeframe
print(f"Immediate actions: {len(roadmap.immediate_actions)}")
print(f"Near-term actions: {len(roadmap.near_term_actions)}")
print(f"Medium-term actions: {len(roadmap.medium_term_actions)}")

# Access action details
for action in roadmap.immediate_actions:
    print(f"\n{action.action_id}: {action.description}")
    print(f"Severity: {action.severity}, Effort: {action.effort}")
    print(f"CSF: {action.csf_subcategory}")
    print(f"Technical steps: {len(action.technical_steps)}")
    print(f"Administrative steps: {len(action.administrative_steps)}")
```

### Analysis Pipeline

**Module**: `orchestration.analysis_pipeline`

**Purpose**: Orchestrate complete analysis workflow.

**Key Classes**:
- `AnalysisPipeline`: End-to-end workflow manager

**Example**:
```python
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader.load("config.yaml")

# Initialize pipeline
pipeline = AnalysisPipeline(config)

# Execute complete analysis
result = pipeline.execute(
    policy_path="isms_policy.pdf",
    domain="isms"
)

# Access results
print(f"Analysis completed in {result.duration_seconds:.1f} seconds")
print(f"Output directory: {result.output_dir}")
print(f"Gaps found: {len(result.gap_report.gaps)}")

# Cleanup
pipeline.cleanup()
```


## Usage Examples

### Example 1: Analyze Single Policy

```python
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader.load("config.yaml")

# Initialize and execute
pipeline = AnalysisPipeline(config)
result = pipeline.execute("isms_policy.pdf", domain="isms")

# Print summary
print(f"Analysis complete: {result.output_dir}")
print(f"Gaps: {len(result.gap_report.gaps)}")
print(f"Critical: {sum(1 for g in result.gap_report.gaps if g.severity == 'critical')}")

pipeline.cleanup()
```

### Example 2: Batch Process Multiple Policies

```python
import glob
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader

config = ConfigLoader.load("config.yaml")
pipeline = AnalysisPipeline(config)

# Process all PDFs in directory
for policy_path in glob.glob("policies/*.pdf"):
    print(f"Analyzing {policy_path}...")
    result = pipeline.execute(policy_path)
    print(f"  Gaps found: {len(result.gap_report.gaps)}")
    print(f"  Output: {result.output_dir}")

pipeline.cleanup()
```

### Example 3: Custom Analysis with Component Access

```python
from ingestion.document_parser import DocumentParser
from ingestion.text_chunker import TextChunker
from retrieval.embedding_engine import EmbeddingEngine
from retrieval.vector_store import VectorStore
from reference_builder.reference_catalog import ReferenceCatalog
from retrieval.hybrid_retriever import HybridRetriever
from analysis.gap_analysis_engine import GapAnalysisEngine
from analysis.llm_runtime import LLMRuntime

# Parse document
parser = DocumentParser()
doc = parser.parse("policy.pdf", "pdf")

# Chunk text
chunker = TextChunker(chunk_size=512, overlap=50)
chunks = chunker.chunk(doc.text, doc.structure)

# Generate embeddings
engine = EmbeddingEngine("models/embeddings/all-MiniLM-L6-v2")
for chunk in chunks:
    chunk.embedding = engine.embed_text(chunk.text)

# Store embeddings
store = VectorStore(".chroma")
store.add_embeddings(
    embeddings=[c.embedding for c in chunks],
    metadata=[{"chunk_id": c.chunk_id} for c in chunks],
    collection="custom_analysis"
)

# Load catalog and retrieve
catalog = ReferenceCatalog.load("context/reference_catalog.json")
retriever = HybridRetriever(store, engine, catalog)

# Analyze gaps
llm = LLMRuntime("models/llm/qwen2.5-3b-instruct.gguf")
gap_engine = GapAnalysisEngine(retriever, llm, catalog)
report = gap_engine.analyze(chunks, domain="isms")

# Print results
for gap in report.gaps:
    print(f"{gap.subcategory_id}: {gap.severity} - {gap.gap_explanation[:100]}")
```

### Example 4: Validate JSON Outputs

```python
import json
from models.schemas import (
    validate_gap_analysis_report,
    validate_implementation_roadmap,
    get_schema_errors
)

# Load and validate gap report
with open("outputs/2024-03-15_14-30-00/gap_analysis_report.json") as f:
    report = json.load(f)

try:
    validate_gap_analysis_report(report)
    print("Gap report is valid!")
except Exception as e:
    errors = get_schema_errors(report, GAP_ANALYSIS_REPORT_SCHEMA)
    print(f"Validation errors: {errors}")

# Load and validate roadmap
with open("outputs/2024-03-15_14-30-00/implementation_roadmap.json") as f:
    roadmap = json.load(f)

try:
    validate_implementation_roadmap(roadmap)
    print("Roadmap is valid!")
except Exception as e:
    print(f"Validation error: {e}")
```

## Developer Guide

### Extending the System

#### Adding a New Document Format

1. **Create Parser Class**:
```python
# ingestion/my_format_parser.py
class MyFormatParser:
    def parse(self, file_path: str) -> ParsedDocument:
        # Implement parsing logic
        text = self._extract_text(file_path)
        structure = self._extract_structure(file_path)
        return ParsedDocument(
            text=text,
            file_path=file_path,
            file_type="myformat",
            page_count=self._count_pages(file_path),
            structure=structure,
            metadata={}
        )
```

2. **Integrate with DocumentParser**:
```python
# ingestion/document_parser.py
from ingestion.my_format_parser import MyFormatParser

class DocumentParser:
    def parse(self, file_path: str, file_type: str) -> ParsedDocument:
        if file_type == "myformat":
            parser = MyFormatParser()
            return parser.parse(file_path)
        # ... existing formats
```

3. **Add Tests**:
```python
# tests/unit/test_my_format_parser.py
def test_my_format_parsing():
    parser = MyFormatParser()
    doc = parser.parse("test.myformat")
    assert doc.text is not None
    assert doc.file_type == "myformat"
```

#### Adding a New LLM Backend

1. **Create Runtime Class**:
```python
# analysis/my_llm_runtime.py
class MyLLMRuntime:
    def __init__(self, model_path: str):
        self.model = self._load_model(model_path)
    
    def generate(self, prompt: str, max_tokens: int, temperature: float) -> str:
        # Implement generation logic
        return self.model.generate(prompt, max_tokens, temperature)
    
    def generate_structured(self, prompt: str, schema: Dict) -> Dict:
        # Implement structured generation
        response = self.generate(prompt, max_tokens=512, temperature=0.1)
        return json.loads(response)
```

2. **Integrate with LLMRuntime**:
```python
# analysis/llm_runtime.py
from analysis.my_llm_runtime import MyLLMRuntime

class LLMRuntime:
    def __init__(self, model_path: str, backend: str = "ollama"):
        if backend == "my_backend":
            self.runtime = MyLLMRuntime(model_path)
        # ... existing backends
```

#### Adding a New CSF Framework

1. **Create Framework Catalog**:
```python
# reference_builder/nist_privacy_catalog.py
class NISTPrivacyCatalog:
    def build_from_guide(self, guide_path: str) -> List[PrivacyControl]:
        # Parse NIST Privacy Framework guide
        controls = self._extract_controls(guide_path)
        return controls
    
    def persist(self, output_path: str):
        # Save to JSON
        with open(output_path, 'w') as f:
            json.dump(self.controls, f)
```

2. **Integrate with Analysis Engine**:
```python
# analysis/multi_framework_engine.py
class MultiFrameworkEngine:
    def __init__(self, frameworks: List[str]):
        self.catalogs = {}
        for framework in frameworks:
            if framework == "nist_csf":
                self.catalogs[framework] = ReferenceCatalog.load("...")
            elif framework == "nist_privacy":
                self.catalogs[framework] = NISTPrivacyCatalog.load("...")
    
    def analyze(self, policy_chunks: List[TextChunk]) -> Dict[str, GapAnalysisReport]:
        results = {}
        for framework, catalog in self.catalogs.items():
            results[framework] = self._analyze_framework(policy_chunks, catalog)
        return results
```

### Best Practices

#### Error Handling

Always use try-except blocks with specific exceptions:

```python
from utils.error_handler import (
    UnsupportedFormatError,
    OCRRequiredError,
    ParsingError,
    ModelNotFoundError
)

try:
    doc = parser.parse(file_path, file_type)
except UnsupportedFormatError as e:
    logger.error(f"Unsupported format: {e}")
    return None
except OCRRequiredError as e:
    logger.error(f"OCR required: {e}")
    return None
except ParsingError as e:
    logger.error(f"Parsing failed: {e}")
    return None
```

#### Logging

Use the centralized logger:

```python
from utils.logger import get_logger

logger = get_logger(__name__)

logger.info("Starting document parsing")
logger.warning("Memory usage at 85%")
logger.error("Failed to load model", exc_info=True)
```

#### Configuration

Load configuration using ConfigLoader:

```python
from utils.config_loader import ConfigLoader

config = ConfigLoader.load("config.yaml")
chunk_size = config.get("chunk_size", 512)  # Default to 512
temperature = config.get("temperature", 0.1)
```

#### Testing

Write both unit tests and property tests:

```python
# Unit test
def test_chunk_size_constraint():
    chunker = TextChunker(chunk_size=512, overlap=50)
    chunks = chunker.chunk("long text" * 1000, structure)
    for chunk in chunks:
        assert len(chunk.text.split()) <= 512

# Property test
from hypothesis import given, strategies as st

@given(text=st.text(min_size=100, max_size=10000))
def test_chunking_preserves_content(text):
    chunker = TextChunker(chunk_size=512, overlap=50)
    chunks = chunker.chunk(text, structure)
    reconstructed = "".join(c.text for c in chunks)
    assert text in reconstructed  # All content preserved
```

## Generating Full API Documentation

### Using Sphinx

1. **Install Sphinx**:
```bash
pip install sphinx sphinx-rtd-theme
```

2. **Initialize Sphinx**:
```bash
cd docs
sphinx-quickstart
```

3. **Configure Sphinx** (`docs/conf.py`):
```python
import os
import sys
sys.path.insert(0, os.path.abspath('..'))

extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
]

html_theme = 'sphinx_rtd_theme'
```

4. **Generate Documentation**:
```bash
sphinx-apidoc -o docs/source .
sphinx-build -b html docs/source docs/build
```

5. **View Documentation**:
```bash
open docs/build/index.html
```

### Using pdoc

1. **Install pdoc**:
```bash
pip install pdoc
```

2. **Generate Documentation**:
```bash
pdoc --html --output-dir docs/api .
```

3. **View Documentation**:
```bash
open docs/api/index.html
```

### Using pydoc

1. **Generate HTML Documentation**:
```bash
python -m pydoc -w ingestion.document_parser
python -m pydoc -w retrieval.hybrid_retriever
python -m pydoc -w analysis.gap_analysis_engine
```

2. **Start Documentation Server**:
```bash
python -m pydoc -p 8080
```

3. **View Documentation**:
```
http://localhost:8080
```

## See Also

- [README.md](../README.md) - Quick start guide
- [EXAMPLES.md](EXAMPLES.md) - Usage examples
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
- [SCHEMAS.md](SCHEMAS.md) - JSON schema documentation
- [Source Code](../) - Complete implementation
