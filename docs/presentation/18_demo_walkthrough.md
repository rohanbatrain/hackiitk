# 18 – Demo Walkthrough

## Demo objective

Show end-to-end policy analysis and explain generated artifacts.

## Suggested demo script

1. Show repository root and key folders (`cli`, `orchestration`, `analysis`, `reporting`).
2. Show sample policy input from `tests/fixtures/dummy_policies/`.
3. Run:
   - `python -m cli.main --policy-path <sample> --domain isms --verbose`
4. Show generated output directory and files.
5. Open `gap_analysis_report.md` and explain gap severity/status fields.
6. Open `revised_policy.md` and point out mandatory human-review warning.
7. Open `implementation_roadmap.md` and explain timeframe prioritization.
8. Show latest audit log in `audit_logs/` and explain traceability fields.

## Demo talking points

- Two-stage safety architecture (deterministic first, constrained LLM second)
- Offline-first execution boundary
- Why outputs are draft recommendations, not automatic compliance certification
