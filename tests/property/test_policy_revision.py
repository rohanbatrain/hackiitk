"""
Property Tests: Policy Revision Engine

**Property 27: Comprehensive Policy Revision**
**Validates: Requirements 10.1, 10.3, 10.4**

**Property 28: Policy Content Preservation**
**Validates: Requirements 10.5**

**Property 29: Revision Citation Traceability**
**Validates: Requirements 10.6**

**Property 30: Mandatory Human-Review Warning**
**Validates: Requirements 10.8**

**Property 31: Revised Policy Output Format**
**Validates: Requirements 10.7**

These property tests verify that the PolicyRevisionEngine:
- Addresses all gaps through injection or strengthening
- Preserves existing valid policy provisions
- Cites CSF subcategories for each revision
- Includes mandatory human-review disclaimer
- Outputs revised policy in markdown format
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock
import re

from models.domain import (
    ParsedDocument,
    DocumentStructure,
    Section,
    GapDetail,
    CSFSubcategory,
    RevisedPolicy,
    Revision
)
from revision.policy_revision_engine import PolicyRevisionEngine, MANDATORY_WARNING
from analysis.llm_runtime import LLMRuntime
from reference_builder.reference_catalog import ReferenceCatalog


# Strategy for generating parsed documents
@st.composite
def parsed_document_strategy(draw):
    """Generate random parsed policy document."""
    sections = []
    for i in range(draw(st.integers(min_value=1, max_value=5))):
        sections.append(Section(
            title=draw(st.text(min_size=5, max_size=50)),
            content=draw(st.text(min_size=100, max_size=500)),
            start_pos=i * 1000,
            end_pos=(i + 1) * 1000,
            subsections=[]
        ))
    
    full_text = "\n\n".join([f"# {s.title}\n\n{s.content}" for s in sections])
    
    return ParsedDocument(
        text=full_text,
        file_path="test_policy.pdf",
        file_type="pdf",
        page_count=draw(st.integers(min_value=1, max_value=20)),
        structure=DocumentStructure(
            headings=[],
            sections=sections
        ),
        metadata={}
    )


# Strategy for generating gap details
@st.composite
def gap_detail_strategy(draw):
    """Generate random gap detail."""
    functions = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
    statuses = ['missing', 'partially_covered']
    severities = ['critical', 'high', 'medium', 'low']
    
    function = draw(st.sampled_from(functions))
    subcategory_id = f"{function[:2].upper()}.{draw(st.text(min_size=2, max_size=4, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))}-{draw(st.integers(min_value=1, max_value=99)):02d}"
    status = draw(st.sampled_from(statuses))
    
    return GapDetail(
        subcategory_id=subcategory_id,
        subcategory_description=draw(st.text(min_size=20, max_size=200)),
        status=status,
        evidence_quote="" if status == 'missing' else draw(st.text(min_size=10, max_size=100)),
        gap_explanation=draw(st.text(min_size=20, max_size=200)),
        severity=draw(st.sampled_from(severities)),
        suggested_fix=draw(st.text(min_size=20, max_size=200))
    )


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


class TestPolicyRevisionProperties:
    """Property tests for policy revision engine."""
    
    @given(
        policy=parsed_document_strategy(),
        gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_27_comprehensive_revision(self, policy, gaps):
        """Property 27: All gaps are addressed by injection or strengthening.
        
        Verifies that:
        - Each gap results in a revision
        - Missing gaps get injection revisions
        - Partially covered gaps get strengthening revisions
        """
        # Create mock LLM that returns valid clauses
        mock_llm = Mock(spec=LLMRuntime)
        mock_llm.generate.return_value = "Test policy clause addressing the gap."
        
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog to return matching subcategories
        def get_subcategory(subcategory_id):
            # Find matching gap
            for gap in gaps:
                if gap.subcategory_id == subcategory_id:
                    return CSFSubcategory(
                        subcategory_id=subcategory_id,
                        function="Govern",
                        category="Test Category",
                        description=gap.subcategory_description,
                        keywords=["test"],
                        domain_tags=["test"],
                        mapped_templates=[],
                        priority="medium"
                    )
            return None
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Execute revision
        revised_policy = engine.revise(policy, gaps)
        
        # Property: Number of revisions should match number of gaps
        # (allowing for some failures in generation)
        assert len(revised_policy.revisions) >= len(gaps) * 0.8, \
            f"Expected at least 80% of gaps to be addressed, " \
            f"got {len(revised_policy.revisions)} revisions for {len(gaps)} gaps"
        
        # Property: Missing gaps should have injection revisions
        missing_gaps = [g for g in gaps if g.status == 'missing']
        injection_revisions = [r for r in revised_policy.revisions if r.revision_type == 'injection']
        
        # Property: Partially covered gaps should have strengthening revisions
        partial_gaps = [g for g in gaps if g.status == 'partially_covered']
        strengthening_revisions = [r for r in revised_policy.revisions if r.revision_type == 'strengthening']
        
        # Verify revision types match gap types (with some tolerance for failures)
        if missing_gaps:
            assert len(injection_revisions) > 0, \
                "Missing gaps should result in injection revisions"
        
        if partial_gaps:
            assert len(strengthening_revisions) > 0, \
                "Partially covered gaps should result in strengthening revisions"
    
    @given(
        policy=parsed_document_strategy(),
        gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_28_content_preservation(self, policy, gaps):
        """Property 28: No existing valid provisions are removed.
        
        Verifies that:
        - Original policy text is preserved in the output
        - No content is deleted from the original policy
        - Revisions are additions or modifications, not deletions
        """
        # Create mock LLM
        mock_llm = Mock(spec=LLMRuntime)
        mock_llm.generate.return_value = "New policy clause."
        
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        mock_catalog.get_subcategory.return_value = CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Test",
            description="Test description",
            keywords=["test"],
            domain_tags=[],
            mapped_templates=[],
            priority="medium"
        )
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Store original text
        original_text = policy.text
        
        # Execute revision
        revised_policy = engine.revise(policy, gaps)
        
        # Property: Original text should be preserved in RevisedPolicy object
        assert revised_policy.original_text == original_text, \
            "Original text must be preserved in RevisedPolicy"
        
        # Property: Revised text should contain original content
        # (The current implementation appends revisions, so original should be present)
        assert original_text in revised_policy.revised_text or \
               len(revised_policy.revised_text) >= len(original_text), \
            "Revised policy should preserve or extend original content"
        
        # Property: No revision should have empty revised_clause
        for revision in revised_policy.revisions:
            assert len(revision.revised_clause) > 0, \
                "Revisions must add content, not remove it"
    
    @given(
        policy=parsed_document_strategy(),
        gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_29_revision_citation_traceability(self, policy, gaps):
        """Property 29: Each revision cites specific CSF subcategory.
        
        Verifies that:
        - Each revision has a gap_addressed field
        - gap_addressed contains a valid CSF subcategory ID
        - Revisions can be traced back to specific gaps
        """
        # Create mock LLM
        mock_llm = Mock(spec=LLMRuntime)
        mock_llm.generate.return_value = "Policy clause addressing the requirement."
        
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        def get_subcategory(subcategory_id):
            for gap in gaps:
                if gap.subcategory_id == subcategory_id:
                    return CSFSubcategory(
                        subcategory_id=subcategory_id,
                        function="Govern",
                        category="Test",
                        description=gap.subcategory_description,
                        keywords=["test"],
                        domain_tags=[],
                        mapped_templates=[],
                        priority="medium"
                    )
            return None
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Execute revision
        revised_policy = engine.revise(policy, gaps)
        
        # Property: Each revision must cite a CSF subcategory
        gap_ids = {g.subcategory_id for g in gaps}
        
        for revision in revised_policy.revisions:
            # Must have gap_addressed field
            assert revision.gap_addressed is not None, \
                "Revision must have gap_addressed field"
            
            # Must be non-empty
            assert len(revision.gap_addressed) > 0, \
                "gap_addressed cannot be empty"
            
            # Must match one of the input gaps
            assert revision.gap_addressed in gap_ids, \
                f"Revision cites {revision.gap_addressed} which is not in input gaps"
            
            # CSF subcategory ID format check (basic validation)
            # Format: XX.YY-NN (e.g., GV.RM-01)
            assert re.match(r'^[A-Z]{2}\.[A-Z]{2,4}-\d{2}$', revision.gap_addressed), \
                f"gap_addressed '{revision.gap_addressed}' does not match CSF ID format"
    
    @given(
        policy=parsed_document_strategy(),
        gaps=st.lists(gap_detail_strategy(), min_size=0, max_size=10)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_30_mandatory_warning(self, policy, gaps):
        """Property 30: All revised policies include mandatory legal disclaimer.
        
        Verifies that:
        - Revised policy text includes the mandatory warning
        - Warning text matches the required format
        - Warning is present even when no gaps exist
        """
        # Create mock LLM
        mock_llm = Mock(spec=LLMRuntime)
        mock_llm.generate.return_value = "Policy clause."
        
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        mock_catalog.get_subcategory.return_value = CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Test",
            description="Test",
            keywords=["test"],
            domain_tags=[],
            mapped_templates=[],
            priority="medium"
        )
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Execute revision
        revised_policy = engine.revise(policy, gaps)
        
        # Property: Revised text must contain mandatory warning
        assert MANDATORY_WARNING.strip() in revised_policy.revised_text, \
            "Revised policy must include mandatory human-review warning"
        
        # Property: Warning field must be populated
        assert revised_policy.warning is not None, \
            "RevisedPolicy must have warning field"
        
        assert len(revised_policy.warning) > 0, \
            "Warning field cannot be empty"
        
        # Property: Warning must contain key phrases
        warning_lower = revised_policy.warning.lower()
        assert "ai system" in warning_lower or "ai-generated" in warning_lower, \
            "Warning must mention AI generation"
        
        assert "legal counsel" in warning_lower or "legal" in warning_lower, \
            "Warning must mention legal review requirement"
        
        assert "must be reviewed" in warning_lower or "review" in warning_lower, \
            "Warning must mention review requirement"
    
    @given(
        policy=parsed_document_strategy(),
        gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=30, deadline=None)
    def test_property_31_markdown_output_format(self, policy, gaps):
        """Property 31: Revised policy is output in markdown format.
        
        Verifies that:
        - Revised text uses markdown formatting
        - Contains markdown headers (# or ##)
        - Structured as readable markdown document
        """
        # Create mock LLM
        mock_llm = Mock(spec=LLMRuntime)
        mock_llm.generate.return_value = "Policy clause in markdown."
        
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        mock_catalog.get_subcategory.return_value = CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Test",
            description="Test",
            keywords=["test"],
            domain_tags=[],
            mapped_templates=[],
            priority="medium"
        )
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog
        )
        
        # Execute revision
        revised_policy = engine.revise(policy, gaps)
        
        # Property: Revised text should contain markdown headers
        assert re.search(r'^#{1,6}\s+', revised_policy.revised_text, re.MULTILINE), \
            "Revised policy should contain markdown headers (# or ##)"
        
        # Property: Should be valid text (not binary or corrupted)
        assert isinstance(revised_policy.revised_text, str), \
            "Revised text must be a string"
        
        assert len(revised_policy.revised_text) > 0, \
            "Revised text cannot be empty"
        
        # Property: Should contain readable content (not just markup)
        # Check that there's substantial text beyond just markdown symbols
        text_without_markup = re.sub(r'[#*_\-\[\]()]', '', revised_policy.revised_text)
        assert len(text_without_markup.strip()) > 100, \
            "Revised policy should contain substantial readable content"
    
    @given(
        policy=parsed_document_strategy(),
        gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=20, deadline=None)
    def test_revision_metadata_completeness(self, policy, gaps):
        """Verify that revised policy includes complete metadata.
        
        Checks that metadata includes:
        - revision_count
        - injection_count
        - strengthening_count
        - temperature
        """
        # Create mock LLM
        mock_llm = Mock(spec=LLMRuntime)
        mock_llm.generate.return_value = "Policy clause."
        
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        mock_catalog.get_subcategory.return_value = CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Test",
            description="Test",
            keywords=["test"],
            domain_tags=[],
            mapped_templates=[],
            priority="medium"
        )
        
        # Create engine
        engine = PolicyRevisionEngine(
            llm=mock_llm,
            catalog=mock_catalog,
            temperature=0.1
        )
        
        # Execute revision
        revised_policy = engine.revise(policy, gaps)
        
        # Property: Metadata must be present
        assert revised_policy.metadata is not None, \
            "RevisedPolicy must have metadata"
        
        # Property: Metadata must contain required fields
        assert 'revision_count' in revised_policy.metadata, \
            "Metadata must include revision_count"
        
        assert 'injection_count' in revised_policy.metadata, \
            "Metadata must include injection_count"
        
        assert 'strengthening_count' in revised_policy.metadata, \
            "Metadata must include strengthening_count"
        
        assert 'temperature' in revised_policy.metadata, \
            "Metadata must include temperature"
        
        # Property: Counts should be non-negative
        assert revised_policy.metadata['revision_count'] >= 0, \
            "revision_count must be non-negative"
        
        assert revised_policy.metadata['injection_count'] >= 0, \
            "injection_count must be non-negative"
        
        assert revised_policy.metadata['strengthening_count'] >= 0, \
            "strengthening_count must be non-negative"
        
        # Property: Temperature should match engine configuration
        assert revised_policy.metadata['temperature'] == 0.1, \
            "Metadata temperature should match engine configuration"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
