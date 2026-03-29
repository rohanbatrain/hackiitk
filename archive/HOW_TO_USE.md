# 🚀 How to Use the Offline Policy Gap Analyzer

## Your System is Ready!

You have a fully validated, production-ready system with:
- ✅ 438 tests passing
- ✅ LLM models loaded (qwen2.5:3b-instruct, phi3.5:3.8b)
- ✅ All components operational

Let's get you started!

---

## 🎯 Quick Start (3 Steps)

### Step 1: Test with a Dummy Policy (30 seconds)

```bash
# Navigate to your project directory
cd /Users/rohan/Documents/HACKIITK

# Activate your virtual environment
source venv/bin/activate

# Run analysis on a test policy
python -m cli.main analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms
```

**What happens:**
- System parses the policy
- Identifies gaps against NIST CSF 2.0
- Generates gap report, revised policy, and roadmap
- Creates timestamped output directory with all results

### Step 2: Check the Results

```bash
# Results are in outputs/analysis_YYYY-MM-DD_HH-MM-SS/
ls -la outputs/

# View the gap analysis report
cat outputs/analysis_*/gap_analysis_report.md

# Or open in your editor
open outputs/analysis_*/gap_analysis_report.md
```

### Step 3: Analyze Your Own Policy

```bash
# Analyze your policy document
python -m cli.main analyze /path/to/your/policy.pdf --domain isms

# Or with custom output location
python -m cli.main analyze your_policy.pdf --domain isms --output ./my_results
```

---

## 📋 Command Line Interface (CLI)

### Basic Usage

```bash
python -m cli.main analyze <policy_file> --domain <domain_type>
```

### Available Domains

Choose the domain that best matches your policy:

- **`isms`** - Information Security Management System
  - Use for: General security policies, ISO 27001-related policies
  - Focuses on: Governance (GV) function subcategories

- **`risk_management`** - Risk Management
  - Use for: Risk assessment and management policies
  - Focuses on: GV.RM, GV.OV, ID.RA subcategories

- **`patch_management`** - Patch Management
  - Use for: Vulnerability and patch management policies
  - Focuses on: ID.RA, PR.DS, PR.PS subcategories

- **`data_privacy`** - Data Privacy
  - Use for: Data protection and privacy policies
  - Focuses on: PR.AA, PR.DS, PR.AT subcategories
  - Note: Includes privacy framework limitation warning

### CLI Options

```bash
# Full command with all options
python -m cli.main analyze policy.pdf \
  --domain isms \
  --config my_config.yaml \
  --output ./results \
  --model qwen2.5:3b-instruct

# See all available options
python -m cli.main --help

# Check version
python -m cli.main --version
```

### CLI Examples

```bash
# Example 1: Basic ISMS analysis
python -m cli.main analyze corporate_security_policy.pdf --domain isms

# Example 2: Risk management with custom output
python -m cli.main analyze risk_policy.docx --domain risk_management --output ./risk_analysis

# Example 3: Using different model
python -m cli.main analyze policy.pdf --domain isms --model phi3.5:3.8b

# Example 4: With custom configuration
python -m cli.main analyze policy.pdf --config custom_config.yaml
```

---

## 🐍 Python API Usage

### Basic Python Script

Create a file `analyze_policy.py`:

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

# Run analysis
result = pipeline.execute(
    policy_path="path/to/your/policy.pdf",
    domain="isms"  # or "risk_management", "patch_management", "data_privacy"
)

# Access results
print(f"✅ Analysis complete!")
print(f"📁 Results saved to: {result.output_dir}")
print(f"🔍 Found {len(result.gaps)} gaps")
print(f"📋 Generated {len(result.roadmap.immediate_actions)} immediate actions")

# Access specific outputs
for gap in result.gaps:
    print(f"  - {gap.subcategory_id}: {gap.severity} - {gap.gap_explanation}")
```

Run it:

```bash
python analyze_policy.py
```

### Advanced Python Usage

```python
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader
from pathlib import Path
import json

# Custom configuration
config = ConfigLoader.get_default_config()
config['llm']['model'] = 'qwen2.5:3b-instruct'
config['llm']['temperature'] = 0.1
config['retrieval']['top_k'] = 5

# Create pipeline
pipeline = AnalysisPipeline(config)

