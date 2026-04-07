# Appendix A – Code Reference Map

Primary runtime chain:

- `cli/main.py`
- `orchestration/analysis_pipeline.py`
- `ingestion/document_parser.py`
- `ingestion/text_chunker.py`
- `retrieval/*`
- `analysis/stage_a_detector.py`
- `analysis/stage_b_reasoner.py`
- `analysis/gap_analysis_engine.py`
- `revision/policy_revision_engine.py`
- `reporting/gap_report_generator.py`
- `reporting/roadmap_generator.py`
- `reporting/audit_logger.py`

Core contracts:

- `models/domain.py`
- `models/schemas.py`

Config/deps:

- `requirements.txt`
- `constraints.txt`
- `pyproject.toml`
- `config.example.yaml`
- `config.yaml`
- `utils/config_loader.py`

Tests/CI:

- `tests/`
- `.github/workflows/`
