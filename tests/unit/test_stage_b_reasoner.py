"""
Unit tests for Stage B Constrained Reasoner.

Tests cover:
- Prompt construction with required context
- JSON schema validation
- LLM response parsing
- Error handling for invalid JSON
- Integration with LLM runtime

**Validates: Requirements 9.5, 9.6**
"""

import pytest
import json
from unittest.mock import Mock, MagicMock, patch
from jsonschema import ValidationError

from analysis.stage_b_reasoner import StageBReasoner
from models.domain import CoverageAssessment, CSFSubcategory, GapDetail
from models.schemas import GAP_DETAIL_SCHEMA


@pytest.fixture
def mock_llm():
    """Create a mock LLM runtime."""
    llm = Mock()
    llm.generate_structured = MagicMock()
    return llm


@pytest.fixture
def sample_subcategory():
    """Create a sample CSF subcategory."""
    return CSFSubcategory(
        subcategory_id='GV.RM-01',
        function='Govern',
        category='Risk Management Strategy',
        description='Risk management objectives are established and agreed to by organizational stakeholders',
        keywords=['risk', 'management', 'objectives', 'stakeholders'],
        domain_tags=['isms', 'risk_management'],
        mapped_templates=['Risk Management Policy Template'],
        priority='critical'
    )


@pytest.fixture
def sample_assessment():
    """Create a sample coverage assessment."""
    return CoverageAssessment(
        subcategory_id='GV.RM-01',
        status='ambiguous',
        lexical_score=0.4,
        semantic_score=0.5,
        evidence_spans=['The organization manages risks through periodic assessments'],
        confidence=0.45
    )


@pytest.fixture
def sample_policy_section():
    """Create a sample policy section."""
    return """
    ## Risk Management
    
    The organization shall establish and maintain a risk management process
    to identify, assess, and mitigate information security risks. Risk
    assessments shall be conducted annually and whenever significant changes
    occur to the information systems or business environment.
    
    Risk management activities shall be documented and reported to senior
    management on a quarterly basis.
    """


class TestStageBReasonerInitialization:
    """Tests for Stage B reasoner initialization."""
    
    def test_initialization_with_defaults(self, mock_llm):
        """Test initialization with default parameters."""
        reasoner = StageBReasoner(llm=mock_llm)
        
        assert reasoner.llm == mock_llm
        assert reasoner.temperature == 0.1
        assert reasoner.max_tokens == 512
        assert reasoner.prompt_version == "1.0.0"
    
    def test_initialization_with_custom_parameters(self, mock_llm):
        """Test initialization with custom parameters."""
        reasoner = StageBReasoner(
            llm=mock_llm,
            temperature=0.2,
            max_tokens=1024
        )
        
        assert reasoner.temperature == 0.2
        assert reasoner.max_tokens == 1024
    
    def test_repr(self, mock_llm):
        """Test string representation."""
        reasoner = StageBReasoner(llm=mock_llm)
        repr_str = repr(reasoner)
        
        assert 'StageBReasoner' in repr_str
        assert 'temperature=0.1' in repr_str
        assert 'max_tokens=512' in repr_str