# Run analysis
result = pipeline.execute(
    policy_path="corporate_policy.pdf",
    domain="isms"
)

# Process results programmatically
print(f"\n📊 Analysis Summary:")
print(f"   Total Gaps: {len(result.gaps)}")

# Count by severity
severity_counts = {}
for gap in result.gaps:
    severity_counts[gap.severity] = severity_counts.get(gap.severity, 0) + 1

print(f"\n🔴 Critical: {severity_counts.get('critical', 0)}")
print(f"🟠 High: {severity_counts.get('high', 0)}")
print(f"🟡 Medium: {severity_counts.get('medium', 0)}")
print(f"🟢 Low: {severity_counts.get('low', 0)}")

# Export to custom format
custom_report = {
    'policy': result.input_file,
    'analysis_date': result.analysis_date,
    'total_gaps': len(result.gaps),
    'severity_breakdown': severity_counts,
    'immediate_actions': len(result.roadmap.immediate_actions),
    'gaps': [
        {
            'id': gap.subcategory_id,
            'severity': gap.severity,
            'description': gap.gap_explanation
        }
        for gap in result.gaps
    ]
}

# Save custom report
with open('custom_report.json', 'w') as f:
    json.dump(custom_report, f, indent=2)

print(f"\n✅ Custom report saved to: custom_report.json")
```

---

## ⚙️ Configuration

### Create Custom Configuration

Create `my_config.yaml`:

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

Use it:

```bash
python -m cli.main analyze policy.pdf --config my_config.yaml
```

### Configuration Options Explained

**Chunking:**
- `chunk_size`: Larger = more context, slower processing
- `overlap`: Ensures context isn't lost at boundaries

**Retrieval:**
- `top_k`: More results = better coverage, slower
- `use_reranking`: Improves accuracy but adds processing time

**LLM:**
- `model`: Choose based on speed/quality tradeoff
  - `qwen2.5:3b-instruct` - Fast, good quality (1.9 GB)
  - `phi3.5:3.8b` - Balanced (2.2 GB)
- `temperature`: Lower = more deterministic (0.1 recommended)
- `max_tokens`: Longer = more detailed output

**Analysis:**
- `severity_thresholds`: Adjust gap classification sensitivity

---

## 📂 Understanding the Output

After analysis, you'll find these files in `outputs/analysis_YYYY-MM-DD_HH-MM-SS/`:

### 1. gap_analysis_report.md

Human-readable gap analysis with:
- Executive summary
- Detailed gap descriptions
- Evidence quotes from your policy
- Suggested fixes for each gap

**Example:**
```markdown
## Gap 1: GV.RM-01 - Risk Management Strategy [CRITICAL]

**Status:** Missing
**CSF Requirement:** Organizational risk management strategy is established

**Gap Explanation:** The policy does not define a formal risk management 
strategy or process for identifying, assessing, and mitigating risks.

**Evidence:** No mention of risk assessment found in the policy.

**Suggested Fix:** Add a Risk Management section that defines risk appetite,
assessment methodology, and treatment options.
```

### 2. gap_analysis_report.json

Machine-readable gap data for integration:

```json
{
  "gaps": [
    {
      "subcategory_id": "GV.RM-01",
      "description": "Risk Management Strategy",
      "status": "missing",
      "evidence_quote": "",
      "gap_explanation": "No formal risk management strategy defined",
      "severity": "critical",
      "suggested_fix": "Add Risk Management section..."
    }
  ]
}
```

### 3. revised_policy.md

Improved policy text with:
- Original content preserved
- New sections for missing requirements
- Strengthened language for partial coverage
- Citations to CSF subcategories
- Mandatory human-review warning

### 4. implementation_roadmap.md

Prioritized action plan with:
- **Immediate actions** (0-3 months) - Critical/High severity
- **Near-term actions** (3-6 months) - Medium severity
- **Medium-term actions** (6-12 months) - Low severity

Each action includes:
- Technical steps
- Administrative steps
- Physical steps
- Effort estimate
- CSF subcategory reference

### 5. implementation_roadmap.json

Machine-readable roadmap for project management tools

### 6. audit_log.json

Immutable compliance log with:
- Input file hash
- Model versions
- Configuration parameters
- Timestamp
- Output directory

### 7. analysis.log

Detailed operation log for troubleshooting

---

## 🎓 Common Use Cases

### Use Case 1: Initial Policy Assessment

```bash
# Analyze your current policy
python -m cli.main analyze current_policy.pdf --domain isms

