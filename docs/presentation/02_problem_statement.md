# 02 – Problem Statement

## Problem this repository addresses

Organizations maintain policy documents but often lack a repeatable way to:

- Map policy content to NIST CSF 2.0 outcomes
- Identify missing or partial controls quickly
- Produce remediation wording and action plans
- Preserve traceability for compliance evidence

## Intended solution in this repository

A local execution system that:

1. Parses policy text
2. Compares policy evidence against CSF subcategories
3. Classifies coverage and identifies gaps
4. Produces structured remediation outputs
5. Records execution metadata in audit logs

## Why “offline” matters here

Policy documents can be sensitive. The design intent is to keep processing on local infrastructure using:

- Local embedding models
- Local vector store
- Local LLM backends (Ollama localhost or llama.cpp local file)

## Output-oriented problem framing

The repository is designed to convert one policy input into an actionable output bundle:

- `gap_analysis_report.(md|json)`
- `revised_policy.md`
- `implementation_roadmap.(md|json)`
- Audit entry under `audit_logs/`
