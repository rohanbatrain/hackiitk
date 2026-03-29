# Implementation Plan: Offline Policy Gap Analyzer

## Overview

This implementation plan converts the design into actionable coding tasks for building a Python-based offline policy gap analyzer. The system performs NIST CSF 2.0 gap analysis using hybrid RAG, two-stage safety architecture, and local LLM execution on consumer hardware. Tasks are organized incrementally with property-based tests integrated throughout to validate correctness properties early.

## Tasks

- [x] 1. Project setup and infrastructure
  - Create directory structure: `ingestion/`, `reference_builder/`, `retrieval/`, `analysis/`, `revision/`, `reporting/`, `models/`, `tests/`, `docs/`
  - Create `requirements.txt` with pinned versions: `PyMuPDF>=1.23.0`, `pdfplumber>=0.10.0`, `python-docx>=1.0.0`, `sentence-transformers>=2.2.0`, `chromadb>=0.4.0`, `langchain>=0.1.0`, `llama-cpp-python>=0.2.0` or `ollama-python>=0.1.0`, `hypothesis>=6.90.0`, `pytest>=7.4.0`, `pyyaml>=6.0`, `rank-bm25>=0.2.0`
  - Create `config.yaml` with default parameters: chunk_size=512, overlap=50, top_k=5, temperature=0.1, max_tokens=512
  - Create `setup.py` or `pyproject.toml` for package installation
  - Create `.gitignore` for Python projects (exclude `models/`, `__pycache__/`, `*.pyc`, `outputs/`)
  - _Requirements: 17.2, 17.3, 17.4, 18.1, 18.6, 20.2_


- [ ] 2. Core data models and schemas
  - [x] 2.1 Create data models module (`models/domain.py`)
    - Implement dataclasses: `ParsedDocument`, `DocumentStructure`, `Heading`, `Section`, `TextChunk`, `CSFSubcategory`, `RetrievalResult`, `CoverageAssessment`, `GapDetail`, `GapAnalysisReport`, `Revision`, `RevisedPolicy`, `ActionItem`, `ImplementationRoadmap`, `AuditLogEntry`
    - Add type hints for all fields
    - Include docstrings for each dataclass
    - _Requirements: Design data models section_
  
  - [x] 2.2 Write property test for data model serialization
    - **Property 7: Reference Catalog Persistence Round-Trip**
    - **Validates: Requirements 3.4, 13.4**
    - Test that serializing any data model to JSON then deserializing produces equivalent structure
    - Use Hypothesis to generate random data model instances
  
  - [x] 2.3 Create JSON schemas (`models/schemas.py`)
    - Define JSON schema for gap analysis report with fields: subcategory_id, description, status, evidence_quote, gap_explanation, severity, suggested_fix
    - Define JSON schema for implementation roadmap with fields: action_id, timeframe, severity, effort, csf_subcategory, policy_section, description, technical_steps, administrative_steps, physical_steps
    - Add schema validation functions using `jsonschema` library
    - _Requirements: 14.9_

- [x] 3. Document parsing components
  - [x] 3.1 Implement Document Parser (`ingestion/document_parser.py`)
    - Create `DocumentParser` class with `parse()` method
    - Implement PDF parsing using PyMuPDF as primary parser
    - Implement pdfplumber as fallback for complex tables
    - Implement DOCX parsing using python-docx
    - Implement TXT parsing with encoding detection
    - Add OCR detection and rejection logic for scanned PDFs
    - Implement structure extraction: headings, sections, paragraphs
    - Add 100-page limit check
    - Raise `UnsupportedFormatError`, `OCRRequiredError`, `ParsingError` exceptions
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6, 2.7, 2.8_
  
  - [x] 3.2 Write unit tests for Document Parser
    - Test PDF extraction with sample policy PDF
    - Test pdfplumber fallback with complex table PDF
    - Test OCR-required PDF rejection
    - Test DOCX structure preservation
    - Test TXT file reading
    - Test unsupported format error
    - Test 100-page limit enforcement
    - _Requirements: 2.1-2.9_
  
  - [x] 3.3 Write property test for multi-format parsing
    - **Property 3: Multi-Format Document Parsing**
    - **Validates: Requirements 2.1, 2.4, 2.5, 2.7**
    - Test that any valid PDF/DOCX/TXT file produces ParsedDocument with preserved structure
  
  - [x] 3.4 Write property test for unsupported format rejection
    - **Property 4: Unsupported Format Rejection**
    - **Validates: Requirements 2.6**
    - Test that any unsupported format returns error with supported formats list
  
  - [x] 3.5 Write property test for graceful parsing failure
    - **Property 5: Graceful Parsing Failure**
    - **Validates: Requirements 2.9**
    - Test that parsing failures log errors and terminate gracefully without crashes

