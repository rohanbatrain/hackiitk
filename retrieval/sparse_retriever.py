"""
Sparse Retrieval component using BM25 algorithm.

This module provides keyword-based retrieval using the BM25 algorithm
for exact keyword matching. It complements dense vector similarity search
in the hybrid retrieval architecture.

**Validates: Requirements 7.2**
"""

import logging
from typing import List, Dict, Optional
from rank_bm25 import BM25Okapi


logger = logging.getLogger(__name__)


class SparseRetriever:
    """Sparse retriever using BM25 algorithm for keyword matching.
    
    Implements keyword-based retrieval to complement dense vector similarity
    search. BM25 is particularly effective for exact terminology matching
    and prevents missing critical CSF subcategories due to vocabulary differences.
    
    Attributes:
        corpus: List of documents (CSF subcategory descriptions)
        corpus_metadata: Metadata for each document in corpus
        bm25: BM25Okapi instance for scoring
    """
    
    def __init__(self):
        """Initialize sparse retriever."""
        self.corpus: List[str] = []
        self.corpus_metadata: List[Dict] = []
        self.bm25: Optional[BM25Okapi] = None
        self._is_indexed = False
    
    def index_documents(self, documents: List[str], metadata: List[Dict]) -> None:
        """Index documents for BM25 retrieval.
        
        Args:
            documents: List of text documents to index (e.g., CSF subcategory descriptions)
            metadata: List of metadata dictionaries for each document
            
        Raises:
            ValueError: If documents and metadata lengths don't match
        """
        if len(documents) != len(metadata):
            raise ValueError(
                f"Documents count ({len(documents)}) must match metadata count ({len(metadata)})"
            )
        
        if not documents:
            raise ValueError("Cannot index empty document list")
        
        self.corpus = documents
        self.corpus_metadata = metadata
        
        # Tokenize documents (simple whitespace tokenization)
        tokenized_corpus = [doc.lower().split() for doc in documents]
        
        # Create BM25 index
        self.bm25 = BM25Okapi(tokenized_corpus)
        self._is_indexed = True
        
        logger.info(f"Indexed {len(documents)} documents for BM25 retrieval")
    
    def retrieve(self, query: str, top_k: int = 5) -> List[Dict]:
        """Retrieve top-k documents using BM25 keyword matching.
        
        Args:
            query: Query text for keyword matching
            top_k: Number of top results to return
            
        Returns:
            List of dictionaries containing:
                - document: Original document text
                - score: BM25 relevance score
                - metadata: Associated metadata
                - rank: Result rank (0-indexed)
                
        Raises:
            RuntimeError: If retriever not indexed
            ValueError: If query is empty
        """
        if not self._is_indexed:
            raise RuntimeError("Retriever must be indexed before retrieval. Call index_documents() first.")
        
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")
        
        # Tokenize query
        tokenized_query = query.lower().split()
        
        # Get BM25 scores for all documents
        scores = self.bm25.get_scores(tokenized_query)
        
        # Get top-k indices
        top_k_actual = min(top_k, len(self.corpus))
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:top_k_actual]
        
        # Build results
        results = []
        for rank, idx in enumerate(top_indices):
            results.append({
                'document': self.corpus[idx],
                'score': float(scores[idx]),
                'metadata': self.corpus_metadata[idx],
                'rank': rank
            })
        
        logger.debug(f"Retrieved {len(results)} results for query: '{query[:50]}...'")
        
        return results
    
    def get_corpus_size(self) -> int:
        """Get number of indexed documents.
        
        Returns:
            Number of documents in corpus
        """
        return len(self.corpus)
    
    def is_indexed(self) -> bool:
        """Check if retriever has been indexed.
        
        Returns:
            True if indexed, False otherwise
        """
        return self._is_indexed
