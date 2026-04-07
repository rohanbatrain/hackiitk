# 01 – Project Summary

## Project name

Offline Policy Gap Analyzer.

## Primary objective

Analyze an organization’s policy document against NIST CSF 2.0 subcategories, then produce:

- Gap analysis report
- Revised policy draft text
- Prioritized implementation roadmap
- Immutable-style audit log entries

## Core value proposition

- Local-first analysis with local embedding + local LLM runtime
- Structured two-stage gap analysis design:
  - Stage A deterministic scoring/classification
  - Stage B constrained structured LLM reasoning
- Outputs suitable for governance/compliance workflows

## High-level capabilities found in code

- Multi-format ingestion (`.pdf`, `.docx`, `.txt`, `.md`)
- Chunking and embeddings for retrieval
- Hybrid retrieval (dense + sparse + optional rerank)
- Domain-prioritized CSF mapping (`isms`, `risk_management`, `patch_management`, `data_privacy`)
- Gap detection and severity assignment
- Policy revision drafting
- Implementation roadmap generation
- Markdown + JSON output artifacts
- Audit log generation and file hash traceability

## Runtime shape (current main path)

Main runtime path is:

- CLI: `cli/main.py`
- Pipeline orchestrator: `orchestration/analysis_pipeline.py`

## Maturity reality

The codebase includes a strong core implementation, but also signs of mixed maturity:

- Some modules are placeholder/stub style (`analysis/cli.py`, parts of `reference_builder/cis_parser.py`)
- Some docs and workflows reference CLI modes that do not match current extreme-test CLI implementation
- Test/docs quality appears broad but heterogeneous
