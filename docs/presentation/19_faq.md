# 19 – FAQ

## Is this truly fully offline?

Operationally yes after local models/dependencies are already installed and local backend configuration is used.

## Which CLI should I trust?

Primary execution path is `cli/main.py` (`policy-analyzer` / `python -m cli.main`).

## What file types are supported?

`.pdf`, `.docx`, `.txt`, `.md`.

## Does it support scanned PDFs?

No. Scanned PDFs without text layer are rejected.

## How many CSF subcategories are analyzed?

Catalog expects 49 NIST CSF 2.0 subcategories.

## Does it replace human compliance/legal review?

No. Generated revisions are explicitly draft-only and require human approval.

## Why do some docs/commands seem inconsistent?

Repository contains overlapping generations of docs/CLI/test tooling; use implementation-grounded paths documented in this package.
