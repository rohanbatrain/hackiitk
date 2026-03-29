"""
Unit tests for Policy Revision Engine.

Tests cover:
- Clause injection for missing subcategories
- Clause strengthening for partial coverage
- Mandatory warning appending
- Revision tracking and metadata
- Integration with LLM runtime

**Validates: Requirements 10.1, 10.2, 10.3, 10.4, 10.5, 10.6, 10.7, 10.8**
"""

import pytest
from unittest.mock import Mock, MagicMock

from revision.policy_revision_engine import PolicyRevisionEngine, MANDATORY_WARNING
from models.domain import (
    ParsedDocument,
    DocumentStructure,
    Section,
    GapDetail,
    CSFSubcategory,
    RevisedPolicy,
    Revision
)
from analysis.llm_runtime import LLMRuntime
from reference_builder.reference_catalog import ReferenceCatalog


@pytest.fixture
def mock_llm():
    """Create a mock LLM runtime."""
    llm = Mock(spec=LLMRuntime)
    llm.generate = MagicMock()
    return llm


@pytest.fixture
def mock_catalog():
    """Create a mock reference catalog."""
    catalog = Mock(spec=ReferenceCatalog)
    catalog.get_subcategory = MagicMock()
    return catalog


@pytest.fixture
def sample_policy():
    """Create a sample parsed policy document."""
    sections = [
        Section(
            title="Risk Management",
            content="The organization shall conduct risk assessments annually.",
            start_pos=0,
            end_pos=100,
            subsections=[]
        ),
        Section(
            title="Access Control",
            content="Access to systems shall be granted based on role.",
            start_pos=100,
            end_pos=200,
            subsections=[]
        )
    ]
    
    full_text = "# Risk Management\n\nThe organization shall conduct risk assessments annually.\n\n# Access Control\n\nAccess to systems shall be granted based on role."
    
    return ParsedDocument(
        text=full_text,
        file_path="test_policy.pdf",
        file_type="pdf",
        page_count=2,
        structure=DocumentStructure(
            headings=[],
            sections=sections
        ),
        metadata={}
    )


@pytest.fixture
def sample_missing_gap():
    """Create a sample gap for missing subcategory."""
    return GapDetail(
        subcategory_id='GV.SC-01',
        subcategory_description='Supply chain risk management processes are identified',
        status='missing',
        evidence_quote='',
        gap_explanation='Policy does not address supply chain risk management',
        severity='high',
        suggested_fix='Add section on supply chain risk management'
    )


@pytest.fixture
def sample_partial_gap():
    """Create a sample gap for partially covered subcategory."""
    return GapDetail(
        subcategory_id='GV.RM-01',
        subcategory_description='Risk management objectives are established',
        status='partially_covered',
        evidence_quote='The organization shall conduct risk assessments annually',
        gap_explanation='Policy mentions risk assessments but not objectives',
        severity='medium',
        suggested_fix='Add explicit risk management objectives'
    )


@pytest.fixture
def sample_subcategory():
    """Create a sample CSF subcategory."""
    return CSFSubcategory(
        subcategory_id='GV.SC-01',
        function='Govern',
        category='Supply Chain Risk Management',
        description='Supply chain risk management processes are identified',
        keywords=['supply', 'chain', 'risk', 'vendor'],
        domain_tags=['isms', 'supply_chain'],
        mapped_templates=['Supply Chain Policy Template'],
        priority='high'
    )


class TestPolicyRevisionEngineInitialization:
    """Tests for policy revision engine initialization."""
    
    def test_initialization_with_defaults(self, mock_llm, mock_catalog):
        """Test initialization with default parameters."""
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        assert engine.llm == mock_llm
        assert engine.catalog == mock_catalog
        assert engine.temperature == 0.1
    
    def test_initialization_with_custom_temperature(self, mock_llm, mock_catalog):
        """Test initialization with custom temperature."""
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog,
            temperature=0.2
        )
        
        assert engine.temperature == 0.2
    
    def test_repr(self, mock_llm, mock_catalog):
        """Test string representation."""
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog,
            temperature=0.1
        )
        
        repr_str = repr(engine)
        assert 'PolicyRevisionEngine' in repr_str
        assert 'temperature=0.1' in repr_str


