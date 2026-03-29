# Requirements Document

## Introduction

The Offline Policy Gap Analyzer is a local LLM-powered system that analyzes organizational cybersecurity policies against NIST CSF 2.0 standards using the CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024) as the reference baseline. The system identifies gaps, generates revised policy text, and creates prioritized improvement roadmaps while operating entirely offline on consumer-grade hardware without any cloud dependencies.

## Glossary

- **Policy_Analyzer**: The complete offline system that performs gap analysis, policy revision, and roadmap generation
- **Document_Parser**: The component responsible for extracting text from PDF, DOCX, and TXT policy files
- **Reference_Catalog**: The locally stored, structured representation of the CIS MS-ISAC NIST CSF 2.0 policy template guide
- **Embedding_Engine**: The local sentence transformer model that converts text into dense vector representations
- **Vector_Store**: The local database (ChromaDB or FAISS) that stores and retrieves embedded text chunks
- **Retrieval_Engine**: The hybrid search component combining semantic similarity and keyword matching
- **LLM_Runtime**: The local language model inference engine (llama.cpp or Ollama) running quantized models
- **Gap_Analysis_Engine**: The component that identifies missing or weak policy provisions against NIST standards
- **Policy_Revision_Engine**: The component that generates improved policy text addressing identified gaps
- **Roadmap_Generator**: The component that creates prioritized implementation plans
- **Organizational_Policy**: The input policy document provided by the user for analysis
- **NIST_CSF_2.0**: The National Institute of Standards and Technology Cybersecurity Framework version 2.0
- **CIS_Guide**: The CIS MS-ISAC NIST Cybersecurity Framework Policy Template Guide (2024)
- **CSF_Subcategory**: A specific outcome or control within the NIST framework (e.g., GV.RM-01, ID.AM-1)
- **Gap**: A missing, incomplete, or inadequate policy provision when compared to NIST standards
- **Coverage_Status**: The classification of a CSF subcategory as Covered, Partially_Covered, Missing, or Ambiguous
- **Quantized_Model**: A compressed LLM using 4-bit or 8-bit precision in GGUF format for local execution
- **Offline_Mode**: Operation without any network connectivity or external API calls
- **Consumer_Hardware**: Typical laptop or workstation with 8-16GB RAM and limited GPU resources

## Requirements

### Requirement 1: Offline Operation

**User Story:** As a security analyst, I want the system to operate completely offline, so that sensitive policy documents never leave the local machine and comply with data sovereignty requirements.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL execute all operations without requiring internet connectivity
2. THE Policy_Analyzer SHALL NOT make external API calls to cloud services
3. THE Policy_Analyzer SHALL store all model files locally before runtime execution
4. THE Policy_Analyzer SHALL store the Reference_Catalog locally before runtime execution
5. WHEN the system detects an active network connection, THE Policy_Analyzer SHALL log a warning but continue offline operation
6. THE Policy_Analyzer SHALL verify that all required local resources exist before beginning analysis

### Requirement 2: Document Ingestion

**User Story:** As a security analyst, I want to upload policy documents in common formats, so that I can analyze existing organizational policies without manual conversion.

#### Acceptance Criteria

1. WHEN a PDF file is provided, THE Document_Parser SHALL extract text content using PyMuPDF as the primary parser
2. WHEN complex tabular data is encountered in a PDF, THE Document_Parser SHALL use pdfplumber as a fallback parser for precise table extraction
3. WHEN a PDF contains only scanned images without a text layer, THE Document_Parser SHALL reject the file with an error message stating "OCR is not supported; please provide a text-based PDF"
4. WHEN a DOCX file is provided, THE Document_Parser SHALL extract text content preserving structural hierarchy
5. WHEN a TXT file is provided, THE Document_Parser SHALL read the plain text content
6. IF a file format is unsupported, THEN THE Document_Parser SHALL return an error message specifying supported formats (PDF, DOCX, TXT)
7. THE Document_Parser SHALL preserve structural boundaries including headings, paragraphs, and section markers
8. THE Document_Parser SHALL handle multi-page documents up to 100 pages in length
9. IF text extraction fails, THEN THE Document_Parser SHALL log the specific error and terminate gracefully

### Requirement 3: Reference Catalog Construction