class TestPromptConstruction:
    """Tests for prompt construction with required context."""
    
    def test_prompt_includes_policy_section(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that prompt includes the policy section text."""
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'risk management process',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test fix'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        # Extract the prompt
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt']
        
        # Verify policy section is in prompt
        assert 'Risk Management' in prompt
        assert 'risk management process' in prompt
    
    def test_prompt_includes_csf_subcategory_details(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that prompt includes CSF subcategory details."""
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt']
        
        # Verify CSF details are in prompt
        assert sample_subcategory.subcategory_id in prompt
        assert sample_subcategory.function in prompt
        assert sample_subcategory.category in prompt
        assert sample_subcategory.description in prompt
    
    def test_prompt_includes_evidence_spans(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that prompt includes evidence spans from Stage A."""
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt']
        
        # Verify evidence spans are in prompt
        for evidence in sample_assessment.evidence_spans:
            assert evidence in prompt
    
    def test_prompt_includes_stage_a_scores(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that prompt includes Stage A assessment scores."""
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt']
        
        # Verify Stage A scores are in prompt
        assert str(sample_assessment.confidence) in prompt or f"{sample_assessment.confidence:.3f}" in prompt
        assert str(sample_assessment.lexical_score) in prompt or f"{sample_assessment.lexical_score:.3f}" in prompt
        assert str(sample_assessment.semantic_score) in prompt or f"{sample_assessment.semantic_score:.3f}" in prompt
    
    def test_prompt_includes_json_schema(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that prompt includes JSON schema for structured output."""
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt']
        
        # Verify JSON structure is described in prompt
        assert 'JSON' in prompt
        assert 'subcategory_id' in prompt
        assert 'evidence_quote' in prompt
        assert 'gap_explanation' in prompt
        assert 'suggested_fix' in prompt
    
    def test_prompt_guidance_for_missing_status(
        self,
        mock_llm,
        sample_subcategory,
        sample_policy_section
    ):
        """Test that prompt provides correct guidance for missing status."""
        assessment = CoverageAssessment(
            subcategory_id='GV.RM-01',
            status='missing',
            lexical_score=0.1,
            semantic_score=0.2,
            evidence_spans=[],
            confidence=0.15
        )
        
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'missing',
            'evidence_quote': '',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        reasoner.reason_about_gap(
            assessment=assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        call_args = mock_llm.generate_structured.call_args
        prompt = call_args[1]['prompt']
        
        # Verify guidance for missing status
        assert 'missing' in prompt.lower()
        assert 'NO coverage' in prompt or 'no coverage' in prompt


class TestLLMResponseParsing:
    """Tests for LLM response parsing."""
    
    def test_successful_response_parsing(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test successful parsing of valid LLM response."""
        expected_response = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'risk management process to identify, assess, and mitigate',
            'gap_explanation': 'Policy does not explicitly mention stakeholder agreement',
            'severity': 'high',
            'suggested_fix': 'Add: Risk management objectives shall be approved by stakeholders'
        }
        
        mock_llm.generate_structured.return_value = expected_response
        
        reasoner = StageBReasoner(llm=mock_llm)
        gap_detail = reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        # Verify GapDetail was created correctly
        assert isinstance(gap_detail, GapDetail)
        assert gap_detail.subcategory_id == 'GV.RM-01'
        assert gap_detail.status == 'partially_covered'
        assert gap_detail.severity == 'high'
        assert gap_detail.evidence_quote == expected_response['evidence_quote']
        assert gap_detail.gap_explanation == expected_response['gap_explanation']
        assert gap_detail.suggested_fix == expected_response['suggested_fix']
    
    def test_response_with_missing_status(
        self,
        mock_llm,
        sample_subcategory,
        sample_policy_section
    ):
        """Test parsing response with missing status."""
        assessment = CoverageAssessment(
            subcategory_id='GV.RM-01',
            status='missing',
            lexical_score=0.1,
            semantic_score=0.2,
            evidence_spans=[],
            confidence=0.15
        )
        
        expected_response = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'missing',
            'evidence_quote': '',
            'gap_explanation': 'No risk management objectives mentioned in policy',
            'severity': 'critical',
            'suggested_fix': 'Add comprehensive risk management objectives section'
        }
        
        mock_llm.generate_structured.return_value = expected_response
        
        reasoner = StageBReasoner(llm=mock_llm)
        gap_detail = reasoner.reason_about_gap(
            assessment=assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='critical'
        )
        
        assert gap_detail.status == 'missing'
        assert gap_detail.evidence_quote == ''
        assert gap_detail.severity == 'critical'


class TestJSONSchemaValidation:
    """Tests for JSON schema validation."""
    
    def test_valid_response_passes_validation(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that valid response passes schema validation."""
        valid_response = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test evidence',
            'gap_explanation': 'test explanation',
            'severity': 'high',
            'suggested_fix': 'test fix'
        }
        
        mock_llm.generate_structured.return_value = valid_response
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        # Should not raise any exceptions
        gap_detail = reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        assert gap_detail is not None
    
    def test_validate_response_method(self, mock_llm):
        """Test the validate_response method."""
        reasoner = StageBReasoner(llm=mock_llm)
        
        valid_response = {
            'subcategory_id': 'GV.RM-01',
            'description': 'Test description',
            'status': 'missing',
            'evidence_quote': '',
            'gap_explanation': 'Test explanation',
            'severity': 'high',
            'suggested_fix': 'Test fix'
        }
        
        assert reasoner.validate_response(valid_response) is True
    
    def test_validate_response_with_invalid_data(self, mock_llm):
        """Test validation with invalid response data."""
        reasoner = StageBReasoner(llm=mock_llm)
        
        invalid_response = {
            'subcategory_id': 'GV.RM-01',
            # Missing required fields
        }
        
        assert reasoner.validate_response(invalid_response) is False


class TestErrorHandling:
    """Tests for error handling."""
    
    def test_llm_generation_failure(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test handling of LLM generation failure."""
        mock_llm.generate_structured.side_effect = RuntimeError("LLM generation failed")
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        with pytest.raises(RuntimeError) as exc_info:
            reasoner.reason_about_gap(
                assessment=sample_assessment,
                subcategory=sample_subcategory,
                policy_section=sample_policy_section,
                severity='high'
            )
        
        assert "Stage B reasoning failed" in str(exc_info.value)
    
    def test_invalid_json_response(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test handling of invalid JSON response."""
        # LLM returns response missing required fields
        mock_llm.generate_structured.side_effect = RuntimeError("Failed to generate valid JSON")
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        with pytest.raises(RuntimeError):
            reasoner.reason_about_gap(
                assessment=sample_assessment,
                subcategory=sample_subcategory,
                policy_section=sample_policy_section,
                severity='high'
            )
    
    def test_schema_validation_failure(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test handling of schema validation failure."""
        # Return response with invalid status value
        invalid_response = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'invalid_status',  # Not in enum
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        mock_llm.generate_structured.side_effect = ValueError("Invalid status value")
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        with pytest.raises(RuntimeError):
            reasoner.reason_about_gap(
                assessment=sample_assessment,
                subcategory=sample_subcategory,
                policy_section=sample_policy_section,
                severity='high'
            )


class TestLLMRuntimeIntegration:
    """Tests for integration with LLM runtime."""
    
    def test_llm_called_with_correct_parameters(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that LLM is called with correct parameters."""
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(
            llm=mock_llm,
            temperature=0.15,
            max_tokens=1024
        )
        
        reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        # Verify LLM was called with correct parameters
        call_args = mock_llm.generate_structured.call_args
        assert call_args[1]['temperature'] == 0.15
        assert call_args[1]['max_tokens'] == 1024
        assert call_args[1]['schema'] == GAP_DETAIL_SCHEMA
        assert call_args[1]['max_retries'] == 3
    
    def test_low_temperature_for_determinism(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment,
        sample_policy_section
    ):
        """Test that low temperature is used for deterministic output."""
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        call_args = mock_llm.generate_structured.call_args
        temperature = call_args[1]['temperature']
        
        # Verify low temperature for determinism
        assert temperature <= 0.2, "Temperature should be low for deterministic output"


class TestEdgeCases:
    """Tests for edge cases."""
    
    def test_empty_evidence_spans(
        self,
        mock_llm,
        sample_subcategory,
        sample_policy_section
    ):
        """Test handling of empty evidence spans."""
        assessment = CoverageAssessment(
            subcategory_id='GV.RM-01',
            status='missing',
            lexical_score=0.0,
            semantic_score=0.0,
            evidence_spans=[],
            confidence=0.0
        )
        
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'missing',
            'evidence_quote': '',
            'gap_explanation': 'No evidence found',
            'severity': 'high',
            'suggested_fix': 'Add policy section'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        # Should handle empty evidence spans gracefully
        gap_detail = reasoner.reason_about_gap(
            assessment=assessment,
            subcategory=sample_subcategory,
            policy_section=sample_policy_section,
            severity='high'
        )
        
        assert gap_detail.evidence_quote == ''
    
    def test_very_long_policy_section(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment
    ):
        """Test handling of very long policy sections."""
        # Create a very long policy section
        long_section = "This is a policy section. " * 500  # ~3000 words
        
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'test',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        # Should handle long sections (may truncate in prompt)
        gap_detail = reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=long_section,
            severity='high'
        )
        
        assert gap_detail is not None
    
    def test_special_characters_in_policy(
        self,
        mock_llm,
        sample_subcategory,
        sample_assessment
    ):
        """Test handling of special characters in policy text."""
        policy_with_special_chars = """
        ## Risk Management & Compliance
        
        The organization's risk management process includes:
        - Assessment of "high-risk" scenarios
        - Mitigation strategies (technical & administrative)
        - Reporting to C-level executives
        
        Note: See Appendix A for details.
        """
        
        mock_llm.generate_structured.return_value = {
            'subcategory_id': 'GV.RM-01',
            'description': sample_subcategory.description,
            'status': 'partially_covered',
            'evidence_quote': 'risk management process',
            'gap_explanation': 'test',
            'severity': 'high',
            'suggested_fix': 'test'
        }
        
        reasoner = StageBReasoner(llm=mock_llm)
        
        # Should handle special characters gracefully
        gap_detail = reasoner.reason_about_gap(
            assessment=sample_assessment,
            subcategory=sample_subcategory,
            policy_section=policy_with_special_chars,
            severity='high'
        )
        
        assert gap_detail is not None
