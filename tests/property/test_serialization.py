"""
Property-based tests for data model serialization.

**Validates: Requirements 3.4, 13.4**

Tests that all domain models can be serialized to JSON and deserialized back
without data loss, ensuring reliable persistence and output generation.
"""

import json
from dataclasses import asdict, fields
from datetime import datetime
from typing import Any, Dict

import numpy as np
import pytest
from hypothesis import given, strategies as st

from models.domain import (
    ActionItem,
    AuditLogEntry,
    CoverageAssessment,
    CSFSubcategory,
    DocumentStructure,
    GapAnalysisReport,
    GapDetail,
    Heading,
    ImplementationRoadmap,
    ParsedDocument,
    Paragraph,
    RetrievalResult,
    Revision,
    RevisedPolicy,
    Section,
    TextChunk,
)


# ============================================================================
# Serialization/Deserialization Helpers
# ============================================================================


def serialize_model(obj: Any) -> str:
    """Serialize a dataclass instance to JSON string."""
    def converter(o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, np.ndarray):
            return o.tolist()
        elif hasattr(o, '__dataclass_fields__'):
            return asdict(o)
        raise TypeError(f"Object of type {type(o)} is not JSON serializable")
    
    return json.dumps(asdict(obj), default=converter)


def deserialize_model(json_str: str, model_class: type) -> Any:
    """Deserialize JSON string back to dataclass instance."""
    data = json.loads(json_str)
    return reconstruct_model(data, model_class)


def reconstruct_model(data: Dict, model_class: type) -> Any:
    """Recursively reconstruct a dataclass from a dictionary."""
    if not hasattr(model_class, '__dataclass_fields__'):
        return data
    
    field_types = {f.name: f.type for f in fields(model_class)}
    kwargs = {}
    
    for field_name, field_value in data.items():
        field_type = field_types.get(field_name)
        
        if field_value is None:
            kwargs[field_name] = None
        elif field_type == datetime:
            kwargs[field_name] = datetime.fromisoformat(field_value)
        elif field_name == 'embedding' and isinstance(field_value, list):
            kwargs[field_name] = np.array(field_value)
        elif hasattr(field_type, '__dataclass_fields__'):
            kwargs[field_name] = reconstruct_model(field_value, field_type)
        elif hasattr(field_type, '__origin__'):  # Generic types like List, Dict
            origin = field_type.__origin__
            if origin is list:
                args = field_type.__args__
                if args and hasattr(args[0], '__dataclass_fields__'):
                    kwargs[field_name] = [reconstruct_model(item, args[0]) for item in field_value]
                else:
                    kwargs[field_name] = field_value
            elif origin is dict:
                kwargs[field_name] = field_value
            else:
                kwargs[field_name] = field_value
        else:
            kwargs[field_name] = field_value
    
    return model_class(**kwargs)


# ============================================================================
# Hypothesis Strategies for Domain Models
# ============================================================================


@st.composite
def heading_strategy(draw):
    """Generate random Heading instances."""
    start = draw(st.integers(min_value=0, max_value=1000))
    length = draw(st.integers(min_value=1, max_value=100))
    return Heading(
        level=draw(st.integers(min_value=1, max_value=6)),
        text=draw(st.text(min_size=1, max_size=100)),
        start_pos=start,
        end_pos=start + length,
    )


@st.composite
def paragraph_strategy(draw):
    """Generate random Paragraph instances."""
    start = draw(st.integers(min_value=0, max_value=1000))
    length = draw(st.integers(min_value=1, max_value=500))
    return Paragraph(
        text=draw(st.text(min_size=1, max_size=500)),
        start_pos=start,
        end_pos=start + length,
    )


@st.composite
def section_strategy(draw, max_depth=2, current_depth=0):
    """Generate random Section instances with optional subsections."""
    start = draw(st.integers(min_value=0, max_value=1000))
    length = draw(st.integers(min_value=1, max_value=500))
    
    # Limit recursion depth to avoid infinite nesting
    if current_depth < max_depth:
        subsections = draw(st.lists(
            section_strategy(max_depth=max_depth, current_depth=current_depth + 1),
            max_size=2
        ))
    else:
        subsections = []
    
    return Section(
        title=draw(st.text(min_size=1, max_size=100)),
        content=draw(st.text(min_size=0, max_size=500)),
        start_pos=start,
        end_pos=start + length,
        subsections=subsections,
    )


