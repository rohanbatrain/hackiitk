# 10 – Data Flow

## Primary data objects

- `ParsedDocument`
- `DocumentStructure` + `Section`/`Heading`
- `TextChunk`
- `CoverageAssessment`
- `GapDetail`
- `GapAnalysisReport`
- `RevisedPolicy`
- `ImplementationRoadmap`
- `AuditLogEntry`

## Flow chain

1. File bytes -> parsed text/structure (`ParsedDocument`)
2. Text -> chunk list (`TextChunk[]`)
3. Chunks -> embeddings -> vector store (`policy` collection)
4. Catalog subcategories -> retrieval/scoring context
5. Stage A -> `CoverageAssessment[]`
6. Stage B -> `GapDetail[]`
7. Report assembly -> `GapAnalysisReport`
8. Revision generation -> `RevisedPolicy`
9. Roadmap generation -> `ImplementationRoadmap`
10. Serialization -> markdown/json output files + audit JSON

## Intermediate persistence

- Vector store persistence directory (Chroma)
- Catalog JSON persistence (`data/reference_catalog.json` or configured)
- Output run directory artifacts
- Audit logs in `audit_logs/`