**User Story:** As a system administrator, I want the CIS guide parsed into a structured catalog, so that the system can perform deterministic gap analysis against known standards.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL parse the CIS_Guide into a structured Reference_Catalog during initialization
2. THE Reference_Catalog SHALL store CSF_Function, Category, CSF_Subcategory, subcategory_text, and mapped_policy_templates for each entry
3. THE Reference_Catalog SHALL include keywords and domain_tags for each CSF_Subcategory
4. THE Reference_Catalog SHALL persist to local storage for reuse across multiple analysis sessions
5. WHEN the CIS_Guide is updated, THE Policy_Analyzer SHALL provide a mechanism to rebuild the Reference_Catalog
6. THE Reference_Catalog SHALL contain all 49 NIST CSF 2.0 subcategories mapped in the CIS_Guide

### Requirement 4: Text Chunking and Segmentation

**User Story:** As a developer, I want policy documents chunked intelligently, so that semantic context is preserved within embedding boundaries.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL segment extracted text into chunks of 512 tokens maximum
2. THE Policy_Analyzer SHALL apply a 50-token overlap between consecutive chunks
3. WHERE structural boundaries exist (headings, paragraphs), THE Policy_Analyzer SHALL prefer splitting at those boundaries
4. THE Policy_Analyzer SHALL preserve complete sentences within chunks when possible
5. WHEN a CSF_Subcategory description spans multiple lines, THE Policy_Analyzer SHALL keep it within a single chunk

### Requirement 5: Local Embedding Generation

**User Story:** As a security analyst, I want text converted to embeddings locally, so that semantic search operates without cloud dependencies.

#### Acceptance Criteria

1. THE Embedding_Engine SHALL use a local sentence transformer model stored on disk
2. THE Embedding_Engine SHALL generate embeddings without network calls
3. THE Embedding_Engine SHALL produce 384-dimensional vectors for all-MiniLM-L6-v2 model
4. WHEN processing the Reference_Catalog, THE Embedding_Engine SHALL embed all CSF_Subcategory descriptions
5. WHEN processing an Organizational_Policy, THE Embedding_Engine SHALL embed all text chunks
6. THE Embedding_Engine SHALL operate on CPU-only hardware configurations
7. THE Embedding_Engine SHALL process at least 100 text chunks per minute on consumer hardware

### Requirement 6: Vector Storage and Persistence

**User Story:** As a system administrator, I want embeddings stored locally, so that repeated analyses do not require re-embedding the reference catalog.

#### Acceptance Criteria

1. THE Vector_Store SHALL persist embeddings to local disk storage
2. THE Vector_Store SHALL support semantic similarity search operations
3. THE Vector_Store SHALL return the top-k most similar chunks for a given query vector
4. THE Vector_Store SHALL store metadata alongside embeddings including source_text, CSF_Subcategory, and chunk_id
5. WHEN the Policy_Analyzer restarts, THE Vector_Store SHALL load previously stored embeddings from disk
6. THE Vector_Store SHALL support collections for separating Reference_Catalog embeddings from policy embeddings

### Requirement 7: Hybrid Retrieval

**User Story:** As a security analyst, I want both semantic and keyword matching, so that specific CSF subcategories are never missed due to terminology differences.

#### Acceptance Criteria

1. THE Retrieval_Engine SHALL combine dense vector similarity search with sparse keyword matching
2. THE Retrieval_Engine SHALL use BM25 or TF-IDF for keyword-based retrieval
3. WHEN querying for relevant standards, THE Retrieval_Engine SHALL retrieve top-5 results from semantic search
4. WHEN querying for relevant standards, THE Retrieval_Engine SHALL retrieve top-5 results from keyword search
5. THE Retrieval_Engine SHALL merge and deduplicate results from both retrieval methods
6. THE Retrieval_Engine SHALL use a local cross-encoder reranking model to reorder merged results by relevance score
7. THE Retrieval_Engine SHALL feed only the top-ranked, most relevant chunks to the LLM context window
8. THE Retrieval_Engine SHALL return CSF_Subcategory identifiers with each retrieved chunk
9. THE Retrieval_Engine SHALL be orchestrated using LangChain to manage the retrieval pipeline

### Requirement 8: Local LLM Execution

**User Story:** As a security analyst, I want the LLM to run locally on my hardware, so that policy analysis operates without cloud dependencies and within memory constraints.

#### Acceptance Criteria

1. THE LLM_Runtime SHALL execute Quantized_Models in GGUF format
2. THE LLM_Runtime SHALL operate within 8GB of system memory for 3B parameter models
3. THE LLM_Runtime SHALL operate within 16GB of system memory for 7B parameter models
4. THE LLM_Runtime SHALL support llama.cpp or Ollama as the inference backend
5. WHEN memory usage exceeds 90 percent of available RAM, THE LLM_Runtime SHALL truncate context to prevent crashes
6. THE LLM_Runtime SHALL expose a local API endpoint for the Policy_Analyzer to invoke
7. THE LLM_Runtime SHALL NOT require GPU acceleration for operation
8. THE Policy_Analyzer SHALL use LangChain to orchestrate interactions between document parsers, embedding models, vector database, and the LLM_Runtime

