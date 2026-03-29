"""
Property Test: Two-Stage Analysis Execution

**Property 21: Two-Stage Analysis Execution**
**Validates: Requirements 9.1, 9.2, 9.3, 9.7**

This property test verifies that the gap analysis engine correctly implements
the two-stage safety architecture:
- Stage A executes for ALL subcategories
- Stage B executes ONLY for Ambiguous and Missing subcategories
- Covered subcategories skip Stage B processing

This ensures deterministic evidence detection is always performed first,
and expensive LLM reasoning is only applied when necessary.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock, patch, call
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


# Strategy for generating coverage assessments
@st.composite
def coverage_assessment_strategy(draw, subcategory_id=None):
    """Generate random coverage assessment."""
    statuses = ['covered', 'partially_covered', 'missing', 'ambiguous']
    status = draw(st.sampled_from(statuses))
    
    # Generate scores consistent with status
    if status == 'covered':
        confidence = draw(st.floats(min_value=0.8, max_value=1.0))
    elif status == 'partially_covered':
        confidence = draw(st.floats(min_value=0.5, max_value=0.8))
    elif status == 'missing':
        confidence = draw(st.floats(min_value=0.0, max_value=0.3))
    else:  # ambiguous
        confidence = draw(st.floats(min_value=0.3, max_value=0.5))
    
    return CoverageAssessment(
        subcategory_id=subcategory_id or f"TEST-{draw(st.integers(min_value=1, max_value=99)):02d}",
        status=status,
        lexical_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        semantic_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        evidence_spans=draw(st.lists(st.text(min_size=20, max_size=200), min_size=0, max_size=5)),
        confidence=confidence
    )


class TestTwoStageExecution:
    """Property tests for two-stage analysis execution."""
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=1, max_size=20)
    )
    @settings(max_examples=50, deadline=None)
    def test_stage_a_executes_for_all_subcategories(self, policy_chunks, subcategories):
        """Property: Stage A must execute for ALL subcategories.
        
        Verifies that the gap analysis engine calls Stage A detector
        exactly once for each CSF subcategory, regardless of domain
        or other factors.
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog to return our subcategories
        mock_catalog.get_all_subcategories.return_value = subcategories
        mock_catalog.get_by_domain.return_value = subcategories
        
        # Configure Stage A to return covered assessments (skip Stage B)
        mock_stage_a.detect_evidence.return_value = CoverageAssessment(
            subcategory_id="TEST-01",
            status='covered',
            lexical_score=0.9,
            semantic_score=0.9,
            evidence_spans=["test evidence"],
            confidence=0.9
        )
        
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
        
        # Property: Stage A must be called exactly once per subcategory
        assert mock_stage_a.detect_evidence.call_count == len(subcategories), \
            f"Stage A should be called {len(subcategories)} times, but was called {mock_stage_a.detect_evidence.call_count} times"
        
        # Verify each subcategory was analyzed
        analyzed_ids = [
            call_args[1]['subcategory'].subcategory_id
            for call_args in mock_stage_a.detect_evidence.call_args_list
        ]
        expected_ids = [s.subcategory_id for s in subcategories]
        
        assert set(analyzed_ids) == set(expected_ids), \
            f"Stage A should analyze all subcategories: expected {expected_ids}, got {analyzed_ids}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=3, max_size=10)
    )
    @settings(max_examples=50, deadline=None)
    def test_stage_b_only_for_ambiguous_and_missing(self, policy_chunks, subcategories):
        """Property: Stage B executes ONLY for Ambiguous and Missing subcategories.
        
        Verifies that:
        1. Covered subcategories skip Stage B
        2. Ambiguous subcategories trigger Stage B
        3. Missing subcategories trigger Stage B
        4. Partially covered subcategories trigger Stage B
        """
        # Ensure we have at least one of each status
        assume(len(subcategories) >= 4)
        
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Create assessments with different statuses
        assessments = []
        covered_count = 0
        needs_stage_b_count = 0
        
        for i, subcategory in enumerate(subcategories):
            if i % 4 == 0:
                status = 'covered'
                confidence = 0.9
                covered_count += 1
            elif i % 4 == 1:
                status = 'ambiguous'
                confidence = 0.4
                needs_stage_b_count += 1
            elif i % 4 == 2:
                status = 'missing'
                confidence = 0.1
                needs_stage_b_count += 1
            else:
                status = 'partially_covered'
                confidence = 0.6
                needs_stage_b_count += 1
            
            assessments.append(CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status=status,
                lexical_score=confidence,
                semantic_score=confidence,
                evidence_spans=["test evidence"] if status != 'missing' else [],
                confidence=confidence
            ))
        
        # Configure Stage A to return our assessments
        mock_stage_a.detect_evidence.side_effect = assessments
        
        # Configure Stage B to return gap details
        mock_stage_b.reason_about_gap.return_value = GapDetail(
            subcategory_id="TEST-01",
            subcategory_description="Test description",
            status='missing',
            evidence_quote="",
            gap_explanation="Test gap",
            severity='high',
            suggested_fix="Test fix"
        )
        
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
        
        # Property: Stage B should be called exactly for non-covered subcategories
        assert mock_stage_b.reason_about_gap.call_count == needs_stage_b_count, \
            f"Stage B should be called {needs_stage_b_count} times (for ambiguous/missing/partial), " \
            f"but was called {mock_stage_b.reason_about_gap.call_count} times"
        
        # Property: Covered subcategories should be in the report
        assert len(report.covered_subcategories) == covered_count, \
            f"Report should have {covered_count} covered subcategories, " \
            f"got {len(report.covered_subcategories)}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        subcategories=st.lists(csf_subcategory_strategy(), min_size=5, max_size=15)
    )
    @settings(max_examples=30, deadline=None)
    def test_covered_subcategories_skip_stage_b(self, policy_chunks, subcategories):
        """Property: Covered subcategories must skip Stage B entirely.
        
        Verifies that when Stage A marks a subcategory as 'covered',
        Stage B is never invoked for that subcategory.
        """
        # Create mock components
        mock_stage_a = Mock(spec=StageADetector)
        mock_stage_b = Mock(spec=StageBReasoner)
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog
        mock_catalog.get_all_subcategories.return_value = subcategories
        
        # Configure Stage A to return all covered assessments
        covered_assessments = [
            CoverageAssessment(
                subcategory_id=s.subcategory_id,
                status='covered',
                lexical_score=0.9,
                semantic_score=0.9,
                evidence_spans=["test evidence"],
                confidence=0.9
            )
            for s in subcategories
        ]
        mock_stage_a.detect_evidence.side_effect = covered_assessments
        
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
        
        # Property: Stage B should NEVER be called when all are covered
        assert mock_stage_b.reason_about_gap.call_count == 0, \
            f"Stage B should not be called for covered subcategories, " \
            f"but was called {mock_stage_b.reason_about_gap.call_count} times"
        
        # Property: All subcategories should be in covered list
        assert len(report.covered_subcategories) == len(subcategories), \
            f"All {len(subcategories)} subcategories should be covered, " \
            f"got {len(report.covered_subcategories)}"
        
        # Property: No gaps should be reported
        assert len(report.gaps) == 0, \
            f"No gaps should be reported for all-covered policy, got {len(report.gaps)}"
    
    @given(
        policy_chunks=st.lists(text_chunk_strategy(), min_size=1, max_size=10),
        num_subcategories=st.integers(min_value=1, max_value=20)
    )
    @settings(max_examples=30, deadline=None)
    def test_stage_execution_order(self, policy_chunks, num_subcategories):
        """Property: Stage A must complete before Stage B begins.
        
        Verifies that the two-stage architecture maintains strict ordering:
        all Stage A assessments complete before any Stage B reasoning starts.
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
        
        # Track execution order
        execution_log = []
        
        # Create mock Stage A that logs execution
        mock_stage_a = Mock(spec=StageADetector)
        def stage_a_side_effect(policy_chunks, subcategory):
            execution_log.append(('stage_a', subcategory.subcategory_id))
            return CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status='missing',  # Force Stage B execution
                lexical_score=0.1,
                semantic_score=0.1,
                evidence_spans=[],
                confidence=0.1
            )
        mock_stage_a.detect_evidence.side_effect = stage_a_side_effect
        
        # Create mock Stage B that logs execution
        mock_stage_b = Mock(spec=StageBReasoner)
        def stage_b_side_effect(assessment, subcategory, policy_section, severity):
            execution_log.append(('stage_b', assessment.subcategory_id))
            return GapDetail(
                subcategory_id=assessment.subcategory_id,
                subcategory_description=subcategory.description,
                status='missing',
                evidence_quote="",
                gap_explanation="Test gap",
                severity=severity,
                suggested_fix="Test fix"
            )
        mock_stage_b.reason_about_gap.side_effect = stage_b_side_effect
        
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        mock_catalog.get_all_subcategories.return_value = subcategories
        
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
        
        # Property: All Stage A executions must come before any Stage B execution
        stage_a_indices = [i for i, (stage, _) in enumerate(execution_log) if stage == 'stage_a']
        stage_b_indices = [i for i, (stage, _) in enumerate(execution_log) if stage == 'stage_b']
        
        if stage_a_indices and stage_b_indices:
            max_stage_a_index = max(stage_a_indices)
            min_stage_b_index = min(stage_b_indices)
            
            assert max_stage_a_index < min_stage_b_index, \
                f"All Stage A executions must complete before Stage B begins. " \
                f"Last Stage A at index {max_stage_a_index}, first Stage B at {min_stage_b_index}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