- [x] 4. Text chunking component
  - [x] 4.1 Implement Text Chunker (`ingestion/text_chunker.py`)
    - Create `TextChunker` class with configurable chunk_size and overlap
    - Implement `chunk()` method using LangChain's RecursiveCharacterTextSplitter
    - Add structure-aware splitting logic (prefer boundaries at headings, paragraphs)
    - Add sentence preservation logic
    - Track metadata: source_file, start_pos, end_pos, page_number, section_title
    - Generate unique chunk_id for each chunk
    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 4.2 Write property test for chunk size constraint
    - **Property 8: Chunk Size Constraint**
    - **Validates: Requirements 4.1**
    - Test that all chunks have maximum 512 tokens for any input text
  
  - [x] 4.3 Write property test for chunk overlap consistency
    - **Property 9: Chunk Overlap Consistency**
    - **Validates: Requirements 4.2**
    - Test that consecutive chunks have exactly 50 tokens overlap
  
  - [x] 4.4 Write property test for structural boundary preservation
    - **Property 10: Structural Boundary Preservation**
    - **Validates: Requirements 4.3**
    - Test that chunking prefers structural boundaries when possible
  
  - [x] 4.5 Write property test for sentence preservation
    - **Property 11: Sentence Preservation in Chunks**
    - **Validates: Requirements 4.4**
    - Test that complete sentences are preserved within chunks when possible

- [x] 5. Checkpoint - Ensure document ingestion tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [ ] 6. Reference catalog builder
  - [ ] 6.1 Implement Reference Catalog (`reference_builder/reference_catalog.py`)
    - Create `ReferenceCatalog` class with CIS guide parsing logic
    - Implement `build_from_cis_guide()` method to parse CIS PDF
    - Extract all 49 NIST CSF 2.0 subcategories with fields: subcategory_id, function, category, description, keywords, domain_tags, mapped_templates, priority
    - Implement `persist()` method to save catalog as JSON
    - Implement `load()` method to load catalog from JSON
    - Implement `get_subcategory()`, `get_by_function()`, `get_by_domain()` query methods
    - Add validation to ensure all 49 subcategories present
    - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 3.6_
  
  - [ ] 6.2 Write property test for catalog completeness
    - **Property 6: Reference Catalog Completeness**
    - **Validates: Requirements 3.2, 3.3, 3.6**
    - Test that any built catalog contains all 49 subcategories with required fields
  
  - [ ] 6.3 Write property test for catalog persistence round-trip
    - **Property 7: Reference Catalog Persistence Round-Trip**
    - **Validates: Requirements 3.4, 13.4**
    - Test that persisting then loading catalog produces equivalent structure
  
  - [ ] 6.4 Create CIS guide parser helper
    - Implement logic to extract CSF subcategory mappings from CIS PDF
    - Parse policy template recommendations for each subcategory
    - Extract keywords and domain tags from template descriptions
    - Assign priority levels (critical/high/medium/low) based on CIS guidance
    - _Requirements: 3.1, 3.2_

- [x] 7. Embedding engine component
  - [x] 7.1 Implement Embedding Engine (`retrieval/embedding_engine.py`)
    - Create `EmbeddingEngine` class with local model loading
    - Load sentence-transformers model (all-MiniLM-L6-v2) from local path
    - Implement `embed_text()` for single text embedding
    - Implement `embed_batch()` for efficient batch processing
    - Implement `verify_offline()` to check no network calls
    - Add CPU optimization using numpy operations
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_
  
  - [x] 7.2 Write property test for embedding dimensionality
    - **Property 13: Embedding Dimensionality**
    - **Validates: Requirements 5.3**
    - Test that any text produces exactly 384-dimensional vector
  
  - [x] 7.3 Write property test for complete embedding coverage
    - **Property 14: Complete Embedding Coverage**
    - **Validates: Requirements 5.4, 5.5**
    - Test that all chunks in any document are embedded without skipping
  
  - [x] 7.4 Write property test for offline operation
    - **Property 1: Complete Offline Operation**
    - **Validates: Requirements 1.1, 1.2, 5.2**
    - Test that embedding generation makes no network calls
    - Use network monitoring to verify offline operation
  
  - [x] 7.5 Write unit tests for embedding performance
    - Test batch processing efficiency (100+ chunks per minute)
    - Test CPU-only operation
    - Test memory usage stays within bounds
    - _Requirements: 5.6, 5.7_

- [x] 8. Vector store component
  - [x] 8.1 Implement Vector Store (`retrieval/vector_store.py`)
    - Create `VectorStore` class with ChromaDB backend
    - Implement `add_embeddings()` to store embeddings with metadata
    - Implement `similarity_search()` for top-k retrieval
    - Implement `load_collection()` and `persist_collection()` for disk storage
    - Support separate collections for reference catalog and policy embeddings
    - Store metadata: source_text, CSF_Subcategory, chunk_id
    - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6_
  
  - [x] 8.2 Write property test for persistence round-trip
    - **Property 15: Vector Store Persistence Round-Trip**
    - **Validates: Requirements 6.1, 6.5**
    - Test that persisting then loading embeddings produces equivalent data
  
  - [x] 8.3 Write property test for similarity search result count
    - **Property 16: Similarity Search Result Count**
    - **Validates: Requirements 6.3**
    - Test that similarity search returns exactly k results (or fewer if collection smaller)
  
  - [x] 8.4 Write property test for metadata preservation
    - **Property 17: Metadata Preservation in Vector Store**
    - **Validates: Requirements 6.4**
    - Test that metadata is preserved and retrievable with embeddings
  
  - [x] 8.5 Write property test for collection isolation
    - **Property 18: Collection Isolation**
    - **Validates: Requirements 6.6**
    - Test that queries to one collection never return results from another