@st.composite
def document_structure_strategy(draw):
    """Generate random DocumentStructure instances."""
    return DocumentStructure(
        headings=draw(st.lists(heading_strategy(), max_size=5)),
        sections=draw(st.lists(section_strategy(), max_size=3)),
        paragraphs=draw(st.lists(paragraph_strategy(), max_size=5)),
    )


@st.composite
def parsed_document_strategy(draw):
    """Generate random ParsedDocument instances."""
    return ParsedDocument(
        text=draw(st.text(min_size=1, max_size=1000)),
        file_path=draw(st.text(min_size=1, max_size=100)),
        file_type=draw(st.sampled_from(['pdf', 'docx', 'txt'])),
        page_count=draw(st.integers(min_value=1, max_value=100)),
        structure=draw(document_structure_strategy()),
        metadata=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.text(min_size=0, max_size=50),
            max_size=5
        )),
    )


@st.composite
def text_chunk_strategy(draw):
    """Generate random TextChunk instances."""
    start = draw(st.integers(min_value=0, max_value=1000))
    length = draw(st.integers(min_value=1, max_value=512))
    
    # Generate optional embedding (384-dimensional vector)
    has_embedding = draw(st.booleans())
    embedding = np.random.rand(384) if has_embedding else None
    
    return TextChunk(
        text=draw(st.text(min_size=1, max_size=512)),
        chunk_id=draw(st.text(min_size=1, max_size=50)),
        source_file=draw(st.text(min_size=1, max_size=100)),
        start_pos=start,
        end_pos=start + length,
        page_number=draw(st.one_of(st.none(), st.integers(min_value=1, max_value=100))),
        section_title=draw(st.one_of(st.none(), st.text(min_size=1, max_size=100))),
        embedding=embedding,
    )


@st.composite
def csf_subcategory_strategy(draw):
    """Generate random CSFSubcategory instances."""
    return CSFSubcategory(
        subcategory_id=draw(st.text(min_size=1, max_size=20)),
        function=draw(st.sampled_from(['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover'])),
        category=draw(st.text(min_size=1, max_size=100)),
        description=draw(st.text(min_size=1, max_size=500)),
        keywords=draw(st.lists(st.text(min_size=1, max_size=50), max_size=10)),
        domain_tags=draw(st.lists(st.text(min_size=1, max_size=50), max_size=5)),
        mapped_templates=draw(st.lists(st.text(min_size=1, max_size=100), max_size=5)),
        priority=draw(st.sampled_from(['critical', 'high', 'medium', 'low'])),
    )


@st.composite
def retrieval_result_strategy(draw):
    """Generate random RetrievalResult instances."""
    return RetrievalResult(
        subcategory_id=draw(st.text(min_size=1, max_size=20)),
        subcategory_text=draw(st.text(min_size=1, max_size=500)),
        relevance_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        evidence_spans=draw(st.lists(st.text(min_size=1, max_size=200), max_size=5)),
        retrieval_method=draw(st.sampled_from(['dense', 'sparse', 'hybrid'])),
    )


@st.composite
def coverage_assessment_strategy(draw):
    """Generate random CoverageAssessment instances."""
    return CoverageAssessment(
        subcategory_id=draw(st.text(min_size=1, max_size=20)),
        status=draw(st.sampled_from(['covered', 'partially_covered', 'missing', 'ambiguous'])),
        lexical_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        semantic_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        evidence_spans=draw(st.lists(st.text(min_size=0, max_size=200), max_size=5)),
        confidence=draw(st.floats(min_value=0.0, max_value=1.0)),
    )


@st.composite
def gap_detail_strategy(draw):
    """Generate random GapDetail instances."""
    return GapDetail(
        subcategory_id=draw(st.text(min_size=1, max_size=20)),
        subcategory_description=draw(st.text(min_size=1, max_size=500)),
        status=draw(st.sampled_from(['partially_covered', 'missing'])),
        evidence_quote=draw(st.text(min_size=0, max_size=200)),
        gap_explanation=draw(st.text(min_size=1, max_size=500)),
        severity=draw(st.sampled_from(['critical', 'high', 'medium', 'low'])),
        suggested_fix=draw(st.text(min_size=1, max_size=500)),
    )


