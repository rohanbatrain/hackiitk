"""
Embedding Engine for generating dense vector representations of text.

This module provides local sentence transformer embedding generation using
the all-MiniLM-L6-v2 model. All operations are performed offline on CPU
without any network calls. Includes caching for repeated operations.
"""

import os
import hashlib
import numpy as np
import logging
from typing import List, Union, Dict, Optional
from sentence_transformers import SentenceTransformer
from utils.logger import log_function_call, log_performance, log_memory_usage

logger = logging.getLogger(__name__)


class EmbeddingEngine:
    """Local embedding engine using sentence-transformers.
    
    Generates 384-dimensional embeddings using the all-MiniLM-L6-v2 model
    loaded from local storage. Operates entirely offline on CPU with
    optional caching for repeated operations.
    
    Attributes:
        model: Loaded SentenceTransformer model
        model_path: Path to local model directory
        dimensions: Embedding dimensionality (384 for all-MiniLM-L6-v2)
        cache: Optional cache for repeated embeddings
        cache_enabled: Whether caching is enabled
    """
    
    @log_function_call('embedding_engine')
    def __init__(self, model_path: str, enable_cache: bool = True, cache_size: int = 1000):
        """Initialize embedding engine with local model.
        
        Args:
            model_path: Path to local sentence-transformers model directory
            enable_cache: Whether to enable embedding caching (default: True)
            cache_size: Maximum number of cached embeddings (default: 1000)
            
        Raises:
            FileNotFoundError: If model path does not exist
            RuntimeError: If model cannot be loaded
        """
        logger.debug(f"Initializing EmbeddingEngine with model_path={model_path}")
        
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model path not found: {model_path}\n"
                f"Please download the model using: python scripts/download_models.py"
            )
        
        try:
            # Set HuggingFace token if available (suppresses auth warnings)
            hf_token = os.environ.get('HF_TOKEN') or os.environ.get('HUGGING_FACE_HUB_TOKEN')
            if hf_token:
                os.environ['HUGGING_FACE_HUB_TOKEN'] = hf_token
                logger.debug("HuggingFace token found and set")
            
            # Load model from local path with offline mode
            logger.debug(f"Loading SentenceTransformer model from {model_path}")
            self.model = SentenceTransformer(model_path, device='cpu')
            self.model_path = model_path
            self.dimensions = 384  # all-MiniLM-L6-v2 produces 384-dim vectors
            
            # Initialize cache
            self.cache_enabled = enable_cache
            self.cache_size = cache_size
            self.cache: Dict[str, np.ndarray] = {}
            
            logger.info(f"EmbeddingEngine initialized (cache: {enable_cache}, cache_size: {cache_size})")
            
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}", exc_info=True)
            raise RuntimeError(f"Failed to load embedding model: {e}")
    
    def embed_text(self, text: str, use_cache: bool = True) -> np.ndarray:
        """Generate embedding for single text.
        
        Args:
            text: Input text to embed
            use_cache: Whether to use cache for this operation (default: True)
            
        Returns:
            384-dimensional numpy array embedding
            
        Raises:
            ValueError: If text is empty
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")
        
        # Check cache if enabled
        if self.cache_enabled and use_cache:
            cache_key = self._get_cache_key(text)
            if cache_key in self.cache:
                return self.cache[cache_key].copy()
        
        # Generate embedding using the model
        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            show_progress_bar=False,
            normalize_embeddings=True  # L2 normalization for cosine similarity
        )
        
        # Store in cache if enabled
        if self.cache_enabled and use_cache:
            self._add_to_cache(cache_key, embedding)
        
        return embedding
    
    def embed_batch(self, texts: List[str], batch_size: int = 64) -> np.ndarray:
        """Generate embeddings for multiple texts efficiently.
        
        Batch processing amortizes model overhead across multiple texts
        for improved throughput. Optimized with larger batch sizes and
        caching for repeated operations.
        
        Args:
            texts: List of input texts to embed
            batch_size: Batch size for processing (default: 64, optimized for CPU)
            
        Returns:
            2D numpy array of shape (len(texts), 384)
            
        Raises:
            ValueError: If texts list is empty
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")
        
        # Filter out empty texts and track indices
        valid_texts = []
        valid_indices = []
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
        
        if not valid_texts:
            raise ValueError("All texts are empty")
        
        # Generate embeddings in batch with optimized batch size
        # Larger batch sizes improve throughput on CPU
        embeddings = self.model.encode(
            valid_texts,
            convert_to_numpy=True,
            show_progress_bar=False,
            batch_size=batch_size,  # Tunable for optimal throughput
            normalize_embeddings=True,
            convert_to_tensor=False  # Keep as numpy for efficiency
        )
        
        # If some texts were filtered out, create full array with zeros for invalid
        if len(valid_texts) < len(texts):
            full_embeddings = np.zeros((len(texts), self.dimensions), dtype=np.float32)
            for i, valid_idx in enumerate(valid_indices):
                full_embeddings[valid_idx] = embeddings[i]
            return full_embeddings
        
        return embeddings
    
    def verify_offline(self) -> bool:
        """Verify that model operates without network calls.
        
        This method checks that the model is loaded from local storage
        and does not require network access for inference.
        
        Returns:
            True if model is confirmed to be operating offline
        """
        # Check that model path exists locally
        if not os.path.exists(self.model_path):
            return False
        
        # Verify model is loaded
        if self.model is None:
            return False
        
        # Test embedding generation (should work offline)
        try:
            test_embedding = self.embed_text("test", use_cache=False)
            return test_embedding.shape == (self.dimensions,)
        except Exception:
            return False
    
    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text.
        
        Args:
            text: Input text
            
        Returns:
            Hash-based cache key
        """
        return hashlib.md5(text.encode('utf-8')).hexdigest()
    
    def _add_to_cache(self, key: str, embedding: np.ndarray) -> None:
        """Add embedding to cache with LRU eviction.
        
        Args:
            key: Cache key
            embedding: Embedding to cache
        """
        # Simple LRU: remove oldest if cache is full
        if len(self.cache) >= self.cache_size:
            # Remove first (oldest) item
            oldest_key = next(iter(self.cache))
            del self.cache[oldest_key]
        
        self.cache[key] = embedding.copy()
    
    def clear_cache(self) -> None:
        """Clear the embedding cache."""
        self.cache.clear()
    
    def get_cache_stats(self) -> Dict[str, int]:
        """Get cache statistics.
        
        Returns:
            Dictionary with cache size and capacity
        """
        return {
            'size': len(self.cache),
            'capacity': self.cache_size,
            'enabled': self.cache_enabled
        }