### Requirement 9: Gap Analysis Execution

**User Story:** As a security analyst, I want the system to identify policy gaps using a two-stage safety architecture, so that analysis is deterministic, reproducible, and minimizes hallucination risks.

#### Acceptance Criteria

1. THE Gap_Analysis_Engine SHALL execute analysis in two distinct stages: Stage A (deterministic evidence detection) and Stage B (constrained LLM reasoning)
2. IN Stage A, THE Gap_Analysis_Engine SHALL chunk the Organizational_Policy text and retrieve top matching CSF_Subcategories using the Retrieval_Engine
3. IN Stage A, THE Gap_Analysis_Engine SHALL score evidence by lexical overlap, embedding similarity, and section heuristics
4. IN Stage A, THE Gap_Analysis_Engine SHALL mark each CSF_Subcategory with a preliminary Coverage_Status: Covered, Partially_Covered, Missing, or Ambiguous
5. IN Stage B, THE Gap_Analysis_Engine SHALL provide the LLM_Runtime with only the matched policy section, CSF_Subcategory text, evidence spans, and a strict output schema
6. IN Stage B, THE Gap_Analysis_Engine SHALL prompt the LLM to explain why coverage exists or not, what exact gap is present, and what revision language is needed
7. WHEN a CSF_Subcategory is marked as Covered in Stage A, THE Gap_Analysis_Engine SHALL skip Stage B processing for that subcategory
8. WHEN a CSF_Subcategory is marked as Ambiguous in Stage A, THE Gap_Analysis_Engine SHALL flag it for manual review in the output report
9. WHEN a CSF_Subcategory is Missing, THE Gap_Analysis_Engine SHALL provide the specific NIST requirement text in the gap report
10. WHEN a CSF_Subcategory is Partially_Covered, THE Gap_Analysis_Engine SHALL explain what specific elements are inadequate
11. THE Gap_Analysis_Engine SHALL assign a severity level (Critical, High, Medium, Low) to each identified Gap
12. THE Gap_Analysis_Engine SHALL generate a structured gap analysis report in both markdown and JSON formats

### Requirement 10: Policy Revision Generation

**User Story:** As a security analyst, I want the system to generate improved policy text with mandatory human-review warnings, so that I have concrete language to address identified gaps while understanding that AI-generated content requires validation.

#### Acceptance Criteria

1. WHEN gaps are identified, THE Policy_Revision_Engine SHALL generate revised policy text addressing each Gap
2. THE Policy_Revision_Engine SHALL preserve the original policy structure and tone
3. THE Policy_Revision_Engine SHALL inject new clauses for Missing CSF_Subcategories
4. THE Policy_Revision_Engine SHALL strengthen language for Partially_Covered CSF_Subcategories
5. THE Policy_Revision_Engine SHALL NOT remove existing valid policy provisions
6. THE Policy_Revision_Engine SHALL cite the specific CSF_Subcategory addressed by each revision
7. THE Policy_Revision_Engine SHALL output the complete revised policy document in markdown format
8. THE Policy_Revision_Engine SHALL append a prominent legal and compliance warning to all revised policy documents stating: "IMPORTANT: This revised policy was generated by an AI system and is provided as a draft baseline only. The CIS MS-ISAC templates are advisory and may not reflect the most recent applicable standards or your organization's specific legal, regulatory, or operational requirements. This document MUST be reviewed, validated, and approved by qualified legal counsel, compliance officers, and security leadership before adoption."

### Requirement 11: Implementation Roadmap Generation

**User Story:** As a security manager, I want a prioritized action plan, so that I can systematically implement policy improvements aligned with organizational risk tolerance.

#### Acceptance Criteria

1. WHEN gaps are identified, THE Roadmap_Generator SHALL create a prioritized implementation plan
2. THE Roadmap_Generator SHALL categorize actions into Immediate, Near_Term, and Medium_Term timeframes
3. THE Roadmap_Generator SHALL prioritize Critical and High severity gaps in the Immediate category
4. THE Roadmap_Generator SHALL include specific technical, administrative, and physical actions for each Gap
5. THE Roadmap_Generator SHALL reference the CSF_Subcategory and policy section for each action item
6. THE Roadmap_Generator SHALL estimate relative implementation effort (Low, Medium, High) for each action
7. THE Roadmap_Generator SHALL output the roadmap in markdown format

