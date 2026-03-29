"""
Gap Analysis Engine - Integration of Stage A and Stage B.

This module implements the complete two-stage gap analysis architecture that
orchestrates deterministic evidence detection (Stage A) with constrained LLM
reasoning (Stage B) to identify policy gaps against NIST CSF 2.0 standards.

The engine:
1. Executes Stage A for all relevant CSF subcategories
2. Filters Covered subcategories (skips Stage B)
3. Executes Stage B only for Ambiguous and Missing subcategories
4. Assigns severity levels based on CSF priority
5. Generates structured gap analysis reports

**Validates: Requirements 9.1, 9.7, 9.11**
"""

import logging
import hashlib
from datetime import datetime
from typing import List, Dict, Optional

from models.domain import (
    TextChunk,
    CSFSubcategory,
    CoverageAssessment,
    GapDetail,
    GapAnalysisReport
)
from analysis.stage_a_detector import StageADetector
from analysis.stage_b_reasoner import StageBReasoner
from analysis.domain_mapper import DomainMapper
from reference_builder.reference_catalog import ReferenceCatalog


logger = logging.getLogger(__name__)


class GapAnalysisEngine:
    """Orchestrates two-stage gap analysis for policy documents.
    
    The engine implements a safety-first architecture:
    - Stage A: Deterministic evidence detection for all subcategories
    - Stage B: Constrained LLM reasoning only for ambiguous/missing cases
    
    This approach minimizes hallucination risks while providing comprehensive
    gap analysis with structured, reproducible outputs.
    
    Attributes:
        stage_a: Stage A detector for deterministic evidence detection
        stage_b: Stage B reasoner for constrained LLM reasoning
        catalog: Reference catalog of CSF subcategories
        model_name: LLM model name for metadata
        model_version: LLM model version for metadata
        embedding_model: Embedding model name for metadata
        prompt_version: Prompt template version for metadata
    """
    
    def __init__(
        self,
        stage_a: StageADetector,
        stage_b: StageBReasoner,
        catalog: ReferenceCatalog,
        model_name: str = "unknown",
        model_version: str = "unknown",
        embedding_model: str = "all-MiniLM-L6-v2",
        prompt_version: str = "1.0.0"
    ):
        """Initialize gap analysis engine.
        
        Args:
            stage_a: Stage A detector for evidence detection
            stage_b: Stage B reasoner for LLM-based reasoning
            catalog: Reference catalog of CSF subcategories
            model_name: LLM model name for metadata
            model_version: LLM model version for metadata
            embedding_model: Embedding model name for metadata
            prompt_version: Prompt template version for metadata
        """
        self.stage_a = stage_a
        self.stage_b = stage_b
        self.catalog = catalog
        self.domain_mapper = DomainMapper(catalog)
        self.model_name = model_name
        self.model_version = model_version
        self.embedding_model = embedding_model
        self.prompt_version = prompt_version
        
        logger.info(
            f"Initialized GapAnalysisEngine with model={model_name}, "
            f"version={model_version}, embedding={embedding_model}"
        )
    
    def analyze(
        self,
        policy_chunks: List[TextChunk],
        input_file: str,
        domain: Optional[str] = None,
        config_hash: Optional[str] = None,
        retrieval_params: Optional[Dict] = None
    ) -> GapAnalysisReport:
        """Execute complete two-stage gap analysis.
        
        Workflow:
        1. Get relevant CSF subcategories (all or domain-specific)
        2. Execute Stage A for all subcategories
        3. Filter Covered subcategories (skip Stage B)
        4. Execute Stage B for Ambiguous and Missing subcategories
        5. Assign severity levels based on CSF priority
        6. Generate structured gap analysis report
        
        Args:
            policy_chunks: Parsed and chunked policy text
            input_file: Path to input policy document
            domain: Optional policy domain for prioritization
            config_hash: Optional configuration hash for metadata
            retrieval_params: Optional retrieval parameters for metadata
            
        Returns:
            GapAnalysisReport with identified gaps and metadata
            
        Raises:
            ValueError: If policy_chunks is empty
            RuntimeError: If analysis fails
        """
        if not policy_chunks:
            raise ValueError("policy_chunks cannot be empty")
        
        logger.info(
            f"Starting gap analysis for {input_file} "
            f"({len(policy_chunks)} chunks, domain={domain})"
        )
        
        # Get relevant CSF subcategories
        subcategories = self._get_relevant_subcategories(domain)
        logger.info(f"Analyzing {len(subcategories)} CSF subcategories")
        
        # Execute Stage A for all subcategories
        logger.info("Executing Stage A: Deterministic evidence detection")
        stage_a_assessments = self._execute_stage_a(policy_chunks, subcategories)
        
        # Separate covered from ambiguous/missing
        covered_assessments = [
            a for a in stage_a_assessments if a.status == 'covered'
        ]
        needs_stage_b = [
            a for a in stage_a_assessments 
            if a.status in ['ambiguous', 'missing', 'partially_covered']
        ]
        
        logger.info(
            f"Stage A results: {len(covered_assessments)} covered, "
            f"{len(needs_stage_b)} need Stage B analysis"
        )
        
        # Execute Stage B for ambiguous/missing cases
        gaps = []
        if needs_stage_b:
            logger.info("Executing Stage B: Constrained LLM reasoning")
            gaps = self._execute_stage_b(
                needs_stage_b,
                policy_chunks,
                subcategories
            )
        
        # Extract covered subcategory IDs
        covered_subcategories = [a.subcategory_id for a in covered_assessments]
        
        # Calculate input file hash
        input_file_hash = self._calculate_file_hash(input_file)
        
        # Build metadata
        metadata = {
            'prompt_version': self.prompt_version,
            'config_hash': config_hash or 'default',
            'retrieval_params': retrieval_params or {},
            'total_subcategories_analyzed': len(subcategories),
            'covered_count': len(covered_assessments),
            'gap_count': len(gaps),
            'domain': domain
        }
        
        # Generate report
        report = GapAnalysisReport(
            analysis_date=datetime.now(),
            input_file=input_file,
            input_file_hash=input_file_hash,
            model_name=self.model_name,
            model_version=self.model_version,
            embedding_model=self.embedding_model,
            gaps=gaps,
            covered_subcategories=covered_subcategories,
            metadata=metadata
        )
        
        logger.info(
            f"Gap analysis complete: {len(gaps)} gaps identified, "
            f"{len(covered_subcategories)} subcategories covered"
        )
        
        return report
    
    def _get_relevant_subcategories(
        self,
        domain: Optional[str]
    ) -> List[CSFSubcategory]:
        """Get relevant CSF subcategories based on policy domain.
        
        Uses DomainMapper to apply domain-specific prioritization rules.
        If domain is specified, returns prioritized subcategories for that domain.
        Otherwise, returns all subcategories from the catalog.
        
        Args:
            domain: Optional policy domain ('isms', 'risk_management', etc.)
            
        Returns:
            List of relevant CSF subcategories
        """
        # Use DomainMapper for domain-specific prioritization
        subcategories, warning = self.domain_mapper.get_prioritized_subcategories(domain)
        
        # Log warning if present (e.g., for data privacy domain)
        if warning:
            logger.warning(f"Domain limitation: {warning}")
        
        return subcategories
    
    def _execute_stage_a(
        self,
        policy_chunks: List[TextChunk],
        subcategories: List[CSFSubcategory]
    ) -> List[CoverageAssessment]:
        """Execute Stage A for all subcategories.
        
        Performs deterministic evidence detection using lexical, semantic,
        and structural scoring for each CSF subcategory.
        
        Args:
            policy_chunks: Policy text chunks to analyze
            subcategories: CSF subcategories to check coverage for
            
        Returns:
            List of coverage assessments for all subcategories
        """
        assessments = []
        
        for i, subcategory in enumerate(subcategories, 1):
            logger.debug(
                f"Stage A: Analyzing {subcategory.subcategory_id} "
                f"({i}/{len(subcategories)})"
            )
            
            try:
                assessment = self.stage_a.detect_evidence(
                    policy_chunks=policy_chunks,
                    subcategory=subcategory
                )
                assessments.append(assessment)
                
            except Exception as e:
                logger.error(
                    f"Stage A failed for {subcategory.subcategory_id}: {e}"
                )
                # Create a missing assessment as fallback
                assessments.append(CoverageAssessment(
                    subcategory_id=subcategory.subcategory_id,
                    status='missing',
                    lexical_score=0.0,
                    semantic_score=0.0,
                    evidence_spans=[],
                    confidence=0.0
                ))
        
        return assessments
    
    def _execute_stage_b(
        self,
        assessments: List[CoverageAssessment],
        policy_chunks: List[TextChunk],
        subcategories: List[CSFSubcategory]
    ) -> List[GapDetail]:
        """Execute Stage B for ambiguous and missing cases.
        
        Applies constrained LLM reasoning only to cases that need it,
        using strict output schemas to ensure structured results.
        
        Args:
            assessments: Stage A assessments needing Stage B analysis
            policy_chunks: Policy text chunks for context
            subcategories: All CSF subcategories for lookup
            
        Returns:
            List of gap details from Stage B analysis
        """
        gaps = []
        
        # Build subcategory lookup map
        subcategory_map = {s.subcategory_id: s for s in subcategories}
        
        for i, assessment in enumerate(assessments, 1):
            logger.debug(
                f"Stage B: Analyzing {assessment.subcategory_id} "
                f"({i}/{len(assessments)})"
            )
            
            # Get subcategory details
            subcategory = subcategory_map.get(assessment.subcategory_id)
            if not subcategory:
                logger.warning(
                    f"Subcategory {assessment.subcategory_id} not found in catalog"
                )
                continue
            
            # Assign severity based on CSF priority
            severity = self._assign_severity(subcategory)
            
            # Get policy section for context (use evidence spans or first chunks)
            policy_section = self._get_policy_section(
                assessment,
                policy_chunks
            )
            
            try:
                gap_detail = self.stage_b.reason_about_gap(
                    assessment=assessment,
                    subcategory=subcategory,
                    policy_section=policy_section,
                    severity=severity
                )
                gaps.append(gap_detail)
                
            except Exception as e:
                logger.error(
                    f"Stage B failed for {assessment.subcategory_id}: {e}"
                )
                # Continue with other gaps rather than failing completely
                continue
        
        return gaps
    
    def _assign_severity(self, subcategory: CSFSubcategory) -> str:
        """Assign severity level based on CSF priority.
        
        Maps CSF subcategory priority to gap severity:
        - critical → critical
        - high → high
        - medium → medium
        - low → low
        
        Args:
            subcategory: CSF subcategory with priority
            
        Returns:
            Severity level string
        """
        priority = subcategory.priority.lower()
        
        # Direct mapping from priority to severity
        severity_map = {
            'critical': 'critical',
            'high': 'high',
            'medium': 'medium',
            'low': 'low'
        }
        
        return severity_map.get(priority, 'medium')
    
    def _get_policy_section(
        self,
        assessment: CoverageAssessment,
        policy_chunks: List[TextChunk]
    ) -> str:
        """Get relevant policy section for Stage B context.
        
        Uses evidence spans from Stage A if available, otherwise uses
        the first few policy chunks as context.
        
        Args:
            assessment: Stage A coverage assessment
            policy_chunks: All policy chunks
            
        Returns:
            Policy section text for LLM context
        """
        # If evidence spans exist, use them
        if assessment.evidence_spans:
            return "\n\n".join(assessment.evidence_spans)
        
        # Otherwise, use first few chunks as context
        # Limit to ~2000 characters to avoid context overflow
        combined_text = ""
        for chunk in policy_chunks[:5]:
            if len(combined_text) + len(chunk.text) > 2000:
                break
            combined_text += chunk.text + "\n\n"
        
        return combined_text.strip() or "No policy text available"
    
    def _calculate_file_hash(self, file_path: str) -> str:
        """Calculate SHA-256 hash of input file.
        
        Args:
            file_path: Path to file
            
        Returns:
            Hex string of SHA-256 hash
        """
        try:
            sha256_hash = hashlib.sha256()
            with open(file_path, "rb") as f:
                for byte_block in iter(lambda: f.read(4096), b""):
                    sha256_hash.update(byte_block)
            return sha256_hash.hexdigest()
        except Exception as e:
            logger.warning(f"Failed to calculate file hash: {e}")
            return "unknown"
    
    def __repr__(self) -> str:
        """String representation of gap analysis engine."""
        return (
            f"GapAnalysisEngine(model={self.model_name}, "
            f"version={self.model_version}, embedding={self.embedding_model})"
        )
