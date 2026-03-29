# Limitations

This document describes the known limitations, constraints, and edge cases of the Offline Policy Gap Analyzer.

## Document Processing Limitations

### OCR Not Supported

**Limitation**: The system cannot process scanned PDFs that contain only images without a text layer.

**Impact**: Policies that are scanned documents or image-based PDFs will be rejected with an error message.

**Workaround**: 
- Use external OCR tools (e.g., Adobe Acrobat, Tesseract) to convert scanned PDFs to text-based PDFs
- Request the original digital document from the policy author
- Manually transcribe the policy to a text-based format (DOCX or TXT)

**Rationale**: OCR support would require additional dependencies (Tesseract, pytesseract) and network calls for cloud OCR services, violating the offline operation constraint. OCR accuracy is also variable and could introduce errors into the analysis.

### Document Size Limit

**Limitation**: Maximum document size is 100 pages.

**Impact**: Policies exceeding 100 pages will be rejected or truncated.

**Workaround**:
- Split large policy documents into logical sections (e.g., separate ISMS policy from incident response procedures)
- Analyze each section independently
- Manually consolidate the gap reports

**Rationale**: Consumer hardware memory constraints (8-16GB RAM) limit the size of documents that can be processed efficiently. Larger documents risk memory exhaustion and significantly slower processing times.

### Complex Table Extraction

**Limitation**: While pdfplumber provides fallback support for complex tables, some highly complex or nested table structures may not extract perfectly.

**Impact**: Policy content within complex tables may be partially lost or misformatted.

**Workaround**:
- Convert complex tables to simpler formats before analysis
- Use DOCX format which preserves table structure better
- Manually review extracted text for completeness

**Rationale**: PDF table extraction is inherently challenging due to the lack of semantic structure in PDF format. The system uses best-effort extraction with PyMuPDF and pdfplumber fallback.

### Unsupported File Formats

**Limitation**: Only PDF, DOCX, and TXT formats are supported.

**Impact**: Policies in other formats (ODT, RTF, HTML, etc.) cannot be analyzed directly.

**Workaround**:
- Convert documents to supported formats using office software
- Export HTML to PDF or copy text to TXT file
- Use online conversion tools (requires internet)

**Rationale**: Supporting additional formats would increase dependency complexity and maintenance burden. The three supported formats cover the vast majority of policy documents.

## Framework Scope Limitations

### NIST CSF 2.0 Cybersecurity Focus

**Limitation**: The NIST Cybersecurity Framework 2.0 addresses cybersecurity aspects of data protection but is not a complete privacy framework.

**Impact**: Privacy-specific compliance requirements (GDPR, CCPA, HIPAA privacy rules) may extend beyond CSF scope.

**Warning**: When analyzing data privacy policies, the system logs a warning:
> "The NIST CSF 2.0 addresses cybersecurity aspects of data protection but is not a complete privacy framework. Privacy-specific compliance requirements may extend beyond CSF scope."

**Workaround**:
- Use additional privacy frameworks (NIST Privacy Framework, ISO 27701) for comprehensive privacy analysis
- Manually review privacy policies against specific regulatory requirements
- Supplement CSF analysis with privacy-specific checklists

**Rationale**: NIST CSF 2.0 is a cybersecurity framework, not a privacy framework. While it includes data protection controls (PR.DS, PR.AA), it does not cover all privacy principles (notice, choice, access, correction, etc.).

### CIS Guide Coverage

**Limitation**: The system relies on the CIS MS-ISAC NIST CSF 2.0 Policy Template Guide (2024) as the reference baseline. This guide covers 49 of the 106 NIST CSF 2.0 subcategories.

**Impact**: Subcategories not mapped in the CIS guide will not be analyzed.

**Workaround**:
- Manually review policies against the complete NIST CSF 2.0 framework
- Supplement with additional policy templates for uncovered subcategories
- Update the Reference Catalog with custom mappings

**Rationale**: The CIS guide provides practical, actionable policy templates for the most critical CSF subcategories. Full CSF coverage would require significantly more reference data and longer analysis times.

## Hardware and Performance Limitations

