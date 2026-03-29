"""
Domain data models for the Offline Policy Gap Analyzer.

This module defines the core domain objects used throughout the system for
representing policy documents, CSF subcategories, analysis results, and outputs.
All models support serialization for JSON output and persistence.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any
from datetime import datetime


@dataclass
class ParsedDocument:
    """Represents a parsed policy document.
    
    Attributes:
        text: Full extracted text content
        file_path: Path to the source document
        file_type: Document format ('pdf', 'docx', 'txt')
        page_count: Number of pages in the document
        structure: Hierarchical structure of the document
        metadata: Additional document metadata (author, date, etc.)
    """
    text: str
    file_path: str
    file_type: str
    page_count: int
    structure: 'DocumentStructure'
    metadata: Dict


@dataclass
class DocumentStructure:
    """Hierarchical structure of a document.
    
    Attributes:
        headings: List of all headings in the document
        sections: List of top-level sections
        paragraphs: List of all paragraphs (deprecated, use sections)
    """
    headings: List['Heading']
    sections: List['Section']
    paragraphs: List['Paragraph'] = field(default_factory=list)


@dataclass
class Heading:
    """Document heading with position information.
    
    Attributes:
        level: Heading level (1, 2, 3, etc.)
        text: Heading text content
        start_pos: Character position where heading starts
        end_pos: Character position where heading ends
    """
    level: int
    text: str
    start_pos: int
    end_pos: int


@dataclass
class Section:
    """Document section with hierarchical structure.
    
    Attributes:
        title: Section title/heading
        content: Section text content
        start_pos: Character position where section starts
        end_pos: Character position where section ends
        subsections: Nested subsections within this section
    """
    title: str
    content: str
    start_pos: int
    end_pos: int
    subsections: List['Section'] = field(default_factory=list)


@dataclass
class Paragraph:
    """Document paragraph (deprecated, use Section instead).
    
    Attributes:
        text: Paragraph text content
        start_pos: Character position where paragraph starts
        end_pos: Character position where paragraph ends
    """
    text: str
    start_pos: int
    end_pos: int


@dataclass
class TextChunk:
    """Chunk of text with metadata for embedding and retrieval.
    
    Attributes:
        text: Chunk text content
        chunk_id: Unique identifier for this chunk
        source_file: Path to source document
        start_pos: Character position in source document
        end_pos: Character position in source document
        page_number: Page number in source document (if applicable)
        section_title: Title of section containing this chunk
        embedding: Dense vector embedding (384-dim for all-MiniLM-L6-v2), typically numpy.ndarray
    """
    text: str
    chunk_id: str
    source_file: str
    start_pos: int
    end_pos: int
    page_number: Optional[int] = None
    section_title: Optional[str] = None
    embedding: Optional[Any] = None  # numpy.ndarray when available


@dataclass
class CSFSubcategory:
    """NIST CSF 2.0 subcategory from reference catalog.
    
    Attributes:
        subcategory_id: CSF subcategory identifier (e.g., 'GV.RM-01')
        function: CSF function ('Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover')
        category: CSF category name (e.g., 'Risk Management Strategy')
        description: Full NIST outcome text describing the subcategory
        keywords: Keywords for sparse retrieval and keyword matching
        domain_tags: Policy domain tags (e.g., ['isms', 'risk_management'])
        mapped_templates: CIS policy templates that address this subcategory
        priority: Priority level ('critical', 'high', 'medium', 'low')
    """
    subcategory_id: str
    function: str
    category: str
    description: str
    keywords: List[str]
    domain_tags: List[str]
    mapped_templates: List[str]
    priority: str


@dataclass
class RetrievalResult:
    """Result from hybrid retrieval combining dense and sparse search.
    
    Attributes:
        subcategory_id: CSF subcategory identifier
        subcategory_text: Full subcategory description text
        relevance_score: Combined relevance score (0.0 to 1.0)
        evidence_spans: Matching text spans from policy document
        retrieval_method: Method used ('dense', 'sparse', or 'hybrid')
    """
    subcategory_id: str
    subcategory_text: str
    relevance_score: float
    evidence_spans: List[str]
    retrieval_method: str


@dataclass
class CoverageAssessment:
    """Stage A deterministic coverage assessment.
    
    Attributes:
        subcategory_id: CSF subcategory identifier
        status: Coverage status ('covered', 'partially_covered', 'missing', 'ambiguous')
        lexical_score: Keyword overlap score (0.0 to 1.0)
        semantic_score: Embedding similarity score (0.0 to 1.0)
        evidence_spans: Text spans supporting the assessment
        confidence: Combined confidence score (0.0 to 1.0)
    """
    subcategory_id: str
    status: str
    lexical_score: float
    semantic_score: float
    evidence_spans: List[str]
    confidence: float


@dataclass
class GapDetail:
    """Detailed gap information from Stage B analysis.
    
    Attributes:
        subcategory_id: CSF subcategory identifier
        subcategory_description: Full NIST outcome text
        status: Gap status ('partially_covered' or 'missing')
        evidence_quote: Relevant text from policy (empty if missing)
        gap_explanation: Explanation of what is missing or inadequate
        severity: Gap severity ('critical', 'high', 'medium', 'low')
        suggested_fix: Suggested policy language to address the gap
    """
    subcategory_id: str
    subcategory_description: str
    status: str
    evidence_quote: str
    gap_explanation: str
    severity: str
    suggested_fix: str


@dataclass
class GapAnalysisReport:
    """Complete gap analysis output.
    
    Attributes:
        analysis_date: Timestamp of analysis execution
        input_file: Path to analyzed policy document
        input_file_hash: SHA-256 hash of input file for traceability
        model_name: LLM model name used for analysis
        model_version: LLM model version/quantization
        embedding_model: Embedding model name
        gaps: List of identified gaps
        covered_subcategories: List of CSF subcategory IDs that are covered
        metadata: Additional metadata (prompt_version, config_hash, retrieval_params)
    """
    analysis_date: datetime
    input_file: str
    input_file_hash: str
    model_name: str
    model_version: str
    embedding_model: str
    gaps: List[GapDetail]
    covered_subcategories: List[str]
    metadata: Dict


@dataclass
class Revision:
    """Single policy revision addressing a gap.
    
    Attributes:
        section: Policy section being revised
        gap_addressed: CSF subcategory ID being addressed
        original_clause: Original policy text (empty if new injection)
        revised_clause: Revised or new policy text
        revision_type: Type of revision ('injection' or 'strengthening')
    """
    section: str
    gap_addressed: str
    original_clause: str
    revised_clause: str
    revision_type: str


@dataclass
class RevisedPolicy:
    """Revised policy document addressing identified gaps.
    
    Attributes:
        original_text: Original policy text
        revised_text: Complete revised policy text
        revisions: List of individual revisions made
        warning: Mandatory human-review warning text
        metadata: Additional metadata about the revision process
    """
    original_text: str
    revised_text: str
    revisions: List[Revision]
    warning: str
    metadata: Dict


@dataclass
class ActionItem:
    """Implementation roadmap action item.
    
    Attributes:
        action_id: Unique action identifier
        timeframe: Implementation timeframe ('immediate', 'near_term', 'medium_term')
        severity: Gap severity this addresses ('critical', 'high', 'medium', 'low')
        effort: Implementation effort estimate ('low', 'medium', 'high')
        csf_subcategory: CSF subcategory ID being addressed
        policy_section: Policy section requiring changes
        description: Action description
        technical_steps: List of technical implementation steps
        administrative_steps: List of administrative/policy steps
        physical_steps: List of physical security steps
    """
    action_id: str
    timeframe: str
    severity: str
    effort: str
    csf_subcategory: str
    policy_section: str
    description: str
    technical_steps: List[str]
    administrative_steps: List[str]
    physical_steps: List[str]


@dataclass
class ImplementationRoadmap:
    """Prioritized implementation plan for addressing gaps.
    
    Attributes:
        immediate_actions: Actions for 0-3 months (Critical/High severity)
        near_term_actions: Actions for 3-6 months (Medium severity)
        medium_term_actions: Actions for 6-12 months (Low severity)
        metadata: Additional metadata about roadmap generation
    """
    immediate_actions: List[ActionItem]
    near_term_actions: List[ActionItem]
    medium_term_actions: List[ActionItem]
    metadata: Dict


@dataclass
class AuditLogEntry:
    """Immutable audit log entry for compliance traceability.
    
    Attributes:
        timestamp: Analysis execution timestamp
        input_file_path: Path to analyzed policy document
        input_file_hash: SHA-256 hash of input file
        model_name: LLM model name used
        model_version: LLM model version/quantization
        embedding_model_version: Embedding model version
        configuration_parameters: Analysis configuration parameters
        retrieval_parameters: Retrieval configuration parameters
        prompt_template_version: Version of prompt templates used
        output_directory: Directory where outputs were written
        analysis_duration_seconds: Total analysis duration
    """
    timestamp: datetime
    input_file_path: str
    input_file_hash: str
    model_name: str
    model_version: str
    embedding_model_version: str
    configuration_parameters: Dict
    retrieval_parameters: Dict
    prompt_template_version: str
    output_directory: str
    analysis_duration_seconds: float
