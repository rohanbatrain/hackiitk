# 🚀 Quick Start Demo - Offline Policy Gap Analyzer

## Your System is Ready!

You have successfully validated the Offline Policy Gap Analyzer with:
- ✅ 439 tests passing
- ✅ LLM models loaded (qwen2.5:3b-instruct, phi3.5:3.8b)
- ✅ All core components operational

## How to Use It Right Now

### Option 1: Command Line Interface (Easiest)

```bash
# Analyze a policy document
python -m cli.main analyze path/to/your/policy.pdf --domain isms

# With custom output directory
python -m cli.main analyze policy.pdf --domain risk_management --output ./my_results

# With custom configuration
python -m cli.main analyze policy.pdf --config my_config.yaml

# See all options
python -m cli.main --help
```

**Available domains:**
- `isms` - Information Security Management System
- `risk_management` - Risk Management policies
- `patch_management` - Patch Management policies
- `data_privacy` - Data Privacy policies

### Option 2: Python API (Most Flexible)

```python
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader
from pathlib import Path

# Load default configuration
config = ConfigLoader.get_default_config()

# Or load custom configuration
# config = ConfigLoader.load("my_config.yaml")

# Create analysis pipeline
pipeline = AnalysisPipeline(config)

# Run analysis on a policy document
result = pipeline.execute(
    policy_path="path/to/policy.pdf",
    domain="isms"  # Optional: focuses analysis on relevant CSF subcategories
)

print(f"Analysis complete! Results saved to: {result.output_dir}")
print(f"Found {len(result.gaps)} gaps")
print(f"Generated {len(result.roadmap.immediate_actions)} immediate actions")
```

### Option 3: Example Script (Pre-configured)

```bash
# Use the provided example script
python examples/run_analysis.py path/to/policy.pdf --domain isms
```

## What You'll Get

After running analysis, you'll find these files in a timestamped output directory:

```
outputs/analysis_2024-03-28_17-30-45/
├── gap_analysis_report.md          # Human-readable gap analysis
├── gap_analysis_report.json        # Machine-readable gap data
├── revised_policy.md                # Improved policy text
├── implementation_roadmap.md        # Prioritized action plan
├── implementation_roadmap.json      # Machine-readable roadmap
├── audit_log.json                   # Immutable compliance log
└── analysis.log                     # Detailed operation log
```

## Example Outputs

### Gap Analysis Report (gap_analysis_report.md)

```markdown
# NIST CSF 2.0 Gap Analysis Report

**Analysis Date:** 2024-03-28 17:30:45
**Policy Analyzed:** corporate_security_policy.pdf
**Domain Focus:** Information Security Management System (ISMS)
**Model Used:** qwen2.5:3b-instruct

## Executive Summary

- **Total Gaps Identified:** 12
- **Critical Severity:** 3
- **High Severity:** 5
- **Medium Severity:** 4

## Identified Gaps

### Gap 1: GV.RM-01 - Risk Management Strategy [CRITICAL]

**Status:** Missing
**CSF Requirement:** Organizational risk management strategy is established, communicated, and maintained

**Gap Explanation:** The policy does not define a formal risk management strategy or process for identifying, assessing, and mitigating cybersecurity risks.

**Evidence:** No mention of risk assessment, risk appetite, or risk management processes found in the policy.

**Suggested Fix:** Add a dedicated Risk Management section that:
- Defines the organization's risk appetite and tolerance
- Establishes a risk assessment methodology
- Outlines risk treatment options (accept, mitigate, transfer, avoid)
- Specifies risk review frequency and escalation procedures

---

[... more gaps ...]
```

### Implementation Roadmap (implementation_roadmap.md)