- [x] 9. Checkpoint - Ensure embedding and storage tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 10. Hybrid retrieval engine
  - [x] 10.1 Implement sparse retrieval (`retrieval/sparse_retriever.py`)
    - Create `SparseRetriever` class using BM25 algorithm
    - Implement keyword-based retrieval using rank-bm25 library
    - Index CSF subcategory keywords for matching
    - Return top-k results with relevance scores
    - _Requirements: 7.2_
  
  - [x] 10.2 Implement cross-encoder reranker (`retrieval/reranker.py`)
    - Create `Reranker` class with local cross-encoder model
    - Load cross-encoder model (e.g., cross-encoder/ms-marco-MiniLM-L-6-v2)
    - Implement `rerank()` method to score query-document pairs
    - Return reranked results sorted by relevance
    - _Requirements: 7.6_
  
  - [x] 10.3 Implement Hybrid Retriever (`retrieval/hybrid_retriever.py`)
    - Create `HybridRetriever` class orchestrating dense + sparse retrieval
    - Implement `retrieve()` method combining both approaches
    - Implement `dense_retrieve()` using vector store similarity search
    - Implement `sparse_retrieve()` using BM25 keyword matching
    - Merge and deduplicate results from both methods
    - Apply cross-encoder reranking to merged results
    - Return top-k final results with CSF subcategory metadata
    - Integrate with LangChain retriever abstraction
    - _Requirements: 7.1, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9_
  
  - [x] 10.4 Write property test for hybrid retrieval combination
    - **Property 19: Hybrid Retrieval Combination**
    - **Validates: Requirements 7.1, 7.3, 7.4, 7.5, 7.6**
    - Test that retrieval combines dense + sparse, merges, deduplicates, and reranks
  
  - [x] 10.5 Write property test for retrieval result metadata
    - **Property 20: Retrieval Result Metadata**
    - **Validates: Requirements 7.8**
    - Test that all retrieved chunks include CSF subcategory identifiers
  
  - [x] 10.6 Write unit tests for retrieval accuracy
    - Test dense retrieval finds semantically similar content
    - Test sparse retrieval finds exact keyword matches
    - Test reranking improves relevance ordering
    - Test deduplication removes duplicate results
    - _Requirements: 7.1-7.9_

- [x] 11. LLM runtime component
  - [x] 11.1 Implement LLM Runtime (`analysis/llm_runtime.py`)
    - Create `LLMRuntime` class supporting llama.cpp and Ollama backends
    - Implement model loading from local GGUF files
    - Implement `generate()` method with temperature and max_tokens parameters
    - Implement `generate_structured()` for JSON schema-constrained output
    - Implement `check_memory()` for RAM usage monitoring
    - Implement `verify_offline()` to ensure no network calls
    - Add context truncation at 90% RAM threshold
    - Integrate with LangChain LLM abstraction
    - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5, 8.6, 8.7, 8.8_
  
  - [x] 11.2 Write property test for offline LLM operation
    - **Property 1: Complete Offline Operation**
    - **Validates: Requirements 1.1, 1.2, 8.5**
    - Test that LLM inference makes no network calls
  
  - [x] 11.3 Write property test for multi-model support
    - **Property 49: Multi-Model Support**
    - **Validates: Requirements 17.6**
    - Test that system loads and executes multiple model options (Qwen2.5-3B, Phi-3.5-mini, Mistral-7B, Qwen3-8B)
  
  - [x] 11.4 Write unit tests for LLM runtime
    - Test model loading from local path
    - Test memory monitoring and context truncation
    - Test structured JSON output generation
    - Test error handling for unavailable models
    - _Requirements: 8.1-8.8_

- [x] 12. Model download and setup script
  - [x] 12.1 Create model setup script (`scripts/setup_models.py`)
    - Download sentence-transformers model (all-MiniLM-L6-v2) to `models/embeddings/`
    - Download cross-encoder model to `models/reranker/`
    - Download default LLM model (Qwen2.5-3B-Instruct GGUF) to `models/llm/`
    - Verify model file integrity with checksums
    - Print download progress and storage locations
    - _Requirements: 17.2, 17.3, 17.4, 17.5_
  
  - [x] 12.2 Write property test for local resource verification
    - **Property 2: Local Resource Verification**
    - **Validates: Requirements 1.6, 17.1**
    - Test that system verifies all required resources exist before execution
    - Test that missing resources trigger descriptive errors with download instructions