### Consumer Hardware Constraints

**Limitation**: The system is optimized for consumer hardware (8-16GB RAM, CPU-only).

**Impact**: 
- Analysis of 20-page policies takes ~10 minutes on 8GB RAM systems
- Larger policies (50+ pages) may take 20-30 minutes
- Memory usage can approach 90% of available RAM during analysis

**Workaround**:
- Close other applications to free memory
- Use smaller LLM models (3B instead of 7B parameters)
- Reduce chunk size and top_k retrieval parameters in configuration
- Process policies in smaller sections

**Rationale**: The system is designed for offline operation on typical laptops without requiring specialized hardware or cloud resources.

### CPU-Only Operation

**Limitation**: The system does not utilize GPU acceleration.

**Impact**: LLM inference and embedding generation are slower than GPU-accelerated alternatives.

**Performance**:
- Embedding generation: ~100 chunks/minute on CPU
- LLM generation: ~10-15 tokens/second on CPU (3B models)
- LLM generation: ~5-8 tokens/second on CPU (7B models)

**Workaround**:
- Use smaller models for faster processing
- Enable GPU acceleration manually (requires llama-cpp-python with CUDA support)
- Run analysis overnight for large policy sets

**Rationale**: GPU support would require CUDA/ROCm dependencies and is not available on all consumer hardware. CPU-only operation ensures maximum compatibility.

### Memory Management

**Limitation**: When memory usage exceeds 90% of available RAM, the system truncates context to prevent crashes.

**Impact**: Very long policy documents may have context truncated, potentially missing some content in LLM reasoning.

**Workaround**:
- Use systems with more RAM (16GB recommended)
- Split large policies into smaller sections
- Use models with smaller context windows to reduce memory footprint

**Rationale**: Graceful degradation prevents system crashes and allows analysis to complete even on memory-constrained systems.

## Analysis Quality Limitations

### LLM Hallucination Risk

**Limitation**: Despite the two-stage safety architecture, LLMs can still generate incorrect or hallucinated content.

**Impact**: Gap explanations, suggested fixes, and revised policy text may contain inaccuracies.

**Mitigation**:
- Two-stage architecture minimizes hallucination by using deterministic Stage A for most decisions
- Stage B uses low temperature (0.1) for conservative, factual outputs
- Strict output schemas constrain LLM responses
- Mandatory human-review warning appended to all revised policies

**Workaround**:
- Always review LLM-generated content with qualified legal counsel and compliance officers
- Cross-reference suggested fixes with official NIST CSF 2.0 documentation
- Validate revised policies against organizational requirements

**Rationale**: LLMs are probabilistic models and cannot guarantee 100% accuracy. Human review is essential for policy adoption.

### Ambiguous Coverage Detection

**Limitation**: Some policy provisions may be ambiguous, making it difficult to determine coverage status definitively.

**Impact**: Subcategories marked as "Ambiguous" require manual review to determine actual coverage.

**Handling**: The system flags ambiguous subcategories in the gap report with a recommendation for manual review.

**Workaround**:
- Review ambiguous subcategories manually against NIST CSF 2.0 documentation
- Clarify ambiguous policy language to improve future analysis
- Use domain-specific prioritization to focus on critical subcategories

**Rationale**: Natural language is inherently ambiguous. The system errs on the side of caution by flagging uncertain cases rather than making incorrect determinations.

### Terminology Variations

**Limitation**: Policies may use different terminology than NIST CSF 2.0 (e.g., "vulnerability assessment" vs. "vulnerability scanning").

**Impact**: Hybrid retrieval may miss some relevant policy provisions if terminology differs significantly.

**Mitigation**:
- Hybrid retrieval combines semantic similarity (handles synonyms) with keyword matching (exact terms)
- Cross-encoder reranking improves precision
- Domain-specific prioritization focuses on relevant subcategories

**Workaround**:
- Use consistent terminology aligned with NIST CSF 2.0 in policies
- Manually review gap reports for missed provisions
- Update Reference Catalog keywords to include organizational terminology

**Rationale**: Organizations use varied terminology. The hybrid approach balances precision and recall.

