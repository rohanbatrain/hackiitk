# 07 – How to Run

## Primary command (actual main CLI)

```bash
python -m cli.main --policy-path /absolute/path/to/policy.pdf
```

Equivalent if installed as package:

```bash
policy-analyzer --policy-path /absolute/path/to/policy.pdf
```

## Common options

- `--config PATH` – config file path
- `--domain {isms,risk_management,patch_management,data_privacy}`
- `--output-dir PATH`
- `--model NAME` – overrides `config.model_name`
- `--verbose`

## Wrapper script

Repository includes `./pa` wrapper that tries to activate local venv and runs:

```bash
python -m cli.main "$@"
```

## Output location

Pipeline creates output subdirectory:

- `<output-dir or config.output_dir>/<policy_stem>_<timestamp>/`

containing core output files.

## Exit behavior

- `0` success
- `1` general failure
- `130` interrupt (SIGINT / Ctrl+C)
