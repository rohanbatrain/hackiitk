"""
Property test for Stage B input constraint.

**Property 23: Stage B Input Constraint**
**Validates: Requirements 9.5**

This test verifies that Stage B only receives matched policy sections,
not the entire document. This constraint is critical for:
1. Minimizing hallucination risks by limiting LLM context
2. Ensuring deterministic, reproducible results
3. Reducing computational overhead

The test uses Hypothesis to generate various policy documents and verifies
that the Stage B reasoner only processes relevant sections.
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock, MagicMock, patch, call
import re

from analysis.stage_b_reasoner import StageBReasoner
from models.domain import CoverageAssessment, CSFSubcategory, GapDetail


# Strategy for generating CSF subcategories
@st.composite
def csf_subcategory_strategy(draw):
    """Generate random CSF subcategory."""
    functions = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
    categories = ['Risk Management', 'Asset Management', 'Data Security', 'Access Control']
    
    function = draw(st.sampled_from(functions))
    category = draw(st.sampled_from(categories))
    
    # Generate subcategory ID (e.g., GV.RM-01)
    function_code = function[:2].upper()
    category_code = ''.join(word[0].upper() for word in category.split()[:2])
    number = draw(st.integers(min_value=1, max_value=20))
    subcategory_id = f"{function_code}.{category_code}-{number:02d}"
    
    return CSFSubcategory(
        subcategory_id=subcategory_id,
        function=function,
        category=category,
        description=draw(st.text(min_size=50, max_size=200)),
        keywords=draw(st.lists(st.text(min_size=3, max_size=15), min_size=1, max_size=10)),
        domain_tags=draw(st.lists(st.sampled_from(['isms', 'risk', 'data', 'access']), min_size=1, max_size=3)),
        mapped_templates=draw(st.lists(st.text(min_size=10, max_size=30), min_size=0, max_size=3)),
        priority=draw(st.sampled_from(['critical', 'high', 'medium', 'low']))
    )


# Strategy for generating coverage assessments
@st.composite
def coverage_assessment_strategy(draw, subcategory_id):
    """Generate random coverage assessment."""
    status = draw(st.sampled_from(['ambiguous', 'missing', 'partially_covered']))
    
    return CoverageAssessment(
        subcategory_id=subcategory_id,
        status=status,
        lexical_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        semantic_score=draw(st.floats(min_value=0.0, max_value=1.0)),
        evidence_spans=draw(st.lists(st.text(min_size=20, max_size=100), min_size=0, max_size=3)),
        confidence=draw(st.floats(min_value=0.0, max_value=1.0))
    )


# Strategy for generating policy documents
@st.composite
def policy_document_strategy(draw):
    """Generate random policy document with multiple sections."""
    num_sections = draw(st.integers(min_value=3, max_value=10))
    
    sections = []
    for i in range(num_sections):
        section_title = draw(st.text(min_size=10, max_size=50))
        section_content = draw(st.text(min_size=100, max_size=500))
        sections.append(f"## {section_title}\n\n{section_content}\n\n")
    
    full_document = "".join(sections)
    
    # Return both full document and a single section
    section_index = draw(st.integers(min_value=0, max_value=num_sections-1))
    single_section = sections[section_index]
    
    return full_document, single_section


@pytest.mark.property
class TestStageBInputConstraint:
    """Property tests for Stage B input constraint (Property 23)."""
    
    @given(
        subcategory=csf_subcategory_strategy(),
        policy_data=policy_document_strategy(),
        severity=st.sampled_from(['critical', 'high', 'medium', 'low'])
    )
    @settings(max_examples=50, deadline=None)
    def test_stage_b_receives_only_matched_section(
        self,
        subcategory,
        policy_data,
        severity
    ):
        """
        Property 23: Stage B only receives matched policy section, not entire document.
        
        This test verifies that:
        1. Stage B reasoner receives only the relevant policy section
        2. The entire document is NOT passed to the LLM
        3. The policy section is a proper substring of the full document
        """
        full_document, matched_section = policy_data
        
        # Assume the matched section is actually in the document
        assume(matched_section in full_document)
        assume(len(matched_section) < len(full_document))
        
        # Create coverage assessment
        assessment = CoverageAssessment(
            subcategory_id=subcategory.subcategory_id,
            status='ambiguous',
            lexical_score=0.4,
            semantic_score=0.5,
            evidence_spans=['some evidence'],
            confidence=0.45
        )
        
        # Mock LLM runtime to capture what it receives
        mock_llm = Mock()
        mock_llm.generate_structured = MagicMock(return_value={
            'subcategory_id': subcategory.subcategory_id,
            'description': subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test evidence',
            'gap_explanation': 'test explanation',
            'severity': severity,
            'suggested_fix': 'test fix'
        })
        
        # Create Stage B reasoner
        reasoner = StageBReasoner(llm=mock_llm)
        
        # Call reason_about_gap with matched section (NOT full document)
        reasoner.reason_about_gap(
            assessment=assessment,
            subcategory=subcategory,
            policy_section=matched_section,
            severity=severity
        )
        
        # Verify LLM was called
        assert mock_llm.generate_structured.called
        
        # Extract the prompt that was passed to the LLM
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt'] if 'prompt' in call_args[1] else call_args[0][0]
        
        # CRITICAL ASSERTION: Verify the prompt contains the matched section
        assert matched_section[:100] in prompt, \
            "Stage B prompt must contain the matched policy section"
        
        # CRITICAL ASSERTION: Verify the prompt does NOT contain the full document
        # We check that sections NOT in matched_section are NOT in the prompt
        other_sections = full_document.replace(matched_section, '')
        if len(other_sections) > 100:
            # Sample some text from other sections
            sample_from_other = other_sections[:100]
            assert sample_from_other not in prompt, \
                "Stage B prompt must NOT contain text from other policy sections"
    
    @given(
        subcategory=csf_subcategory_strategy(),
        section_length=st.integers(min_value=100, max_value=3000)
    )
    @settings(max_examples=30, deadline=None)
    def test_stage_b_prompt_length_constraint(
        self,
        subcategory,
        section_length
    ):
        """
        Verify that Stage B prompts are constrained to reasonable lengths.
        
        This ensures that:
        1. Only relevant policy sections are included
        2. Context doesn't exceed LLM limits
        3. Memory usage stays within bounds
        """
        # Generate a policy section of specified length
        policy_section = "a" * section_length
        
        assessment = CoverageAssessment(
            subcategory_id=subcategory.subcategory_id,
            status='missing',
            lexical_score=0.1,
            semantic_score=0.2,
            evidence_spans=[],
            confidence=0.15
        )
        
        # Mock LLM runtime
        mock_llm = Mock()
        mock_llm.generate_structured = MagicMock(return_value={
            'subcategory_id': subcategory.subcategory_id,
            'description': subcategory.description,
            'status': 'missing',
            'evidence_quote': '',
            'gap_explanation': 'test explanation',
            'severity': 'high',
            'suggested_fix': 'test fix'
        })
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        # Call with the policy section
        reasoner.reason_about_gap(
            assessment=assessment,
            subcategory=subcategory,
            policy_section=policy_section,
            severity='high'
        )
        
        # Extract prompt
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt'] if 'prompt' in call_args[1] else call_args[0][0]
        
        # Verify prompt length is reasonable (not just the raw section)
        # The prompt should include instructions, schema, etc., but truncate long sections
        # Maximum reasonable prompt length: ~5000 characters
        assert len(prompt) < 10000, \
            "Stage B prompt should be constrained to reasonable length"
        
        # If section is very long, verify it was truncated in the prompt
        if section_length > 2500:
            # The prompt should truncate the section to ~2000 chars
            assert prompt.count('a' * 100) < section_length / 100, \
                "Long policy sections should be truncated in Stage B prompts"
    
    @given(
        subcategory=csf_subcategory_strategy()
    )
    @settings(max_examples=20, deadline=None)
    def test_stage_b_never_receives_full_document_marker(
        self,
        subcategory
    ):
        """
        Verify that Stage B never receives markers indicating full document.
        
        This test checks that the input to Stage B doesn't contain
        markers or metadata suggesting it's the complete document.
        """
        # Create a "full document" with clear markers
        full_document = """
        # Complete Policy Document
        
        ## Section 1: Introduction
        This is the introduction section.
        
        ## Section 2: Scope
        This is the scope section.
        
        ## Section 3: Requirements
        This is the requirements section.
        
        ## Section 4: Conclusion
        This is the conclusion section.
        """
        
        # Extract just one section
        matched_section = """
        ## Section 3: Requirements
        This is the requirements section.
        """
        
        assessment = CoverageAssessment(
            subcategory_id=subcategory.subcategory_id,
            status='ambiguous',
            lexical_score=0.4,
            semantic_score=0.5,
            evidence_spans=['requirements section'],
            confidence=0.45
        )
        
        # Mock LLM runtime
        mock_llm = Mock()
        mock_llm.generate_structured = MagicMock(return_value={
            'subcategory_id': subcategory.subcategory_id,
            'description': subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'requirements section',
            'gap_explanation': 'test explanation',
            'severity': 'medium',
            'suggested_fix': 'test fix'
        })
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        # Call with matched section only
        reasoner.reason_about_gap(
            assessment=assessment,
            subcategory=subcategory,
            policy_section=matched_section,
            severity='medium'
        )
        
        # Extract prompt
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt'] if 'prompt' in call_args[1] else call_args[0][0]
        
        # Verify prompt does NOT contain markers from other sections
        assert "Section 1: Introduction" not in prompt
        assert "Section 2: Scope" not in prompt
        assert "Section 4: Conclusion" not in prompt
        assert "Complete Policy Document" not in prompt
        
        # Verify prompt DOES contain the matched section
        assert "Section 3: Requirements" in prompt
        assert "requirements section" in prompt


@pytest.mark.property
def test_stage_b_input_constraint_integration():
    """
    Integration test verifying Stage B input constraint in realistic scenario.
    
    This test uses a realistic policy document and verifies that Stage B
    only processes the relevant section for a specific CSF subcategory.
    """
    # Realistic policy document with multiple sections
    full_policy = """
    # Information Security Management System Policy
    
    ## 1. Purpose
    This policy establishes the framework for managing information security
    across the organization.
    
    ## 2. Scope
    This policy applies to all employees, contractors, and third parties
    who access organizational information systems.
    
    ## 3. Risk Management
    The organization shall establish and maintain a risk management process
    to identify, assess, and mitigate information security risks. Risk
    assessments shall be conducted annually and whenever significant changes
    occur to the information systems or business environment.
    
    ## 4. Access Control
    Access to information systems shall be granted based on the principle
    of least privilege. User access rights shall be reviewed quarterly.
    
    ## 5. Incident Response
    The organization shall maintain an incident response plan to detect,
    respond to, and recover from security incidents.
    """
    
    # Extract just the Risk Management section
    risk_section = """
    ## 3. Risk Management
    The organization shall establish and maintain a risk management process
    to identify, assess, and mitigate information security risks. Risk
    assessments shall be conducted annually and whenever significant changes
    occur to the information systems or business environment.
    """
    
    # Create a Risk Management subcategory
    subcategory = CSFSubcategory(
        subcategory_id='GV.RM-01',
        function='Govern',
        category='Risk Management Strategy',
        description='Risk management objectives are established and agreed to by organizational stakeholders',
        keywords=['risk', 'management', 'objectives', 'stakeholders'],
        domain_tags=['isms', 'risk_management'],
        mapped_templates=['Risk Management Policy Template'],
        priority='critical'
    )
    
    assessment = CoverageAssessment(
        subcategory_id='GV.RM-01',
        status='partially_covered',
        lexical_score=0.6,
        semantic_score=0.7,
        evidence_spans=[risk_section.strip()],
        confidence=0.65
    )
    
    # Mock LLM runtime
    mock_llm = Mock()
    mock_llm.generate_structured = MagicMock(return_value={
        'subcategory_id': 'GV.RM-01',
        'description': subcategory.description,
        'status': 'partially_covered',
        'evidence_quote': 'risk management process to identify, assess, and mitigate',
        'gap_explanation': 'Policy mentions risk management but does not explicitly establish objectives agreed to by stakeholders',
        'severity': 'high',
        'suggested_fix': 'Add: "Risk management objectives shall be documented and approved by executive leadership and key stakeholders"'
    })
    
    reasoner = StageBReasoner(llm=mock_llm)
    
    # Call with ONLY the risk section (not full policy)
    gap_detail = reasoner.reason_about_gap(
        assessment=assessment,
        subcategory=subcategory,
        policy_section=risk_section,
        severity='high'
    )
    
    # Verify LLM was called
    assert mock_llm.generate_structured.called
    
    # Extract prompt
    call_args = mock_llm.generate_structured.call_args
    prompt = call_args[1]['prompt'] if 'prompt' in call_args[1] else call_args[0][0]
    
    # CRITICAL ASSERTIONS: Verify input constraint
    assert "Risk Management" in prompt, "Prompt must contain the relevant section"
    assert "risk management process" in prompt, "Prompt must contain section content"
    
    # Verify other sections are NOT in the prompt
    assert "Purpose" not in prompt or "## 1. Purpose" not in prompt
    assert "Access Control" not in prompt or "## 4. Access Control" not in prompt
    assert "Incident Response" not in prompt or "## 5. Incident Response" not in prompt
    
    # Verify the gap detail was created correctly
    assert gap_detail.subcategory_id == 'GV.RM-01'
    assert gap_detail.status == 'partially_covered'
    assert gap_detail.severity == 'high'
