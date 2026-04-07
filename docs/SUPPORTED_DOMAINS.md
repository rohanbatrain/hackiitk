# Supported Policy Domains

## Overview

The Offline Policy Gap Analyzer supports four specialized policy domains, each with tailored NIST CSF 2.0 subcategory prioritization for targeted gap analysis.

## Supported Domains

### 1. ISMS (Information Security Management System)
**Domain ID**: `isms`

**Description**: Comprehensive Information Security Management System analysis

**Scope**: All NIST CSF 2.0 functions and subcategories
- Govern (GV)
- Identify (ID)
- Protect (PR)
- Detect (DE)
- Respond (RS)
- Recover (RC)

**Use Case**: 
- Complete organizational security posture assessment
- ISO 27001 alignment
- Comprehensive security program evaluation
- Enterprise-wide security policy analysis

**Example**:
```bash
uv run policy-analyzer --policy-path isms_policy.pdf --domain isms
```

**Prioritization**: Evaluates against all CSF subcategories for comprehensive coverage

**Warnings**: None

---

### 2. Risk Management
**Domain ID**: `risk_management`

**Description**: Risk Management focused analysis

**Prioritized Subcategories**:
- **GV.RM-01**: Risk management strategy is established and communicated
- **GV.RM-02**: Risk appetite and risk tolerance statements are established, communicated, and maintained
- **GV.RM-03**: Cybersecurity risk management activities and outcomes are included in enterprise risk management processes
- **GV.OV-01**: Organizational cybersecurity strategy is established and communicated
- **ID.RA-01**: Vulnerabilities in assets are identified, validated, and recorded
- **ID.RA-02**: Cyber threat intelligence is received from information sharing forums and sources
- **ID.RA-03**: Internal and external threats to the organization are identified and recorded
- **ID.RA-04**: Potential impacts and likelihoods of threats exploiting vulnerabilities are identified and recorded
- **ID.RA-05**: Threats, vulnerabilities, likelihoods, and impacts are used to understand inherent risk and inform risk response decisions

**Use Case**:
- Risk assessment policy review
- Risk management framework evaluation
- Threat and vulnerability management
- Risk governance alignment

**Example**:
```bash
uv run policy-analyzer --policy-path risk_policy.pdf --domain risk_management
```

**Focus Areas**:
- Risk governance and strategy
- Risk assessment processes
- Threat intelligence integration
- Vulnerability management

**Warnings**: None

---

### 3. Patch Management
**Domain ID**: `patch_management`

**Description**: Patch and Vulnerability Management analysis

**Prioritized Subcategories**:
- **ID.RA-01**: Vulnerabilities in assets are identified, validated, and recorded
- **PR.DS-01**: The confidentiality, integrity, and availability of data-at-rest are protected
- **PR.DS-02**: The confidentiality, integrity, and availability of data-in-transit are protected
- **PR.PS-01**: Configuration management practices are established and applied
- **PR.PS-02**: Software is maintained, replaced, and removed commensurate with risk

**Use Case**:
- Patch management policy evaluation
- Vulnerability remediation processes
- Software lifecycle management
- Configuration management review

**Example**:
```bash
uv run policy-analyzer --policy-path patch_policy.pdf --domain patch_management
```

**Focus Areas**:
- Vulnerability identification and tracking
- Patch deployment processes
- Software maintenance and updates
- Configuration baseline management
- Data protection during patching

**Warnings**: None

---

### 4. Data Privacy
**Domain ID**: `data_privacy`

**Description**: Data Privacy and Protection analysis

**Prioritized Subcategories**:
- **PR.AA-01**: Identities and credentials for authorized users, services, and hardware are managed by the organization
- **PR.AA-02**: Identities are proofed and bound to credentials based on risk
- **PR.AA-03**: Users, services, and hardware are authenticated
- **PR.AA-05**: Access permissions, entitlements, and authorizations are defined in a policy, managed, enforced, and reviewed, and incorporate the principles of least privilege and separation of duties
- **PR.DS-01**: The confidentiality, integrity, and availability of data-at-rest are protected
- **PR.DS-02**: The confidentiality, integrity, and availability of data-in-transit are protected
- **PR.AT-01**: Personnel are provided with cybersecurity awareness and training so that they can perform their cybersecurity-related tasks

**Use Case**:
- Data privacy policy review
- Personal data protection assessment
- Access control evaluation
- Privacy training compliance

**Example**:
```bash
uv run policy-analyzer --policy-path privacy_policy.pdf --domain data_privacy
```

**Focus Areas**:
- Identity and access management
- Data protection (at-rest and in-transit)
- Privacy awareness and training
- Least privilege enforcement
- Data confidentiality controls

**⚠️ Important Warning**:
> The NIST CSF 2.0 addresses cybersecurity aspects of data protection but is not a complete privacy framework. Privacy-specific compliance requirements may extend beyond CSF scope.

**Additional Considerations**:
- GDPR compliance requires additional controls
- CCPA/CPRA have specific requirements beyond CSF
- Consider supplementing with privacy-specific frameworks (ISO 27701, NIST Privacy Framework)

---

## Auto-Detection

If no domain is specified, the analyzer evaluates against all CSF subcategories:

```bash
# Auto-detect mode (analyzes all CSF functions)
uv run policy-analyzer --policy-path policy.pdf
```