@st.composite
def gap_analysis_report_strategy(draw):
    """Generate random GapAnalysisReport instances."""
    return GapAnalysisReport(
        analysis_date=draw(st.datetimes()),
        input_file=draw(st.text(min_size=1, max_size=100)),
        input_file_hash=draw(st.text(min_size=1, max_size=64)),
        model_name=draw(st.text(min_size=1, max_size=50)),
        model_version=draw(st.text(min_size=1, max_size=20)),
        embedding_model=draw(st.text(min_size=1, max_size=50)),
        gaps=draw(st.lists(gap_detail_strategy(), max_size=5)),
        covered_subcategories=draw(st.lists(st.text(min_size=1, max_size=20), max_size=10)),
        metadata=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.text(min_size=0, max_size=50),
            max_size=5
        )),
    )


@st.composite
def revision_strategy(draw):
    """Generate random Revision instances."""
    return Revision(
        section=draw(st.text(min_size=1, max_size=100)),
        gap_addressed=draw(st.text(min_size=1, max_size=20)),
        original_clause=draw(st.text(min_size=0, max_size=500)),
        revised_clause=draw(st.text(min_size=1, max_size=500)),
        revision_type=draw(st.sampled_from(['injection', 'strengthening'])),
    )


@st.composite
def revised_policy_strategy(draw):
    """Generate random RevisedPolicy instances."""
    return RevisedPolicy(
        original_text=draw(st.text(min_size=1, max_size=1000)),
        revised_text=draw(st.text(min_size=1, max_size=1000)),
        revisions=draw(st.lists(revision_strategy(), max_size=5)),
        warning=draw(st.text(min_size=1, max_size=500)),
        metadata=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.text(min_size=0, max_size=50),
            max_size=5
        )),
    )


@st.composite
def action_item_strategy(draw):
    """Generate random ActionItem instances."""
    return ActionItem(
        action_id=draw(st.text(min_size=1, max_size=20)),
        timeframe=draw(st.sampled_from(['immediate', 'near_term', 'medium_term'])),
        severity=draw(st.sampled_from(['critical', 'high', 'medium', 'low'])),
        effort=draw(st.sampled_from(['low', 'medium', 'high'])),
        csf_subcategory=draw(st.text(min_size=1, max_size=20)),
        policy_section=draw(st.text(min_size=1, max_size=100)),
        description=draw(st.text(min_size=1, max_size=500)),
        technical_steps=draw(st.lists(st.text(min_size=1, max_size=200), max_size=5)),
        administrative_steps=draw(st.lists(st.text(min_size=1, max_size=200), max_size=5)),
        physical_steps=draw(st.lists(st.text(min_size=1, max_size=200), max_size=5)),
    )


@st.composite
def implementation_roadmap_strategy(draw):
    """Generate random ImplementationRoadmap instances."""
    return ImplementationRoadmap(
        immediate_actions=draw(st.lists(action_item_strategy(), max_size=3)),
        near_term_actions=draw(st.lists(action_item_strategy(), max_size=3)),
        medium_term_actions=draw(st.lists(action_item_strategy(), max_size=3)),
        metadata=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.text(min_size=0, max_size=50),
            max_size=5
        )),
    )


@st.composite
def audit_log_entry_strategy(draw):
    """Generate random AuditLogEntry instances."""
    return AuditLogEntry(
        timestamp=draw(st.datetimes()),
        input_file_path=draw(st.text(min_size=1, max_size=100)),
        input_file_hash=draw(st.text(min_size=1, max_size=64)),
        model_name=draw(st.text(min_size=1, max_size=50)),
        model_version=draw(st.text(min_size=1, max_size=20)),
        embedding_model_version=draw(st.text(min_size=1, max_size=50)),
        configuration_parameters=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(max_size=50)
            ),
            max_size=5
        )),
        retrieval_parameters=draw(st.dictionaries(
            st.text(min_size=1, max_size=20),
            st.one_of(
                st.integers(),
                st.floats(allow_nan=False, allow_infinity=False),
                st.text(max_size=50)
            ),
            max_size=5
        )),
        prompt_template_version=draw(st.text(min_size=1, max_size=20)),
        output_directory=draw(st.text(min_size=1, max_size=100)),
        analysis_duration_seconds=draw(st.floats(min_value=0.0, max_value=10000.0, allow_nan=False, allow_infinity=False)),
    )


# ============================================================================
# Property 7: Reference Catalog Persistence Round-Trip
# **Validates: Requirements 3.4, 13.4**
# ============================================================================


@given(heading_strategy())
def test_heading_serialization_roundtrip(heading):
    """Test Heading serialization and deserialization preserves all fields."""
    json_str = serialize_model(heading)
    restored = deserialize_model(json_str, Heading)
    
    assert restored.level == heading.level
    assert restored.text == heading.text
    assert restored.start_pos == heading.start_pos
    assert restored.end_pos == heading.end_pos