## Operational Limitations

### Offline Operation Requirement

**Limitation**: All models and reference data must be downloaded before offline operation.

**Impact**: Initial setup requires internet connectivity. Model downloads can take 30-60 minutes depending on connection speed.

**Workaround**:
- Download models on a system with internet access
- Transfer model files to offline systems via USB or network share
- Use `scripts/download_models.py --verify` to check model integrity

**Rationale**: Offline operation is a core requirement for data sovereignty and sensitive document handling.

### Single-User Operation

**Limitation**: The system is designed for single-user, local operation. It does not support multi-user collaboration or concurrent analysis.

**Impact**: Multiple users cannot collaborate on policy analysis in real-time.

**Workaround**:
- Share output files (gap reports, revised policies) via email or file sharing
- Use version control (Git) to track policy revisions
- Run multiple instances on separate systems

**Rationale**: Multi-user support would require server infrastructure and network connectivity, violating the offline constraint.

### No Real-Time Monitoring

**Limitation**: The system performs point-in-time analysis. It does not monitor policies for continuous compliance or detect policy drift over time.

**Impact**: Policies must be re-analyzed manually to detect changes or new gaps.

**Workaround**:
- Schedule periodic policy reviews (quarterly, annually)
- Re-run analysis after policy updates
- Use version control to track policy changes over time

**Rationale**: Continuous monitoring would require persistent background processes and is beyond the scope of offline, on-demand analysis.

## Known Edge Cases

### Empty or Minimal Policies

**Edge Case**: Policies with very little content (< 1 page) may not provide sufficient context for meaningful analysis.

**Handling**: The system will analyze the content but may identify most subcategories as "Missing."

**Recommendation**: Ensure policies have sufficient detail before analysis.

### Policies in Non-English Languages

**Edge Case**: The system is designed for English-language policies. Non-English policies may produce poor results.

**Handling**: Embedding models and LLMs are trained primarily on English text. Non-English content may not be understood correctly.

**Workaround**: Translate policies to English before analysis using professional translation services.

### Highly Technical or Domain-Specific Policies

**Edge Case**: Policies with highly technical jargon or domain-specific terminology may not align well with NIST CSF 2.0 language.

**Handling**: Hybrid retrieval and semantic similarity help bridge terminology gaps, but some mismatches may occur.

**Workaround**: Review gap reports carefully and manually validate coverage for technical provisions.

### Policies with Extensive Cross-References

**Edge Case**: Policies that heavily reference external documents (e.g., "See Incident Response Plan for details") may appear to have gaps.

**Handling**: The system analyzes only the provided document. External references are not followed.

**Workaround**: Analyze all related policy documents separately and manually consolidate results.

## Future Improvements

The following limitations may be addressed in future versions:

### Planned Enhancements

1. **Agentic RAG Architecture**: Multi-agent workflows (Planner Agent, Retriever Agent, Critic Agent) for improved precision
2. **Iterative Self-Correction**: LLM-based validation and refinement of gap analysis results
3. **Enhanced Privacy Framework Support**: Integration with NIST Privacy Framework and ISO 27701
4. **Multi-Language Support**: Embedding models and LLMs trained on multiple languages
5. **Incremental Analysis**: Track policy changes over time and identify new gaps
6. **GPU Acceleration**: Optional GPU support for faster processing

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed discussion of future architectural improvements.

## Reporting Issues

If you encounter limitations not documented here, please report them:

1. Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for known issues
2. Review [GitHub Issues](https://github.com/your-repo/issues) for existing reports
3. Submit a new issue with:
   - Description of the limitation
   - Steps to reproduce
   - Expected vs. actual behavior
   - System configuration (OS, RAM, Python version)
   - Sample policy (if not sensitive)

## Disclaimer

This system is provided as a tool to assist with policy gap analysis. It does not replace professional legal counsel, compliance expertise, or security leadership judgment. All outputs must be reviewed and validated by qualified personnel before adoption.

The CIS MS-ISAC templates are advisory and may not reflect the most recent applicable standards or your organization's specific legal, regulatory, or operational requirements.
