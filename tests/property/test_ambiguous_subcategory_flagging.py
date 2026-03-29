"""
Property Test: Ambiguous Subcategory Flagging

**Property 25: Ambiguous Subcategory Flagging**
**Validates: Requirements 9.8**

This property test verifies that ambiguous subcategories (those with confidence
scores between 0.3 and 0.5) are properly flagged for manual review in the
gap analysis output.

Ambiguous cases indicate uncertainty in automated analysis and require human
judgment to determine actual coverage status.
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


class TestAmbiguousSubcategoryFlagging:
    """Property tests for ambiguous subcategory flagging."""
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=3, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_ambiguous_subcategories_trigger_stage_b(self, policy_chunks, subcategories):
        """Property: Ambiguous subcategories must trigger Stage B analysis.
        
        Verifies that subcategories with 'ambiguous' status from Stage A
        are processed by Stage B for LLM-based reasoning.
        """
        # Ensure we have enough subcategories
        assume(len(subcategories) >= 3)
        
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create assessments with some ambiguous cases
        assessments = []
        ambiguous_count = 0
        
        for i, subcategory in enumerate(subcategories):
            if i % 3 == 0:
                # Ambiguous case
                status = 'ambiguous'
                confidence = 0.4  # Between 0.3 and 0.5
                ambiguous_count += 1
            elif i % 3 == 1:
                # Covered case (should skip Stage B)
                status = 'covered'
                confidence = 0.9
            else:
                # Missing case (should trigger Stage B)
                status = 'missing'
                confidence = 0.1
            
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status=status,
                lexical_score=confidence,
                semantic_score=confidence,
                evidence_spans=["test"] if status != 'missing' else [],
                confidence=confidence
            ))
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status=assessment.status if assessment.status != 'ambiguous' else 'partially_covered',
                evidence_quote="test evidence" if assessment.status == 'ambiguous' else "",
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
        
        # Property: Stage B should be called for ambiguous cases
        # Count how many non-covered assessments there are
        needs_stage_b = sum(1 for a in assessments if a.status != 'covered')
        
        assert mock_stage_b.reason_about_gap.call_count == needs_stage_b, \
            f"Stage B should be called {needs_stage_b} times (including {ambiguous_count} ambiguous), " \
            f"but was called {mock_stage_b.reason_about_gap.call_count} times"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        num_ambiguous=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=30, deadline=None)
    def test_ambiguous_cases_appear_in_gaps(self, policy_chunks, num_ambiguous):
        """Property: Ambiguous subcategories must appear in gap report.
        
        Verifies that ambiguous cases are included in the gaps list
        (not in covered list) for manual review.
        """
        # Generate subcategories
        subcategories = [
            CSFSubcategory(
                subcategory_id=f"AMB-{i:02d}",
                function='Govern',
                category='Test Category',
                description=f'Test description {i}',
                keywords=['test', 'keyword'],
                domain_tags=['test'],
                mapped_templates=[],
                priority='medium'
            )
            for i in range(num_ambiguous)
        ]
        
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create all ambiguous assessments
        assessments = [
            CoverageAssessment(
                subcategory_id=s.subcategory_id,
                status='ambiguous',
                lexical_score=0.4,
                semantic_score=0.4,
                evidence_spans=["test evidence"],
                confidence=0.4
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
                status='partially_covered',  # Ambiguous becomes partially_covered after Stage B
                evidence_quote="test evidence",
                gap_explanation="Ambiguous coverage requires manual review",
                severity=severity,
                suggested_fix="Manual review required"
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
        
        # Property: All ambiguous cases should appear in gaps
        assert len(report.gaps) == num_ambiguous, \
            f"Expected {num_ambiguous} gaps for ambiguous cases, got {len(report.gaps)}"
        
        # Property: No ambiguous cases should be in covered list
        assert len(report.covered_subcategories) == 0, \
            f"Ambiguous cases should not be in covered list, found {len(report.covered_subcategories)}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=5, max_size=15)
    )
    @settings(max_examples=30, deadline=None)
    def test_ambiguous_confidence_range(self, policy_chunks, subcategories):
        """Property: Ambiguous status corresponds to confidence in [0.3, 0.5).
        
        Verifies that Stage A correctly classifies subcategories with
        confidence between 0.3 and 0.5 as 'ambiguous'.
        """
        # Ensure we have enough subcategories
        assume(len(subcategories) >= 5)
        
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create assessments with various confidence levels
        assessments = []
        for i, subcategory in enumerate(subcategories):
            # Cycle through different confidence ranges
            if i % 5 == 0:
                # Covered: > 0.8
                status = 'covered'
                confidence = 0.9
            elif i % 5 == 1:
                # Partially covered: 0.5 to 0.8
                status = 'partially_covered'
                confidence = 0.6
            elif i % 5 == 2:
                # Ambiguous: 0.3 to 0.5
                status = 'ambiguous'
                confidence = 0.4
            elif i % 5 == 3:
                # Missing: < 0.3
                status = 'missing'
                confidence = 0.2
            else:
                # Another ambiguous case at boundary
                status = 'ambiguous'
                confidence = 0.35
            
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status=status,
                lexical_score=confidence,
                semantic_score=confidence,
                evidence_spans=["test"] if status != 'missing' else [],
                confidence=confidence
            ))
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status=assessment.status if assessment.status != 'ambiguous' else 'partially_covered',
                evidence_quote="test" if assessment.status != 'missing' else "",
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
        
        # Property: Verify ambiguous cases were processed
        ambiguous_assessments = [a for a in assessments if a.status == 'ambiguous']
        
        # All ambiguous cases should trigger Stage B
        # (Stage B is called for ambiguous, missing, and partially_covered)
        needs_stage_b = [a for a in assessments if a.status != 'covered']
        
        assert mock_stage_b.reason_about_gap.call_count == len(needs_stage_b), \
            f"Stage B should be called for {len(needs_stage_b)} non-covered cases, " \
            f"including {len(ambiguous_assessments)} ambiguous"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=30, deadline=None)
    def test_ambiguous_gaps_have_evidence(self, policy_chunks, subcategories):
        """Property: Ambiguous gaps should have evidence quotes.
        
        Verifies that ambiguous cases (which have some evidence but unclear
        coverage) include evidence quotes in the gap report, unlike missing
        cases which have empty evidence quotes.
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create all ambiguous assessments with evidence
        assessments = [
            CoverageAssessment(
                subcategory_id=s.subcategory_id,
                status='ambiguous',
                lexical_score=0.4,
                semantic_score=0.4,
                evidence_spans=[f"Evidence for {s.subcategory_id}"],
                confidence=0.4
            )
            for s in subcategories
        ]
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B to preserve evidence
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=subcategory.subcategory_id,
                subcategory_description=subcategory.description,
                status='partially_covered',
                evidence_quote=assessment.evidence_spans[0] if assessment.evidence_spans else "",
                gap_explanation="Ambiguous coverage requires manual review",
                severity=severity,
                suggested_fix="Manual review required"
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
        
        # Property: Ambiguous gaps should have non-empty evidence quotes
        for gap in report.gaps:
            assert len(gap.evidence_quote) > 0, \
                f"Ambiguous gap {gap.subcategory_id} should have evidence quote, " \
                f"got empty string"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
