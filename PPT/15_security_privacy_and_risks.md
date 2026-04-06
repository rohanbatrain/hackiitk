# 15 – Security, Privacy, and Risks

## Security/privacy posture in code

- Local processing architecture intended to reduce data exfiltration risk
- Audit logs include file hash and metadata for traceability
- Stage B constrained schema output reduces free-form model drift
- Mandatory warning on revised policy output requires human review

## Trust boundaries

- User document input boundary
- Local model/runtime boundary (embedding + LLM)
- File artifact boundary (reports/roadmaps/audit logs)

## Risk points

- Malicious document parsing risk (PDF parser attack surface)
- Placeholder retrieval/chunk linking may reduce analytical correctness
- Config mismatch can lead to unintended defaults and misleading operations
- “Immutable” audit logging is best-effort file-permission approach, not cryptographic append-only ledger
- If Ollama configured beyond localhost or misconfigured environment, privacy assumption can be broken

## Governance requirement from implementation

AI-generated revised policy text is explicitly draft-only and must be reviewed by legal/compliance/security leadership before adoption.
