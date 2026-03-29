"""
Property Test: Gap Report Completeness

**Property 24: Gap Report Completeness**
**Validates: Requirements 9.6, 9.9, 9.10, 9.11**

This property test verifies that all gap reports include the required fields:
- subcategory_id: CSF subcategory identifier
- description: Full NIST outcome text
- status: Gap status (partially_covered or missing)
- evidence_quote: Relevant policy text (or empty if missing)
- gap_explanation: Clear explanation of the gap
- severity: Gap severity level (critical/high/medium/low)
- suggested_fix: Specific policy language to address the gap

This ensures gap reports are complete, structured, and actionable.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock
import numpy as np

from models.domain import (
    TextChunk,
    CSFSubcategory,
    CoverageAssessment,
    GapDetail
)
from analysis.gap_analysis_engine import GapAnalysisEngine
from analysis.stage_a_detector import StageADetector
from analysis.stage_b_reasoner import StageBReasoner
from reference_builder.reference_catalog import ReferenceCatalog


# Required fields for gap details
REQUIRED_GAP_FIELDS = {
    'subcategory_id',
    'subcategory_description',
    'status',
    'evidence_quote',
    'gap_explanation',
    'severity',
    'suggested_fix'
}

# Valid severity levels
VALID_SEVERITIES = {'critical', 'high', 'medium', 'low'}

# Valid gap statuses
VALID_GAP_STATUSES = {'partially_covered', 'missing'}


# Strategy for generating CSF subcategories
@st.composite
def csf_subcategory_strategy(draw):
    """Generate random CSF subcategory."""
    functions = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
    priorities = ['critical', 'high', 'medium', 'low']
    
    function = draw(st.sampled_from(functions))
    subcategory_id = f"{function[:2].upper()}.{draw(st.text(min_size=2, max_size=4, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))}-{draw(st.integers(min_value=1, max_value=99)):02d}"
    
    return CSFSubcategory(
        subcategory_id=subcategory_id,
        function=function,
        category=draw(st.text(min_size=5, max_size=50)),
        description=draw(st.text(min_size=20, max_size=200)),
        keywords=draw(st.lists(st.text(min_size=3, max_size=15), min_size=1, max_size=10)),
        domain_tags=draw(st.lists(st.text(min_size=3, max_size=20), min_size=0, max_size=5)),
        mapped_templates=draw(st.lists(st.text(min_size=5, max_size=30), min_size=0, max_size=3)),
        priority=draw(st.sampled_from(priorities))
    )


# Strategy for generating text chunks
@st.composite
def text_chunk_strategy(draw):
    """Generate random text chunk."""
    chunk_id = f"chunk_{draw(st.integers(min_value=1, max_value=1000))}"
    
    return TextChunk(
        text=draw(st.text(min_size=50, max_size=500)),
        chunk_id=chunk_id,
        source_file="test_policy.pdf",
        start_pos=draw(st.integers(min_value=0, max_value=10000)),
        end_pos=draw(st.integers(min_value=0, max_value=10000)),
        page_number=draw(st.integers(min_value=1, max_value=100)),
        section_title=draw(st.text(min_size=5, max_size=50)),
        embedding=np.random.rand(384)
    )


class TestGapReportCompleteness:
    """Property tests for gap report completeness."""
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_all_gaps_have_required_fields(self, policy_chunks, subcategories):
        """Property: All gaps must include all required fields.
        
        Verifies that every gap in the report contains:
        - subcategory_id
        - subcategory_description (description)
        - status
        - evidence_quote
        - gap_explanation
        - severity
        - suggested_fix
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create assessments that will trigger Stage B (missing/ambiguous)
        assessments = []
        for subcategory in subcategories:
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status='missing',  # Force Stage B
                lexical_score=0.1,
                semantic_score=0.1,
                evidence_spans=[],
                confidence=0.1
            ))
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B to return complete gap details
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status='missing',
                evidence_quote="",
                gap_explanation=f"Gap explanation for {subcategory.subcategory_id}",
                severity=severity,
                suggested_fix=f"Suggested fix for {subcategory.subcategory_id}"
            )
        
        mock_stage_b.reason_about_gap.side_effect = create_gap_detail
        
        # Create engine
        engine = GapAnalysisEngine(
            stage_a=mock_stage_a,
            stage_b=mock_stage_b,
            catalog=mock_catalog
        )
        
        # Execute analysis
        report = engine.analyze(
            policy_chunks=policy_chunks,
            input_file="test_policy.pdf"
        )
        
        # Property: All gaps must have all required fields
        for gap in report.gaps:
            # Check all required fields are present and non-None
            assert gap.subcategory_id is not None, \
                "Gap must have subcategory_id"
            assert gap.subcategory_description is not None, \
                "Gap must have subcategory_description"
            assert gap.status is not None, \
                "Gap must have status"
            assert gap.evidence_quote is not None, \
                "Gap must have evidence_quote (can be empty string)"
            assert gap.gap_explanation is not None, \
                "Gap must have gap_explanation"
            assert gap.severity is not None, \
                "Gap must have severity"
            assert gap.suggested_fix is not None, \
                "Gap must have suggested_fix"
            
            # Check fields are not empty strings (except evidence_quote for missing)
            assert len(gap.subcategory_id) > 0, \
                "subcategory_id cannot be empty"
            assert len(gap.subcategory_description) > 0, \
                "subcategory_description cannot be empty"
            assert len(gap.status) > 0, \
                "status cannot be empty"
            assert len(gap.gap_explanation) > 0, \
                "gap_explanation cannot be empty"
            assert len(gap.severity) > 0, \
                "severity cannot be empty"
            assert len(gap.suggested_fix) > 0, \
                "suggested_fix cannot be empty"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_gap_severity_is_valid(self, policy_chunks, subcategories):
        """Property: All gap severity levels must be valid.
        
        Verifies that severity is one of: critical, high, medium, low.
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create missing assessments
        assessments = [
            CoverageAssessment(
                subcategory_id=s.subcategory_id,
                status='missing',
                lexical_score=0.1,
                semantic_score=0.1,
                evidence_spans=[],
                confidence=0.1
            )
            for s in subcategories
        ]
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status='missing',
                evidence_quote="",
                gap_explanation="Test gap",
                severity=severity,  # Use the severity assigned by engine
                suggested_fix="Test fix"
            )
        
        mock_stage_b.reason_about_gap.side_effect = create_gap_detail
        
        # Create engine
        engine = GapAnalysisEngine(
            stage_a=mock_stage_a,
            stage_b=mock_stage_b,
            catalog=mock_catalog
        )
        
        # Execute analysis
        report = engine.analyze(
            policy_chunks=policy_chunks,
            input_file="test_policy.pdf"
        )
        
        # Property: All severities must be valid
        for gap in report.gaps:
            assert gap.severity in VALID_SEVERITIES, \
                f"Gap severity '{gap.severity}' is not in valid set {VALID_SEVERITIES}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_gap_status_is_valid(self, policy_chunks, subcategories):
        """Property: All gap statuses must be valid.
        
        Verifies that gap status is either 'partially_covered' or 'missing'.
        Covered subcategories should not appear in gaps.
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create mixed assessments
        assessments = []
        for i, subcategory in enumerate(subcategories):
            if i % 2 == 0:
                status = 'missing'
            else:
                status = 'partially_covered'
            
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status=status,
                lexical_score=0.1 if status == 'missing' else 0.6,
                semantic_score=0.1 if status == 'missing' else 0.6,
                evidence_spans=[] if status == 'missing' else ["test"],
                confidence=0.1 if status == 'missing' else 0.6
            ))
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status=assessment.status,  # Use status from assessment
                evidence_quote="" if assessment.status == 'missing' else "test evidence",
                gap_explanation="Test gap",
                severity=severity,
                suggested_fix="Test fix"
            )
        
        mock_stage_b.reason_about_gap.side_effect = create_gap_detail
        
        # Create engine
        engine = GapAnalysisEngine(
            stage_a=mock_stage_a,
            stage_b=mock_stage_b,
            catalog=mock_catalog
        )
        
        # Execute analysis
        report = engine.analyze(
            policy_chunks=policy_chunks,
            input_file="test_policy.pdf"
        )
        
        # Property: All gap statuses must be valid
        for gap in report.gaps:
            assert gap.status in VALID_GAP_STATUSES, \
                f"Gap status '{gap.status}' is not in valid set {VALID_GAP_STATUSES}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=30, deadline=None)
    def test_missing_gaps_have_empty_evidence_quote(self, policy_chunks, subcategories):
        """Property: Missing gaps should have empty evidence_quote.
        
        Verifies that when status is 'missing', evidence_quote is empty
        (since there's no policy text to quote).
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create all missing assessments
        assessments = [
            CoverageAssessment(
                subcategory_id=s.subcategory_id,
                status='missing',
                lexical_score=0.1,
                semantic_score=0.1,
                evidence_spans=[],
                confidence=0.1
            )
            for s in subcategories
        ]
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status='missing',
                evidence_quote="",  # Empty for missing
                gap_explanation="Test gap",
                severity=severity,
                suggested_fix="Test fix"
            )
        
        mock_stage_b.reason_about_gap.side_effect = create_gap_detail
        
        # Create engine
        engine = GapAnalysisEngine(
            stage_a=mock_stage_a,
            stage_b=mock_stage_b,
            catalog=mock_catalog
        )
        
        # Execute analysis
        report = engine.analyze(
            policy_chunks=policy_chunks,
            input_file="test_policy.pdf"
        )
        
        # Property: Missing gaps should have empty evidence_quote
        for gap in report.gaps:
            if gap.status == 'missing':
                assert gap.evidence_quote == "", \
                    f"Missing gap {gap.subcategory_id} should have empty evidence_quote, " \
                    f"got '{gap.evidence_quote}'"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=30, deadline=None)
    def test_report_metadata_completeness(self, policy_chunks, subcategories):
        """Property: Gap analysis report must include complete metadata.
        
        Verifies that the report includes:
        - analysis_date
        - input_file
        - input_file_hash
        - model_name
        - model_version
        - embedding_model
        - gaps list
        - covered_subcategories list
        - metadata dict
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create mixed assessments
        assessments = []
        for i, subcategory in enumerate(subcategories):
            status = 'covered' if i % 2 == 0 else 'missing'
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status=status,
                lexical_score=0.9 if status == 'covered' else 0.1,
                semantic_score=0.9 if status == 'covered' else 0.1,
                evidence_spans=["test"] if status == 'covered' else [],
                confidence=0.9 if status == 'covered' else 0.1
            ))
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status='missing',
                evidence_quote="",
                gap_explanation="Test gap",
                severity=severity,
                suggested_fix="Test fix"
            )
        
        mock_stage_b.reason_about_gap.side_effect = create_gap_detail
        
        # Create engine
        engine = GapAnalysisEngine(
            stage_a=mock_stage_a,
            stage_b=mock_stage_b,
            catalog=mock_catalog,
            model_name="test-model",
            model_version="1.0",
            embedding_model="test-embedding"
        )
        
        # Execute analysis
        report = engine.analyze(
            policy_chunks=policy_chunks,
            input_file="test_policy.pdf"
        )
        
        # Property: Report must have all required metadata fields
        assert report.analysis_date is not None, "Report must have analysis_date"
        assert report.input_file is not None, "Report must have input_file"
        assert report.input_file_hash is not None, "Report must have input_file_hash"
        assert report.model_name is not None, "Report must have model_name"
        assert report.model_version is not None, "Report must have model_version"
        assert report.embedding_model is not None, "Report must have embedding_model"
        assert report.gaps is not None, "Report must have gaps list"
        assert report.covered_subcategories is not None, "Report must have covered_subcategories list"
        assert report.metadata is not None, "Report must have metadata dict"
        
        # Property: Metadata dict must contain expected keys
        assert 'prompt_version' in report.metadata, "Metadata must include prompt_version"
        assert 'config_hash' in report.metadata, "Metadata must include config_hash"
        assert 'retrieval_params' in report.metadata, "Metadata must include retrieval_params"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
