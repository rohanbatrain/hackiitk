# Simple Start Guide

## Step 1: Run Quick Setup

```bash
./quick_setup.sh
```

Wait for it to complete (2-3 minutes).

## Step 2: Activate Virtual Environment

```bash
source venv/bin/activate
```

You should see `(venv)` at the start of your prompt.

## Step 3: Test It

```bash
python -m cli.main --help
```

You should see the help message.

## Step 4: Try It

```bash
python -m cli.main analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms --dry-run
```

## Daily Usage

Every time you want to use the tool:

```bash
# 1. Activate
source venv/bin/activate

# 2. Use it
python -m cli.main analyze your-policy.pdf --domain isms

# 3. Deactivate when done
deactivate
```

## Commands

All commands use: `python -m cli.main [command] [options]`

```bash
# Get help
python -m cli.main --help

# Analyze
python -m cli.main analyze policy.pdf --domain isms

# Dry run
python -m cli.main analyze policy.pdf --domain isms --dry-run

# List models
python -m cli.main list-models

# System info
python -m cli.main info
```

## Troubleshooting

### "No module named 'click'"

```bash
source venv/bin/activate
pip install click rich tabulate
```

### "Command not found"

Make sure you activated:
```bash
source venv/bin/activate
```

### Start fresh

```bash
rm -rf venv
./quick_setup.sh
```

---

**That's it!** Just activate and use `python -m cli.main` for all commands.
