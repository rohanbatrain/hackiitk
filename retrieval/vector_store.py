"""
Vector Store component for embedding persistence and similarity search.

This module provides local vector storage using ChromaDB for semantic search
operations. It supports separate collections for reference catalog and policy
embeddings, with full persistence to disk for offline operation.
"""

import os
import logging
from typing import List, Dict, Optional, Any
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except (ImportError, Exception) as e:
    CHROMADB_AVAILABLE = False
    CHROMADB_ERROR = str(e)


logger = logging.getLogger(__name__)


class VectorStore:
    """Local vector store for embedding persistence and similarity search.
    
    Uses ChromaDB as the backend for storing embeddings with metadata and
    performing efficient similarity search operations. Supports multiple
    collections for separating reference catalog and policy embeddings.
    
    Attributes:
        persist_directory: Directory path for persistent storage
        client: ChromaDB client instance
        collections: Dictionary of loaded collection objects
    """
    
    def __init__(self, persist_directory: str = "./vector_store"):
        """Initialize vector store with local persistence.
        
        Args:
            persist_directory: Path to directory for storing embeddings
            
        Raises:
            RuntimeError: If ChromaDB is not available
        """
        if not CHROMADB_AVAILABLE:
            raise RuntimeError(
                f"ChromaDB is not available: {CHROMADB_ERROR}. "
                "Note: ChromaDB requires Python < 3.14 due to Pydantic v1 compatibility issues. "
                "Please use Python 3.11 or 3.12 for full functionality."
            )
        
        self.persist_directory = persist_directory
        
        # Create directory if it doesn't exist
        os.makedirs(persist_directory, exist_ok=True)
        
        # Initialize ChromaDB client with persistence
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False,  # Disable telemetry for offline operation
                allow_reset=True
            )
        )
        
        # Track loaded collections
        self.collections: Dict[str, Any] = {}
        
        logger.info(f"Initialized VectorStore with persistence at {persist_directory}")
    
    def add_embeddings(
        self,
        embeddings: np.ndarray,
        metadata: List[Dict],
        collection_name: str,
        ids: Optional[List[str]] = None
    ) -> None:
        """Store embeddings with metadata in specified collection.
        
        Args:
            embeddings: Numpy array of embeddings (shape: [n_samples, embedding_dim])
            metadata: List of metadata dictionaries for each embedding
            collection_name: Name of the collection to store in
            ids: Optional list of unique IDs for each embedding
            
        Raises:
            ValueError: If embeddings and metadata lengths don't match
        """
        if len(embeddings) != len(metadata):
            raise ValueError(
                f"Embeddings count ({len(embeddings)}) must match metadata count ({len(metadata)})"
            )
        
        # Get or create collection
        collection = self._get_or_create_collection(collection_name)
        
        # Generate IDs if not provided
        if ids is None:
            # Use chunk_id from metadata if available, otherwise generate
            ids = [
                meta.get("chunk_id", f"{collection_name}_{i}")
                for i, meta in enumerate(metadata)
            ]
        
        # Convert numpy array to list for ChromaDB
        embeddings_list = embeddings.tolist()
        
        # ChromaDB requires documents (text) for each embedding
        # Use source_text from metadata or empty string
        documents = [
            meta.get("source_text", meta.get("text", ""))
            for meta in metadata
        ]
        
        # Add to collection
        collection.add(
            embeddings=embeddings_list,
            documents=documents,
            metadatas=metadata,
            ids=ids
        )
        
        logger.info(
            f"Added {len(embeddings)} embeddings to collection '{collection_name}'"
        )
    
    def similarity_search(
        self,
        query_embedding: np.ndarray,
        collection_name: str,
        top_k: int = 5,
        filter_metadata: Optional[Dict] = None
    ) -> List[Dict]:
        """Retrieve top-k most similar embeddings from collection.
        
        Args:
            query_embedding: Query embedding vector (shape: [embedding_dim])
            collection_name: Name of collection to search
            top_k: Number of results to return
            filter_metadata: Optional metadata filters for search
            
        Returns:
            List of dictionaries containing:
                - id: Embedding ID
                - distance: Similarity distance (lower is more similar)
                - metadata: Associated metadata
                - document: Source text
                
        Raises:
            ValueError: If collection doesn't exist
        """
        if collection_name not in self.collections:
            if not self.load_collection(collection_name):
                raise ValueError(f"Collection '{collection_name}' does not exist")
        
        collection = self.collections[collection_name]
        
        # Get collection size to handle edge case where top_k > collection size
        collection_count = collection.count()
        actual_k = min(top_k, collection_count)
        
        if actual_k == 0:
            logger.warning(f"Collection '{collection_name}' is empty")
            return []
        
        # Convert numpy array to list for ChromaDB
        query_list = query_embedding.tolist()
        
        # Perform similarity search
        results = collection.query(
            query_embeddings=[query_list],
            n_results=actual_k,
            where=filter_metadata
        )
        
        # Format results
        formatted_results = []
        for i in range(len(results['ids'][0])):
            formatted_results.append({
                'id': results['ids'][0][i],
                'distance': results['distances'][0][i],
                'metadata': results['metadatas'][0][i],
                'document': results['documents'][0][i]
            })
        
        logger.debug(
            f"Retrieved {len(formatted_results)} results from collection '{collection_name}'"
        )
        
        return formatted_results
    
    def load_collection(self, collection_name: str) -> bool:
        """Load previously persisted collection from disk.
        
        Args:
            collection_name: Name of collection to load
            
        Returns:
            True if collection exists and was loaded, False otherwise
        """
        try:
            collection = self.client.get_collection(name=collection_name)
            self.collections[collection_name] = collection
            logger.info(f"Loaded collection '{collection_name}' from disk")
            return True
        except Exception as e:
            logger.debug(f"Collection '{collection_name}' not found: {e}")
            return False
    
    def persist_collection(self, collection_name: str) -> None:
        """Persist collection to disk.
        
        Note: ChromaDB PersistentClient automatically persists data,
        so this method is primarily for explicit confirmation and logging.
        
        Args:
            collection_name: Name of collection to persist
        """
        if collection_name in self.collections:
            # ChromaDB automatically persists with PersistentClient
            logger.info(f"Collection '{collection_name}' persisted to {self.persist_directory}")
        else:
            logger.warning(f"Collection '{collection_name}' not loaded, nothing to persist")
    
    def delete_collection(self, collection_name: str) -> None:
        """Delete a collection and its data.
        
        Args:
            collection_name: Name of collection to delete
        """
        try:
            self.client.delete_collection(name=collection_name)
            if collection_name in self.collections:
                del self.collections[collection_name]
            logger.info(f"Deleted collection '{collection_name}'")
        except Exception as e:
            logger.warning(f"Failed to delete collection '{collection_name}': {e}")
    
    def list_collections(self) -> List[str]:
        """List all available collections.
        
        Returns:
            List of collection names
        """
        collections = self.client.list_collections()
        return [col.name for col in collections]
    
    def get_collection_count(self, collection_name: str) -> int:
        """Get number of embeddings in a collection.
        
        Args:
            collection_name: Name of collection
            
        Returns:
            Number of embeddings in collection, or 0 if collection doesn't exist
        """
        if collection_name not in self.collections:
            if not self.load_collection(collection_name):
                return 0
        
        return self.collections[collection_name].count()
    
    def _get_or_create_collection(self, collection_name: str) -> Any:
        """Get existing collection or create new one.
        
        Args:
            collection_name: Name of collection
            
        Returns:
            ChromaDB collection object
        """
        if collection_name in self.collections:
            return self.collections[collection_name]
        
        # Try to load existing collection
        if self.load_collection(collection_name):
            return self.collections[collection_name]
        
        # Create new collection
        collection = self.client.create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"}  # Use cosine similarity
        )
        self.collections[collection_name] = collection
        logger.info(f"Created new collection '{collection_name}'")
        
        return collection
    
    def reset(self) -> None:
        """Reset the vector store by deleting all collections.
        
        Warning: This will delete all stored embeddings!
        """
        self.client.reset()
        self.collections = {}
        logger.warning("Vector store reset - all collections deleted")