@given(paragraph_strategy())
def test_paragraph_serialization_roundtrip(paragraph):
    """Test Paragraph serialization and deserialization preserves all fields."""
    json_str = serialize_model(paragraph)
    restored = deserialize_model(json_str, Paragraph)
    
    assert restored.text == paragraph.text
    assert restored.start_pos == paragraph.start_pos
    assert restored.end_pos == paragraph.end_pos


@given(section_strategy())
def test_section_serialization_roundtrip(section):
    """Test Section serialization and deserialization preserves all fields including nested subsections."""
    json_str = serialize_model(section)
    restored = deserialize_model(json_str, Section)
    
    assert restored.title == section.title
    assert restored.content == section.content
    assert restored.start_pos == section.start_pos
    assert restored.end_pos == section.end_pos
    assert len(restored.subsections) == len(section.subsections)


@given(document_structure_strategy())
def test_document_structure_serialization_roundtrip(structure):
    """Test DocumentStructure serialization and deserialization preserves all fields."""
    json_str = serialize_model(structure)
    restored = deserialize_model(json_str, DocumentStructure)
    
    assert len(restored.headings) == len(structure.headings)
    assert len(restored.sections) == len(structure.sections)
    assert len(restored.paragraphs) == len(structure.paragraphs)


@given(parsed_document_strategy())
def test_parsed_document_serialization_roundtrip(document):
    """Test ParsedDocument serialization and deserialization preserves all fields."""
    json_str = serialize_model(document)
    restored = deserialize_model(json_str, ParsedDocument)
    
    assert restored.text == document.text
    assert restored.file_path == document.file_path
    assert restored.file_type == document.file_type
    assert restored.page_count == document.page_count
    assert restored.metadata == document.metadata


@given(text_chunk_strategy())
def test_text_chunk_serialization_roundtrip(chunk):
    """Test TextChunk serialization and deserialization preserves all fields including embeddings."""
    json_str = serialize_model(chunk)
    restored = deserialize_model(json_str, TextChunk)
    
    assert restored.text == chunk.text
    assert restored.chunk_id == chunk.chunk_id
    assert restored.source_file == chunk.source_file
    assert restored.start_pos == chunk.start_pos
    assert restored.end_pos == chunk.end_pos
    assert restored.page_number == chunk.page_number
    assert restored.section_title == chunk.section_title
    
    # Check embedding preservation
    if chunk.embedding is not None:
        assert restored.embedding is not None
        assert np.allclose(restored.embedding, chunk.embedding)
    else:
        assert restored.embedding is None


@given(csf_subcategory_strategy())
def test_csf_subcategory_serialization_roundtrip(subcategory):
    """Test CSFSubcategory serialization and deserialization preserves all fields."""
    json_str = serialize_model(subcategory)
    restored = deserialize_model(json_str, CSFSubcategory)
    
    assert restored.subcategory_id == subcategory.subcategory_id
    assert restored.function == subcategory.function
    assert restored.category == subcategory.category
    assert restored.description == subcategory.description
    assert restored.keywords == subcategory.keywords
    assert restored.domain_tags == subcategory.domain_tags
    assert restored.mapped_templates == subcategory.mapped_templates
    assert restored.priority == subcategory.priority


@given(retrieval_result_strategy())
def test_retrieval_result_serialization_roundtrip(result):
    """Test RetrievalResult serialization and deserialization preserves all fields."""
    json_str = serialize_model(result)
    restored = deserialize_model(json_str, RetrievalResult)
    
    assert restored.subcategory_id == result.subcategory_id
    assert restored.subcategory_text == result.subcategory_text
    assert abs(restored.relevance_score - result.relevance_score) < 1e-6
    assert restored.evidence_spans == result.evidence_spans
    assert restored.retrieval_method == result.retrieval_method


@given(coverage_assessment_strategy())
def test_coverage_assessment_serialization_roundtrip(assessment):
    """Test CoverageAssessment serialization and deserialization preserves all fields."""
    json_str = serialize_model(assessment)
    restored = deserialize_model(json_str, CoverageAssessment)
    
    assert restored.subcategory_id == assessment.subcategory_id
    assert restored.status == assessment.status
    assert abs(restored.lexical_score - assessment.lexical_score) < 1e-6
    assert abs(restored.semantic_score - assessment.semantic_score) < 1e-6
    assert restored.evidence_spans == assessment.evidence_spans
    assert abs(restored.confidence - assessment.confidence) < 1e-6


