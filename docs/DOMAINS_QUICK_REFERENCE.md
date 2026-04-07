# Domains Quick Reference

## Supported Domains

| Domain | ID | Subcategories | Speed | Use For |
|--------|----|--------------:|-------|---------|
| **ISMS** | `isms` | ~106 | Slow | Comprehensive security |
| **Risk Management** | `risk_management` | 9 | Fast | Risk processes |
| **Patch Management** | `patch_management` | 5 | Fastest | Vulnerability mgmt |
| **Data Privacy** | `data_privacy` | 7 | Fast | Data protection |
| **Auto-detect** | _(none)_ | ~106 | Slow | General assessment |

## Quick Commands

```bash
# ISMS (comprehensive)
uv run policy-analyzer --policy-path policy.pdf --domain isms

# Risk Management
uv run policy-analyzer --policy-path policy.pdf --domain risk_management

# Patch Management
uv run policy-analyzer --policy-path policy.pdf --domain patch_management

# Data Privacy
uv run policy-analyzer --policy-path policy.pdf --domain data_privacy

# Auto-detect
uv run policy-analyzer --policy-path policy.pdf
```

## Domain Focus Areas

### ISMS
- All 6 CSF functions
- Complete security posture
- ISO 27001 alignment

### Risk Management
- **GV.RM**: Risk management strategy
- **GV.OV**: Organizational strategy
- **ID.RA**: Risk assessment

### Patch Management
- **ID.RA**: Vulnerability identification
- **PR.DS**: Data protection
- **PR.PS**: Platform security

### Data Privacy
- **PR.AA**: Identity & access
- **PR.DS**: Data security
- **PR.AT**: Awareness & training

⚠️ **Privacy Note**: CSF is not a complete privacy framework

## Selection Guide

```
Need comprehensive analysis? → isms
Focused on risk processes? → risk_management
Reviewing patch procedures? → patch_management
Analyzing data protection? → data_privacy
Not sure? → (no domain flag)
```

## CSF Functions

- **GV**: Govern
- **ID**: Identify
- **PR**: Protect
- **DE**: Detect
- **RS**: Respond
- **RC**: Recover
