# 08 – How to Use

## End-user usage flow

1. Ensure local models and dependencies are installed.
2. Ensure policy file is text-based (`.pdf/.docx/.txt/.md` supported).
3. Run analysis command with optional domain/config.
4. Review generated outputs in run directory.
5. Review audit log entry for traceability.
6. Perform mandatory human review of AI-generated revision text.

## Input expectations

- PDF must contain extractable text (OCR/scanned-only PDFs rejected).
- Maximum document length enforced by parser logic (`MAX_PAGES = 100`).
- Very short content (<50 chars after parse) is rejected by pipeline validation.

## Understanding outputs

- Gap report JSON/Markdown: gaps, covered subcategories, metadata
- Revised policy: draft revisions and mandatory warning language
- Roadmap: immediate/near-term/medium-term actions

## Common mistakes

- Using scanned PDFs without OCR text layer
- Missing local embedding/LLM resources
- Assuming stale docs command variants are current
- Supplying config schema that does not match loader expectations

## Offline verification checklist

- Confirm LLM backend points to localhost Ollama or local GGUF (llama.cpp)
- Confirm embedding model loads from local filesystem path
- Confirm no cloud API keys are required by active path
- Run in network-restricted environment and validate successful completion
