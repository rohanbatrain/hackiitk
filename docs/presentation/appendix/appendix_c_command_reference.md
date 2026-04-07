# Appendix C – Practical Command Reference

## Primary analyzer commands

```bash
python -m cli.main --policy-path /absolute/path/to/policy.pdf
python -m cli.main --policy-path /absolute/path/to/policy.pdf --domain isms
python -m cli.main --policy-path /absolute/path/to/policy.pdf --config /absolute/path/to/config.yaml --output-dir /absolute/path/to/output
```

## Package-installed equivalent

```bash
policy-analyzer --policy-path /absolute/path/to/policy.pdf
```

## Setup/model/catalog helpers

```bash
python scripts/setup_models.py --all
python scripts/download_models.py --all
python scripts/build_catalog.py --input ./data/cis_guide.pdf --output ./reference_catalog.json
```

## Extreme test CLI (actual implemented argument style)

```bash
python -m tests.extreme.cli
python -m tests.extreme.cli --categories stress chaos
python -m tests.extreme.cli --verbose --fail-fast
```

## General pytest paths seen in workflows

```bash
python -m pytest tests/ -v --tb=short
python -m pytest tests/integration/ -v --tb=short
python -m pytest tests/unit/ -v --tb=short
```
