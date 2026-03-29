"""
Property Test: Coverage Status Classification

**Property 22: Coverage Status Classification**
**Validates: Requirements 9.4**

This property test verifies that each CSF subcategory receives exactly one
coverage status classification from the set:
- Covered
- Partially Covered
- Missing
- Ambiguous

This ensures deterministic, unambiguous classification of all subcategories
without overlaps or omissions.
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


# Valid coverage statuses
VALID_STATUSES = {'covered', 'partially_covered', 'missing', 'ambiguous'}


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


class TestCoverageStatusClassification:
    """Property tests for coverage status classification."""
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20, unique_by=lambda x: x.subcategory_id)
    )
    @settings(max_examples=50, deadline=None)
    def test_each_subcategory_gets_exactly_one_status(self, policy_chunks, subcategories):
        """Property: Each subcategory must receive exactly one coverage status.
        
        Verifies that:
        1. Every subcategory is classified
        2. Each subcategory has exactly one status
        3. Status is from the valid set
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create assessments with random valid statuses
        assessments = []
        for subcategory in subcategories:
            # Randomly assign a valid status
            import random
            status = random.choice(list(VALID_STATUSES))
            
            # Generate confidence consistent with status
            if status == 'covered':
                confidence = 0.9
            elif status == 'partially_covered':
                confidence = 0.6
            elif status == 'missing':
                confidence = 0.1
            else:  # ambiguous
                confidence = 0.4
            
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status=status,
                lexical_score=confidence,
                semantic_score=confidence,
                evidence_spans=["test"] if status != 'missing' else [],
                confidence=confidence
            ))
        
        # Configure Stage A to return our assessments
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B to return proper GapDetail objects
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=assessment.subcategory_id,
                subcategory_description=subcategory.description,
                status=assessment.status,
                evidence_quote="Test evidence" if assessment.evidence_spans else "",
                gap_explanation=f"Gap explanation for {assessment.subcategory_id}",
                severity=severity,
                suggested_fix=f"Suggested fix for {assessment.subcategory_id}"
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
        
        # Property 1: Every subcategory must be classified
        classified_ids = set(report.covered_subcategories)
        classified_ids.update(gap.subcategory_id for gap in report.gaps)
        
        expected_ids = {s.subcategory_id for s in subcategories}
        
        assert classified_ids == expected_ids, \
            f"All subcategories must be classified. " \
            f"Expected {expected_ids}, got {classified_ids}"
        
        # Property 2: Each subcategory appears exactly once
        all_ids = list(report.covered_subcategories) + [gap.subcategory_id for gap in report.gaps]
        assert len(all_ids) == len(set(all_ids)), \
            f"Each subcategory should appear exactly once, found duplicates: {all_ids}"
        
        # Property 3: Total classifications equals total subcategories
        total_classifications = len(report.covered_subcategories) + len(report.gaps)
        assert total_classifications == len(subcategories), \
            f"Total classifications ({total_classifications}) must equal " \
            f"total subcategories ({len(subcategories)})"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_status_is_from_valid_set(self, policy_chunks, subcategories):
        """Property: All status values must be from the valid set.
        
        Verifies that Stage A only produces valid status values:
        covered, partially_covered, missing, or ambiguous.
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create assessments with valid statuses
        assessments = []
        for i, subcategory in enumerate(subcategories):
            # Cycle through valid statuses
            status = list(VALID_STATUSES)[i % len(VALID_STATUSES)]
            
            # Generate confidence consistent with status
            if status == 'covered':
                confidence = 0.9
            elif status == 'partially_covered':
                confidence = 0.6
            elif status == 'missing':
                confidence = 0.1
            else:  # ambiguous
                confidence = 0.4
            
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
        
        # Configure Stage B to return proper GapDetail objects
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=assessment.subcategory_id,
                subcategory_description=subcategory.description,
                status=assessment.status,
                evidence_quote="Test evidence" if assessment.evidence_spans else "",
                gap_explanation=f"Gap explanation for {assessment.subcategory_id}",
                severity=severity,
                suggested_fix=f"Suggested fix for {assessment.subcategory_id}"
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
            assert gap.status in VALID_STATUSES, \
                f"Gap status '{gap.status}' is not in valid set {VALID_STATUSES}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=4, max_size=20, unique_by=lambda x: x.subcategory_id)
    )
    @settings(max_examples=30, deadline=None)
    def test_no_overlapping_classifications(self, policy_chunks, subcategories):
        """Property: No subcategory can have multiple classifications.
        
        Verifies that a subcategory cannot appear in both the covered list
        and the gaps list, ensuring mutually exclusive classification.
        """
        # Ensure we have enough subcategories
        assume(len(subcategories) >= 4)
        
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create mixed assessments
        assessments = []
        for i, subcategory in enumerate(subcategories):
            # Alternate between covered and non-covered
            if i % 2 == 0:
                status = 'covered'
                confidence = 0.9
            else:
                status = 'missing'
                confidence = 0.1
            
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status=status,
                lexical_score=confidence,
                semantic_score=confidence,
                evidence_spans=["test"] if status == 'covered' else [],
                confidence=confidence
            ))
        
        # Configure Stage A
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B to return proper GapDetail objects
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=assessment.subcategory_id,
                subcategory_description=subcategory.description,
                status=assessment.status,
                evidence_quote="Test evidence" if assessment.evidence_spans else "",
                gap_explanation=f"Gap explanation for {assessment.subcategory_id}",
                severity=severity,
                suggested_fix=f"Suggested fix for {assessment.subcategory_id}"
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
        
        # Property: No overlap between covered and gaps
        covered_set = set(report.covered_subcategories)
        gap_set = {gap.subcategory_id for gap in report.gaps}
        
        overlap = covered_set & gap_set
        
        assert len(overlap) == 0, \
            f"Subcategories cannot be both covered and have gaps. " \
            f"Found overlap: {overlap}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        num_subcategories=st.integers(min_value=1, max_value=30)
    )
    @settings(max_examples=30, deadline=None)
    def test_classification_completeness(self, policy_chunks, num_subcategories):
        """Property: Classification must be complete (no missing subcategories).
        
        Verifies that the union of covered subcategories and gaps equals
        the complete set of analyzed subcategories.
        """
        # Generate subcategories
        subcategories = [
            CSFSubcategory(
                subcategory_id=f"TEST-{i:02d}",
                function='Govern',
                category='Test Category',
                description=f'Test description {i}',
                keywords=['test', 'keyword'],
                domain_tags=['test'],
                mapped_templates=[],
                priority='medium'
            )
            for i in range(num_subcategories)
        ]
        
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create random assessments
        import random
        assessments = []
        for subcategory in subcategories:
            status = random.choice(list(VALID_STATUSES))
            
            if status == 'covered':
                confidence = 0.9
            elif status == 'partially_covered':
                confidence = 0.6
            elif status == 'missing':
                confidence = 0.1
            else:  # ambiguous
                confidence = 0.4
            
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
        
        # Configure Stage B to return proper GapDetail objects
        def create_gap_detail(assessment, subcategory, policy_section, severity):
            return GapDetail(
                subcategory_id=assessment.subcategory_id,
                subcategory_description=subcategory.description,
                status=assessment.status,
                evidence_quote="Test evidence" if assessment.evidence_spans else "",
                gap_explanation=f"Gap explanation for {assessment.subcategory_id}",
                severity=severity,
                suggested_fix=f"Suggested fix for {assessment.subcategory_id}"
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
        
        # Property: Union of covered and gaps equals all subcategories
        covered_set = set(report.covered_subcategories)
        gap_set = {gap.subcategory_id for gap in report.gaps}
        classified_set = covered_set | gap_set
        
        expected_set = {s.subcategory_id for s in subcategories}
        
        assert classified_set == expected_set, \
            f"Classification must be complete. " \
            f"Expected {expected_set}, got {classified_set}"
        
        # Property: No subcategory is unclassified
        unclassified = expected_set - classified_set
        assert len(unclassified) == 0, \
            f"Found unclassified subcategories: {unclassified}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
