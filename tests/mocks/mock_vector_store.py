"""
Mock VectorStore for testing when ChromaDB is not available.

This provides a simple in-memory implementation for testing purposes.
"""

import numpy as np
from typing import List, Dict, Optional, Any
import logging

logger = logging.getLogger(__name__)


class MockVectorStore:
    """Simple in-memory vector store for testing."""
    
    def __init__(self, persist_directory: str = "./vector_store"):
        """Initialize mock vector store."""
        self.persist_directory = persist_directory
        self.collections: Dict[str, Dict] = {}
        logger.info(f"Initialized MockVectorStore at {persist_directory}")
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict],
        collection_name: str,
        ids: Optional[List[str]] = None
    ) -> None:
        """Store embeddings with metadata."""
        if len(embeddings) != len(metadata):
            raise ValueError(
                f"Embeddings count ({len(embeddings)}) must match metadata count ({len(metadata)})"
            )
        
        if collection_name not in self.collections:
            self.collections[collection_name] = {
                'embeddings': [],
                'metadata': [],
                'ids': [],
                'documents': []
            }
        
        if ids is None:
            ids = [
                meta.get("chunk_id", f"{collection_name}_{i}")
                for i, meta in enumerate(metadata)
            ]
        
        documents = [
            meta.get("source_text", meta.get("text", ""))
            for meta in metadata
        ]
        
        collection = self.collections[collection_name]
        collection['embeddings'].extend(embeddings)
        collection['metadata'].extend(metadata)
        collection['ids'].extend(ids)
        collection['documents'].extend(documents)
        
        logger.info(f"Added {len(embeddings)} embeddings to collection '{collection_name}'")
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        collection_name: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve top-k most similar embeddings."""
        if collection_name not in self.collections:
            raise ValueError(f"Collection '{collection_name}' does not exist")
        
        collection = self.collections[collection_name]
        if len(collection['embeddings']) == 0:
            return []
        
        # Calculate cosine similarities
        embeddings_array = np.array(collection['embeddings'])
        query_norm = query_embedding / np.linalg.norm(query_embedding)
        embeddings_norm = embeddings_array / np.linalg.norm(embeddings_array, axis=1, keepdims=True)
        similarities = np.dot(embeddings_norm, query_norm)
        
        # Convert to distances (1 - similarity for cosine)
        distances = 1 - similarities
        
        # Get top-k indices
        actual_k = min(top_k, len(distances))
        top_indices = np.argsort(distances)[:actual_k]
        
        # Format results
        results = []
        for idx in top_indices:
            results.append({
                'id': collection['ids'][idx],
                'distance': float(distances[idx]),
                'metadata': collection['metadata'][idx],
                'document': collection['documents'][idx]
            })
        
        return results
    
    def load_collection(self, collection_name: str) -> bool:
        """Load collection (no-op for in-memory store)."""
        return collection_name in self.collections
    
    def persist_collection(self, collection_name: str) -> None:
        """Persist collection (no-op for in-memory store)."""
        logger.info(f"MockVectorStore: persist_collection called for '{collection_name}'")
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection."""
        if collection_name in self.collections:
            del self.collections[collection_name]
            logger.info(f"Deleted collection '{collection_name}'")
    
    def list_collections(self) -> List[str]:
        """List all collections."""
        return list(self.collections.keys())
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get number of embeddings in collection."""
        if collection_name not in self.collections:
            return 0
        return len(self.collections[collection_name]['embeddings'])
    
    def _get_or_create_collection(self, collection_name: str) -> Dict:
        """Get or create collection."""
        if collection_name not in self.collections:
            self.collections[collection_name] = {
                'embeddings': [],
                'metadata': [],
                'ids': [],
                'documents': []
            }
        return self.collections[collection_name]
    
    def reset(self) -> None:
        """Reset the vector store."""
        self.collections = {}
        logger.warning("MockVectorStore reset - all collections deleted")