- [x] 13. Checkpoint - Ensure retrieval and LLM tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 14. Gap analysis engine - Stage A
  - [x] 14.1 Implement Stage A evidence detector (`analysis/stage_a_detector.py`)
    - Create `StageADetector` class for deterministic evidence detection
    - Implement `detect_evidence()` method for each CSF subcategory
    - Calculate lexical score using keyword overlap from CSFSubcategory.keywords
    - Calculate semantic score using cosine similarity between embeddings
    - Apply section heuristics (boost score when section name matches CSF category)
    - Classify coverage status: Covered (>0.8), Partial (0.5-0.8), Missing (<0.3), Ambiguous (0.3-0.5)
    - Return `CoverageAssessment` with scores, evidence spans, and confidence
    - _Requirements: 9.2, 9.3, 9.4_
  
  - [x] 14.2 Write unit tests for Stage A scoring
    - Test lexical scoring with keyword matches
    - Test semantic scoring with embedding similarity
    - Test section heuristics boost scores correctly
    - Test coverage classification thresholds
    - Test evidence span extraction
    - _Requirements: 9.2, 9.3, 9.4_

- [x] 15. Gap analysis engine - Stage B
  - [x] 15.1 Implement Stage B constrained reasoner (`analysis/stage_b_reasoner.py`)
    - Create `StageBReasoner` class for LLM-based reasoning
    - Implement `reason_about_gap()` method for ambiguous/missing cases
    - Build prompt with: policy section, CSF subcategory text, evidence spans, strict JSON schema
    - Call LLM with low temperature (0.1) for deterministic output
    - Parse LLM response into structured `GapDetail` object
    - Validate JSON output conforms to schema
    - _Requirements: 9.5, 9.6_
  
  - [x] 15.2 Write property test for Stage B input constraint
    - **Property 23: Stage B Input Constraint**
    - **Validates: Requirements 9.5**
    - Test that Stage B only receives matched policy section, not entire document
  
  - [x] 15.3 Write unit tests for Stage B reasoning
    - Test prompt construction with required context
    - Test JSON schema validation
    - Test LLM response parsing
    - Test error handling for invalid JSON
    - _Requirements: 9.5, 9.6_

- [x] 16. Gap analysis engine - Integration
  - [x] 16.1 Implement Gap Analysis Engine (`analysis/gap_analysis_engine.py`)
    - Create `GapAnalysisEngine` class orchestrating Stage A and Stage B
    - Implement `analyze()` method as main entry point
    - Execute Stage A for all relevant CSF subcategories
    - Filter Covered subcategories (skip Stage B)
    - Execute Stage B only for Ambiguous and Missing subcategories
    - Assign severity levels: Critical/High/Medium/Low based on CSF priority
    - Generate `GapAnalysisReport` with all gaps and metadata
    - _Requirements: 9.1, 9.7, 9.11_
  
  - [x] 16.2 Write property test for two-stage execution
    - **Property 21: Two-Stage Analysis Execution**
    - **Validates: Requirements 9.1, 9.2, 9.3, 9.7**
    - Test that Stage A executes for all subcategories, Stage B only for Ambiguous/Missing
  
  - [x] 16.3 Write property test for coverage status classification
    - **Property 22: Coverage Status Classification**
    - **Validates: Requirements 9.4**
    - Test that each subcategory gets exactly one status: Covered/Partial/Missing/Ambiguous
  
  - [x] 16.4 Write property test for gap report completeness
    - **Property 24: Gap Report Completeness**
    - **Validates: Requirements 9.6, 9.9, 9.10, 9.11**
    - Test that all gaps include required fields: subcategory_id, description, status, evidence_quote, gap_explanation, severity, suggested_fix
  
  - [x] 16.5 Write property test for ambiguous subcategory flagging
    - **Property 25: Ambiguous Subcategory Flagging**
    - **Validates: Requirements 9.8**
    - Test that Ambiguous subcategories are flagged for manual review

- [x] 17. Output generation - Gap reports
  - [x] 17.1 Implement gap report generator (`reporting/gap_report_generator.py`)
    - Create `GapReportGenerator` class
    - Implement `generate_markdown()` to create gap_analysis_report.md
    - Implement `generate_json()` to create gap_analysis_report.json
    - Include metadata: analysis_date, model_version, input_file, prompt_version, config_hash, retrieval_params
    - Format markdown with sections for each gap, severity indicators, evidence quotes
    - Validate JSON conforms to documented schema
    - _Requirements: 9.12, 14.1, 14.2, 14.7, 14.9_
  
  - [x] 17.2 Write property test for dual format generation
    - **Property 26: Dual Format Gap Report Generation**
    - **Validates: Requirements 9.12, 14.1, 14.2**
    - Test that both markdown and JSON reports are generated for any analysis
  
  - [x] 17.3 Write property test for JSON schema conformance
    - **Property 42: JSON Schema Conformance**
    - **Validates: Requirements 14.9**
    - Test that JSON output conforms to documented schema with all required fields