# Review the gap report
open outputs/analysis_*/gap_analysis_report.md

# Share the roadmap with management
open outputs/analysis_*/implementation_roadmap.md
```

### Use Case 2: Policy Revision

```bash
# Analyze current policy
python -m cli.main analyze old_policy.pdf --domain isms

# Review the revised policy
open outputs/analysis_*/revised_policy.md

# Use as starting point for your updated policy
# (Remember: AI-generated content requires human review!)
```

### Use Case 3: Compliance Tracking

```python
# Track compliance over time
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader
import json
from datetime import datetime

config = ConfigLoader.get_default_config()
pipeline = AnalysisPipeline(config)

# Analyze current policy
result = pipeline.execute("policy_v2.pdf", domain="isms")

# Track metrics
metrics = {
    'date': datetime.now().isoformat(),
    'version': 'v2',
    'total_gaps': len(result.gaps),
    'critical_gaps': len([g for g in result.gaps if g.severity == 'critical']),
    'high_gaps': len([g for g in result.gaps if g.severity == 'high'])
}

# Append to tracking file
with open('compliance_tracking.json', 'a') as f:
    f.write(json.dumps(metrics) + '\n')

print(f"Compliance metrics saved!")
```

### Use Case 4: Batch Analysis

```python
# Analyze multiple policies
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader
from pathlib import Path

config = ConfigLoader.get_default_config()
pipeline = AnalysisPipeline(config)

policies = [
    ('isms_policy.pdf', 'isms'),
    ('risk_policy.pdf', 'risk_management'),
    ('patch_policy.pdf', 'patch_management'),
    ('privacy_policy.pdf', 'data_privacy')
]

results = {}
for policy_file, domain in policies:
    print(f"\n📄 Analyzing {policy_file}...")
    result = pipeline.execute(policy_file, domain=domain)
    results[policy_file] = {
        'gaps': len(result.gaps),
        'output_dir': str(result.output_dir)
    }
    print(f"   ✅ Found {len(result.gaps)} gaps")

print(f"\n📊 Summary:")
for policy, data in results.items():
    print(f"   {policy}: {data['gaps']} gaps")
```

---

## 🔧 Troubleshooting

### Issue: "Model not found"

```bash
# Check available models
ollama list

# Download the model
ollama pull qwen2.5:3b-instruct

# Verify Ollama is running
curl http://localhost:11434/api/tags
```

### Issue: "Out of memory"

```yaml
# Use smaller model in config.yaml
llm:
  model: "qwen2.5:3b-instruct"  # Smaller model (1.9 GB)
```

### Issue: "Parsing failed"

- Ensure PDF is text-based (not scanned image)
- Try converting to DOCX or TXT format
- Check file isn't corrupted

### Issue: "Slow performance"

```yaml
# Optimize configuration
retrieval:
  top_k: 3  # Reduce from 5
  use_reranking: false  # Disable for speed

llm:
  max_tokens: 256  # Reduce from 512
```

---

## 📚 Next Steps

1. **Try the dummy policies** to see how it works
2. **Analyze your own policy** with appropriate domain
3. **Review the outputs** and understand the gaps
4. **Customize configuration** for your needs
5. **Integrate into your workflow** using Python API

---

## 💡 Tips & Best Practices

1. **Choose the right domain** - Focuses analysis on relevant CSF subcategories
2. **Review AI-generated content** - Always have humans validate revised policies
3. **Track over time** - Run analysis periodically to track improvements
4. **Use audit logs** - Maintain compliance records
5. **Customize configuration** - Tune for your speed/quality needs
6. **Start with dummy policies** - Learn the system before production use

---

## 🆘 Getting Help

- **Documentation:** See `docs/` directory
- **Examples:** See `examples/` directory
- **Troubleshooting:** See `docs/TROUBLESHOOTING.md`
- **Test Data:** See `tests/fixtures/dummy_policies/`

---

**Your system is ready! Start analyzing policies now! 🚀**

```bash
# Quick test
python -m cli.main analyze tests/fixtures/dummy_policies/isms_policy.md --domain isms
```
