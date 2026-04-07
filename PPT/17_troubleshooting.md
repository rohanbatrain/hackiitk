# 17 – Troubleshooting

## Common failure: missing runtime dependencies

Symptom:

- `No module named pytest` (or other module import failures)

Action:

- Install dependencies in active environment:
  - `pip install -r requirements.txt`

## Common failure: model path not found

Symptom:

- embedding/LLM initialization failures from missing local model path

Action:

- run setup/download scripts:
  - `python scripts/setup_models.py --all`

## Common failure: scanned PDF rejected

Symptom:

- OCR-required parsing error

Action:

- convert PDF to text-based (OCR externally) or use DOCX/TXT/MD

## Common failure: catalog missing

Symptom:

- catalog load/build errors

Action:

- ensure `data/reference_catalog.json` exists or build catalog with script

## Common failure: command mismatch from docs

Symptom:

- copied command from old docs fails (especially test CLI syntax)

Action:

- use current implemented command paths from code (`cli/main.py`, `tests/extreme/cli.py` argument definitions)

## Sandbox note for this analysis run

In this sandbox clone, baseline full pytest run via system Python failed because `pytest` is not installed in that runtime, and bundled venv scripts appear copied from a different machine path (invalid shebangs). This is an environment artifact, not necessarily a repository logic defect.