- [x] 18. Checkpoint - Ensure gap analysis tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 19. Policy revision engine
  - [x] 19.1 Implement Policy Revision Engine (`revision/policy_revision_engine.py`)
    - Create `PolicyRevisionEngine` class
    - Implement `revise()` method to generate revised policy from gaps
    - Implement `inject_clause()` to add new clauses for Missing subcategories
    - Implement `strengthen_clause()` to improve Partial coverage
    - Implement `append_warning()` to add mandatory human-review disclaimer
    - Preserve original policy structure and tone in prompts
    - Cite CSF subcategory for each revision
    - Use low temperature (0.1) for conservative revisions
    - Track revisions in `Revision` objects with original/revised text
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8_
  
  - [x] 19.2 Write property test for comprehensive policy revision
    - **Property 27: Comprehensive Policy Revision**
    - **Validates: Requirements 10.1, 10.3, 10.4**
    - Test that all gaps are addressed by injection or strengthening
  
  - [x] 19.3 Write property test for policy content preservation
    - **Property 28: Policy Content Preservation**
    - **Validates: Requirements 10.5**
    - Test that no existing valid provisions are removed
  
  - [x] 19.4 Write property test for revision citation traceability
    - **Property 29: Revision Citation Traceability**
    - **Validates: Requirements 10.6**
    - Test that each revision cites specific CSF subcategory
  
  - [x] 19.5 Write property test for mandatory warning
    - **Property 30: Mandatory Human-Review Warning**
    - **Validates: Requirements 10.8**
    - Test that all revised policies include mandatory legal disclaimer
  
  - [x] 19.6 Write property test for revised policy output format
    - **Property 31: Revised Policy Output Format**
    - **Validates: Requirements 10.7**
    - Test that revised policy is output in markdown format

- [x] 20. Roadmap generator
  - [x] 20.1 Implement Roadmap Generator (`reporting/roadmap_generator.py`)
    - Create `RoadmapGenerator` class
    - Implement `generate()` method to create implementation roadmap from gaps
    - Implement `prioritize()` to categorize gaps: Critical/High → Immediate, Medium → Near-term, Low → Medium-term
    - Implement `create_action()` to generate `ActionItem` for each gap
    - Implement `estimate_effort()` to assign Low/Medium/High effort estimates
    - Include technical, administrative, and physical steps for each action
    - Reference CSF subcategory and policy section for traceability
    - Generate both markdown and JSON outputs
    - _Requirements: 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7_
  
  - [x] 20.2 Write property test for roadmap generation
    - **Property 32: Roadmap Generation from Gaps**
    - **Validates: Requirements 11.1, 11.2**
    - Test that roadmap is created with Immediate/Near-term/Medium-term categories
  
  - [x] 20.3 Write property test for severity-based prioritization
    - **Property 33: Severity-Based Prioritization**
    - **Validates: Requirements 11.3**
    - Test that Critical/High gaps are Immediate, Medium are Near-term, Low are Medium-term
  
  - [x] 20.4 Write property test for action item completeness
    - **Property 34: Action Item Completeness**
    - **Validates: Requirements 11.4, 11.5, 11.6**
    - Test that all action items include required fields and steps
  
  - [x] 20.5 Write property test for roadmap output format
    - **Property 35: Roadmap Output Format**
    - **Validates: Requirements 11.7, 14.4, 14.5**
    - Test that roadmap is output in both markdown and JSON formats

- [x] 21. Domain-specific prioritization
  - [x] 21.1 Implement domain mapper (`analysis/domain_mapper.py`)
    - Create `DomainMapper` class with CSF subcategory prioritization rules
    - Map ISMS domain → prioritize GV function subcategories
    - Map Risk Management domain → prioritize GV.RM, GV.OV, ID.RA
    - Map Patch Management domain → prioritize ID.RA, PR.DS, PR.PS
    - Map Data Privacy domain → prioritize PR.AA, PR.DS, PR.AT
    - Add privacy framework limitation warning for Data Privacy domain
    - Implement fallback to all CSF functions when domain unknown
    - _Requirements: 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7_
  
  - [x] 21.2 Write property test for domain-specific prioritization
    - **Property 36: Domain-Specific CSF Prioritization**
    - **Validates: Requirements 12.1, 12.2, 12.3, 12.4**
    - Test that each domain prioritizes correct CSF subcategories
  
  - [x] 21.3 Write property test for unknown domain fallback
    - **Property 37: Unknown Domain Fallback**
    - **Validates: Requirements 12.6**
    - Test that unknown domains evaluate against all CSF functions

- [ ] 22. Checkpoint - Ensure revision and roadmap tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 23. Audit logging and compliance
  - [x] 23.1 Implement immutable audit logger (`reporting/audit_logger.py`)
    - Create `AuditLogger` class with append-only logging
    - Implement `log_analysis()` to create `AuditLogEntry` for each run
    - Include fields: timestamp, input_file_path, input_file_hash (SHA-256), model_name, model_version, embedding_model_version, configuration_parameters, retrieval_parameters, prompt_template_version, output_directory, analysis_duration_seconds
    - Store audit logs in append-only format (prevent modification/deletion)
    - Write logs to `audit_logs/` directory with timestamp-based filenames
    - _Requirements: 15.8, 15.9, 15.10_
  
  - [x] 23.2 Write property test for immutable audit log
    - **Property 46: Immutable Audit Log**
    - **Validates: Requirements 15.8, 15.9, 15.10**
    - Test that audit log entries cannot be modified or deleted after creation
    - Test that all required fields are present in audit log

