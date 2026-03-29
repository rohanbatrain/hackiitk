"""
Unit tests for domain data models.

Tests basic instantiation and field access for all domain models.
"""

import pytest
from datetime import datetime
import numpy as np

from models.domain import (
    ParsedDocument,
    DocumentStructure,
    Heading,
    Section,
    Paragraph,
    TextChunk,
    CSFSubcategory,
    RetrievalResult,
    CoverageAssessment,
    GapDetail,
    GapAnalysisReport,
    Revision,
    RevisedPolicy,
    ActionItem,
    ImplementationRoadmap,
    AuditLogEntry,
)


def test_parsed_document_instantiation():
    """Test ParsedDocument can be instantiated with required fields."""
    structure = DocumentStructure(headings=[], sections=[])
    doc = ParsedDocument(
        text="Sample policy text",
        file_path="/path/to/policy.pdf",
        file_type="pdf",
        page_count=10,
        structure=structure,
        metadata={"author": "Test Author"},
    )
    assert doc.text == "Sample policy text"
    assert doc.file_type == "pdf"
    assert doc.page_count == 10


def test_document_structure_instantiation():
    """Test DocumentStructure can be instantiated."""
    heading = Heading(level=1, text="Introduction", start_pos=0, end_pos=12)
    section = Section(
        title="Introduction",
        content="This is the introduction.",
        start_pos=0,
        end_pos=25,
    )
    structure = DocumentStructure(headings=[heading], sections=[section])
    assert len(structure.headings) == 1
    assert len(structure.sections) == 1


def test_text_chunk_instantiation():
    """Test TextChunk can be instantiated with optional fields."""
    chunk = TextChunk(
        text="Sample chunk text",
        chunk_id="chunk_001",
        source_file="/path/to/policy.pdf",
        start_pos=0,
        end_pos=17,
        page_number=1,
        section_title="Introduction",
        embedding=np.random.rand(384),
    )
    assert chunk.chunk_id == "chunk_001"
    assert chunk.page_number == 1
    assert chunk.embedding.shape == (384,)


def test_csf_subcategory_instantiation():
    """Test CSFSubcategory can be instantiated."""
    subcategory = CSFSubcategory(
        subcategory_id="GV.RM-01",
        function="Govern",
        category="Risk Management Strategy",
        description="Risk management objectives are established and agreed to by organizational stakeholders.",
        keywords=["risk", "management", "objectives"],
        domain_tags=["isms", "risk_management"],
        mapped_templates=["Risk Management Policy"],
        priority="high",
    )
    assert subcategory.subcategory_id == "GV.RM-01"
    assert subcategory.function == "Govern"
    assert subcategory.priority == "high"


def test_retrieval_result_instantiation():
    """Test RetrievalResult can be instantiated."""
    result = RetrievalResult(
        subcategory_id="GV.RM-01",
        subcategory_text="Risk management objectives...",
        relevance_score=0.85,
        evidence_spans=["The organization shall establish risk management objectives."],
        retrieval_method="hybrid",
    )
    assert result.relevance_score == 0.85
    assert result.retrieval_method == "hybrid"


def test_coverage_assessment_instantiation():
    """Test CoverageAssessment can be instantiated."""
    assessment = CoverageAssessment(
        subcategory_id="GV.RM-01",
        status="partially_covered",
        lexical_score=0.6,
        semantic_score=0.7,
        evidence_spans=["Risk management is addressed in Section 3."],
        confidence=0.65,
    )
    assert assessment.status == "partially_covered"
    assert assessment.confidence == 0.65


def test_gap_detail_instantiation():
    """Test GapDetail can be instantiated."""
    gap = GapDetail(
        subcategory_id="GV.RM-01",
        subcategory_description="Risk management objectives are established...",
        status="missing",
        evidence_quote="",
        gap_explanation="The policy does not address risk management objectives.",
        severity="high",
        suggested_fix="Add section: 'Risk Management Objectives: The organization shall...'",
    )
    assert gap.status == "missing"
    assert gap.severity == "high"


