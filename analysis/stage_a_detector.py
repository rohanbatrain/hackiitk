"""
Stage A Evidence Detector for deterministic gap analysis.

This module implements the first stage of the two-stage safety architecture
for gap analysis. Stage A performs deterministic evidence detection using:
1. Lexical scoring: Keyword overlap from CSF subcategory keywords
2. Semantic scoring: Cosine similarity between embeddings
3. Section heuristics: Boost scores when section names match CSF categories

Stage A classifies coverage status without LLM involvement to minimize
hallucination risks and provide reproducible, deterministic results.

**Validates: Requirements 9.2, 9.3, 9.4**
"""

import logging
import re
from typing import List, Dict, Optional, Tuple
import numpy as np

from models.domain import (
    TextChunk,
    CSFSubcategory,
    CoverageAssessment,
    RetrievalResult
)
from retrieval.hybrid_retriever import HybridRetriever
from retrieval.embedding_engine import EmbeddingEngine


logger = logging.getLogger(__name__)


class StageADetector:
    """Deterministic evidence detector for Stage A gap analysis.
    
    Performs evidence detection using lexical, semantic, and structural
    heuristics to classify CSF subcategory coverage without LLM involvement.
    
    Coverage classification thresholds:
    - Covered: confidence > 0.8
    - Partially Covered: 0.5 <= confidence <= 0.8
    - Missing: confidence < 0.3
    - Ambiguous: 0.3 <= confidence < 0.5
    
    Attributes:
        retriever: Hybrid retriever for finding relevant policy chunks
        embedding_engine: Embedding engine for semantic similarity
        lexical_weight: Weight for lexical scoring (default 0.3)
        semantic_weight: Weight for semantic scoring (default 0.5)
        section_weight: Weight for section heuristics (default 0.2)
    """
    
    # Coverage status thresholds
    COVERED_THRESHOLD = 0.8
    PARTIAL_UPPER_THRESHOLD = 0.8
    PARTIAL_LOWER_THRESHOLD = 0.5
    MISSING_THRESHOLD = 0.3
    
    def __init__(
        self,
        retriever: HybridRetriever,
        embedding_engine: EmbeddingEngine,
        lexical_weight: float = 0.3,
        semantic_weight: float = 0.5,
        section_weight: float = 0.2
    ):
        """Initialize Stage A detector.
        
        Args:
            retriever: Hybrid retriever for policy chunk retrieval
            embedding_engine: Embedding engine for semantic similarity
            lexical_weight: Weight for lexical scoring (0.0 to 1.0)
            semantic_weight: Weight for semantic scoring (0.0 to 1.0)
            section_weight: Weight for section heuristics (0.0 to 1.0)
            
        Raises:
            ValueError: If weights don't sum to 1.0
        """
        if not np.isclose(lexical_weight + semantic_weight + section_weight, 1.0):
            raise ValueError(
                f"Weights must sum to 1.0, got {lexical_weight + semantic_weight + section_weight}"
            )
        
        self.retriever = retriever
        self.embedding_engine = embedding_engine
        self.lexical_weight = lexical_weight
        self.semantic_weight = semantic_weight
        self.section_weight = section_weight
        
        logger.info(
            f"Initialized StageADetector with weights: "
            f"lexical={lexical_weight}, semantic={semantic_weight}, section={section_weight}"
        )
    
    def detect_evidence(
        self,
        policy_chunks: List[TextChunk],
        subcategory: CSFSubcategory,
        top_k: int = 5
    ) -> CoverageAssessment:
        """Detect evidence for a CSF subcategory in policy chunks.
        
        Performs three types of scoring:
        1. Lexical: Keyword overlap between subcategory keywords and policy text
        2. Semantic: Cosine similarity between subcategory and policy embeddings
        3. Section: Heuristic boost when section names match CSF categories
        
        Args:
            policy_chunks: List of policy text chunks to search
            subcategory: CSF subcategory to find evidence for
            top_k: Number of top chunks to consider for scoring
            
        Returns:
            CoverageAssessment with scores, status, and evidence spans
        """
        logger.debug(f"Detecting evidence for {subcategory.subcategory_id}")
        
        # Retrieve most relevant policy chunks for this subcategory
        retrieval_results = self.retriever.retrieve(
            query_text=subcategory.description,
            top_k=top_k
        )
        
        # If no results, mark as missing
        if not retrieval_results:
            return CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status='missing',
                lexical_score=0.0,
                semantic_score=0.0,
                evidence_spans=[],
                confidence=0.0
            )
        
        # Find corresponding policy chunks from retrieval results
        relevant_chunks = self._get_relevant_chunks(policy_chunks, retrieval_results)
        
        if not relevant_chunks:
            return CoverageAssessment(
                subcategory_id=subcategory.subcategory_id,
                status='missing',
                lexical_score=0.0,
                semantic_score=0.0,
                evidence_spans=[],
                confidence=0.0
            )
        
        # Calculate lexical score
        lexical_score = self._calculate_lexical_score(
            relevant_chunks,
            subcategory.keywords
        )
        
        # Calculate semantic score
        semantic_score = self._calculate_semantic_score(
            relevant_chunks,
            subcategory.description
        )
        
        # Calculate section heuristic score
        section_score = self._calculate_section_score(
            relevant_chunks,
            subcategory.category
        )
        
        # Combine scores with weights
        confidence = (
            self.lexical_weight * lexical_score +
            self.semantic_weight * semantic_score +
            self.section_weight * section_score
        )
        
        # Classify coverage status based on confidence
        status = self._classify_coverage(confidence)
        
        # Extract evidence spans from relevant chunks
        evidence_spans = [chunk.text for chunk in relevant_chunks[:3]]  # Top 3 chunks
        
        logger.debug(
            f"{subcategory.subcategory_id}: lexical={lexical_score:.3f}, "
            f"semantic={semantic_score:.3f}, section={section_score:.3f}, "
            f"confidence={confidence:.3f}, status={status}"
        )
        
        return CoverageAssessment(
            subcategory_id=subcategory.subcategory_id,
            status=status,
            lexical_score=lexical_score,
            semantic_score=semantic_score,
            evidence_spans=evidence_spans,
            confidence=confidence
        )
    
    def _get_relevant_chunks(
        self,
        policy_chunks: List[TextChunk],
        retrieval_results: List[RetrievalResult]
    ) -> List[TextChunk]:
        """Get policy chunks corresponding to retrieval results.
        
        Note: This is a simplified implementation. In production, retrieval
        results would directly reference policy chunks. For now, we use
        the retrieval to guide which chunks to examine.
        
        Args:
            policy_chunks: All policy chunks
            retrieval_results: Retrieval results from hybrid retriever
            
        Returns:
            List of relevant policy chunks
        """
        # For now, return top chunks based on retrieval scores
        # In a full implementation, retrieval would return chunk IDs
        # that we could use to look up specific chunks
        
        # Simple heuristic: return chunks that contain evidence spans
        relevant_chunks = []
        
        for result in retrieval_results:
            # Evidence spans from retrieval are CSF descriptions, not policy text
            # So we need to find policy chunks that match the query
            # For now, just return the first few chunks as a placeholder
            pass
        
        # Fallback: return first few chunks for scoring
        # This will be improved when retrieval properly tracks policy chunks
        return policy_chunks[:min(5, len(policy_chunks))]
    
    def _calculate_lexical_score(
        self,
        chunks: List[TextChunk],
        keywords: List[str]
    ) -> float:
        """Calculate lexical score based on keyword overlap.
        
        Computes the ratio of subcategory keywords found in the policy chunks.
        Uses case-insensitive matching and word boundaries.
        
        Args:
            chunks: Policy text chunks to search
            keywords: CSF subcategory keywords
            
        Returns:
            Lexical score between 0.0 and 1.0
        """
        if not keywords:
            return 0.0
        
        # Combine all chunk text
        combined_text = ' '.join(chunk.text.lower() for chunk in chunks)
        
        # Count how many keywords are found
        found_keywords = 0
        for keyword in keywords:
            # Use word boundary matching for more accurate detection
            pattern = r'\b' + re.escape(keyword.lower()) + r'\b'
            if re.search(pattern, combined_text):
                found_keywords += 1
        
        # Calculate ratio of found keywords
        score = found_keywords / len(keywords)
        
        return score
    
    def _calculate_semantic_score(
        self,
        chunks: List[TextChunk],
        subcategory_description: str
    ) -> float:
        """Calculate semantic score using cosine similarity.
        
        Computes cosine similarity between the subcategory description
        embedding and the policy chunk embeddings.
        
        Args:
            chunks: Policy text chunks with embeddings
            subcategory_description: CSF subcategory description text
            
        Returns:
            Semantic score between 0.0 and 1.0 (max similarity)
        """
        # Generate embedding for subcategory description
        subcategory_embedding = self.embedding_engine.embed_text(
            subcategory_description
        )
        
        # Calculate cosine similarity with each chunk
        max_similarity = 0.0
        
        for chunk in chunks:
            # Generate embedding if not already present
            if chunk.embedding is None:
                chunk_embedding = self.embedding_engine.embed_text(chunk.text)
            else:
                chunk_embedding = chunk.embedding
            
            # Compute cosine similarity (embeddings are already normalized)
            similarity = np.dot(subcategory_embedding, chunk_embedding)
            
            # Track maximum similarity
            max_similarity = max(max_similarity, similarity)
        
        # Ensure score is in [0, 1] range
        score = max(0.0, min(1.0, max_similarity))
        
        return score
    
    def _calculate_section_score(
        self,
        chunks: List[TextChunk],
        csf_category: str
    ) -> float:
        """Calculate section heuristic score.
        
        Boosts score when policy section names match CSF category names.
        For example, if analyzing "Risk Management Strategy" subcategory
        and policy has a "Risk Management" section, boost the score.
        
        Args:
            chunks: Policy text chunks with section titles
            csf_category: CSF category name (e.g., "Risk Management Strategy")
            
        Returns:
            Section score between 0.0 and 1.0
        """
        if not csf_category:
            return 0.0
        
        # Extract key terms from CSF category (remove common words)
        csf_terms = self._extract_key_terms(csf_category)
        
        # Check if any chunk's section title matches CSF terms
        max_match_score = 0.0
        
        for chunk in chunks:
            if chunk.section_title:
                section_terms = self._extract_key_terms(chunk.section_title)
                
                # Calculate overlap between CSF terms and section terms
                if csf_terms and section_terms:
                    overlap = len(csf_terms & section_terms)
                    match_score = overlap / len(csf_terms)
                    max_match_score = max(max_match_score, match_score)
        
        return max_match_score
    
    def _extract_key_terms(self, text: str) -> set:
        """Extract key terms from text by removing common words.
        
        Args:
            text: Input text
            
        Returns:
            Set of lowercase key terms
        """
        # Common words to ignore (minimal stop words to preserve domain terms)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to',
            'for', 'of', 'with', 'by', 'from', 'as', 'is', 'are', 'was',
            'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do',
            'does', 'did', 'will', 'would', 'should', 'could', 'may',
            'might', 'must', 'can', 'policy', 'policies'
        }
        
        # Tokenize and filter
        words = re.findall(r'\b\w+\b', text.lower())
        key_terms = {word for word in words if word not in stop_words and len(word) > 2}
        
        return key_terms
    
    def _classify_coverage(self, confidence: float) -> str:
        """Classify coverage status based on confidence score.
        
        Thresholds:
        - Covered: > 0.8
        - Partially Covered: 0.5 to 0.8
        - Missing: < 0.3
        - Ambiguous: 0.3 to 0.5
        
        Args:
            confidence: Combined confidence score (0.0 to 1.0)
            
        Returns:
            Coverage status string
        """
        if confidence > self.COVERED_THRESHOLD:
            return 'covered'
        elif confidence >= self.PARTIAL_LOWER_THRESHOLD:
            return 'partially_covered'
        elif confidence < self.MISSING_THRESHOLD:
            return 'missing'
        else:
            return 'ambiguous'
