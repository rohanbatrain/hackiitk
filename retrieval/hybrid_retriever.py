"""
Hybrid Retrieval Engine combining dense and sparse search with reranking.

This module orchestrates the hybrid retrieval pipeline that combines:
1. Dense retrieval: Vector similarity search via ChromaDB/FAISS
2. Sparse retrieval: BM25 keyword matching
3. Fusion: Merge and deduplicate results from both methods
4. Reranking: Cross-encoder scoring for improved precision

The hybrid approach prevents terminology mismatches from missing critical
CSF subcategories while maintaining semantic understanding.

**Validates: Requirements 7.1, 7.3, 7.4, 7.5, 7.6, 7.7, 7.8, 7.9**
"""

import logging
from typing import List, Dict, Optional
import numpy as np

from retrieval.vector_store import VectorStore
from retrieval.embedding_engine import EmbeddingEngine
from retrieval.sparse_retriever import SparseRetriever
from retrieval.reranker import Reranker
from reference_builder.reference_catalog import ReferenceCatalog
from models.domain import RetrievalResult


logger = logging.getLogger(__name__)


class HybridRetriever:
    """Hybrid retriever combining dense and sparse search with reranking.
    
    Orchestrates the complete retrieval pipeline:
    1. Dense retrieval using vector similarity search
    2. Sparse retrieval using BM25 keyword matching
    3. Result fusion with deduplication
    4. Cross-encoder reranking for precision
    
    Attributes:
        vector_store: Vector store for dense retrieval
        embedding_engine: Embedding engine for query vectorization
        sparse_retriever: BM25-based sparse retriever
        reranker: Cross-encoder reranker
        catalog: Reference catalog of CSF subcategories
    """
    
    def __init__(
        self,
        vector_store: VectorStore,
        embedding_engine: EmbeddingEngine,
        catalog: ReferenceCatalog,
        reranker: Optional[Reranker] = None
    ):
        """Initialize hybrid retriever with required components.
        
        Args:
            vector_store: Initialized vector store with reference catalog collection
            embedding_engine: Embedding engine for query vectorization
            catalog: Reference catalog for metadata lookup
            reranker: Optional cross-encoder reranker (if None, skips reranking)
        """
        self.vector_store = vector_store
        self.embedding_engine = embedding_engine
        self.catalog = catalog
        self.reranker = reranker
        self.sparse_retriever = SparseRetriever()
        
        # Initialize sparse retriever with catalog
        self._initialize_sparse_retriever()
        
        logger.info("Initialized HybridRetriever")
    
    def _initialize_sparse_retriever(self) -> None:
        """Initialize sparse retriever with CSF subcategory corpus."""
        # Get all subcategories from catalog
        subcategories = self.catalog.get_all_subcategories()
        
        if not subcategories:
            logger.warning("Reference catalog is empty, sparse retrieval will not work")
            return
        
        # Build corpus from subcategory descriptions
        documents = [sub.description for sub in subcategories]
        
        # Build metadata including subcategory ID and keywords
        metadata = [
            {
                'subcategory_id': sub.subcategory_id,
                'function': sub.function,
                'category': sub.category,
                'keywords': sub.keywords,
                'description': sub.description
            }
            for sub in subcategories
        ]
        
        # Index documents
        self.sparse_retriever.index_documents(documents, metadata)
        
        logger.info(f"Initialized sparse retriever with {len(documents)} CSF subcategories")
    
    def retrieve(
        self,
        query_text: str,
        top_k: int = 5,
        dense_weight: float = 0.5,
        sparse_weight: float = 0.5
    ) -> List[RetrievalResult]:
        """Retrieve most relevant CSF subcategories using hybrid search.
        
        Combines dense vector similarity and sparse keyword matching,
        merges and deduplicates results, then applies cross-encoder reranking.
        
        Args:
            query_text: Policy text chunk to match against CSF subcategories
            top_k: Number of final results to return after reranking
            dense_weight: Weight for dense retrieval scores (0.0 to 1.0)
            sparse_weight: Weight for sparse retrieval scores (0.0 to 1.0)
            
        Returns:
            List of RetrievalResult objects with subcategory info and scores
            
        Raises:
            ValueError: If query is empty or weights are invalid
        """
        if not query_text or not query_text.strip():
            raise ValueError("Query text cannot be empty")
        
        if dense_weight < 0 or sparse_weight < 0:
            raise ValueError("Weights must be non-negative")
        
        if dense_weight + sparse_weight == 0:
            raise ValueError("At least one weight must be positive")
        
        # Normalize weights
        total_weight = dense_weight + sparse_weight
        dense_weight = dense_weight / total_weight
        sparse_weight = sparse_weight / total_weight
        
        # Retrieve from both methods
        dense_results = self.dense_retrieve(query_text, top_k=top_k)
        sparse_results = self.sparse_retrieve(query_text, top_k=top_k)
        
        # Merge and deduplicate results
        merged_results = self._merge_results(
            dense_results,
            sparse_results,
            dense_weight,
            sparse_weight
        )
        
        # Apply reranking if available
        if self.reranker is not None and merged_results:
            reranked_results = self._rerank_results(query_text, merged_results, top_k)
        else:
            # Sort by combined score and take top-k
            merged_results.sort(key=lambda x: x['score'], reverse=True)
            reranked_results = merged_results[:top_k]
        
        # Convert to RetrievalResult objects
        final_results = self._format_results(reranked_results, query_text)
        
        logger.info(f"Retrieved {len(final_results)} results for query")
        
        return final_results
    
    def dense_retrieve(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Perform dense vector similarity search.
        
        Args:
            query_text: Query text to embed and search
            top_k: Number of results to retrieve
            
        Returns:
            List of search results from vector store
        """
        # Generate query embedding
        query_embedding = self.embedding_engine.embed_text(query_text)
        
        # Search vector store
        results = self.vector_store.similarity_search(
            query_embedding=query_embedding,
            collection_name="catalog",
            top_k=top_k
        )
        
        # Normalize scores (convert distance to similarity)
        # ChromaDB returns cosine distance, convert to similarity: 1 - distance
        for result in results:
            result['score'] = 1.0 - result['distance']
            result['method'] = 'dense'
        
        logger.debug(f"Dense retrieval returned {len(results)} results")
        
        return results
    
    def sparse_retrieve(self, query_text: str, top_k: int = 5) -> List[Dict]:
        """Perform sparse BM25 keyword matching.
        
        Args:
            query_text: Query text for keyword matching
            top_k: Number of results to retrieve
            
        Returns:
            List of BM25 search results
        """
        if not self.sparse_retriever.is_indexed():
            logger.warning("Sparse retriever not indexed, returning empty results")
            return []
        
        results = self.sparse_retriever.retrieve(query_text, top_k=top_k)
        
        # Normalize BM25 scores to 0-1 range
        if results:
            max_score = max(r['score'] for r in results)
            if max_score > 0:
                for result in results:
                    result['score'] = result['score'] / max_score
        
        # Add method tag
        for result in results:
            result['method'] = 'sparse'
        
        logger.debug(f"Sparse retrieval returned {len(results)} results")
        
        return results
    
    def _merge_results(
        self,
        dense_results: List[Dict],
        sparse_results: List[Dict],
        dense_weight: float,
        sparse_weight: float
    ) -> List[Dict]:
        """Merge and deduplicate results from dense and sparse retrieval.
        
        Args:
            dense_results: Results from dense retrieval
            sparse_results: Results from sparse retrieval
            dense_weight: Weight for dense scores
            sparse_weight: Weight for sparse scores
            
        Returns:
            Merged and deduplicated results with combined scores
        """
        # Build map of subcategory_id -> result
        merged_map: Dict[str, Dict] = {}
        
        # Add dense results
        for result in dense_results:
            subcategory_id = result['metadata'].get('subcategory_id')
            if subcategory_id:
                merged_map[subcategory_id] = {
                    'subcategory_id': subcategory_id,
                    'document': result.get('document', ''),
                    'metadata': result['metadata'],
                    'dense_score': result['score'] * dense_weight,
                    'sparse_score': 0.0,
                    'methods': ['dense']
                }
        
        # Add sparse results (merge if duplicate)
        for result in sparse_results:
            subcategory_id = result['metadata'].get('subcategory_id')
            if subcategory_id:
                if subcategory_id in merged_map:
                    # Merge with existing result
                    merged_map[subcategory_id]['sparse_score'] = result['score'] * sparse_weight
                    merged_map[subcategory_id]['methods'].append('sparse')
                else:
                    # Add new result
                    merged_map[subcategory_id] = {
                        'subcategory_id': subcategory_id,
                        'document': result.get('document', ''),
                        'metadata': result['metadata'],
                        'dense_score': 0.0,
                        'sparse_score': result['score'] * sparse_weight,
                        'methods': ['sparse']
                    }
        
        # Calculate combined scores
        merged_results = []
        for subcategory_id, result in merged_map.items():
            combined_score = result['dense_score'] + result['sparse_score']
            method = 'hybrid' if len(result['methods']) > 1 else result['methods'][0]
            
            merged_results.append({
                'subcategory_id': subcategory_id,
                'document': result['document'],
                'metadata': result['metadata'],
                'score': combined_score,
                'method': method
            })
        
        logger.debug(
            f"Merged {len(dense_results)} dense + {len(sparse_results)} sparse "
            f"into {len(merged_results)} unique results"
        )
        
        return merged_results
    
    def _rerank_results(
        self,
        query: str,
        candidates: List[Dict],
        top_k: int
    ) -> List[Dict]:
        """Apply cross-encoder reranking to merged results.
        
        Args:
            query: Query text
            candidates: Merged candidate results
            top_k: Number of results to return
            
        Returns:
            Reranked results sorted by cross-encoder scores
        """
        if not candidates:
            return []
        
        # Extract documents and metadata
        documents = [c['document'] for c in candidates]
        metadata_list = [c['metadata'] for c in candidates]
        
        # Rerank using cross-encoder
        reranked = self.reranker.rerank(
            query=query,
            documents=documents,
            metadata=metadata_list,
            top_k=top_k
        )
        
        # Preserve method information from candidates
        for reranked_result in reranked:
            subcategory_id = reranked_result['metadata'].get('subcategory_id')
            # Find original candidate to get method
            for candidate in candidates:
                if candidate['subcategory_id'] == subcategory_id:
                    reranked_result['method'] = candidate['method']
                    break
        
        logger.debug(f"Reranked {len(candidates)} candidates to top {len(reranked)}")
        
        return reranked
    
    def _format_results(
        self,
        results: List[Dict],
        query_text: str
    ) -> List[RetrievalResult]:
        """Format results into RetrievalResult objects.
        
        Args:
            results: Reranked results
            query_text: Original query text for evidence extraction
            
        Returns:
            List of RetrievalResult objects
        """
        formatted_results = []
        
        for result in results:
            subcategory_id = result['metadata'].get('subcategory_id', '')
            
            # Get full subcategory from catalog
            subcategory = self.catalog.get_subcategory(subcategory_id)
            
            if subcategory:
                subcategory_text = subcategory.description
            else:
                subcategory_text = result.get('document', '')
            
            # Extract evidence spans (for now, use the document text)
            # In a more sophisticated implementation, this would extract
            # specific matching spans from the query text
            evidence_spans = [result.get('document', '')]
            
            formatted_results.append(
                RetrievalResult(
                    subcategory_id=subcategory_id,
                    subcategory_text=subcategory_text,
                    relevance_score=result['score'],
                    evidence_spans=evidence_spans,
                    retrieval_method=result.get('method', 'hybrid')
                )
            )
        
        return formatted_results
