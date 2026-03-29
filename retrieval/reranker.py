"""
Cross-Encoder Reranker for improving retrieval precision.

This module provides reranking functionality using a local cross-encoder model
to score query-document pairs. Reranking improves precision by 15-20% in RAG
benchmarks by providing more accurate relevance scores than initial retrieval.

**Validates: Requirements 7.6**
"""

import logging
import os
from typing import List, Dict, Tuple
import numpy as np

try:
    from sentence_transformers import CrossEncoder
    CROSS_ENCODER_AVAILABLE = True
except ImportError:
    CROSS_ENCODER_AVAILABLE = False


logger = logging.getLogger(__name__)


class Reranker:
    """Cross-encoder reranker for query-document scoring.
    
    Uses a local cross-encoder model to score query-document pairs and
    rerank retrieval results by relevance. Cross-encoders provide more
    accurate relevance scores than bi-encoders by jointly encoding the
    query and document.
    
    Attributes:
        model: Loaded CrossEncoder model
        model_path: Path to local model directory
    """
    
    def __init__(self, model_path: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"):
        """Initialize reranker with local cross-encoder model.
        
        Args:
            model_path: Path to local cross-encoder model or HuggingFace model name
            
        Raises:
            RuntimeError: If cross-encoder library not available or model cannot be loaded
        """
        if not CROSS_ENCODER_AVAILABLE:
            raise RuntimeError(
                "sentence-transformers library with CrossEncoder support is not available. "
                "Please install: pip install sentence-transformers"
            )
        
        try:
            # Set HuggingFace token if available (suppresses auth warnings)
            hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')
            if hf_token:
                os.environ['HUGGING_FACE_HUB_TOKEN'] = hf_token
                logger.debug("Using HuggingFace token for model downloads")
            
            # Load cross-encoder model
            self.model = CrossEncoder(model_path, device='cpu')
            self.model_path = model_path
            logger.info(f"Loaded cross-encoder model from: {model_path}")
        except Exception as e:
            raise RuntimeError(f"Failed to load cross-encoder model: {e}")
    
    def rerank(
        self,
        query: str,
        documents: List[str],
        metadata: List[Dict],
        top_k: int = 5
    ) -> List[Dict]:
        """Rerank documents by relevance to query.
        
        Args:
            query: Query text
            documents: List of document texts to rerank
            metadata: List of metadata dictionaries for each document
            top_k: Number of top results to return after reranking
            
        Returns:
            List of dictionaries containing:
                - document: Document text
                - score: Cross-encoder relevance score
                - metadata: Associated metadata
                - rank: Reranked position (0-indexed)
                
        Raises:
            ValueError: If documents and metadata lengths don't match or inputs are empty
        """
        if len(documents) != len(metadata):
            raise ValueError(
                f"Documents count ({len(documents)}) must match metadata count ({len(metadata)})"
            )
        
        if not documents:
            raise ValueError("Cannot rerank empty document list")
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Create query-document pairs
        pairs = [(query, doc) for doc in documents]
        
        # Score all pairs
        scores = self.model.predict(pairs)
        
        # Convert to numpy array if not already
        if not isinstance(scores, np.ndarray):
            scores = np.array(scores)
        
        # Get top-k indices by score
        top_k_actual = min(top_k, len(documents))
        top_indices = np.argsort(scores)[::-1][:top_k_actual]
        
        # Build reranked results
        results = []
        for rank, idx in enumerate(top_indices):
            results.append({
                'document': documents[idx],
                'score': float(scores[idx]),
                'metadata': metadata[idx],
                'rank': rank
            })
        
        logger.debug(f"Reranked {len(documents)} documents, returning top {len(results)}")
        
        return results
    
    def score_pairs(self, query_document_pairs: List[Tuple[str, str]]) -> np.ndarray:
        """Score query-document pairs without ranking.
        
        Args:
            query_document_pairs: List of (query, document) tuples
            
        Returns:
            Numpy array of relevance scores
            
        Raises:
            ValueError: If pairs list is empty
        """
        if not query_document_pairs:
            raise ValueError("Cannot score empty pairs list")
        
        scores = self.model.predict(query_document_pairs)
        
        if not isinstance(scores, np.ndarray):
            scores = np.array(scores)
        
        return scores