### Requirement 12: Policy Domain Mapping

**User Story:** As a security analyst, I want the system to focus on relevant CSF categories and document framework limitations, so that analysis is targeted to the specific policy type and I understand the scope boundaries.

#### Acceptance Criteria

1. WHEN analyzing an ISMS policy, THE Policy_Analyzer SHALL prioritize Govern (GV) function subcategories
2. WHEN analyzing a Risk Management policy, THE Policy_Analyzer SHALL prioritize GV.RM, GV.OV, and ID.RA subcategories
3. WHEN analyzing a Patch Management policy, THE Policy_Analyzer SHALL prioritize ID.RA, PR.DS, and PR.PS subcategories
4. WHEN analyzing a Data Privacy policy, THE Policy_Analyzer SHALL prioritize PR.AA, PR.DS, and PR.AT subcategories
5. WHEN analyzing a Data Privacy policy, THE Policy_Analyzer SHALL log a warning stating: "The NIST CSF 2.0 addresses cybersecurity aspects of data protection but is not a complete privacy framework. Privacy-specific compliance requirements may extend beyond CSF scope."
6. WHERE policy type cannot be determined, THE Policy_Analyzer SHALL evaluate against all CSF functions
7. THE Policy_Analyzer SHALL allow manual specification of policy domain via configuration parameter

### Requirement 13: Parser and Serializer Round-Trip Testing

**User Story:** As a developer, I want parsers validated through round-trip testing, so that document parsing and generation maintain fidelity.

#### Acceptance Criteria

1. THE Document_Parser SHALL support a corresponding Pretty_Printer for each input format
2. THE Pretty_Printer SHALL format parsed policy structures back into valid markdown documents
3. FOR ALL valid parsed policy objects, parsing then printing then parsing SHALL produce an equivalent object
4. WHEN the Reference_Catalog is serialized to JSON, THE Policy_Analyzer SHALL deserialize it to an equivalent structure
5. THE Policy_Analyzer SHALL include automated tests validating round-trip properties for all parsers

### Requirement 14: Output Generation

**User Story:** As a security analyst, I want all outputs saved in both human-readable and machine-readable formats, so that I can review results, integrate with other tools, and ensure reproducibility.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL generate a gap_analysis_report.md file containing all identified gaps in markdown format
2. THE Policy_Analyzer SHALL generate a gap_analysis_report.json file containing structured gap data with fields: subcategory_id, description, status, evidence_quote, reason, severity, suggested_fix
3. THE Policy_Analyzer SHALL generate a revised_policy.md file containing the improved policy text
4. THE Policy_Analyzer SHALL generate an implementation_roadmap.md file containing the prioritized action plan
5. THE Policy_Analyzer SHALL generate an implementation_roadmap.json file containing structured roadmap data with fields: action_id, timeframe, severity, effort, csf_subcategory, policy_section, description
6. THE Policy_Analyzer SHALL create an output directory with timestamp for each analysis run
7. THE Policy_Analyzer SHALL include metadata in each output file: analysis_date, model_version, model_name, input_file_name, prompt_template_version, configuration_hash, retrieval_parameters
8. WHERE output files already exist, THE Policy_Analyzer SHALL prompt for overwrite confirmation or generate unique filenames
9. THE Policy_Analyzer SHALL ensure all JSON outputs conform to a documented schema for testing and integration purposes

### Requirement 15: Error Handling and Logging

**User Story:** As a system administrator, I want comprehensive error handling and immutable audit logging, so that failures are diagnosed quickly, the system degrades gracefully, and all analysis runs are traceable for compliance and reproducibility.

#### Acceptance Criteria

1. WHEN a file cannot be parsed, THE Policy_Analyzer SHALL log the specific error and continue with available data
2. WHEN the LLM_Runtime is unavailable, THE Policy_Analyzer SHALL return a clear error message with troubleshooting steps
3. WHEN memory limits are approached, THE Policy_Analyzer SHALL log a warning and reduce context window size
4. IF the Vector_Store cannot be initialized, THEN THE Policy_Analyzer SHALL terminate with a descriptive error
5. THE Policy_Analyzer SHALL log all major operations (parsing, embedding, retrieval, generation) with timestamps
6. THE Policy_Analyzer SHALL write logs to a local file in the output directory
7. WHERE an LLM generation fails, THE Policy_Analyzer SHALL retry up to 3 times before reporting failure
8. THE Policy_Analyzer SHALL maintain an immutable audit log for each analysis run containing: input_file_path, input_file_hash, timestamp, model_version, model_name, embedding_model_version, configuration_parameters, retrieval_parameters, prompt_template_version, output_directory
9. THE Policy_Analyzer SHALL NOT allow modification or deletion of audit log entries after creation
10. THE Policy_Analyzer SHALL store audit logs in append-only format to ensure traceability and compliance