def test_gap_analysis_report_instantiation():
    """Test GapAnalysisReport can be instantiated."""
    gap = GapDetail(
        subcategory_id="GV.RM-01",
        subcategory_description="Risk management objectives...",
        status="missing",
        evidence_quote="",
        gap_explanation="Missing risk management objectives.",
        severity="high",
        suggested_fix="Add risk management section.",
    )
    report = GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file="/path/to/policy.pdf",
        input_file_hash="abc123",
        model_name="qwen2.5-3b-instruct",
        model_version="q4_k_m",
        embedding_model="all-MiniLM-L6-v2",
        gaps=[gap],
        covered_subcategories=["GV.OC-01"],
        metadata={"prompt_version": "1.0.0"},
    )
    assert len(report.gaps) == 1
    assert len(report.covered_subcategories) == 1


def test_revision_instantiation():
    """Test Revision can be instantiated."""
    revision = Revision(
        section="Section 3: Risk Management",
        gap_addressed="GV.RM-01",
        original_clause="",
        revised_clause="The organization shall establish risk management objectives.",
        revision_type="injection",
    )
    assert revision.revision_type == "injection"
    assert revision.gap_addressed == "GV.RM-01"


def test_revised_policy_instantiation():
    """Test RevisedPolicy can be instantiated."""
    revision = Revision(
        section="Section 3",
        gap_addressed="GV.RM-01",
        original_clause="",
        revised_clause="New clause text.",
        revision_type="injection",
    )
    policy = RevisedPolicy(
        original_text="Original policy text.",
        revised_text="Revised policy text with new clause.",
        revisions=[revision],
        warning="IMPORTANT: This revised policy was generated by an AI system...",
        metadata={"revision_date": "2024-01-15"},
    )
    assert len(policy.revisions) == 1
    assert "AI system" in policy.warning


def test_action_item_instantiation():
    """Test ActionItem can be instantiated."""
    action = ActionItem(
        action_id="ACT-001",
        timeframe="immediate",
        severity="high",
        effort="medium",
        csf_subcategory="GV.RM-01",
        policy_section="Section 3: Risk Management",
        description="Establish risk management objectives.",
        technical_steps=["Implement risk assessment tool"],
        administrative_steps=["Draft risk management policy"],
        physical_steps=[],
    )
    assert action.action_id == "ACT-001"
    assert action.timeframe == "immediate"
    assert len(action.technical_steps) == 1


def test_implementation_roadmap_instantiation():
    """Test ImplementationRoadmap can be instantiated."""
    action = ActionItem(
        action_id="ACT-001",
        timeframe="immediate",
        severity="high",
        effort="medium",
        csf_subcategory="GV.RM-01",
        policy_section="Section 3",
        description="Establish risk management objectives.",
        technical_steps=[],
        administrative_steps=[],
        physical_steps=[],
    )
    roadmap = ImplementationRoadmap(
        immediate_actions=[action],
        near_term_actions=[],
        medium_term_actions=[],
        metadata={"roadmap_date": "2024-01-15"},
    )
    assert len(roadmap.immediate_actions) == 1
    assert len(roadmap.near_term_actions) == 0


def test_audit_log_entry_instantiation():
    """Test AuditLogEntry can be instantiated."""
    entry = AuditLogEntry(
        timestamp=datetime.now(),
        input_file_path="/path/to/policy.pdf",
        input_file_hash="abc123",
        model_name="qwen2.5-3b-instruct",
        model_version="q4_k_m",
        embedding_model_version="all-MiniLM-L6-v2",
        configuration_parameters={"chunk_size": 512},
        retrieval_parameters={"top_k": 5},
        prompt_template_version="1.0.0",
        output_directory="/path/to/outputs",
        analysis_duration_seconds=120.5,
    )
    assert entry.model_name == "qwen2.5-3b-instruct"
    assert entry.analysis_duration_seconds == 120.5