- [x] 24. Error handling and logging
  - [x] 24.1 Implement error handling framework (`utils/error_handler.py`)
    - Create custom exceptions: `UnsupportedFormatError`, `OCRRequiredError`, `ParsingError`, `ModelNotFoundError`, `MemoryError`, `RetryableError`
    - Implement retry logic with exponential backoff for LLM generation failures
    - Implement graceful degradation for parsing errors (log and continue)
    - Implement memory monitoring and context truncation at 90% RAM threshold
    - Add descriptive error messages with troubleshooting steps
    - _Requirements: 15.1, 15.2, 15.3, 15.4, 15.7_
  
  - [x] 24.2 Implement operation logger (`utils/logger.py`)
    - Create logging configuration with timestamps and severity levels
    - Log all major operations: parsing, embedding, retrieval, generation
    - Write logs to output directory with analysis run
    - Include component name and context in log messages
    - _Requirements: 15.5, 15.6_
  
  - [x] 24.3 Write property test for graceful parsing degradation
    - **Property 43: Graceful Parsing Degradation**
    - **Validates: Requirements 15.1**
    - Test that parsing failures log errors and continue with available data
  
  - [x] 24.4 Write property test for operation logging
    - **Property 44: Operation Logging**
    - **Validates: Requirements 15.5, 15.6**
    - Test that all major operations are logged with timestamps
  
  - [x] 24.5 Write property test for LLM generation retry
    - **Property 45: LLM Generation Retry**
    - **Validates: Requirements 15.7**
    - Test that failed LLM generations retry up to 3 times

- [x] 25. Configuration management
  - [x] 25.1 Implement configuration loader (`utils/config_loader.py`)
    - Create `ConfigLoader` class to parse YAML/JSON config files
    - Support parameters: chunk_size, overlap, top_k, temperature, max_tokens, severity_thresholds, csf_function_priority
    - Implement schema validation for config files
    - Provide documented default values for all parameters
    - Return error messages for invalid configurations
    - _Requirements: 18.1, 18.2, 18.3, 18.4, 18.5, 18.6_
  
  - [x] 25.2 Write property test for configuration file support
    - **Property 47: Configuration File Support**
    - **Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5**
    - Test that all configurable parameters can be set via YAML/JSON
  
  - [x] 25.3 Write property test for configuration default fallback
    - **Property 48: Configuration Default Fallback**
    - **Validates: Requirements 18.6**
    - Test that missing config file uses documented defaults

- [x] 26. LangChain orchestration pipeline
  - [x] 26.1 Implement Analysis Pipeline (`orchestration/analysis_pipeline.py`)
    - Create `AnalysisPipeline` class orchestrating all components
    - Implement `execute()` method as main workflow entry point
    - Implement `initialize_resources()` to load models, vector store, reference catalog
    - Implement `cleanup()` to release resources and finalize audit log
    - Workflow steps: parse document → load/build catalog → chunk and embed → retrieve CSF subcategories → Stage A analysis → Stage B analysis → generate gap report → generate revised policy → generate roadmap → write outputs and audit log
    - Use LangChain abstractions for document loaders, text splitters, retrievers, LLM chains
    - Add progress indicators for long-running operations
    - Handle errors gracefully with detailed logging
    - _Requirements: 7.9, 8.8_
  
  - [x] 26.2 Write integration test for complete pipeline
    - Test end-to-end workflow with sample policy
    - Verify all outputs generated correctly
    - Verify audit log created
    - _Requirements: All requirements_

- [x] 27. Checkpoint - Ensure orchestration and error handling tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 28. Output file generation
  - [x] 28.1 Implement output manager (`reporting/output_manager.py`)
    - Create `OutputManager` class to handle all file outputs
    - Implement timestamped output directory creation
    - Implement file conflict handling (prompt for overwrite or generate unique names)
    - Write gap_analysis_report.md and gap_analysis_report.json
    - Write revised_policy.md
    - Write implementation_roadmap.md and implementation_roadmap.json
    - Include metadata in all outputs: analysis_date, model_version, model_name, input_file_name, prompt_template_version, configuration_hash, retrieval_parameters
    - _Requirements: 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8_
  
  - [x] 28.2 Write property test for output file generation
    - **Property 39: Output File Generation**
    - **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6**
    - Test that all required output files are generated in timestamped directory
  
  - [x] 28.3 Write property test for output metadata inclusion
    - **Property 40: Output Metadata Inclusion**
    - **Validates: Requirements 14.7**
    - Test that all outputs include required metadata fields
  
  - [x] 28.4 Write property test for file conflict handling
    - **Property 41: File Conflict Handling**
    - **Validates: Requirements 14.8**
    - Test that existing files trigger overwrite confirmation or unique filename generation