class TestClauseInjection:
    """Tests for injecting new clauses for missing subcategories."""
    
    def test_inject_clause_for_missing_gap(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_subcategory
    ):
        """Test injection of new clause for missing subcategory."""
        # Configure mocks
        mock_llm.generate.return_value = "The organization shall establish supply chain risk management processes."
        mock_catalog.get_subcategory.return_value = sample_subcategory
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Execute revision
        revised_policy = engine.revise(sample_policy, [sample_missing_gap])
        
        # Verify revision was created
        assert len(revised_policy.revisions) == 1
        revision = revised_policy.revisions[0]
        
        # Verify revision properties
        assert revision.revision_type == 'injection'
        assert revision.gap_addressed == 'GV.SC-01'
        assert revision.original_clause == ''  # No original for injection
        assert len(revision.revised_clause) > 0
    
    def test_inject_clause_calls_llm_with_correct_prompt(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_subcategory
    ):
        """Test that clause injection calls LLM with appropriate prompt."""
        mock_llm.generate.return_value = "New policy clause."
        mock_catalog.get_subcategory.return_value = sample_subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        engine.revise(sample_policy, [sample_missing_gap])
        
        # Verify LLM was called
        assert mock_llm.generate.called
        
        # Extract prompt
        call_args = mock_llm.generate.call_args
        prompt = call_args[1]['prompt']
        
        # Verify prompt contains required elements
        assert sample_missing_gap.subcategory_id in prompt
        assert sample_missing_gap.gap_explanation in prompt
        assert sample_missing_gap.suggested_fix in prompt
        assert sample_subcategory.description in prompt
    
    def test_inject_clause_uses_low_temperature(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_subcategory
    ):
        """Test that clause injection uses low temperature for conservative output."""
        mock_llm.generate.return_value = "New clause."
        mock_catalog.get_subcategory.return_value = sample_subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog,
            temperature=0.1
        )
        
        engine.revise(sample_policy, [sample_missing_gap])
        
        # Verify temperature parameter
        call_args = mock_llm.generate.call_args
        assert call_args[1]['temperature'] == 0.1


class TestClauseStrengthening:
    """Tests for strengthening existing clauses for partial coverage."""
    
    def test_strengthen_clause_for_partial_gap(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_partial_gap
    ):
        """Test strengthening of existing clause for partial coverage."""
        # Configure mocks
        mock_llm.generate.return_value = "The organization shall establish risk management objectives and conduct risk assessments annually."
        
        subcategory = CSFSubcategory(
            subcategory_id='GV.RM-01',
            function='Govern',
            category='Risk Management Strategy',
            description='Risk management objectives are established',
            keywords=['risk', 'objectives'],
            domain_tags=['isms'],
            mapped_templates=[],
            priority='medium'
        )
        mock_catalog.get_subcategory.return_value = subcategory
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Execute revision
        revised_policy = engine.revise(sample_policy, [sample_partial_gap])
        
        # Verify revision was created
        assert len(revised_policy.revisions) == 1
        revision = revised_policy.revisions[0]
        
        # Verify revision properties
        assert revision.revision_type == 'strengthening'
        assert revision.gap_addressed == 'GV.RM-01'
        assert len(revision.original_clause) > 0  # Should have original
        assert len(revision.revised_clause) > 0
    
    def test_strengthen_clause_preserves_original(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_partial_gap
    ):
        """Test that strengthening preserves original clause text."""
        mock_llm.generate.return_value = "Strengthened clause."
        
        subcategory = CSFSubcategory(
            subcategory_id='GV.RM-01',
            function='Govern',
            category='Risk Management Strategy',
            description='Risk management objectives are established',
            keywords=['risk'],
            domain_tags=[],
            mapped_templates=[],
            priority='medium'
        )
        mock_catalog.get_subcategory.return_value = subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        revised_policy = engine.revise(sample_policy, [sample_partial_gap])
        
        # Verify original clause is preserved
        revision = revised_policy.revisions[0]
        assert revision.original_clause == sample_partial_gap.evidence_quote
    
    def test_strengthen_clause_calls_llm_with_original_text(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_partial_gap
    ):
        """Test that strengthening includes original clause in prompt."""
        mock_llm.generate.return_value = "Strengthened clause."
        
        subcategory = CSFSubcategory(
            subcategory_id='GV.RM-01',
            function='Govern',
            category='Risk Management Strategy',
            description='Risk management objectives are established',
            keywords=['risk'],
            domain_tags=[],
            mapped_templates=[],
            priority='medium'
        )
        mock_catalog.get_subcategory.return_value = subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        engine.revise(sample_policy, [sample_partial_gap])
        
        # Extract prompt
        call_args = mock_llm.generate.call_args
        prompt = call_args[1]['prompt']
        
        # Verify original clause is in prompt
        assert sample_partial_gap.evidence_quote in prompt


class TestMandatoryWarning:
    """Tests for mandatory human-review warning."""
    
    def test_append_warning_adds_disclaimer(self, mock_llm, mock_catalog):
        """Test that append_warning adds the mandatory disclaimer."""
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        original_text = "This is a policy document."
        result = engine.append_warning(original_text)
        
        # Verify warning is appended
        assert MANDATORY_WARNING in result
        assert result.startswith(original_text)
    
    def test_revised_policy_includes_warning(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_subcategory
    ):
        """Test that revised policy includes mandatory warning."""
        mock_llm.generate.return_value = "New clause."
        mock_catalog.get_subcategory.return_value = sample_subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        revised_policy = engine.revise(sample_policy, [sample_missing_gap])
        
        # Verify warning is in revised text
        assert MANDATORY_WARNING.strip() in revised_policy.revised_text
        
        # Verify warning field is populated
        assert revised_policy.warning == MANDATORY_WARNING.strip()
    
    def test_warning_included_even_with_no_gaps(
        self,
        mock_llm,
        mock_catalog,
        sample_policy
    ):
        """Test that warning is included even when no gaps exist."""
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Revise with empty gaps list
        revised_policy = engine.revise(sample_policy, [])
        
        # Verify warning is still present
        assert MANDATORY_WARNING.strip() in revised_policy.revised_text
        assert revised_policy.warning == MANDATORY_WARNING.strip()


