# 12 – Policy Gap Analysis Logic

## Stage A (deterministic)

Inputs:

- `policy_chunks`
- one `CSFSubcategory`

Scoring components:

- lexical keyword overlap
- semantic embedding similarity
- section-title heuristic match

Combined confidence:

- weighted sum (lexical/semantic/section)

Classification thresholds in code (`StageADetector`):

- covered: `confidence > 0.65`
- partially_covered: `confidence >= 0.45`
- missing: `confidence < 0.25`
- ambiguous: otherwise

## Stage B (constrained LLM)

Triggered for statuses in:

- `ambiguous`, `missing`, `partially_covered`

Prompt contains:

- subcategory metadata + requirement text
- limited policy section context
- Stage A evidence and scores
- strict JSON shape requirements

Output object becomes `GapDetail` after schema validation.

## Severity assignment

`GapAnalysisEngine` maps subcategory priority directly:

- critical/high/medium/low -> same severity label

## Known implementation caveat

`StageADetector._get_relevant_chunks()` currently falls back to first policy chunks (placeholder behavior), reducing true evidence localization precision.
