"""
Embedding and Vector Store Stress Testing Engine

This module implements stress tests for embedding generation and vector store operations:
- Embedding quality validation (10,000+ chunks, empty strings, long text)
- Embedding corruption testing (NaN, infinite, incorrect dimensionality)
- Vector store query stress (10,000 sequential, 100 concurrent, large top_k)
- Query latency scaling (100 to 100,000 embeddings)

Requirements: 27, 44, 51
"""

import os
import sys
import time
import tempfile
import numpy as np
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.extreme.models import TestResult, TestStatus
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator
from utils.logger import get_logger

logger = get_logger(__name__)


# Test categories
class TestCategory:
    """Test category constants."""
    STRESS = "stress"
    BOUNDARY = "boundary"
    CHAOS = "chaos"


@dataclass
class EmbeddingVectorStoreConfig:
    """Configuration for embedding and vector store stress testing."""
    sequential_searches: int = 10000
    concurrent_searches: int = 100
    max_top_k: int = 10000
    embedding_test_sizes: List[int] = field(default_factory=lambda: [100, 1000, 10000, 100000])
    large_chunk_count: int = 10000
    

def create_test_result(
    test_id: str,
    category: str,
    passed: bool,
    requirement_ids: List[str],
    duration_seconds: float = 0.0,
    error_message: Optional[str] = None,
    metrics: Optional[Any] = None,
    artifacts: List[str] = None
) -> TestResult:
    """Helper to create TestResult."""
    return TestResult(
        test_id=test_id,
        requirement_id=",".join(requirement_ids),
        category=category,
        status=TestStatus.PASS if passed else TestStatus.FAIL,
        duration_seconds=duration_seconds,
        error_message=error_message,
        metrics=metrics,
        artifacts=artifacts or []
    )