### Requirement 16: Performance on Consumer Hardware

**User Story:** As a security analyst, I want the system to run on my laptop, so that I do not need specialized infrastructure for policy analysis.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL complete analysis of a 20-page policy document within 10 minutes on consumer hardware
2. THE Policy_Analyzer SHALL operate with 8GB of system RAM for 3B parameter models
3. THE Policy_Analyzer SHALL operate with 16GB of system RAM for 7B parameter models
4. THE Embedding_Engine SHALL process document chunks at a minimum rate of 50 chunks per minute
5. THE LLM_Runtime SHALL generate gap analysis text at a minimum rate of 10 tokens per second
6. THE Policy_Analyzer SHALL provide progress indicators during long-running operations

### Requirement 17: Model and Reference Data Management

**User Story:** As a system administrator, I want clear procedures for managing local models, so that the system remains functional in offline environments.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL verify the presence of required model files before execution
2. THE Policy_Analyzer SHALL provide a setup script to download models while internet is available
3. THE Policy_Analyzer SHALL document the exact model files required (name, version, format, size)
4. THE Policy_Analyzer SHALL document the storage location for all model files and reference data
5. WHEN a required model file is missing, THE Policy_Analyzer SHALL provide the exact download command
6. THE Policy_Analyzer SHALL support multiple model options (Qwen2.5-3B, Phi-3.5-mini, Mistral-7B)

### Requirement 18: Configuration and Customization

**User Story:** As a security analyst, I want configurable analysis parameters, so that I can tune the system for different organizational contexts.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL accept configuration via a YAML or JSON configuration file
2. THE Policy_Analyzer SHALL allow configuration of chunk_size, overlap, and top_k retrieval parameters
3. THE Policy_Analyzer SHALL allow configuration of LLM temperature and max_tokens parameters
4. THE Policy_Analyzer SHALL allow configuration of severity thresholds for gap classification
5. THE Policy_Analyzer SHALL allow specification of which CSF functions to prioritize
6. WHERE no configuration file is provided, THE Policy_Analyzer SHALL use documented default values

### Requirement 19: Test Data Validation

**User Story:** As a developer, I want the system validated against known test cases, so that gap detection accuracy is measurable.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL be tested against a dummy ISMS policy with intentional governance gaps
2. THE Policy_Analyzer SHALL be tested against a dummy Data Privacy policy with intentional access control gaps
3. THE Policy_Analyzer SHALL be tested against a dummy Patch Management policy with intentional vulnerability management gaps
4. THE Policy_Analyzer SHALL be tested against a dummy Risk Management policy with intentional risk assessment gaps
5. FOR EACH test policy, THE Policy_Analyzer SHALL correctly identify at least 80 percent of intentionally planted gaps
6. THE Policy_Analyzer SHALL include automated test scripts that validate gap detection against expected results

### Requirement 20: Documentation and Usability

**User Story:** As a new user, I want comprehensive documentation covering installation, usage, limitations, and future improvements, so that I can install, configure, and run the system without prior knowledge and understand its evolution path.

#### Acceptance Criteria

1. THE Policy_Analyzer SHALL include a README.md file with installation instructions
2. THE Policy_Analyzer SHALL document all Python dependencies with exact version numbers
3. THE Policy_Analyzer SHALL provide step-by-step instructions for downloading and configuring local models
4. THE Policy_Analyzer SHALL include example commands for analyzing each test policy type
5. THE Policy_Analyzer SHALL document known limitations and hardware requirements
6. THE Policy_Analyzer SHALL include troubleshooting guidance for common errors
7. THE Policy_Analyzer SHALL provide example output files demonstrating expected results
8. THE Policy_Analyzer SHALL document that the NIST CSF 2.0 addresses cybersecurity but is not a complete privacy framework, and privacy-specific compliance may require additional frameworks
9. THE Policy_Analyzer SHALL document the JSON output schemas for gap analysis reports and implementation roadmaps
10. THE Policy_Analyzer SHALL document future architectural improvements including: transition to Agentic RAG architectures with multi-agent workflows (Planner Agent, Retriever Agent, Critic Agent), iterative self-correction mechanisms, and enhanced precision through internal auditing patterns
11. THE Policy_Analyzer SHALL document the rationale for the two-stage analysis architecture and how it minimizes hallucination risks
