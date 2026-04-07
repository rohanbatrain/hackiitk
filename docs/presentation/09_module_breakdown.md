# 09 – Module Breakdown

## cli/

- `main.py`: current argparse-based CLI, path validation, config load, pipeline execution
- `enhanced_commands.py`: additional click-based commands (watch, validate-config, completion)
- `completion.py`: bash/zsh completion script generation

## orchestration/

- `analysis_pipeline.py`: central orchestrator
  - resource init
  - parse/chunk/embed
  - gap analysis
  - revision + roadmap generation
  - output writing + audit logging

## ingestion/

- `document_parser.py`: format parsing + structure extraction
- `text_chunker.py`: recursive split with overlap and metadata

## reference_builder/

- `reference_catalog.py`: CSF subcategory catalog load/persist/getters
- `cis_parser.py`: helper/parser utilities with placeholder extraction implementation

## retrieval/

- `embedding_engine.py`: local sentence-transformers embeddings
- `vector_store.py`: ChromaDB persistence/search
- `sparse_retriever.py`: BM25 indexing/retrieval
- `reranker.py`: cross-encoder reranking
- `hybrid_retriever.py`: orchestrates dense+sparse+rereank fusion

## analysis/

- `llm_runtime.py`: local LLM abstraction and structured generation
- `stage_a_detector.py`: deterministic scoring + classification
- `stage_b_reasoner.py`: constrained JSON-schema-driven LLM reasoning
- `gap_analysis_engine.py`: two-stage analysis orchestration
- `domain_mapper.py`: domain-prioritized CSF selection
- `cli.py`: placeholder legacy CLI (not primary path)

## revision/

- `policy_revision_engine.py`: creates revisions and appends mandatory warning

## reporting/

- `gap_report_generator.py`: markdown/json gap report generation + schema validation
- `roadmap_generator.py`: roadmap generation and serialization
- `output_manager.py`: generalized output writer (partially parallel to pipeline output code)
- `audit_logger.py`: append-style audit log writer

## models/

- `domain.py`: core dataclasses
- `schemas.py`: JSON schemas + validators

## utils/

- `config_loader.py`: config defaults + schema validation
- `error_handler.py`: custom exceptions, retry/degrade utilities
- `logger.py`: structured logging helpers
- `progress.py`: progress bars and step tracking
