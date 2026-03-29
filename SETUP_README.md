# Setup Instructions

## Current Status

✅ Cleaned up - all old scripts archived
✅ One setup script: `setup.sh`
✅ Simple documentation structure

## Files You Need

### Main Files
- `setup.sh` - Complete setup script (run this)
- `pa` - CLI wrapper
- `README.md` - Full documentation
- `START_HERE.md` - Quick start guide
- `RUN_THIS.md` - Test commands

### Documentation
- `CATALOG_EXPLANATION.md` - Why catalog is correct (49 NIST CSF controls)

### Archive
- `archive/` - Old scripts and docs (kept for reference)

## Run Setup Now

```bash
./setup.sh
```

This will:
1. Check/install Python 3.11
2. Create venv311
3. Install all dependencies
4. Download embedding models
5. Verify installation

## After Setup

```bash
# Activate
source venv311/bin/activate

# Test
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms

# Analyze your policy
./pa --policy-path data/policies/Access\ Control\ Policy.md --domain isms
```

## That's It!

Everything is in one script now. No more confusion with 100 files.
