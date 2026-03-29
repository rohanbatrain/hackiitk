"""
Stage B Constrained Reasoner for LLM-based gap analysis.

This module implements the second stage of the two-stage safety architecture
for gap analysis. Stage B applies constrained LLM reasoning only to ambiguous
and missing cases identified by Stage A, using strict output schemas to ensure
structured, parseable results.

Stage B receives:
- Matched policy section (NOT entire document)
- CSF subcategory text
- Evidence spans from Stage A
- Strict JSON schema for output

This constraint minimizes hallucination risks by limiting LLM context to only
relevant policy sections and enforcing structured output.

**Validates: Requirements 9.5, 9.6**
"""

import json
import logging
from typing import Dict, Any, Optional

from models.domain import CoverageAssessment, GapDetail, CSFSubcategory
from models.schemas import GAP_DETAIL_SCHEMA, validate_gap_detail
from analysis.llm_runtime import LLMRuntime


logger = logging.getLogger(__name__)


class StageBReasoner:
    """Constrained LLM reasoner for Stage B gap analysis.
    
    Applies LLM reasoning only to ambiguous and missing cases from Stage A.
    Uses strict prompting and JSON schema validation to ensure deterministic,
    structured outputs that minimize hallucination risks.
    
    Attributes:
        llm: LLM runtime for text generation
        temperature: Sampling temperature for deterministic output (default 0.1)
        max_tokens: Maximum tokens to generate (default 512)
        prompt_version: Version identifier for prompt templates
    """
    
    PROMPT_VERSION = "1.0.0"
    
    def __init__(
        self,
        llm: LLMRuntime,
        temperature: float = 0.1,
        max_tokens: int = 512
    ):
        """Initialize Stage B reasoner.
        
        Args:
            llm: LLM runtime for text generation
            temperature: Sampling temperature (low for determinism)
            max_tokens: Maximum tokens to generate
        """
        self.llm = llm
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.prompt_version = self.PROMPT_VERSION
        
        logger.info(
            f"Initialized StageBReasoner with temperature={temperature}, "
            f"max_tokens={max_tokens}, prompt_version={self.prompt_version}"
        )
    
    def reason_about_gap(
        self,
        assessment: CoverageAssessment,
        subcategory: CSFSubcategory,
        policy_section: str,
        severity: str
    ) -> GapDetail:
        """Reason about a gap using constrained LLM generation.
        
        This method is called only for ambiguous and missing cases from Stage A.
        It provides the LLM with:
        - The matched policy section (NOT entire document)
        - CSF subcategory requirement text
        - Evidence spans from Stage A
        - Strict JSON schema for output
        
        The LLM explains:
        - Why coverage exists or not
        - What specific gap is present
        - What revision language is needed
        
        Args:
            assessment: Stage A coverage assessment
            subcategory: CSF subcategory being analyzed
            policy_section: Matched policy section text (NOT entire document)
            severity: Gap severity level ('critical', 'high', 'medium', 'low')
            
        Returns:
            GapDetail with structured gap information
            
        Raises:
            RuntimeError: If LLM generation fails after retries
            ValueError: If generated JSON doesn't conform to schema
        """
        logger.debug(
            f"Reasoning about {subcategory.subcategory_id} "
            f"(status={assessment.status}, confidence={assessment.confidence:.3f})"
        )
        
        # Build prompt with required context
        prompt = self._build_prompt(
            assessment=assessment,
            subcategory=subcategory,
            policy_section=policy_section,
            severity=severity
        )
        
        # Generate structured JSON response
        try:
            response = self.llm.generate_structured(
                prompt=prompt,
                schema=GAP_DETAIL_SCHEMA,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                max_retries=3
            )
            
            # Validate response conforms to schema
            validate_gap_detail(response)
            
            # Convert to GapDetail object
            gap_detail = GapDetail(
                subcategory_id=response['subcategory_id'],
                subcategory_description=response['description'],
                status=response['status'],
                # Use LLM evidence_quote if provided, otherwise use Stage A evidence spans
                evidence_quote=response['evidence_quote'] or self._format_evidence_spans(assessment.evidence_spans),
                gap_explanation=response['gap_explanation'],
                severity=response['severity'],
                suggested_fix=response['suggested_fix']
            )
            
            logger.debug(
                f"Generated gap detail for {subcategory.subcategory_id}: "
                f"status={gap_detail.status}, severity={gap_detail.severity}"
            )
            
            return gap_detail
            
        except Exception as e:
            logger.error(
                f"Failed to generate gap detail for {subcategory.subcategory_id}: {e}"
            )
            raise RuntimeError(
                f"Stage B reasoning failed for {subcategory.subcategory_id}: {e}"
            )
    
    def _build_prompt(
        self,
        assessment: CoverageAssessment,
        subcategory: CSFSubcategory,
        policy_section: str,
        severity: str
    ) -> str:
        """Build constrained prompt for LLM reasoning.
        
        The prompt includes:
        - Clear instructions for gap analysis
        - Policy section text (NOT entire document)
        - CSF subcategory requirement
        - Evidence spans from Stage A
        - Strict JSON schema
        - Examples of expected output format
        
        Args:
            assessment: Stage A coverage assessment
            subcategory: CSF subcategory being analyzed
            policy_section: Matched policy section text
            severity: Gap severity level
            
        Returns:
            Formatted prompt string
        """
        # Format evidence spans
        evidence_text = "\n".join(
            f"- {span[:200]}..." if len(span) > 200 else f"- {span}"
            for span in assessment.evidence_spans
        ) if assessment.evidence_spans else "No evidence found"
    
    def _format_evidence_spans(self, evidence_spans: list) -> str:
        """Format evidence spans from Stage A into a readable string.
        
        Args:
            evidence_spans: List of evidence text spans from Stage A
            
        Returns:
            Formatted evidence string or empty string if no evidence
        """
        if not evidence_spans:
            return ""
        
        # Join first 3 evidence spans with separator
        formatted = " | ".join(
            span[:150] + "..." if len(span) > 150 else span
            for span in evidence_spans[:3]
        )
        
        return formatted
    
    def _build_prompt(
        self,
        assessment: CoverageAssessment,
        subcategory: CSFSubcategory,
        policy_section: str,
        severity: str
    ) -> str:
        """Build constrained prompt for LLM reasoning.
        
        The prompt includes:
        - Clear instructions for gap analysis
        - Policy section text (NOT entire document)
        - CSF subcategory requirement
        - Evidence spans from Stage A
        - Strict JSON schema
        - Examples of expected output format
        
        Args:
            assessment: Stage A coverage assessment
            subcategory: CSF subcategory being analyzed
            policy_section: Matched policy section text
            severity: Gap severity level
            
        Returns:
            Formatted prompt string
        """
        # Format evidence spans
        evidence_text = "\n".join(
            f"- {span[:200]}..." if len(span) > 200 else f"- {span}"
            for span in assessment.evidence_spans
        ) if assessment.evidence_spans else "No evidence found"
        
        # Determine status based on assessment
        if assessment.status == 'missing':
            status_guidance = (
                "The policy appears to have NO coverage for this requirement. "
                "Set status to 'missing' and evidence_quote to empty string."
            )
        else:  # ambiguous or partially_covered
            status_guidance = (
                "The policy has PARTIAL coverage for this requirement. "
                "Set status to 'partially_covered' and include the relevant evidence_quote."
            )
        
        prompt = f"""You are a cybersecurity policy analyst performing gap analysis against NIST CSF 2.0 standards.

**Task**: Analyze whether the policy section below adequately addresses the CSF subcategory requirement.

**CSF Subcategory**: {subcategory.subcategory_id}
**Function**: {subcategory.function}
**Category**: {subcategory.category}
**Requirement**: {subcategory.description}

**Policy Section**:
{policy_section[:2000]}

**Evidence from Initial Analysis** (Stage A):
{evidence_text}

**Stage A Assessment**:
- Status: {assessment.status}
- Confidence: {assessment.confidence:.3f}
- Lexical Score: {assessment.lexical_score:.3f}
- Semantic Score: {assessment.semantic_score:.3f}

**Instructions**:
{status_guidance}

Analyze the policy section and provide:
1. **evidence_quote**: The exact text from the policy that relates to this requirement (or empty string if missing)
2. **gap_explanation**: A clear explanation of what is missing or inadequate
3. **suggested_fix**: Specific policy language that would address the gap

Be factual and specific. Do not hallucinate policy content that doesn't exist.

**Output Format**:
You must respond with valid JSON matching this exact structure:
{{
  "subcategory_id": "{subcategory.subcategory_id}",
  "description": "{subcategory.description}",
  "status": "missing" or "partially_covered",
  "evidence_quote": "exact text from policy or empty string",
  "gap_explanation": "clear explanation of the gap",
  "severity": "{severity}",
  "suggested_fix": "specific policy language to address the gap"
}}

Respond with ONLY the JSON object, no additional text."""
        
        return prompt
    
    def validate_response(self, response: Dict[str, Any]) -> bool:
        """Validate that LLM response conforms to schema.
        
        Args:
            response: LLM response as dictionary
            
        Returns:
            True if valid, False otherwise
        """
        try:
            validate_gap_detail(response)
            return True
        except Exception as e:
            logger.warning(f"Response validation failed: {e}")
            return False
    
    def __repr__(self) -> str:
        """String representation of Stage B reasoner."""
        return (
            f"StageBReasoner(temperature={self.temperature}, "
            f"max_tokens={self.max_tokens}, prompt_version={self.prompt_version})"
        )
