# 04 – Architecture

## Architectural style

Layered pipeline with typed domain models and file-based artifacts:

1. Ingestion layer
2. Reference/catalog layer
3. Retrieval + embedding layer
4. Two-stage analysis layer
5. Revision and roadmap generation layer
6. Reporting and audit layer

## Major runtime components and responsibilities

- `DocumentParser` (`ingestion/document_parser.py`)
  - Parses PDF/DOCX/TXT/MD
  - Enforces max page limit
  - Rejects scanned PDFs without text layer

- `TextChunker` (`ingestion/text_chunker.py`)
  - Splits text into overlapping chunks
  - Attaches positional metadata and section hints

- `ReferenceCatalog` (`reference_builder/reference_catalog.py`)
  - Loads/persists CSF subcategory catalog
  - Current implementation ultimately relies on hardcoded NIST CSF subcategories

- `EmbeddingEngine` (`retrieval/embedding_engine.py`)
  - Local sentence-transformers embedding generation

- `VectorStore` (`retrieval/vector_store.py`)
  - ChromaDB persistent vector collections

- `HybridRetriever` (`retrieval/hybrid_retriever.py`)
  - Dense + sparse + optional reranking orchestration

- `LLMRuntime` (`analysis/llm_runtime.py`)
  - Local LLM generation through `ollama` or `llama-cpp`
  - Structured JSON generation helper with retry

- `StageADetector` (`analysis/stage_a_detector.py`)
  - Deterministic coverage scoring and classification

- `StageBReasoner` (`analysis/stage_b_reasoner.py`)
  - Constrained prompt-based LLM reasoning for missing/partial/ambiguous cases

- `GapAnalysisEngine` (`analysis/gap_analysis_engine.py`)
  - Orchestrates Stage A + Stage B and assembles `GapAnalysisReport`

- `PolicyRevisionEngine` (`revision/policy_revision_engine.py`)
  - Drafts clause injection/strengthening revisions

- `RoadmapGenerator` (`reporting/roadmap_generator.py`)
  - Produces prioritized action items by timeframe

- `GapReportGenerator` (`reporting/gap_report_generator.py`)
  - Produces markdown/json gap reports

- `AuditLogger` (`reporting/audit_logger.py`)
  - Writes timestamped audit log JSON with file hash and run metadata

- `AnalysisPipeline` (`orchestration/analysis_pipeline.py`)
  - End-to-end orchestration and output writing

## Control flow (actual main path)

CLI `cli/main.py` creates `PipelineConfig`, instantiates `AnalysisPipeline`, and calls `execute(policy_path, domain, output_dir)`.

## Notable design strengths

- Clear typed domain contracts in `models/domain.py`
- Two-stage analysis structure to constrain LLM use
- Artifact outputs in both human and machine-readable formats
- Audit metadata and input hashing for traceability

## Notable weak points

- Retrieval/Stage A coupling currently contains placeholder behavior (policy chunk linkage simplification)
- Catalog build path references CIS parsing but effective extraction is hardcoded catalog list
- Configuration model mismatch between nested `config.yaml` and flat `PipelineConfig`
- Duplicate/stale docs and legacy CLI surfaces increase operational confusion