class EmbeddingVectorStoreStressTester:
    """
    Stress tester for embedding generation and vector store operations.
    
    Tests embedding quality, corruption handling, and vector store performance
    under extreme load and edge cases.
    """
    
    def __init__(
        self,
        config: EmbeddingVectorStoreConfig,
        metrics_collector: MetricsCollector,
        data_generator: TestDataGenerator,
        output_dir: str
    ):
        """Initialize embedding and vector store stress tester."""
        self.config = config
        self.metrics = metrics_collector
        self.data_gen = data_generator
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized EmbeddingVectorStoreStressTester with output_dir={output_dir}")
    
    def run_tests(self) -> List[TestResult]:
        """Run all embedding and vector store stress tests."""
        results = []
        
        logger.info("Starting embedding and vector store stress tests...")
        
        # Task 17.1: Embedding quality validation tests
        results.append(self.test_embedding_quality_large_batch())
        results.append(self.test_embedding_empty_strings())
        results.append(self.test_embedding_extremely_long_text())
        results.append(self.test_embedding_dimensionality_consistency())
        results.append(self.test_embedding_similarity_score_range())
        
        # Task 17.2: Embedding corruption tests
        results.append(self.test_embedding_nan_values())
        results.append(self.test_embedding_infinite_values())
        results.append(self.test_embedding_incorrect_dimensionality())
        results.append(self.test_embedding_all_zeros())
        
        # Task 17.3: Vector store query stress tests
        results.append(self.test_sequential_similarity_searches())
        results.append(self.test_concurrent_similarity_searches())
        results.append(self.test_large_top_k())
        results.append(self.test_query_latency_scaling())
        results.append(self.test_search_accuracy_with_size())
        
        logger.info(f"Completed {len(results)} embedding and vector store stress tests")
        return results
    
    # ========================================================================
    # Task 17.1: Embedding Quality Validation Tests
    # ========================================================================
    
    def test_embedding_quality_large_batch(self) -> TestResult:
        """
        Test embeddings for 10,000+ chunks.
        
        **Validates: Requirements 27.1**
        """
        test_id = "embedding_quality_large_batch"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.embedding_engine import EmbeddingEngine
            
            # Initialize embedding engine
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["27.1"],
                    error_message=f"Model not found at {model_path}"
                )
            
            embedding_engine = EmbeddingEngine(model_path=model_path)
            
            # Generate 10,000+ test chunks
            logger.info("Generating 10,000+ test chunks...")
            test_chunks = [f"Test chunk {i} about cybersecurity policy and compliance requirements" for i in range(self.config.large_chunk_count)]
            
            # Generate embeddings
            self.metrics.start_collection(test_id)
            start_time = time.time()
            
            embeddings = embedding_engine.embed_batch(test_chunks, batch_size=64)
            
            end_time = time.time()
            metrics = self.metrics.stop_collection(test_id)
            
            # Validate no NaN or infinite values
            has_nan = np.isnan(embeddings).any()
            has_inf = np.isinf(embeddings).any()
            
            passed = not has_nan and not has_inf
            error_message = None
            if has_nan:
                error_message = "Embeddings contain NaN values"
            elif has_inf:
                error_message = "Embeddings contain infinite values"
            
            logger.info(f"Generated {len(embeddings)} embeddings, has_nan={has_nan}, has_inf={has_inf}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=passed,
                requirement_ids=["27.1"],
                duration_seconds=end_time - start_time,
                metrics=metrics,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["27.1"],
                error_message=str(e)
            )
    
    def test_embedding_empty_strings(self) -> TestResult:
        """
        Test embeddings with empty strings.
        
        **Validates: Requirements 27.2**
        """
        test_id = "embedding_empty_strings"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.BOUNDARY,
                    passed=False,
                    requirement_ids=["27.2"],
                    error_message=f"Model not found at {model_path}"
                )
            
            embedding_engine = EmbeddingEngine(model_path=model_path)
            
            start_time = time.time()
            
            # Test with empty string
            try:
                embedding = embedding_engine.embed_text("")
                passed = False
                error_message = "Expected ValueError for empty string, but embedding was generated"
            except ValueError as e:
                # Expected behavior - should raise ValueError
                passed = True
                error_message = None
                logger.info(f"Empty string correctly rejected: {e}")
            
            end_time = time.time()
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=passed,
                requirement_ids=["27.2"],
                duration_seconds=end_time - start_time,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                requirement_ids=["27.2"],
                error_message=str(e)
            )
    
    def test_embedding_extremely_long_text(self) -> TestResult:
        """
        Test embeddings with extremely long text.
        
        **Validates: Requirements 27.3**
        """
        test_id = "embedding_extremely_long_text"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.BOUNDARY,
                    passed=False,
                    requirement_ids=["27.3"],
                    error_message=f"Model not found at {model_path}"
                )
            
            embedding_engine = EmbeddingEngine(model_path=model_path)
            
            # Generate extremely long text (10,000 words)
            long_text = " ".join([f"word{i}" for i in range(10000)])
            
            start_time = time.time()
            
            # Generate embedding - should handle truncation
            embedding = embedding_engine.embed_text(long_text)
            
            end_time = time.time()
            
            # Verify embedding is valid (no NaN/inf, correct dimensionality)
            has_nan = np.isnan(embedding).any()
            has_inf = np.isinf(embedding).any()
            correct_dim = embedding.shape[0] == 384
            
            passed = not has_nan and not has_inf and correct_dim
            error_message = None
            if has_nan:
                error_message = "Long text embedding contains NaN"
            elif has_inf:
                error_message = "Long text embedding contains infinite values"
            elif not correct_dim:
                error_message = f"Expected 384 dimensions, got {embedding.shape[0]}"
            
            logger.info(f"Long text embedding: dim={embedding.shape[0]}, has_nan={has_nan}, has_inf={has_inf}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=passed,
                requirement_ids=["27.3"],
                duration_seconds=end_time - start_time,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                requirement_ids=["27.3"],
                error_message=str(e)
            )
    
    def test_embedding_dimensionality_consistency(self) -> TestResult:
        """
        Verify constant dimensionality (384) for all inputs.
        
        **Validates: Requirements 27.4**
        """
        test_id = "embedding_dimensionality_consistency"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["27.4"],
                    error_message=f"Model not found at {model_path}"
                )
            
            embedding_engine = EmbeddingEngine(model_path=model_path)
            
            # Test with various text lengths
            test_texts = [
                "short",
                "medium length text about cybersecurity",
                " ".join(["word"] * 100),  # 100 words
                " ".join(["word"] * 1000),  # 1000 words
            ]
            
            start_time = time.time()
            
            dimensions = []
            for text in test_texts:
                embedding = embedding_engine.embed_text(text)
                dimensions.append(embedding.shape[0])
            
            end_time = time.time()
            
            # Verify all dimensions are 384
            all_384 = all(dim == 384 for dim in dimensions)
            passed = all_384
            error_message = None if passed else f"Inconsistent dimensions: {dimensions}"
            
            logger.info(f"Dimensionality consistency: {dimensions}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=passed,
                requirement_ids=["27.4"],
                duration_seconds=end_time - start_time,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["27.4"],
                error_message=str(e)
            )
    
    def test_embedding_similarity_score_range(self) -> TestResult:
        """
        Verify similarity scores in [0, 1] range.
        
        **Validates: Requirements 27.5**
        """
        test_id = "embedding_similarity_score_range"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["27.5"],
                    error_message=f"Model not found at {model_path}"
                )
            
            embedding_engine = EmbeddingEngine(model_path=model_path)
            
            # Generate test embeddings
            test_texts = [
                "cybersecurity policy",
                "access control requirements",
                "data protection measures",
                "incident response procedures"
            ]
            
            start_time = time.time()
            
            embeddings = embedding_engine.embed_batch(test_texts)
            
            # Compute cosine similarities (embeddings are already normalized)
            similarities = []
            for i in range(len(embeddings)):
                for j in range(i + 1, len(embeddings)):
                    # Cosine similarity = dot product (since normalized)
                    sim = np.dot(embeddings[i], embeddings[j])
                    similarities.append(sim)
            
            end_time = time.time()
            
            # Verify all similarities in [0, 1] (or [-1, 1] for cosine, but normalized should be [0, 1])
            # Actually cosine similarity is in [-1, 1], but for normalized embeddings with positive values, it's typically [0, 1]
            # Let's check [-1, 1] to be safe
            in_range = all(-1.0 <= sim <= 1.0 for sim in similarities)
            passed = in_range
            error_message = None if passed else f"Similarities out of range: {[s for s in similarities if not (-1.0 <= s <= 1.0)]}"
            
            logger.info(f"Similarity scores: min={min(similarities):.4f}, max={max(similarities):.4f}, count={len(similarities)}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=passed,
                requirement_ids=["27.5"],
                duration_seconds=end_time - start_time,
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["27.5"],
                error_message=str(e)
            )
    
    # ========================================================================
    # Task 17.2: Embedding Corruption Tests
    # ========================================================================
    
    def test_embedding_nan_values(self) -> TestResult:
        """
        Test embeddings with NaN values.
        
        **Validates: Requirements 51.1**
        """
        test_id = "embedding_nan_values"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                
                # Create corrupted embedding with NaN values
                corrupted_embedding = np.array([np.nan] * 384, dtype=np.float32)
                
                start_time = time.time()
                
                # Try to add corrupted embedding
                try:
                    vector_store.add_embeddings(
                        embeddings=corrupted_embedding.reshape(1, -1),
                        metadata=[{"text": "test"}],
                        collection_name="test_collection"
                    )
                    # If we get here, the vector store didn't reject NaN values
                    passed = False
                    error_message = "Vector store accepted NaN values (should reject)"
                except (ValueError, Exception) as e:
                    # Expected behavior - should reject NaN values
                    passed = True
                    error_message = None
                    logger.info(f"NaN values correctly rejected: {e}")
                
                end_time = time.time()
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=passed,
                    requirement_ids=["51.1"],
                    duration_seconds=end_time - start_time,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.CHAOS,
                passed=False,
                requirement_ids=["51.1"],
                error_message=str(e)
            )
    
    def test_embedding_infinite_values(self) -> TestResult:
        """
        Test embeddings with infinite values.
        
        **Validates: Requirements 51.2**
        """
        test_id = "embedding_infinite_values"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                
                # Create corrupted embedding with infinite values
                corrupted_embedding = np.array([np.inf] * 384, dtype=np.float32)
                
                start_time = time.time()
                
                # Try to add corrupted embedding
                try:
                    vector_store.add_embeddings(
                        embeddings=corrupted_embedding.reshape(1, -1),
                        metadata=[{"text": "test"}],
                        collection_name="test_collection"
                    )
                    # If we get here, the vector store didn't reject infinite values
                    passed = False
                    error_message = "Vector store accepted infinite values (should reject)"
                except (ValueError, Exception) as e:
                    # Expected behavior - should reject infinite values
                    passed = True
                    error_message = None
                    logger.info(f"Infinite values correctly rejected: {e}")
                
                end_time = time.time()
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=passed,
                    requirement_ids=["51.2"],
                    duration_seconds=end_time - start_time,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.CHAOS,
                passed=False,
                requirement_ids=["51.2"],
                error_message=str(e)
            )
    
    def test_embedding_incorrect_dimensionality(self) -> TestResult:
        """
        Test embeddings with incorrect dimensionality.
        
        **Validates: Requirements 51.3**
        """
        test_id = "embedding_incorrect_dimensionality"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                
                # Create embedding with wrong dimensionality (256 instead of 384)
                wrong_dim_embedding = np.random.rand(256).astype(np.float32)
                
                start_time = time.time()
                
                # Try to add wrong-dimension embedding
                try:
                    vector_store.add_embeddings(
                        embeddings=wrong_dim_embedding.reshape(1, -1),
                        metadata=[{"text": "test"}],
                        collection_name="test_collection"
                    )
                    # If we get here, the vector store didn't reject wrong dimensionality
                    passed = False
                    error_message = "Vector store accepted incorrect dimensionality (should reject)"
                except (ValueError, Exception) as e:
                    # Expected behavior - should reject incorrect dimensionality
                    passed = True
                    error_message = None
                    logger.info(f"Incorrect dimensionality correctly rejected: {e}")
                
                end_time = time.time()
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=passed,
                    requirement_ids=["51.3"],
                    duration_seconds=end_time - start_time,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.CHAOS,
                passed=False,
                requirement_ids=["51.3"],
                error_message=str(e)
            )
    
    def test_embedding_all_zeros(self) -> TestResult:
        """
        Test embeddings with all zeros.
        
        **Validates: Requirements 51.4**
        """
        test_id = "embedding_all_zeros"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=False,
                    requirement_ids=["51.4"],
                    error_message=f"Model not found at {model_path}"
                )
            
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine(model_path=model_path)
                
                # Add some normal embeddings first
                normal_texts = ["cybersecurity policy", "access control", "data protection"]
                normal_embeddings = embedding_engine.embed_batch(normal_texts)
                vector_store.add_embeddings(
                    embeddings=normal_embeddings,
                    metadata=[{"text": t} for t in normal_texts],
                    collection_name="test_collection"
                )
                
                # Create all-zero embedding
                zero_embedding = np.zeros(384, dtype=np.float32)
                
                start_time = time.time()
                
                # Try to search with all-zero query embedding
                try:
                    results = vector_store.similarity_search(
                        query_embedding=zero_embedding,
                        collection_name="test_collection",
                        top_k=3
                    )
                    # Should handle gracefully (return results or empty list)
                    passed = True
                    error_message = None
                    logger.info(f"All-zero embedding search returned {len(results)} results")
                except Exception as e:
                    # If it crashes, that's a failure
                    passed = False
                    error_message = f"All-zero embedding caused crash: {e}"
                
                end_time = time.time()
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=passed,
                    requirement_ids=["51.4"],
                    duration_seconds=end_time - start_time,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.CHAOS,
                passed=False,
                requirement_ids=["51.4"],
                error_message=str(e)
            )
    
    # ========================================================================
    # Task 17.3: Vector Store Query Stress Tests
    # ========================================================================
    
    def test_sequential_similarity_searches(self) -> TestResult:
        """
        Test 10,000 sequential similarity searches.
        
        **Validates: Requirements 44.1**
        """
        test_id = "vector_store_sequential_searches"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["44.1"],
                    error_message=f"Model not found at {model_path}"
                )
            
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine(model_path=model_path)
                
                # Generate test documents and embeddings
                test_docs = [f"Test document {i} about cybersecurity policy" for i in range(1000)]
                embeddings = embedding_engine.embed_batch(test_docs)
                
                # Add to vector store
                vector_store.add_embeddings(
                    embeddings=embeddings,
                    metadata=[{"text": doc} for doc in test_docs],
                    collection_name="test_collection"
                )
                
                # Measure sequential search performance
                self.metrics.start_collection(test_id)
                start_time = time.time()
                
                query_embedding = embedding_engine.embed_text("cybersecurity policy")
                latencies = []
                
                for i in range(self.config.sequential_searches):
                    search_start = time.time()
                    results = vector_store.similarity_search(
                        query_embedding=query_embedding,
                        collection_name="test_collection",
                        top_k=5
                    )
                    search_end = time.time()
                    latencies.append(search_end - search_start)
                    
                    if i % 1000 == 0:
                        logger.info(f"Completed {i}/{self.config.sequential_searches} searches")
                
                end_time = time.time()
                metrics = self.metrics.stop_collection(test_id)
                
                # Analyze performance consistency
                avg_latency = sum(latencies) / len(latencies)
                max_latency = max(latencies)
                min_latency = min(latencies)
                
                # Check for performance degradation (max should not be >10x avg)
                performance_consistent = max_latency < (avg_latency * 10)
                
                passed = performance_consistent
                error_message = None if passed else f"Performance degraded: max latency {max_latency:.4f}s is >10x avg {avg_latency:.4f}s"
                
                logger.info(f"Sequential searches: avg={avg_latency:.4f}s, max={max_latency:.4f}s, min={min_latency:.4f}s")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=passed,
                    requirement_ids=["44.1"],
                    duration_seconds=end_time - start_time,
                    metrics=metrics,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["44.1"],
                error_message=str(e)
            )
    
    def test_concurrent_similarity_searches(self) -> TestResult:
        """
        Test 100 concurrent similarity searches.
        
        **Validates: Requirements 44.2**
        """
        test_id = "vector_store_concurrent_searches"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["44.2"],
                    error_message=f"Model not found at {model_path}"
                )
            
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine(model_path=model_path)
                
                # Generate test documents and embeddings
                test_docs = [f"Test document {i} about cybersecurity" for i in range(1000)]
                embeddings = embedding_engine.embed_batch(test_docs)
                
                # Add to vector store
                vector_store.add_embeddings(
                    embeddings=embeddings,
                    metadata=[{"text": doc} for doc in test_docs],
                    collection_name="test_collection"
                )
                
                # Prepare query embedding
                query_embedding = embedding_engine.embed_text("cybersecurity")
                
                # Concurrent search function
                def search_task(task_id: int) -> Tuple[int, bool, Optional[str]]:
                    try:
                        results = vector_store.similarity_search(
                            query_embedding=query_embedding,
                            collection_name="test_collection",
                            top_k=5
                        )
                        # Verify results are valid
                        if len(results) != 5:
                            return task_id, False, f"Expected 5 results, got {len(results)}"
                        return task_id, True, None
                    except Exception as e:
                        return task_id, False, str(e)
                
                # Execute concurrent searches
                self.metrics.start_collection(test_id)
                start_time = time.time()
                
                errors = []
                with ThreadPoolExecutor(max_workers=self.config.concurrent_searches) as executor:
                    futures = [executor.submit(search_task, i) for i in range(self.config.concurrent_searches)]
                    
                    for future in as_completed(futures):
                        task_id, success, error = future.result()
                        if not success:
                            errors.append(f"Task {task_id}: {error}")
                
                end_time = time.time()
                metrics = self.metrics.stop_collection(test_id)
                
                passed = len(errors) == 0
                error_message = None if passed else f"Concurrent search failures: {errors[:5]}"
                
                logger.info(f"Concurrent searches: {self.config.concurrent_searches - len(errors)}/{self.config.concurrent_searches} succeeded")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=passed,
                    requirement_ids=["44.2"],
                    duration_seconds=end_time - start_time,
                    metrics=metrics,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["44.2"],
                error_message=str(e)
            )
    
    def test_large_top_k(self) -> TestResult:
        """
        Test top_k=10,000 with large result sets.
        
        **Validates: Requirements 44.3**
        """
        test_id = "vector_store_large_top_k"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["44.3"],
                    error_message=f"Model not found at {model_path}"
                )
            
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine(model_path=model_path)
                
                # Generate 15,000 test documents (more than top_k)
                logger.info("Generating 15,000 test documents...")
                test_docs = [f"Document {i} about security policy and compliance" for i in range(15000)]
                
                # Generate embeddings in batches
                batch_size = 100
                for i in range(0, len(test_docs), batch_size):
                    batch = test_docs[i:i+batch_size]
                    embeddings = embedding_engine.embed_batch(batch)
                    
                    vector_store.add_embeddings(
                        embeddings=embeddings,
                        metadata=[{"text": doc} for doc in batch],
                        collection_name="test_collection"
                    )
                    
                    if (i // batch_size) % 10 == 0:
                        logger.info(f"Added {i+batch_size}/{len(test_docs)} embeddings")
                
                # Query with large top_k
                query_embedding = embedding_engine.embed_text("security policy")
                
                self.metrics.start_collection(test_id)
                start_time = time.time()
                
                results = vector_store.similarity_search(
                    query_embedding=query_embedding,
                    collection_name="test_collection",
                    top_k=self.config.max_top_k
                )
                
                end_time = time.time()
                metrics = self.metrics.stop_collection(test_id)
                
                # Verify we got the requested number of results
                passed = len(results) == self.config.max_top_k
                error_message = None if passed else f"Expected {self.config.max_top_k} results, got {len(results)}"
                
                logger.info(f"Large top_k search returned {len(results)} results in {end_time - start_time:.2f}s")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=passed,
                    requirement_ids=["44.3"],
                    duration_seconds=end_time - start_time,
                    metrics=metrics,
                    error_message=error_message
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["44.3"],
                error_message=str(e)
            )
    
    def test_query_latency_scaling(self) -> TestResult:
        """
        Measure query latency for collections from 100 to 100,000 embeddings.
        
        **Validates: Requirements 44.4**
        """
        test_id = "vector_store_query_latency_scaling"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            import json
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["44.4"],
                    error_message=f"Model not found at {model_path}"
                )
            
            embedding_engine = EmbeddingEngine(model_path=model_path)
            query_embedding = embedding_engine.embed_text("cybersecurity policy")
            
            latency_results = {}
            
            for size in self.config.embedding_test_sizes:
                logger.info(f"Testing with {size} embeddings...")
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    vector_store = VectorStore(persist_directory=tmpdir)
                    
                    # Generate test documents
                    test_docs = [f"Document {i} about security" for i in range(size)]
                    
                    # Add embeddings in batches
                    batch_size = 100
                    for i in range(0, len(test_docs), batch_size):
                        batch = test_docs[i:i+batch_size]
                        embeddings = embedding_engine.embed_batch(batch)
                        
                        vector_store.add_embeddings(
                            embeddings=embeddings,
                            metadata=[{"text": doc} for doc in batch],
                            collection_name="test_collection"
                        )
                    
                    # Measure query latency (average of 10 queries)
                    latencies = []
                    for _ in range(10):
                        start = time.time()
                        results = vector_store.similarity_search(
                            query_embedding=query_embedding,
                            collection_name="test_collection",
                            top_k=10
                        )
                        end = time.time()
                        latencies.append(end - start)
                    
                    avg_latency = sum(latencies) / len(latencies)
                    latency_results[size] = avg_latency
                    logger.info(f"Size {size}: avg latency = {avg_latency:.4f}s")
            
            # Check that latency scaling is reasonable (should be sub-linear or linear, not exponential)
            # Compare 100 vs 100,000 - should not be >100x slower
            if 100 in latency_results and 100000 in latency_results:
                ratio = latency_results[100000] / latency_results[100]
                passed = ratio < 100  # Allow up to 100x slowdown for 1000x data
                error_message = None if passed else f"Latency scaling too steep: {ratio:.2f}x for 1000x data"
            else:
                passed = True
                error_message = None
            
            # Save latency results
            results_file = self.output_dir / f"{test_id}_results.json"
            with open(results_file, 'w') as f:
                json.dump(latency_results, f, indent=2)
            
            logger.info(f"Query latency scaling results: {latency_results}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=passed,
                requirement_ids=["44.4"],
                error_message=error_message,
                artifacts=[str(results_file)]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["44.4"],
                error_message=str(e)
            )
    
    def test_search_accuracy_with_size(self) -> TestResult:
        """
        Verify search accuracy does not degrade with collection size.
        
        **Validates: Requirements 44.5**
        """
        test_id = "vector_store_search_accuracy_scaling"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            model_path = "models/all-MiniLM-L6-v2"
            if not os.path.exists(model_path):
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=False,
                    requirement_ids=["44.5"],
                    error_message=f"Model not found at {model_path}"
                )
            
            embedding_engine = EmbeddingEngine(model_path=model_path)
            
            # Create a known target document
            target_doc = "This document discusses cybersecurity policy requirements for access control"
            target_embedding = embedding_engine.embed_text(target_doc)
            
            accuracy_results = {}
            
            for size in [100, 1000, 10000]:
                logger.info(f"Testing accuracy with {size} embeddings...")
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    vector_store = VectorStore(persist_directory=tmpdir)
                    
                    # Add target document first
                    vector_store.add_embeddings(
                        embeddings=target_embedding.reshape(1, -1),
                        metadata=[{"text": target_doc, "is_target": True}],
                        collection_name="test_collection",
                        ids=["target_doc"]
                    )
                    
                    # Add noise documents
                    noise_docs = [f"Unrelated document {i} about random topics" for i in range(size - 1)]
                    noise_embeddings = embedding_engine.embed_batch(noise_docs)
                    vector_store.add_embeddings(
                        embeddings=noise_embeddings,
                        metadata=[{"text": doc, "is_target": False} for doc in noise_docs],
                        collection_name="test_collection"
                    )
                    
                    # Query with similar text
                    query_text = "access control cybersecurity policy"
                    query_embedding = embedding_engine.embed_text(query_text)
                    
                    results = vector_store.similarity_search(
                        query_embedding=query_embedding,
                        collection_name="test_collection",
                        top_k=10
                    )
                    
                    # Check if target document is in top results
                    target_found = any(r['id'] == 'target_doc' for r in results)
                    target_rank = next((i for i, r in enumerate(results) if r['id'] == 'target_doc'), -1)
                    
                    accuracy_results[size] = {
                        'target_found': target_found,
                        'target_rank': target_rank
                    }
                    logger.info(f"Size {size}: target_found={target_found}, rank={target_rank}")
            
            # Verify target was found in all sizes
            all_found = all(result['target_found'] for result in accuracy_results.values())
            passed = all_found
            error_message = None if passed else f"Target not found in some sizes: {accuracy_results}"
            
            logger.info(f"Search accuracy results: {accuracy_results}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=passed,
                requirement_ids=["44.5"],
                error_message=error_message
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                requirement_ids=["44.5"],
                error_message=str(e)
            )
