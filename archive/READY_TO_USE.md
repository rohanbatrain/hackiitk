# ✅ Your Policy Analyzer is Ready!

## Setup Complete ✓

Your Offline Policy Gap Analyzer is fully installed and configured:
- ✓ Virtual environment created at `venv/`
- ✓ All dependencies installed
- ✓ Package installed (v0.1.0)
- ✓ Wrapper script configured (`pa`)
- ✓ Ollama models available

## How to Use

### Step 1: Activate Virtual Environment
```bash
source venv/bin/activate
```

### Step 2: Run Analysis
```bash
./pa --policy-path your_policy.pdf --domain isms
```

That's it! 🎉

## Real Examples

### Example 1: Analyze ISMS Policy
```bash
./pa --policy-path tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

### Example 2: Analyze Privacy Policy
```bash
./pa --policy-path tests/fixtures/dummy_policies/privacy_policy.md --domain data_privacy
```

### Example 3: Analyze Risk Policy
```bash
./pa --policy-path tests/fixtures/dummy_policies/risk_policy.md --domain risk_management
```

### Example 4: Custom Output Directory
```bash
./pa --policy-path my_policy.pdf --output-dir ./my_analysis
```

### Example 5: Use Specific Model
```bash
./pa --policy-path policy.pdf --model phi3.5:3.8b
```

## What You'll Get

After running an analysis, you'll get:

```
outputs/
└── 2026-03-29_14-30-45/
    ├── gap_analysis.json          # Detailed gap report
    ├── revised_policy.md           # Policy with improvements
    ├── implementation_roadmap.md   # Step-by-step action plan
    └── audit_log.json             # Complete audit trail
```

## Available Commands

### Get Help
```bash
./pa --help
```

### Check Version
```bash
./pa --version
```

### Verbose Mode (for debugging)
```bash
./pa --policy-path policy.pdf --verbose
```

## Supported Formats

| Format | Extension | Notes |
|--------|-----------|-------|
| PDF | `.pdf` | Text-based only (no OCR) |
| Word | `.docx` | Microsoft Word documents |
| Text | `.txt` | Plain text files |
| Markdown | `.md` | Markdown files |

## Policy Domains

| Domain | Use For |
|--------|---------|
| `isms` | Information Security Management System policies |
| `risk_management` | Risk management policies |
| `patch_management` | Patch and vulnerability management |
| `data_privacy` | Privacy and data protection policies |

Leave blank to auto-detect!

## Your Ollama Models

You have these models ready to use:
- **qwen2.5:3b-instruct** (1.9 GB) - Default, fast and efficient
- **phi3.5:3.8b** (2.2 GB) - Alternative model

To use a specific model:
```bash
./pa --policy-path policy.pdf --model phi3.5:3.8b
```

## Typical Analysis Output

```
🔍 Analyzing policy: isms_policy.pdf
📂 Domain: isms

[████████████████████████████] 100% - Complete

============================================================
✅ Analysis Complete!
============================================================

📊 Summary:
   • Gaps identified: 12
   • Critical gaps: 2
   • High severity gaps: 4
   • Medium severity gaps: 5
   • Low severity gaps: 1

📁 Outputs generated:
   • Gap analysis report: outputs/2026-03-29_14-30-45/gap_analysis.json
   • Revised policy: outputs/2026-03-29_14-30-45/revised_policy.md
   • Implementation roadmap: outputs/2026-03-29_14-30-45/implementation_roadmap.md
   • Audit log: outputs/2026-03-29_14-30-45/audit_log.json

⏱️  Analysis duration: 45.3 seconds
```

## Tips

1. **First time?** Try analyzing one of the test policies in `tests/fixtures/dummy_policies/`
2. **Slow analysis?** The first run downloads models and may take longer
3. **Need more detail?** Use `--verbose` flag
4. **Custom config?** Create a YAML config and use `--config path/to/config.yaml`

## Troubleshooting

### "command not found: pa"
```bash
chmod +x pa
```

### "No module named 'cli'"
```bash
source venv/bin/activate
```

### Warnings about Pydantic or sys.modules
These are suppressed by the `pa` wrapper. If you see them, you're not using the wrapper.

### Ollama connection issues
Make sure Ollama is running:
```bash
ollama list
```

## Next Steps

1. **Try it out** with a test policy
2. **Analyze your own** policy documents
3. **Review the outputs** to understand gaps
4. **Implement fixes** using the roadmap

## Need More Info?

- Full CLI guide: `docs/CLI_GUIDE.md`
- Test data: `tests/fixtures/TESTING_GUIDE.md`
- Configuration: `utils/config_loader.py`

---

**You're all set!** Start analyzing policies now. 🚀