class TestRevisionTracking:
    """Tests for revision tracking and metadata."""
    
    def test_revisions_list_populated(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_partial_gap
    ):
        """Test that revisions list is populated correctly."""
        mock_llm.generate.return_value = "Policy clause."
        
        def get_subcategory(subcategory_id):
            return CSFSubcategory(
                subcategory_id=subcategory_id,
                function='Govern',
                category='Test',
                description='Test description',
                keywords=['test'],
                domain_tags=[],
                mapped_templates=[],
                priority='medium'
            )
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        revised_policy = engine.revise(
            sample_policy,
            [sample_missing_gap, sample_partial_gap]
        )
        
        # Verify revisions list
        assert len(revised_policy.revisions) == 2
        
        # Verify revision types
        revision_types = {r.revision_type for r in revised_policy.revisions}
        assert 'injection' in revision_types
        assert 'strengthening' in revision_types
    
    def test_metadata_includes_counts(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_partial_gap
    ):
        """Test that metadata includes revision counts."""
        mock_llm.generate.return_value = "Policy clause."
        
        def get_subcategory(subcategory_id):
            return CSFSubcategory(
                subcategory_id=subcategory_id,
                function='Govern',
                category='Test',
                description='Test',
                keywords=['test'],
                domain_tags=[],
                mapped_templates=[],
                priority='medium'
            )
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        revised_policy = engine.revise(
            sample_policy,
            [sample_missing_gap, sample_partial_gap]
        )
        
        # Verify metadata
        assert 'revision_count' in revised_policy.metadata
        assert 'injection_count' in revised_policy.metadata
        assert 'strengthening_count' in revised_policy.metadata
        assert 'temperature' in revised_policy.metadata
        
        # Verify counts
        assert revised_policy.metadata['revision_count'] == 2
        assert revised_policy.metadata['injection_count'] == 1
        assert revised_policy.metadata['strengthening_count'] == 1
        assert revised_policy.metadata['temperature'] == 0.1
    
    def test_original_text_preserved(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_subcategory
    ):
        """Test that original policy text is preserved."""
        mock_llm.generate.return_value = "New clause."
        mock_catalog.get_subcategory.return_value = sample_subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        original_text = sample_policy.text
        revised_policy = engine.revise(sample_policy, [sample_missing_gap])
        
        # Verify original text is preserved
        assert revised_policy.original_text == original_text


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_invalid_policy_raises_error(self, mock_llm, mock_catalog):
        """Test that invalid policy raises ValueError."""
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Create invalid policy (no text)
        invalid_policy = ParsedDocument(
            text="",
            file_path="test.pdf",
            file_type="pdf",
            page_count=1,
            structure=DocumentStructure(headings=[], sections=[]),
            metadata={}
        )
        
        with pytest.raises(ValueError) as exc_info:
            engine.revise(invalid_policy, [])
        
        assert "must have text content" in str(exc_info.value)
    
    def test_llm_generation_failure_continues(
        self,
        mock_llm,
        mock_catalog,
        sample_policy,
        sample_missing_gap,
        sample_subcategory
    ):
        """Test that LLM generation failure doesn't stop entire revision."""
        # First call fails, second succeeds
        mock_llm.generate.side_effect = [
            RuntimeError("Generation failed"),
            "Successful clause"
        ]
        mock_catalog.get_subcategory.return_value = sample_subcategory
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Create two gaps
        gap2 = GapDetail(
            subcategory_id='GV.RM-02',
            subcategory_description='Test',
            status='missing',
            evidence_quote='',
            gap_explanation='Test',
            severity='low',
            suggested_fix='Test'
        )
        
        # Should not raise exception, should continue with other gaps
        revised_policy = engine.revise(
            sample_policy,
            [sample_missing_gap, gap2]
        )
        
        # Should have at least one revision (the successful one)
        assert len(revised_policy.revisions) >= 1


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_gaps_list(self, mock_llm, mock_catalog, sample_policy):
        """Test handling of empty gaps list."""
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        revised_policy = engine.revise(sample_policy, [])
        
        # Should return policy with warning but no revisions
        assert len(revised_policy.revisions) == 0
        assert revised_policy.warning == MANDATORY_WARNING.strip()
        assert revised_policy.metadata['revision_count'] == 0
    
    def test_policy_without_structure(
        self,
        mock_llm,
        mock_catalog,
        sample_missing_gap,
        sample_subcategory
    ):
        """Test handling of policy without structure."""
        mock_llm.generate.return_value = "New clause."
        mock_catalog.get_subcategory.return_value = sample_subcategory
        
        # Create policy without structure
        policy = ParsedDocument(
            text="Simple policy text without structure.",
            file_path="test.pdf",
            file_type="pdf",
            page_count=1,
            structure=DocumentStructure(headings=[], sections=[]),
            metadata={}
        )
        
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Should handle gracefully
        revised_policy = engine.revise(policy, [sample_missing_gap])
        
        assert len(revised_policy.revisions) == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
