# 05 – How It Works End to End

## End-to-end execution sequence

1. User invokes CLI (`policy-analyzer --policy-path ...`).
2. CLI validates file path/extension and optional config path.
3. CLI loads config into `PipelineConfig` (defaults or file-derived).
4. `AnalysisPipeline.execute()` initializes resources (if not already initialized):
   - parser, chunker, catalog, embedding engine, vector store, reranker, hybrid retriever, LLM runtime, analysis engines, reporting engines, audit logger
5. Policy is parsed into `ParsedDocument`.
6. Text is chunked into `TextChunk` list.
7. Chunks are embedded and stored in vector store (`policy` collection).
8. Gap analysis runs:
   - DomainMapper selects/prioritizes subcategories
   - Stage A assesses each subcategory deterministically
   - Stage B reasons on non-covered outcomes
9. Policy revision engine drafts revised policy text and revision records.
10. Roadmap generator creates action plan by timeframe.
11. Pipeline writes artifacts to timestamped output directory.
12. Audit logger writes audit record under `audit_logs/`.
13. CLI prints summary and output locations.

## Output artifact set (primary)

- `gap_analysis_report.md`
- `gap_analysis_report.json`
- `revised_policy.md`
- `implementation_roadmap.md`
- `implementation_roadmap.json`
- plus audit JSON in configured audit directory

## Determinism and variability

- Stage A is deterministic scoring logic.
- Stage B and revision generation use LLMs with low temperature defaults (still not perfectly deterministic across all backends/models).