- [x] 29. Parser round-trip testing
  - [x] 29.1 Implement pretty printer (`ingestion/pretty_printer.py`)
    - Create `PrettyPrinter` class to format parsed policies back to markdown
    - Implement `format_to_markdown()` method
    - Preserve document structure: headings, sections, paragraphs
    - Format with proper markdown syntax
    - _Requirements: 13.1, 13.2_
  
  - [x] 29.2 Write property test for document parser round-trip
    - **Property 38: Document Parser Round-Trip**
    - **Validates: Requirements 13.3**
    - Test that parse → print → parse produces equivalent policy object

- [x] 30. Test data creation
  - [x] 30.1 Create dummy ISMS policy (`tests/fixtures/dummy_policies/isms_policy.pdf`)
    - Write policy with intentional governance gaps (missing GV.SC, GV.OV subcategories)
    - Include sections: Purpose, Scope, Roles, Risk Management, Incident Response
    - Omit supply chain risk management and organizational context
    - _Requirements: 19.1_
  
  - [x] 30.2 Create dummy Data Privacy policy (`tests/fixtures/dummy_policies/privacy_policy.pdf`)
    - Write policy with intentional access control gaps (missing PR.AA, PR.DS subcategories)
    - Include sections: Purpose, Data Collection, Data Usage, Data Retention
    - Omit identity management and data security controls
    - _Requirements: 19.2_
  
  - [x] 30.3 Create dummy Patch Management policy (`tests/fixtures/dummy_policies/patch_policy.pdf`)
    - Write policy with intentional vulnerability management gaps (missing ID.RA, PR.PS subcategories)
    - Include sections: Purpose, Patch Schedule, Testing Procedures
    - Omit vulnerability scanning and protective technology requirements
    - _Requirements: 19.3_
  
  - [x] 30.4 Create dummy Risk Management policy (`tests/fixtures/dummy_policies/risk_policy.pdf`)
    - Write policy with intentional risk assessment gaps (missing GV.RM, ID.RA subcategories)
    - Include sections: Purpose, Risk Identification, Risk Treatment
    - Omit risk management strategy and asset management
    - _Requirements: 19.4_
  
  - [x] 30.5 Create expected outputs for test policies
    - Create expected gap reports for each test policy
    - Document expected gaps to be identified (at least 80% of planted gaps)
    - Create validation scripts to compare actual vs expected outputs
    - _Requirements: 19.5_

- [x] 31. Integration testing with test data
  - [x] 31.1 Write integration test for ISMS policy analysis
    - Test complete analysis of dummy ISMS policy
    - Verify at least 80% of planted gaps identified
    - Verify gap report, revised policy, and roadmap generated
    - _Requirements: 19.1, 19.5_
  
  - [x] 31.2 Write integration test for Data Privacy policy analysis
    - Test complete analysis of dummy privacy policy
    - Verify privacy framework limitation warning logged
    - Verify at least 80% of planted gaps identified
    - _Requirements: 19.2, 19.5, 12.5_
  
  - [x] 31.3 Write integration test for Patch Management policy analysis
    - Test complete analysis of dummy patch policy
    - Verify at least 80% of planted gaps identified
    - Verify roadmap prioritizes critical gaps as Immediate
    - _Requirements: 19.3, 19.5_
  
  - [x] 31.4 Write integration test for Risk Management policy analysis
    - Test complete analysis of dummy risk policy
    - Verify at least 80% of planted gaps identified
    - Verify revised policy includes missing risk provisions
    - _Requirements: 19.4, 19.5_
  
  - [x] 31.5 Create automated test validation script
    - Implement script to run all test policies through analyzer
    - Compare outputs against expected results
    - Generate test report with pass/fail status
    - _Requirements: 19.6_

- [x] 32. Checkpoint - Ensure all integration tests pass
  - Ensure all tests pass, ask the user if questions arise.


- [x] 33. Command-line interface
  - [x] 33.1 Implement CLI (`cli/main.py`)
    - Create command-line interface using argparse or click
    - Accept arguments: `--policy-path`, `--config`, `--domain`, `--output-dir`, `--model`
    - Display progress indicators during analysis
    - Print summary of results (gaps found, outputs generated)
    - Handle keyboard interrupts gracefully
    - Return appropriate exit codes (0 for success, non-zero for errors)
    - _Requirements: 20.4_
  
  - [x] 33.2 Create main entry point (`__main__.py`)
    - Set up entry point for `python -m offline_policy_analyzer`
    - Initialize logging configuration
    - Load configuration
    - Execute analysis pipeline
    - Handle top-level exceptions
    - _Requirements: 20.4_