```markdown
# Implementation Roadmap

## Immediate Actions (0-3 months) - Critical/High Priority

### Action 1: Establish Risk Management Framework
**CSF Subcategory:** GV.RM-01
**Severity:** Critical
**Effort:** High
**Policy Section:** Risk Management (new section)

**Technical Steps:**
1. Deploy risk assessment tool or platform
2. Configure risk scoring methodology
3. Integrate with asset inventory systems

**Administrative Steps:**
1. Draft risk management policy
2. Define risk appetite statement
3. Establish risk review committee
4. Train staff on risk assessment procedures

**Physical Steps:**
1. None required

---

[... more actions ...]
```

## Configuration Options

Create a `config.yaml` file to customize behavior:

```yaml
# Chunking parameters
chunking:
  chunk_size: 512        # Maximum tokens per chunk
  overlap: 50            # Token overlap between chunks

# Retrieval parameters
retrieval:
  top_k: 5              # Number of results to retrieve
  use_reranking: true   # Use cross-encoder reranking

# LLM parameters
llm:
  model: "qwen2.5:3b-instruct"  # Ollama model name
  backend: "ollama"              # or "llama-cpp"
  temperature: 0.1               # Low for deterministic output
  max_tokens: 512                # Maximum generation length

# Analysis parameters
analysis:
  severity_thresholds:
    critical: 0.9
    high: 0.7
    medium: 0.5
    low: 0.3

# Output parameters
output:
  formats: ["markdown", "json"]
  include_metadata: true
  timestamp_format: "%Y-%m-%d_%H-%M-%S"
```

## Testing with Dummy Policies

The system includes dummy policies for testing:

```bash
# Test with ISMS policy
python -m cli.main analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms

# Test with Risk Management policy
python -m cli.main analyze tests/fixtures/dummy_policies/risk_policy.md --domain risk_management

# Test with Patch Management policy
python -m cli.main analyze tests/fixtures/dummy_policies/patch_policy.md --domain patch_management

# Test with Data Privacy policy
python -m cli.main analyze tests/fixtures/dummy_policies/privacy_policy.md --domain data_privacy
```

## Troubleshooting

### Issue: "Model not found"

```bash
# Download the model
ollama pull qwen2.5:3b-instruct

# Verify it's available
ollama list
```

### Issue: "Ollama not running"

```bash
# Start Ollama service
ollama serve

# Or on macOS, Ollama should start automatically
```

### Issue: "Out of memory"

```yaml
# Use a smaller model in config.yaml
llm:
  model: "qwen2.5:3b-instruct"  # Smaller model (1.9 GB)
  # Instead of: "qwen3:8b" (larger model)
```

### Issue: "Parsing failed"

- Ensure PDF is text-based (not scanned image)
- Check file is not corrupted
- Try with DOCX or TXT format instead

## Performance Tips

1. **Use smaller models for faster analysis:**
   - qwen2.5:3b-instruct (1.9 GB) - Fast, good quality
   - phi3.5:3.8b (2.2 GB) - Balanced

2. **Adjust chunk size for longer policies:**
   ```yaml
   chunking:
     chunk_size: 768  # Larger chunks for better context
   ```

3. **Reduce top_k for faster retrieval:**
   ```yaml
   retrieval:
     top_k: 3  # Fewer results, faster processing
   ```

4. **Disable reranking for speed:**
   ```yaml
   retrieval:
     use_reranking: false  # Faster but less accurate
   ```

## Next Steps

1. **Try it on your own policies!**
   ```bash
   python -m cli.main analyze your_policy.pdf --domain isms
   ```

2. **Review the outputs** in the generated directory

3. **Customize the configuration** to match your needs

4. **Read the full documentation:**
   - `README.md` - Complete guide
   - `docs/EXAMPLES.md` - More examples
   - `docs/TROUBLESHOOTING.md` - Common issues
   - `cli/README.md` - CLI reference

## Support

- **Documentation:** See `docs/` directory
- **Examples:** See `examples/` directory
- **Test Data:** See `tests/fixtures/dummy_policies/`
- **Troubleshooting:** See `docs/TROUBLESHOOTING.md`

---

**Your system is ready to analyze policies! 🎉**

Start with a dummy policy to see how it works, then try your own documents.
