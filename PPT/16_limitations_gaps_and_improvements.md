# 16 – Limitations, Gaps, and Improvements

## Real limitations observed

1. `analysis/cli.py` is placeholder and not production execution path.
2. `reference_builder/cis_parser.py` includes placeholder extraction logic.
3. `ReferenceCatalog.build_from_cis_guide()` currently relies on hardcoded subcategory set rather than full dynamic parsing.
4. Stage A relevant-chunk mapping uses placeholder fallback behavior.
5. Config ecosystem is inconsistent (nested vs flat schemas).
6. Docs/workflows include command variants that do not align with current extreme-test CLI implementation.
7. Some repository claims around extensive completion appear broader than directly verified core runtime paths.

## Technical debt indicators

- Duplicate/overlapping command surfaces (argparse + click + legacy module CLI)
- Drift between README/docs and executable code
- Duplicate helper methods in some modules (e.g., repeated helper blocks)

## Improvement opportunities

- Unify config schema and loader compatibility
- Remove/retire legacy placeholder CLI or clearly isolate it
- Implement full CIS guide parser and remove hardcoded fallback dependency
- Fix Stage A evidence-to-policy chunk linkage with explicit chunk IDs
- Tighten offline verification tests in CI with network-disabled harness
- Consolidate docs to one authoritative operations manual
