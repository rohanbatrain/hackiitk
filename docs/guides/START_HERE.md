# 🚀 Policy Analyzer - Start Here

## Quick Setup (3 Steps)

### 1. Run Setup Script
```bash
./setup.sh
```

This installs everything you need (takes 5-10 minutes).

### 2. Activate Environment
```bash
source venv311/bin/activate
```

### 3. Test It
```bash
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

## What This Tool Does

Analyzes your policy documents against **NIST CSF 2.0** (49 security controls) to find compliance gaps.

```
Your Policy → Analyzer → Gap Report + Recommendations
```

## Quick Commands

```bash
# Analyze a policy
./pa --policy-path your_policy.pdf --domain isms

# Show help
./pa --help

# Check version
./pa --version
```

## Available Domains

- `isms` - Information Security
- `risk_management` - Risk Management
- `patch_management` - Patch Management
- `data_privacy` - Data Privacy

## Output

Results saved to `outputs/TIMESTAMP/`:
- Gap analysis report (JSON)
- Revised policy (Markdown)
- Implementation roadmap
- Audit log

## Need Help?

- Full guide: `README.md`
- Test commands: `RUN_THIS.md`
- Catalog info: `CATALOG_EXPLANATION.md`

## Troubleshooting

If setup fails:
```bash
source venv311/bin/activate
pip install torch sentence-transformers chromadb langchain pypdf2 pyyaml click rich
pip install -e .
```

That's it! 🎉
