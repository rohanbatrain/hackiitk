# Usage Examples

This document provides comprehensive examples of using the Offline Policy Gap Analyzer for different policy domains and use cases.

## Table of Contents

- [Basic Usage](#basic-usage)
- [Policy Domain Examples](#policy-domain-examples)
- [Configuration Examples](#configuration-examples)
- [Output Examples](#output-examples)
- [Advanced Usage](#advanced-usage)

## Basic Usage

### Simplest Analysis

```bash
# Analyze a policy with default settings
policy-analyzer --policy-path my_policy.pdf
```

This command:
- Uses default configuration from `config.yaml`
- Auto-detects policy domain (evaluates all CSF functions)
- Uses default model (qwen2.5-3b-instruct)
- Outputs to timestamped directory in `outputs/`

### Specify Output Directory

```bash
# Analyze with custom output location
policy-analyzer --policy-path policy.pdf --output-dir ./my_results
```

### Enable Verbose Logging

```bash
# See detailed progress and debugging information
policy-analyzer --policy-path policy.pdf --verbose
```

## Policy Domain Examples

### ISMS (Information Security Management System) Policy

```bash
# Analyze ISMS policy with domain-specific prioritization
policy-analyzer \
    --policy-path isms_policy.pdf \
    --domain isms \
    --output-dir ./isms_analysis

# Expected output:
# - Prioritizes Govern (GV) function subcategories
# - Focuses on governance, risk management, and oversight
# - Analysis time: ~10 minutes for 20-page policy
```

**Sample ISMS Policy Structure**:
```
1. Purpose and Scope
2. Information Security Governance
3. Risk Management Strategy
4. Asset Management
5. Access Control
6. Incident Response
7. Business Continuity
8. Compliance and Audit
```

**Common Gaps Identified**:
- GV.SC-01: Supply chain risk management
- GV.OV-01: Organizational context and priorities
- ID.AM-01: Asset inventory and management
- PR.AA-01: Identity and access management

### Risk Management Policy

```bash
# Analyze risk management policy
policy-analyzer \
    --policy-path risk_management_policy.docx \
    --domain risk_management \
    --output-dir ./risk_analysis

# Expected output:
# - Prioritizes GV.RM, GV.OV, ID.RA subcategories
# - Focuses on risk assessment and treatment
# - Identifies gaps in risk monitoring and communication
```

**Sample Risk Management Policy Structure**:
```
1. Purpose and Scope
2. Risk Management Framework
3. Risk Identification
4. Risk Assessment Methodology
5. Risk Treatment Options
6. Risk Monitoring and Review
7. Roles and Responsibilities
```

**Common Gaps Identified**:
- GV.RM-02: Risk appetite and tolerance
- GV.RM-03: Risk management strategy determination
- ID.RA-01: Asset vulnerabilities identification
- ID.RA-02: Threat intelligence incorporation

### Patch Management Policy

```bash
# Analyze patch management policy
policy-analyzer \
    --policy-path patch_policy.txt \
    --domain patch_management \
    --output-dir ./patch_analysis \
    --verbose

# Expected output:
# - Prioritizes ID.RA, PR.DS, PR.PS subcategories
# - Focuses on vulnerability management and protective technology
# - Identifies gaps in vulnerability scanning and patch testing
```

**Sample Patch Management Policy Structure**:
```
1. Purpose and Scope
2. Patch Management Process
3. Vulnerability Scanning
4. Patch Prioritization
5. Testing Procedures
6. Deployment Schedule
7. Emergency Patching
8. Verification and Reporting
```

**Common Gaps Identified**:
- ID.RA-01: Vulnerability identification processes
- PR.DS-06: Integrity checking mechanisms
- PR.PS-01: Configuration management
- DE.CM-08: Vulnerability scan results analysis

### Data Privacy Policy

```bash
# Analyze data privacy policy
policy-analyzer \
    --policy-path privacy_policy.pdf \
    --domain data_privacy \
    --output-dir ./privacy_analysis

# Expected output:
# - Prioritizes PR.AA, PR.DS, PR.AT subcategories
# - Focuses on access control and data security
# - Logs warning about NIST CSF privacy framework limitations
# - Identifies gaps in identity management and data protection
```

**Sample Data Privacy Policy Structure**:
```
1. Purpose and Scope
2. Data Collection and Classification
3. Data Usage and Retention
4. Access Control and Authorization
5. Data Security Controls
6. Data Subject Rights
7. Third-Party Data Sharing
8. Breach Notification
```

**Common Gaps Identified**:
- PR.AA-01: Identity and credential management
- PR.DS-01: Data-at-rest protection
- PR.DS-02: Data-in-transit protection
- PR.AT-01: Security awareness training

**Privacy Framework Warning**:
```
WARNING: The NIST CSF 2.0 addresses cybersecurity aspects of data protection 
but is not a complete privacy framework. Privacy-specific compliance requirements 
may extend beyond CSF scope.
```

## Configuration Examples

### Basic Configuration File

```yaml
# config.yaml - Default configuration
chunk_size: 512
overlap: 50
top_k: 5
temperature: 0.1
max_tokens: 512
model_name: "qwen2.5-3b-instruct"
```

Usage:
```bash
policy-analyzer --policy-path policy.pdf --config config.yaml
```

### High-Performance Configuration

```yaml
# config_fast.yaml - Optimized for speed
chunk_size: 256  # Smaller chunks for faster processing
overlap: 25
top_k: 3  # Fewer retrieval results
temperature: 0.1
max_tokens: 256  # Shorter LLM responses
model_name: "qwen2.5-3b-instruct"  # Fastest model
```

Usage:
```bash
policy-analyzer --policy-path policy.pdf --config config_fast.yaml
```

### High-Quality Configuration

```yaml
# config_quality.yaml - Optimized for accuracy
chunk_size: 512
overlap: 100  # More overlap for better context
top_k: 10  # More retrieval results
temperature: 0.05  # Lower temperature for more deterministic output
max_tokens: 1024  # Longer LLM responses
model_name: "qwen3-8b-instruct"  # Larger model for better quality
```

Usage:
```bash
policy-analyzer --policy-path policy.pdf --config config_quality.yaml
```

### Memory-Constrained Configuration

```yaml
# config_lowmem.yaml - For systems with limited RAM
chunk_size: 256
overlap: 25
top_k: 3
temperature: 0.1
max_tokens: 256
model_name: "qwen2.5-3b-instruct"  # Smallest model
```

Usage:
```bash
policy-analyzer --policy-path policy.pdf --config config_lowmem.yaml
```

### Custom Severity Thresholds

```yaml
# config_custom_severity.yaml - Custom gap severity classification
chunk_size: 512
overlap: 50
top_k: 5
temperature: 0.1
max_tokens: 512
model_name: "qwen2.5-3b-instruct"

severity_thresholds:
  critical: 0.95  # Stricter critical threshold
  high: 0.75
  medium: 0.50
  low: 0.25
```

Usage:
```bash
policy-analyzer --policy-path policy.pdf --config config_custom_severity.yaml
```

### Domain-Specific CSF Prioritization

```yaml
# config_custom_domain.yaml - Custom CSF function prioritization
chunk_size: 512
overlap: 50
top_k: 5
temperature: 0.1
max_tokens: 512
model_name: "qwen2.5-3b-instruct"

csf_function_priority:
  - "Govern"
  - "Identify"
  - "Protect"
  # Omit Detect, Respond, Recover for faster analysis
```

Usage:
```bash
policy-analyzer --policy-path policy.pdf --config config_custom_domain.yaml
```

## Output Examples

### Gap Analysis Report (Markdown)

**File**: `outputs/2024-03-15_14-30-00/gap_analysis_report.md`

```markdown
# Gap Analysis Report

**Analysis Date**: 2024-03-15 14:30:00
**Input File**: isms_policy.pdf
**Model**: qwen2.5-3b-instruct
**Domain**: isms

## Summary

- **Total Gaps Identified**: 12
- **Critical**: 2
- **High**: 5
- **Medium**: 3
- **Low**: 2

## Identified Gaps

### Critical Gaps

#### GV.SC-01: Supply Chain Risk Management

**Status**: Missing
**Severity**: Critical
**CSF Description**: Cyber supply chain risk management processes are identified, established, managed, monitored, and improved by organizational stakeholders.

**Evidence**: No evidence found in policy document.

**Gap Explanation**: The policy does not address supply chain cybersecurity risks. There are no provisions for vendor security assessments, third-party risk management, or supply chain monitoring.

**Suggested Fix**: Add a section on "Supply Chain Risk Management" that includes:
- Vendor security assessment requirements
- Third-party risk evaluation criteria
- Supply chain monitoring and audit procedures
- Incident response coordination with suppliers

---

### High Gaps

#### ID.AM-01: Asset Inventory

**Status**: Partially Covered
**Severity**: High
**CSF Description**: Physical devices and systems within the organization are inventoried.

**Evidence**: "The organization maintains an inventory of information assets..." (Section 4.2)

**Gap Explanation**: The policy mentions asset inventory but lacks specific requirements for maintaining currency, completeness, and accuracy. No mention of automated discovery tools or inventory update frequency.

**Suggested Fix**: Strengthen Section 4.2 to include:
- Automated asset discovery requirements
- Inventory update frequency (e.g., quarterly)
- Asset classification and criticality ratings
- Integration with configuration management database (CMDB)

---

[Additional gaps...]

## Ambiguous Subcategories

The following subcategories require manual review:

- **PR.DS-03**: Assets are formally managed throughout removal, transfers, and disposition
  - **Reason**: Policy mentions data disposal but unclear if it covers all asset types
  - **Action**: Review Section 7.4 and clarify scope

## Recommendations

1. **Immediate Actions** (Critical/High gaps):
   - Develop supply chain risk management procedures
   - Implement comprehensive asset inventory system
   - Establish vulnerability management program

2. **Near-Term Actions** (Medium gaps):
   - Enhance access control documentation
   - Implement security awareness training program

3. **Medium-Term Actions** (Low gaps):
   - Develop business continuity testing procedures
   - Establish metrics for security program effectiveness
```

### Gap Analysis Report (JSON)

**File**: `outputs/2024-03-15_14-30-00/gap_analysis_report.json`

```json
{
  "metadata": {
    "analysis_date": "2024-03-15T14:30:00Z",
    "input_file": "isms_policy.pdf",
    "model_name": "qwen2.5-3b-instruct",
    "model_version": "1.0.0",
    "embedding_model": "all-MiniLM-L6-v2",
    "prompt_version": "1.0",
    "configuration_hash": "a1b2c3d4e5f6",
    "retrieval_parameters": {
      "chunk_size": 512,
      "overlap": 50,
      "top_k": 5
    },
    "domain": "isms"
  },
  "summary": {
    "total_gaps": 12,
    "critical": 2,
    "high": 5,
    "medium": 3,
    "low": 2
  },
  "gaps": [
    {
      "subcategory_id": "GV.SC-01",
      "subcategory_description": "Cyber supply chain risk management processes are identified, established, managed, monitored, and improved by organizational stakeholders",
      "status": "missing",
      "evidence_quote": "",
      "gap_explanation": "The policy does not address supply chain cybersecurity risks. There are no provisions for vendor security assessments, third-party risk management, or supply chain monitoring.",
      "severity": "critical",
      "suggested_fix": "Add a section on 'Supply Chain Risk Management' that includes: vendor security assessment requirements, third-party risk evaluation criteria, supply chain monitoring and audit procedures, incident response coordination with suppliers."
    },
    {
      "subcategory_id": "ID.AM-01",
      "subcategory_description": "Physical devices and systems within the organization are inventoried",
      "status": "partially_covered",
      "evidence_quote": "The organization maintains an inventory of information assets...",
      "gap_explanation": "The policy mentions asset inventory but lacks specific requirements for maintaining currency, completeness, and accuracy. No mention of automated discovery tools or inventory update frequency.",
      "severity": "high",
      "suggested_fix": "Strengthen Section 4.2 to include: automated asset discovery requirements, inventory update frequency (e.g., quarterly), asset classification and criticality ratings, integration with configuration management database (CMDB)."
    }
  ],
  "ambiguous_subcategories": [
    {
      "subcategory_id": "PR.DS-03",
      "reason": "Policy mentions data disposal but unclear if it covers all asset types",
      "action": "Review Section 7.4 and clarify scope"
    }
  ]
}
```

### Revised Policy (Markdown)

**File**: `outputs/2024-03-15_14-30-00/revised_policy.md`

```markdown
# Information Security Management System Policy (Revised)

[Original policy content with revisions marked]

## 4. Supply Chain Risk Management [NEW SECTION]

### 4.1 Purpose

This section establishes requirements for managing cybersecurity risks in the organization's supply chain, including vendor relationships, third-party services, and external dependencies.

**CSF Reference**: GV.SC-01

### 4.2 Vendor Security Assessment

All vendors and third-party service providers with access to organizational systems or data must undergo security assessment before engagement and annually thereafter.

Assessment criteria include:
- Security certifications (ISO 27001, SOC 2, etc.)
- Incident response capabilities
- Data protection practices
- Business continuity planning

**CSF Reference**: GV.SC-01

### 4.3 Supply Chain Monitoring

The organization shall implement continuous monitoring of supply chain risks through:
- Regular vendor security audits
- Threat intelligence sharing with critical suppliers
- Contractual security requirements
- Incident notification obligations

**CSF Reference**: GV.SC-01

---

## 5. Asset Management [REVISED SECTION]

### 5.1 Asset Inventory [STRENGTHENED]

The organization maintains a comprehensive inventory of all information assets, including:
- Physical devices (servers, workstations, mobile devices, network equipment)
- Virtual assets (virtual machines, containers, cloud resources)
- Software applications and licenses
- Data repositories and databases

**Inventory Requirements**:
- **Automated Discovery**: Utilize automated asset discovery tools to identify and catalog assets
- **Update Frequency**: Inventory shall be updated quarterly and upon significant changes
- **Asset Classification**: Each asset shall be classified by criticality (Critical/High/Medium/Low)
- **CMDB Integration**: Asset inventory shall integrate with the Configuration Management Database

**CSF Reference**: ID.AM-01

[Additional revisions...]

---

## IMPORTANT LEGAL DISCLAIMER

**This revised policy was generated by an AI system and is provided as a draft baseline only.**

The CIS MS-ISAC templates are advisory and may not reflect the most recent applicable standards or your organization's specific legal, regulatory, or operational requirements.

**This document MUST be reviewed, validated, and approved by qualified legal counsel, compliance officers, and security leadership before adoption.**

Do not implement this policy without proper review and customization for your organizational context.
```

### Implementation Roadmap (Markdown)

**File**: `outputs/2024-03-15_14-30-00/implementation_roadmap.md`

```markdown
# Implementation Roadmap

**Generated**: 2024-03-15 14:30:00
**Policy**: isms_policy.pdf
**Total Actions**: 12

## Immediate Actions (0-3 months)

Critical and High severity gaps requiring immediate attention.

### Action 1: Establish Supply Chain Risk Management Program

**Severity**: Critical
**Effort**: High
**CSF Subcategory**: GV.SC-01
**Policy Section**: New Section 4

**Description**: Develop and implement comprehensive supply chain risk management procedures to address vendor security and third-party risks.

**Technical Steps**:
1. Implement vendor risk assessment platform
2. Develop security questionnaire templates
3. Create vendor security scorecard system
4. Establish automated vendor monitoring

**Administrative Steps**:
1. Define vendor security requirements
2. Create vendor assessment procedures
3. Establish vendor approval workflow
4. Develop vendor contract security clauses
5. Assign supply chain risk management roles

**Physical Steps**:
- None required

---

### Action 2: Implement Comprehensive Asset Inventory System

**Severity**: High
**Effort**: Medium
**CSF Subcategory**: ID.AM-01
**Policy Section**: Section 5.1

**Description**: Deploy automated asset discovery and inventory management system with quarterly update requirements.

**Technical Steps**:
1. Deploy asset discovery tool (e.g., Lansweeper, ServiceNow)
2. Configure automated scanning schedules
3. Integrate with CMDB
4. Implement asset classification tagging
5. Set up inventory reporting dashboards

**Administrative Steps**:
1. Define asset classification criteria
2. Establish inventory update procedures
3. Assign asset management responsibilities
4. Create inventory audit schedule

**Physical Steps**:
1. Conduct initial physical asset audit
2. Apply asset tags to physical devices
3. Document asset locations

---

[Additional immediate actions...]

## Near-Term Actions (3-6 months)

Medium severity gaps to address after immediate priorities.

### Action 6: Enhance Access Control Documentation

**Severity**: Medium
**Effort**: Low
**CSF Subcategory**: PR.AA-01
**Policy Section**: Section 6.2

**Description**: Strengthen access control policy with detailed identity and credential management requirements.

**Technical Steps**:
1. Document current access control mechanisms
2. Implement multi-factor authentication (MFA)
3. Deploy privileged access management (PAM) solution

**Administrative Steps**:
1. Define access request and approval procedures
2. Establish access review schedule (quarterly)
3. Create role-based access control (RBAC) matrix
4. Document credential management requirements

**Physical Steps**:
- None required

---

[Additional near-term actions...]

## Medium-Term Actions (6-12 months)

Low severity gaps and continuous improvement initiatives.

### Action 10: Develop Business Continuity Testing Procedures

**Severity**: Low
**Effort**: Medium
**CSF Subcategory**: RC.RP-01
**Policy Section**: Section 8.3

**Description**: Establish regular business continuity and disaster recovery testing program.

**Technical Steps**:
1. Develop test scenarios and scripts
2. Set up test environments
3. Implement automated backup verification

**Administrative Steps**:
1. Create annual testing schedule
2. Define test success criteria
3. Establish test reporting procedures
4. Assign testing responsibilities

**Physical Steps**:
1. Identify alternate facility requirements
2. Test physical access to backup sites

---

[Additional medium-term actions...]

## Summary

- **Immediate Actions**: 5 (Critical/High severity)
- **Near-Term Actions**: 4 (Medium severity)
- **Medium-Term Actions**: 3 (Low severity)

**Estimated Total Effort**: 18-24 months for complete implementation

**Priority Focus**: Supply chain risk management and asset inventory are the highest priorities requiring immediate attention.
```

### Implementation Roadmap (JSON)

**File**: `outputs/2024-03-15_14-30-00/implementation_roadmap.json`

```json
{
  "metadata": {
    "generated_date": "2024-03-15T14:30:00Z",
    "input_file": "isms_policy.pdf",
    "total_actions": 12
  },
  "immediate_actions": [
    {
      "action_id": "ACT-001",
      "timeframe": "immediate",
      "severity": "critical",
      "effort": "high",
      "csf_subcategory": "GV.SC-01",
      "policy_section": "New Section 4",
      "description": "Establish Supply Chain Risk Management Program",
      "technical_steps": [
        "Implement vendor risk assessment platform",
        "Develop security questionnaire templates",
        "Create vendor security scorecard system",
        "Establish automated vendor monitoring"
      ],
      "administrative_steps": [
        "Define vendor security requirements",
        "Create vendor assessment procedures",
        "Establish vendor approval workflow",
        "Develop vendor contract security clauses",
        "Assign supply chain risk management roles"
      ],
      "physical_steps": []
    }
  ],
  "near_term_actions": [],
  "medium_term_actions": []
}
```

## Advanced Usage

### Batch Processing Multiple Policies

```bash
#!/bin/bash
# analyze_all_policies.sh

# Array of policies to analyze
policies=(
    "policies/isms_policy.pdf:isms"
    "policies/risk_policy.docx:risk_management"
    "policies/patch_policy.txt:patch_management"
    "policies/privacy_policy.pdf:data_privacy"
)

# Analyze each policy
for policy_domain in "${policies[@]}"; do
    IFS=':' read -r policy domain <<< "$policy_domain"
    echo "Analyzing $policy with domain $domain..."
    
    policy-analyzer \
        --policy-path "$policy" \
        --domain "$domain" \
        --output-dir "./results/$(basename $policy .pdf)_analysis"
    
    echo "Completed $policy"
    echo "---"
done

echo "All policies analyzed!"
```

### Custom Model Selection

```bash
# Use specific LLM model
policy-analyzer \
    --policy-path policy.pdf \
    --model phi-3.5-mini-instruct \
    --domain isms

# Use larger model for better quality
policy-analyzer \
    --policy-path complex_policy.pdf \
    --model qwen3-8b-instruct \
    --config config_quality.yaml
```

### Programmatic Usage (Python)

```python
# analyze_policy.py
from orchestration.analysis_pipeline import AnalysisPipeline
from utils.config_loader import ConfigLoader

# Load configuration
config = ConfigLoader.load("config.yaml")

# Initialize pipeline
pipeline = AnalysisPipeline(config)

# Execute analysis
result = pipeline.execute(
    policy_path="isms_policy.pdf",
    domain="isms"
)

# Access results
print(f"Gaps found: {len(result.gaps)}")
print(f"Critical gaps: {result.summary['critical']}")
print(f"Output directory: {result.output_dir}")

# Cleanup
pipeline.cleanup()
```

### Integration with CI/CD

```yaml
# .github/workflows/policy-analysis.yml
name: Policy Analysis

on:
  push:
    paths:
      - 'policies/**'

jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.11'
      
      - name: Install dependencies
        run: |
          pip install -e .
          python scripts/download_models.py --all
      
      - name: Analyze policies
        run: |
          for policy in policies/*.pdf; do
            policy-analyzer --policy-path "$policy" --output-dir "./results"
          done
      
      - name: Upload results
        uses: actions/upload-artifact@v2
        with:
          name: gap-analysis-results
          path: results/
```

## See Also

- [README.md](../README.md) - Quick start guide
- [DEPENDENCIES.md](DEPENDENCIES.md) - Dependency information
- [LIMITATIONS.md](LIMITATIONS.md) - Known limitations
- [TROUBLESHOOTING.md](TROUBLESHOOTING.md) - Common issues and solutions
- [SCHEMAS.md](SCHEMAS.md) - JSON schema documentation
- [ARCHITECTURE.md](ARCHITECTURE.md) - System architecture
