# 📋 Policy Analyzer Cheat Sheet

## Quick Start
```bash
source venv/bin/activate
./pa --policy-path policy.pdf --domain isms
```

## Common Commands

| Command | Description |
|---------|-------------|
| `./pa --help` | Show help |
| `./pa --version` | Show version |
| `./pa --policy-path FILE` | Analyze policy |
| `./pa --policy-path FILE --domain DOMAIN` | Analyze with specific domain |
| `./pa --policy-path FILE --output-dir DIR` | Custom output location |
| `./pa --policy-path FILE --model MODEL` | Use specific model |
| `./pa --policy-path FILE --verbose` | Verbose output |

## Domains
- `isms` - Information Security
- `risk_management` - Risk Management
- `patch_management` - Patch Management
- `data_privacy` - Data Privacy

## File Formats
- `.pdf` - PDF documents
- `.docx` - Word documents
- `.txt` - Text files
- `.md` - Markdown files

## Your Models
- `qwen2.5:3b-instruct` (default)
- `phi3.5:3.8b`

## Examples

### Basic Analysis
```bash
./pa --policy-path isms_policy.pdf --domain isms
```

### Test Policies
```bash
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
./pa --policy-path tests/fixtures/dummy_policies/privacy_policy.md --domain data_privacy
./pa --policy-path tests/fixtures/dummy_policies/risk_policy.md --domain risk_management
```

### Custom Output
```bash
./pa --policy-path policy.pdf --output-dir ./results
```

### Different Model
```bash
./pa --policy-path policy.pdf --model phi3.5:3.8b
```

## Outputs
All results saved to: `outputs/TIMESTAMP/`
- `gap_analysis.json` - Gap report
- `revised_policy.md` - Improved policy
- `implementation_roadmap.md` - Action plan
- `audit_log.json` - Audit trail

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Command not found | `chmod +x pa` |
| Module not found | `source venv/bin/activate` |
| Warnings showing | Use `./pa` not `python -m cli.main` |
| Ollama error | Check `ollama list` |

---

**Quick tip:** Always activate venv first: `source venv/bin/activate`