- [x] 34. Documentation
  - [x] 34.1 Create README.md
    - Write installation instructions with Python version requirement (3.11+)
    - Document model download procedure using setup script
    - Provide example commands for analyzing each policy type
    - Document hardware requirements (8GB RAM for 3B models, 16GB for 7B models)
    - Include quick start guide
    - Link to detailed documentation
    - _Requirements: 20.1, 20.3, 20.4, 20.5_
  
  - [x] 34.2 Create DEPENDENCIES.md
    - List all Python dependencies with exact version numbers
    - Document model dependencies (sentence-transformers, cross-encoder, LLM)
    - Specify model file sizes and storage requirements
    - Document optional dependencies for alternative backends
    - _Requirements: 20.2, 17.3_
  
  - [x] 34.3 Create LIMITATIONS.md
    - Document OCR limitation for scanned PDFs
    - Document NIST CSF 2.0 scope (cybersecurity, not complete privacy framework)
    - Document hardware constraints and performance expectations
    - Document 100-page document limit
    - Document known edge cases and workarounds
    - _Requirements: 20.5, 20.8_
  
  - [x] 34.4 Create TROUBLESHOOTING.md
    - Document common errors and solutions
    - Provide debugging steps for model loading failures
    - Provide debugging steps for memory issues
    - Provide debugging steps for parsing failures
    - Include FAQ section
    - _Requirements: 20.6_
  
  - [x] 34.5 Create EXAMPLES.md
    - Provide example commands for each policy domain
    - Include sample configuration files
    - Show example output files (gap report, revised policy, roadmap)
    - Demonstrate custom configuration usage
    - _Requirements: 20.4, 20.7_
  
  - [x] 34.6 Create SCHEMAS.md
    - Document JSON schema for gap analysis report
    - Document JSON schema for implementation roadmap
    - Provide schema validation examples
    - Include field descriptions and data types
    - _Requirements: 20.9_
  
  - [x] 34.7 Create ARCHITECTURE.md
    - Document two-stage analysis architecture rationale
    - Explain hybrid retrieval approach
    - Describe component interactions
    - Include architecture diagrams from design document
    - Document future improvements (Agentic RAG, multi-agent workflows)
    - _Requirements: 20.10, 20.11_
  
  - [x] 34.8 Create API documentation
    - Generate API documentation using Sphinx or pdoc
    - Document all public classes and methods
    - Include usage examples for each component
    - Provide developer guide for extending the system
    - _Requirements: 20.1_

- [x] 35. Performance optimization and validation
  - [x] 35.1 Write performance tests
    - Test 20-page policy analysis completes within 10 minutes
    - Test embedding engine processes 50+ chunks per minute
    - Test LLM generates 10+ tokens per second
    - Test memory usage stays within 8GB for 3B models, 16GB for 7B models
    - _Requirements: 16.1, 16.2, 16.3, 16.4, 16.5_
  
  - [x] 35.2 Optimize batch processing
    - Tune embedding batch sizes for optimal throughput
    - Implement parallel processing where safe (embedding generation)
    - Add caching for repeated operations
    - Profile and optimize bottlenecks
    - _Requirements: 16.1, 16.4, 16.5_
  
  - [x] 35.3 Add progress indicators
    - Implement progress bars for long-running operations
    - Show percentage completion for document parsing
    - Show percentage completion for embedding generation
    - Show percentage completion for gap analysis
    - Display estimated time remaining
    - _Requirements: 16.6_

- [x] 36. Final integration and wiring
  - [x] 36.1 Wire all components together
    - Integrate document parser → text chunker → embedding engine → vector store
    - Integrate reference catalog builder → embedding engine → vector store
    - Integrate hybrid retriever → gap analysis engine
    - Integrate gap analysis engine → policy revision engine
    - Integrate gap analysis engine → roadmap generator
    - Integrate all components → output manager
    - Integrate all operations → audit logger
    - Ensure LangChain orchestration connects all components
    - _Requirements: All requirements_
  
  - [x] 36.2 Create end-to-end smoke test
    - Test complete workflow with minimal policy document
    - Verify all outputs generated
    - Verify no errors or warnings
    - Verify audit log created
    - Run on clean environment to catch missing dependencies
    - _Requirements: All requirements_
  
  - [x] 36.3 Validate offline operation
    - Disable network connectivity
    - Run complete analysis workflow
    - Verify no network errors
    - Verify all operations complete successfully
    - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6_

- [x] 37. Final checkpoint - Complete system validation
  - Ensure all tests pass, ask the user if questions arise.

## Notes

- Tasks marked with `*` are optional testing tasks and can be skipped for faster MVP
- Each task references specific requirements for traceability
- Property-based tests validate universal correctness properties (49 properties total)
- Unit tests validate specific examples and edge cases
- Integration tests validate end-to-end workflows with dummy policies
- Checkpoints ensure incremental validation throughout implementation
- All code uses Python 3.11+ with type hints and comprehensive docstrings
- LangChain provides orchestration abstractions for RAG pipeline
- Two-stage analysis architecture minimizes hallucination risks
- Hybrid retrieval ensures critical CSF subcategories are never missed
- Immutable audit logging ensures compliance traceability
- System operates entirely offline on consumer hardware (8-16GB RAM)