**Behavior**:
- Evaluates against all 106 NIST CSF 2.0 subcategories
- No domain-specific prioritization
- Suitable for general policy assessment
- Longer analysis time

---

## Domain Selection Guide

### Choose ISMS when:
- ✅ Analyzing comprehensive security policies
- ✅ Evaluating enterprise security programs
- ✅ Aligning with ISO 27001
- ✅ Need complete CSF coverage

### Choose Risk Management when:
- ✅ Focusing on risk assessment processes
- ✅ Evaluating risk governance
- ✅ Reviewing threat management
- ✅ Analyzing vulnerability management programs

### Choose Patch Management when:
- ✅ Reviewing vulnerability remediation policies
- ✅ Evaluating patch deployment processes
- ✅ Assessing software lifecycle management
- ✅ Analyzing configuration management

### Choose Data Privacy when:
- ✅ Reviewing data protection policies
- ✅ Evaluating access control mechanisms
- ✅ Assessing privacy training programs
- ✅ Analyzing data confidentiality controls
- ⚠️ Note: Supplement with privacy-specific frameworks for complete compliance

### Use Auto-Detection when:
- ✅ Unsure of policy focus
- ✅ Need comprehensive analysis
- ✅ Evaluating multi-domain policies
- ✅ Performing initial assessment

---

## Domain Comparison

| Domain | Subcategories | Functions | Analysis Time | Best For |
|--------|--------------|-----------|---------------|----------|
| ISMS | All (~106) | All 6 | Longest | Comprehensive security |
| Risk Management | 9 | GV, ID | Fast | Risk processes |
| Patch Management | 5 | ID, PR | Fastest | Vulnerability mgmt |
| Data Privacy | 7 | PR | Fast | Data protection |
| Auto-detect | All (~106) | All 6 | Longest | General assessment |

---

## NIST CSF 2.0 Function Reference

For context, here are the six NIST CSF 2.0 functions:

1. **Govern (GV)**: Organizational cybersecurity risk management strategy, expectations, and policy
2. **Identify (ID)**: Understanding organizational context, assets, and risks
3. **Protect (PR)**: Safeguards to manage cybersecurity risks
4. **Detect (DE)**: Activities to identify cybersecurity events
5. **Respond (RS)**: Actions regarding detected cybersecurity incidents
6. **Recover (RC)**: Restoration of capabilities or services impaired by incidents

---

## Adding New Domains

To add a new domain, modify `analysis/domain_mapper.py`:

```python
DOMAIN_MAPPINGS = {
    'your_domain': {
        'description': 'Your Domain Description',
        'prioritize_functions': ['Govern', 'Identify'],  # Or []
        'prioritize_subcategories': ['GV.RM-01', 'ID.RA-01'],  # Specific subcategories
        'warning': 'Optional warning message'  # Or None
    }
}
```

Then update `cli/main.py` to add the domain to choices:

```python
parser.add_argument(
    "--domain",
    choices=["isms", "risk_management", "patch_management", "data_privacy", "your_domain"],
    ...
)
```

---

## Examples

### Example 1: ISMS Analysis
```bash
uv run policy-analyzer \
  --policy-path company_security_policy.pdf \
  --domain isms \
  --output-dir ./isms_results
```

### Example 2: Risk Management Focus
```bash
uv run policy-analyzer \
  --policy-path risk_assessment_policy.docx \
  --domain risk_management \
  --output-dir ./risk_results
```

### Example 3: Patch Management Review
```bash
uv run policy-analyzer \
  --policy-path patch_management_procedure.txt \
  --domain patch_management \
  --output-dir ./patch_results
```

### Example 4: Privacy Policy Analysis
```bash
uv run policy-analyzer \
  --policy-path data_privacy_policy.pdf \
  --domain data_privacy \
  --output-dir ./privacy_results \
  --verbose
```

### Example 5: Auto-Detection
```bash
uv run policy-analyzer \
  --policy-path general_policy.pdf \
  --output-dir ./general_results
```

---

## FAQ

**Q: Can I analyze a policy against multiple domains?**
A: Not in a single run. Run the analyzer multiple times with different domains to compare results.

**Q: What happens if I specify the wrong domain?**
A: The analysis will still complete but may miss relevant gaps or flag irrelevant ones. Choose the domain that best matches your policy focus.

**Q: Is ISMS the same as auto-detect?**
A: Yes, both evaluate against all CSF subcategories. ISMS is explicit about comprehensive security analysis.

**Q: Can I customize domain prioritization?**
A: Yes, modify `analysis/domain_mapper.py` or create a custom configuration file.

**Q: Does domain selection affect the LLM analysis?**
A: Yes, the domain context is provided to the LLM to focus its analysis on relevant subcategories.

**Q: Which domain is fastest?**
A: Patch Management (5 subcategories) is fastest, followed by Data Privacy (7) and Risk Management (9).

---

## Summary

Choose the domain that best matches your policy focus:
- **ISMS**: Comprehensive security (all subcategories)
- **Risk Management**: Risk processes and governance (9 subcategories)
- **Patch Management**: Vulnerability and patch processes (5 subcategories)
- **Data Privacy**: Data protection and access control (7 subcategories)
- **Auto-detect**: General assessment (all subcategories)

Each domain provides targeted analysis with appropriate CSF subcategory prioritization.
