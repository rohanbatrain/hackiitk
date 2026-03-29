# Understanding the Reference Catalog

## Your Question

> "The catalog was made using 1 PDF which is wrong. We have a lot of context in the form of MD and PDF files in data/"

## The Answer: The Current Catalog is CORRECT

Let me explain why the catalog should only be built from the CIS guide PDF, not from your policy documents.

## What is the Reference Catalog?

The **Reference Catalog** is the **NIST Cybersecurity Framework (CSF) 2.0** - a standardized framework with **49 security controls** organized into 6 functions:

```
NIST CSF 2.0 Framework (49 Controls)
├── Govern (GV) - 14 controls
├── Identify (ID) - 8 controls  
├── Protect (PR) - 15 controls
├── Detect (DE) - 5 controls
├── Respond (RS) - 4 controls
└── Recover (RC) - 3 controls
```

This is a **universal standard** published by NIST (National Institute of Standards and Technology).

## What are the Policy Files in `data/policies/`?

The 37 MD files in `data/policies/` are **policy templates** - examples of what organizational policies should look like. They are:

- **NOT** the framework itself
- **NOT** part of the reference catalog
- **INPUT** documents to be analyzed
- **EXAMPLES** of policies that organizations write

## The Architecture

```
┌─────────────────────────────────────────────────────────┐
│  REFERENCE CATALOG (data/reference_catalog.json)       │
│                                                         │
│  Source: CIS Guide PDF (NIST CSF 2.0)                  │
│  Content: 49 security controls                         │
│  Purpose: The STANDARD to measure against              │
│                                                         │
│  Example controls:                                      │
│  - GV.OC-01: Organizational mission understood         │
│  - PR.AA-01: Identity management implemented           │
│  - DE.CM-01: Networks monitored for threats            │
└─────────────────────────────────────────────────────────┘
                         ↓
                    USED TO ANALYZE
                         ↓
┌─────────────────────────────────────────────────────────┐
│  POLICY DOCUMENTS (data/policies/*.md)                 │
│                                                         │
│  Source: Your organization / templates                  │
│  Content: Policy text and procedures                   │
│  Purpose: Documents to be ANALYZED                      │
│                                                         │
│  Examples:                                              │
│  - Information Security Policy.md                       │
│  - Access Control Policy.md                             │
│  - Incident Response Policy.md                          │
└─────────────────────────────────────────────────────────┘
                         ↓
                    PRODUCES
                         ↓
┌─────────────────────────────────────────────────────────┐
│  GAP ANALYSIS REPORT                                    │
│                                                         │
│  Shows:                                                 │
│  - Which of the 49 controls are missing                │
│  - Which controls are partially implemented             │
│  - What needs to be added/improved                      │
│  - Recommendations for compliance                       │
└─────────────────────────────────────────────────────────┘
```

## Why Not Build Catalog from Policy Files?

### Reason 1: They're Not the Standard
Your policy files are **implementations** of security practices, not the **framework** itself. It's like:
- Framework = The building code (rules)
- Policies = The actual building (implementation)

You don't create building codes from buildings - you check if buildings meet the code!

### Reason 2: They're What You Analyze
The whole point of the tool is to:
1. Take your policy document
2. Compare it against the 49 NIST CSF controls
3. Find what's missing

If you built the catalog FROM your policies, you'd be comparing your policies against... your policies. That defeats the purpose!

### Reason 3: NIST CSF is Universal
The 49 controls in NIST CSF 2.0 are:
- Standardized across all organizations
- Recognized by regulators and auditors
- Based on industry best practices
- The same for everyone

Your policies are specific to your organization.

## How the Tool Works

### Step 1: Load the Framework (Catalog)
```python
# Load the 49 NIST CSF 2.0 controls
catalog = load_catalog("data/reference_catalog.json")
# Contains: GV.OC-01, GV.OC-02, ..., RC.IM-01 (49 total)
```

### Step 2: Analyze Your Policy
```python
# Analyze your policy against the framework
analyze_policy(
    policy="data/policies/Information-Security-Policy.md",
    catalog=catalog
)
```

### Step 3: Find Gaps
```python
# The tool checks:
# - Does the policy address GV.OC-01? ✓ Yes
# - Does the policy address GV.OC-02? ✗ No - GAP!
# - Does the policy address PR.AA-01? ✓ Partial
# ... for all 49 controls
```

### Step 4: Generate Report
```json
{
  "gaps": [
    {
      "control": "GV.OC-02",
      "severity": "High",
      "description": "Policy doesn't address stakeholder expectations",
      "recommendation": "Add section on stakeholder analysis"
    }
  ]
}
```

## What If You Want More Context?

If you want the analyzer to have more knowledge about security practices, you can:

### Option 1: Enhance Control Descriptions
Add more detail to each of the 49 controls in the catalog (but keep it at 49 controls).

### Option 2: Add Reference Documents (Future Feature)
Create a separate knowledge base that the LLM can reference when analyzing policies. This would be in addition to the catalog, not replacing it.

### Option 3: Use Policy Templates as Examples
The tool could use your policy templates as "good examples" when generating recommendations, but they still wouldn't be part of the framework catalog.

## Summary

| Component | What It Is | Purpose |
|-----------|------------|---------|
| **Reference Catalog** | NIST CSF 2.0 (49 controls) | The STANDARD |
| **CIS Guide PDF** | Source document for catalog | Defines the 49 controls |
| **Policy Files (data/policies/)** | Policy templates | INPUT to be analyzed |
| **Gap Analysis** | Comparison result | Shows what's missing |

## Your Current Setup is Correct

- ✅ Catalog has 49 NIST CSF 2.0 controls
- ✅ Built from CIS guide PDF
- ✅ Policy files are separate (as they should be)
- ✅ Ready to analyze policies

## How to Use It

```bash
# Analyze one of your policy templates
./pa --policy-path data/policies/Information-Security-Policy.md --domain isms

# Analyze a custom policy
./pa --policy-path /path/to/your/company/policy.pdf --domain risk_management

# The tool will:
# 1. Load the 49 NIST CSF controls
# 2. Parse your policy
# 3. Compare policy against controls
# 4. Generate gap report
```

## Bottom Line

**Don't rebuild the catalog from your policy files.** The catalog is the framework (49 controls), and your policy files are what you analyze against that framework. This is the correct architecture!

---

**Still have questions?** The catalog is like a ruler - you don't make the ruler from the things you're measuring. You use the ruler to measure things!