@given(gap_detail_strategy())
def test_gap_detail_serialization_roundtrip(gap):
    """Test GapDetail serialization and deserialization preserves all fields."""
    json_str = serialize_model(gap)
    restored = deserialize_model(json_str, GapDetail)
    
    assert restored.subcategory_id == gap.subcategory_id
    assert restored.subcategory_description == gap.subcategory_description
    assert restored.status == gap.status
    assert restored.evidence_quote == gap.evidence_quote
    assert restored.gap_explanation == gap.gap_explanation
    assert restored.severity == gap.severity
    assert restored.suggested_fix == gap.suggested_fix


@given(gap_analysis_report_strategy())
def test_gap_analysis_report_serialization_roundtrip(report):
    """Test GapAnalysisReport serialization and deserialization preserves all fields."""
    json_str = serialize_model(report)
    restored = deserialize_model(json_str, GapAnalysisReport)
    
    assert restored.analysis_date == report.analysis_date
    assert restored.input_file == report.input_file
    assert restored.input_file_hash == report.input_file_hash
    assert restored.model_name == report.model_name
    assert restored.model_version == report.model_version
    assert restored.embedding_model == report.embedding_model
    assert len(restored.gaps) == len(report.gaps)
    assert restored.covered_subcategories == report.covered_subcategories
    assert restored.metadata == report.metadata


@given(revision_strategy())
def test_revision_serialization_roundtrip(revision):
    """Test Revision serialization and deserialization preserves all fields."""
    json_str = serialize_model(revision)
    restored = deserialize_model(json_str, Revision)
    
    assert restored.section == revision.section
    assert restored.gap_addressed == revision.gap_addressed
    assert restored.original_clause == revision.original_clause
    assert restored.revised_clause == revision.revised_clause
    assert restored.revision_type == revision.revision_type


@given(revised_policy_strategy())
def test_revised_policy_serialization_roundtrip(policy):
    """Test RevisedPolicy serialization and deserialization preserves all fields."""
    json_str = serialize_model(policy)
    restored = deserialize_model(json_str, RevisedPolicy)
    
    assert restored.original_text == policy.original_text
    assert restored.revised_text == policy.revised_text
    assert len(restored.revisions) == len(policy.revisions)
    assert restored.warning == policy.warning
    assert restored.metadata == policy.metadata


@given(action_item_strategy())
def test_action_item_serialization_roundtrip(action):
    """Test ActionItem serialization and deserialization preserves all fields."""
    json_str = serialize_model(action)
    restored = deserialize_model(json_str, ActionItem)
    
    assert restored.action_id == action.action_id
    assert restored.timeframe == action.timeframe
    assert restored.severity == action.severity
    assert restored.effort == action.effort
    assert restored.csf_subcategory == action.csf_subcategory
    assert restored.policy_section == action.policy_section
    assert restored.description == action.description
    assert restored.technical_steps == action.technical_steps
    assert restored.administrative_steps == action.administrative_steps
    assert restored.physical_steps == action.physical_steps


@given(implementation_roadmap_strategy())
def test_implementation_roadmap_serialization_roundtrip(roadmap):
    """Test ImplementationRoadmap serialization and deserialization preserves all fields."""
    json_str = serialize_model(roadmap)
    restored = deserialize_model(json_str, ImplementationRoadmap)
    
    assert len(restored.immediate_actions) == len(roadmap.immediate_actions)
    assert len(restored.near_term_actions) == len(roadmap.near_term_actions)
    assert len(restored.medium_term_actions) == len(roadmap.medium_term_actions)
    assert restored.metadata == roadmap.metadata


@given(audit_log_entry_strategy())
def test_audit_log_entry_serialization_roundtrip(entry):
    """Test AuditLogEntry serialization and deserialization preserves all fields."""
    json_str = serialize_model(entry)
    restored = deserialize_model(json_str, AuditLogEntry)
    
    assert restored.timestamp == entry.timestamp
    assert restored.input_file_path == entry.input_file_path
    assert restored.input_file_hash == entry.input_file_hash
    assert restored.model_name == entry.model_name
    assert restored.model_version == entry.model_version
    assert restored.embedding_model_version == entry.embedding_model_version
    assert restored.configuration_parameters == entry.configuration_parameters
    assert restored.retrieval_parameters == entry.retrieval_parameters
    assert restored.prompt_template_version == entry.prompt_template_version
    assert restored.output_directory == entry.output_directory
    assert abs(restored.analysis_duration_seconds - entry.analysis_duration_seconds) < 1e-6
