"""
Component-Specific Stress Testing Engine

This module implements stress tests for individual components of the Policy Analyzer:
- Retrieval engine (vector store queries, hybrid retrieval, reranking)
- Stage A scoring (lexical/semantic score combinations)
- Output manager (file generation)
- Audit logger (concurrent writes)
- LLM runtime (context windows, temperature)
- Embedding engine (quality validation)

Requirements: 30, 40, 41, 44, 45, 46, 47, 51, 52, 53, 54, 56
"""

import os
import sys
import time
import json
import tempfile
import threading
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
from concurrent.futures import ThreadPoolExecutor, as_completed

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.extreme.models import TestResult, TestStatus, BreakingPoint
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator
from utils.logger import get_logger

logger = get_logger(__name__)

# Test categories as strings
class TestCategory:
    """Test category constants."""
    STRESS = "stress"
    CHAOS = "chaos"
    ADVERSARIAL = "adversarial"
    BOUNDARY = "boundary"
    PERFORMANCE = "performance"
    LLM_STRESS = "llm_stress"


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
    """
    Helper to create TestResult with simplified interface.
    
    Args:
        test_id: Test identifier
        category: Test category
        passed: Whether test passed
        requirement_ids: List of requirement IDs
        duration_seconds: Test duration
        error_message: Error message if failed
        metrics: Performance metrics
        artifacts: List of artifact paths
        
    Returns:
        TestResult object
    """
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


@dataclass
class ComponentStressConfig:
    """Configuration for component stress testing."""
    sequential_searches: int = 10000
    concurrent_searches: int = 100
    max_top_k: int = 10000
    embedding_sizes: List[int] = field(default_factory=lambda: [100, 1000, 10000, 100000])
    output_file_count: int = 1000
    audit_log_entries: int = 10000
    concurrent_audit_writes: int = 100
    
    def __post_init__(self):
        """Validate configuration."""
        if self.sequential_searches < 1:
            raise ValueError("sequential_searches must be >= 1")
        if self.concurrent_searches < 1:
            raise ValueError("concurrent_searches must be >= 1")


class ComponentStressTester:
    """
    Component-specific stress tester for individual system components.
    
    Tests retrieval engine, scoring logic, output generation, audit logging,
    and other components under extreme load and edge cases.
    """
    
    def __init__(
        self,
        config: ComponentStressConfig,
        metrics_collector: MetricsCollector,
        data_generator: TestDataGenerator,
        output_dir: str
    ):
        """
        Initialize component stress tester.
        
        Args:
            config: Component stress test configuration
            metrics_collector: Metrics collector for performance tracking
            data_generator: Test data generator
            output_dir: Directory for test outputs
        """
        self.config = config
        self.metrics = metrics_collector
        self.data_gen = data_generator
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized ComponentStressTester with output_dir={output_dir}")
    
    def _create_vector_store(self, tmpdir: str):
        """
        Create a vector store, using mock if ChromaDB is unavailable.
        
        Returns:
            Tuple of (vector_store, use_mock)
        """
        try:
            from retrieval.vector_store import VectorStore
            return VectorStore(persist_directory=tmpdir), False
        except (RuntimeError, ImportError) as e:
            logger.warning(f"VectorStore unavailable ({e}), using MockVectorStore")
            from tests.mocks.mock_vector_store import MockVectorStore
            return MockVectorStore(), True
    
    def run_tests(self) -> List[TestResult]:
        """
        Run all component stress tests.
        
        Returns:
            List of test results
        """
        results = []
        
        logger.info("Starting component stress tests...")
        
        # Retrieval stress tests (Requirement 44)
        results.append(self.test_sequential_similarity_searches())
        results.append(self.test_concurrent_similarity_searches())
        results.append(self.test_large_top_k())
        results.append(self.test_query_latency_scaling())
        
        # Retrieval failure mode tests (Requirement 45)
        results.append(self.test_dense_retrieval_failure())
        results.append(self.test_sparse_retrieval_failure())
        results.append(self.test_reranking_failure())
        results.append(self.test_empty_result_handling())
        
        # Retrieval accuracy tests (Requirements 30, 54)
        results.append(self.test_keyword_without_content())
        results.append(self.test_content_without_keywords())
        results.append(self.test_misleading_text())
        results.append(self.test_keyword_stuffing())
        
        # Cross-encoder reranking tests (Requirement 40)
        results.append(self.test_rerank_many_candidates())
        results.append(self.test_rerank_identical_scores())
        results.append(self.test_rerank_long_text())
        results.append(self.test_rerank_relevance_improvement())
        
        # Stage A scoring edge cases (Requirement 41)
        results.append(self.test_conflicting_scores())
        results.append(self.test_exact_threshold_scores())
        results.append(self.test_score_boundary_combinations())
        
        logger.info(f"Completed {len(results)} component stress tests")
        return results

    # ========================================================================
    # Retrieval Stress Tests (Requirement 44)
    # ========================================================================
    
    def test_sequential_similarity_searches(self) -> TestResult:
        """
        Test 10,000 sequential similarity searches.
        
        Validates: Requirement 44.1
        """
        test_id = "component_stress_sequential_searches"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.embedding_engine import EmbeddingEngine
            
            # Create vector store with test embeddings
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store, use_mock = self._create_vector_store(tmpdir)
                embedding_engine = EmbeddingEngine()
                
                # Generate test documents and embeddings
                test_docs = [f"Test document {i} about cybersecurity policy" for i in range(1000)]
                embeddings = embedding_engine.generate_embeddings(test_docs)
                
                # Add to vector store
                if use_mock:
                    # MockVectorStore uses add_embeddings with collection_name
                    metadata = [{"text": doc, "chunk_id": f"chunk_{i}"} for i, doc in enumerate(test_docs)]
                    vector_store.add_embeddings(embeddings, metadata, collection_name="test")
                else:
                    for i, (doc, emb) in enumerate(zip(test_docs, embeddings)):
                        vector_store.add_embedding(
                            chunk_id=f"chunk_{i}",
                            embedding=emb,
                            metadata={"text": doc}
                        )
                
                # Measure sequential search performance
                self.metrics.start_collection(test_id)
                start_time = time.time()
                
                query_embedding = embedding_engine.generate_embeddings(["cybersecurity policy"])[0]
                latencies = []
                
                for i in range(self.config.sequential_searches):
                    search_start = time.time()
                    if use_mock:
                        results = vector_store.similarity_search(query_embedding, collection_name="test", top_k=5)
                    else:
                        results = vector_store.similarity_search(query_embedding, top_k=5)
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
                
                logger.info(f"Sequential searches: avg={avg_latency:.4f}s, max={max_latency:.4f}s, min={min_latency:.4f}s")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.STRESS,
                    passed=performance_consistent,
                    requirement_ids=["44.1"],
                    duration_seconds=end_time - start_time,
                    metrics=metrics,
                    error_message=None if performance_consistent else f"Performance degraded: max latency {max_latency:.4f}s is >10x avg {avg_latency:.4f}s"
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
        
        Validates: Requirement 44.2
        """
        test_id = "component_stress_concurrent_searches"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            # Create vector store with test embeddings
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine()
                
                # Generate test documents and embeddings
                test_docs = [f"Test document {i} about cybersecurity" for i in range(1000)]
                embeddings = embedding_engine.generate_embeddings(test_docs)
                
                # Add to vector store
                for i, (doc, emb) in enumerate(zip(test_docs, embeddings)):
                    vector_store.add_embedding(
                        chunk_id=f"chunk_{i}",
                        embedding=emb,
                        metadata={"text": doc}
                    )
                
                # Prepare query embedding
                query_embedding = embedding_engine.generate_embeddings(["cybersecurity"])[0]
                
                # Concurrent search function
                def search_task(task_id: int) -> Tuple[int, bool, Optional[str]]:
                    try:
                        results = vector_store.similarity_search(query_embedding, top_k=5)
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
                    duration_seconds=end_time - start_time,
                    metrics=metrics,
                    error_message=error_message,
                    requirement_ids=["44.2"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                error_message=str(e),
                requirement_ids=["44.2"]
            )

    def test_large_top_k(self) -> TestResult:
        """
        Test top_k=10,000 with large result sets.
        
        Validates: Requirement 44.3
        """
        test_id = "component_stress_large_top_k"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            # Create vector store with many embeddings
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine()
                
                # Generate 15,000 test documents (more than top_k)
                logger.info("Generating 15,000 test documents...")
                test_docs = [f"Document {i} about security policy and compliance" for i in range(15000)]
                
                # Generate embeddings in batches
                batch_size = 100
                for i in range(0, len(test_docs), batch_size):
                    batch = test_docs[i:i+batch_size]
                    embeddings = embedding_engine.generate_embeddings(batch)
                    
                    for j, (doc, emb) in enumerate(zip(batch, embeddings)):
                        vector_store.add_embedding(
                            chunk_id=f"chunk_{i+j}",
                            embedding=emb,
                            metadata={"text": doc}
                        )
                    
                    if (i // batch_size) % 10 == 0:
                        logger.info(f"Added {i+batch_size}/{len(test_docs)} embeddings")
                
                # Query with large top_k
                query_embedding = embedding_engine.generate_embeddings(["security policy"])[0]
                
                self.metrics.start_collection(test_id)
                start_time = time.time()
                
                results = vector_store.similarity_search(query_embedding, top_k=self.config.max_top_k)
                
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
                    duration_seconds=end_time - start_time,
                    metrics=metrics,
                    error_message=error_message,
                    requirement_ids=["44.3"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                error_message=str(e),
                requirement_ids=["44.3"]
            )

    def test_query_latency_scaling(self) -> TestResult:
        """
        Measure query latency for collections from 100 to 100,000 embeddings.
        
        Validates: Requirement 44.4, 44.5
        """
        test_id = "component_stress_query_latency_scaling"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.vector_store import VectorStore
            from retrieval.embedding_engine import EmbeddingEngine
            
            embedding_engine = EmbeddingEngine()
            query_embedding = embedding_engine.generate_embeddings(["cybersecurity policy"])[0]
            
            latency_results = {}
            
            for size in self.config.embedding_sizes:
                logger.info(f"Testing with {size} embeddings...")
                
                with tempfile.TemporaryDirectory() as tmpdir:
                    vector_store = VectorStore(persist_directory=tmpdir)
                    
                    # Generate test documents
                    test_docs = [f"Document {i} about security" for i in range(size)]
                    
                    # Add embeddings in batches
                    batch_size = 100
                    for i in range(0, len(test_docs), batch_size):
                        batch = test_docs[i:i+batch_size]
                        embeddings = embedding_engine.generate_embeddings(batch)
                        
                        for j, (doc, emb) in enumerate(zip(batch, embeddings)):
                            vector_store.add_embedding(
                                chunk_id=f"chunk_{i+j}",
                                embedding=emb,
                                metadata={"text": doc}
                            )
                    
                    # Measure query latency (average of 10 queries)
                    latencies = []
                    for _ in range(10):
                        start = time.time()
                        results = vector_store.similarity_search(query_embedding, top_k=10)
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
                category=TestCategory.PERFORMANCE,
                passed=passed,
                error_message=error_message,
                artifacts=[str(results_file)],
                requirement_ids=["44.4", "44.5"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.PERFORMANCE,
                passed=False,
                error_message=str(e),
                requirement_ids=["44.4", "44.5"]
            )

    # ========================================================================
    # Retrieval Failure Mode Tests (Requirement 45)
    # ========================================================================
    
    def test_dense_retrieval_failure(self) -> TestResult:
        """
        Test dense retrieval failure fallback to sparse retrieval.
        
        Validates: Requirement 45.1
        """
        test_id = "component_stress_dense_retrieval_failure"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            from unittest.mock import patch, MagicMock
            
            # Create hybrid retriever
            with tempfile.TemporaryDirectory() as tmpdir:
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                # Mock dense retrieval to fail
                with patch.object(retriever, '_dense_retrieval', side_effect=Exception("Dense retrieval failed")):
                    # Attempt retrieval - should fall back to sparse only
                    try:
                        results = retriever.retrieve(
                            query="cybersecurity policy",
                            top_k=5
                        )
                        
                        # Should succeed with sparse retrieval fallback
                        passed = True
                        error_message = None
                        logger.info("Dense retrieval failure handled gracefully with sparse fallback")
                        
                    except Exception as e:
                        passed = False
                        error_message = f"Failed to fall back to sparse retrieval: {e}"
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["45.1"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.CHAOS,
                passed=False,
                error_message=str(e),
                requirement_ids=["45.1"]
            )
    
    def test_sparse_retrieval_failure(self) -> TestResult:
        """
        Test sparse retrieval failure fallback to dense retrieval.
        
        Validates: Requirement 45.2
        """
        test_id = "component_stress_sparse_retrieval_failure"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            from unittest.mock import patch
            
            # Create hybrid retriever
            with tempfile.TemporaryDirectory() as tmpdir:
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                # Mock sparse retrieval to fail
                with patch.object(retriever, '_sparse_retrieval', side_effect=Exception("Sparse retrieval failed")):
                    # Attempt retrieval - should fall back to dense only
                    try:
                        results = retriever.retrieve(
                            query="cybersecurity policy",
                            top_k=5
                        )
                        
                        # Should succeed with dense retrieval fallback
                        passed = True
                        error_message = None
                        logger.info("Sparse retrieval failure handled gracefully with dense fallback")
                        
                    except Exception as e:
                        passed = False
                        error_message = f"Failed to fall back to dense retrieval: {e}"
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["45.2"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.CHAOS,
                passed=False,
                error_message=str(e),
                requirement_ids=["45.2"]
            )

    def test_reranking_failure(self) -> TestResult:
        """
        Test reranking failure fallback to pre-reranking results.
        
        Validates: Requirement 45.3
        """
        test_id = "component_stress_reranking_failure"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            from unittest.mock import patch
            
            # Create hybrid retriever
            with tempfile.TemporaryDirectory() as tmpdir:
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                # Mock reranking to fail
                with patch.object(retriever, '_rerank', side_effect=Exception("Reranking failed")):
                    # Attempt retrieval - should use pre-reranking results
                    try:
                        results = retriever.retrieve(
                            query="cybersecurity policy",
                            top_k=5
                        )
                        
                        # Should succeed with pre-reranking results
                        passed = True
                        error_message = None
                        logger.info("Reranking failure handled gracefully with pre-reranking results")
                        
                    except Exception as e:
                        passed = False
                        error_message = f"Failed to use pre-reranking results: {e}"
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.CHAOS,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["45.3"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.CHAOS,
                passed=False,
                error_message=str(e),
                requirement_ids=["45.3"]
            )
    
    def test_empty_result_handling(self) -> TestResult:
        """
        Test handling when both retrieval methods return empty results.
        
        Validates: Requirement 45.4, 45.5
        """
        test_id = "component_stress_empty_result_handling"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            
            # Create hybrid retriever with empty vector store
            with tempfile.TemporaryDirectory() as tmpdir:
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                # Query empty vector store
                results = retriever.retrieve(
                    query="cybersecurity policy",
                    top_k=5
                )
                
                # Should return empty list gracefully
                passed = isinstance(results, list) and len(results) == 0
                error_message = None if passed else f"Expected empty list, got {type(results)} with {len(results)} items"
                
                logger.info(f"Empty result handling: returned {len(results)} results")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.BOUNDARY,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["45.4", "45.5"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                error_message=str(e),
                requirement_ids=["45.4", "45.5"]
            )

    # ========================================================================
    # Retrieval Accuracy Tests (Requirements 30, 54)
    # ========================================================================
    
    def test_keyword_without_content(self) -> TestResult:
        """
        Test with CSF keywords but unrelated content (should not produce false positives).
        
        Validates: Requirement 30.1, 54.5
        """
        test_id = "component_stress_keyword_without_content"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            from retrieval.embedding_engine import EmbeddingEngine
            from retrieval.vector_store import VectorStore
            
            # Create documents with CSF keywords but unrelated content
            misleading_docs = [
                "Our company uses IDENTIFY and PROTECT keywords in marketing materials about product identification and customer protection programs.",
                "The DETECT system monitors social media for brand mentions and the RESPOND team handles customer complaints.",
                "We RECOVER deleted files and provide data GOVERNANCE for file management systems.",
                "Access control lists (ACLs) are used for controlling access to the coffee machine and conference rooms.",
                "Our incident response plan covers how to respond to customer service incidents and product recalls."
            ]
            
            # Create vector store and add misleading documents
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine()
                
                embeddings = embedding_engine.generate_embeddings(misleading_docs)
                for i, (doc, emb) in enumerate(zip(misleading_docs, embeddings)):
                    vector_store.add_embedding(
                        chunk_id=f"chunk_{i}",
                        embedding=emb,
                        metadata={"text": doc}
                    )
                
                # Query for actual cybersecurity content
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                results = retriever.retrieve(
                    query="access control cybersecurity policy",
                    top_k=5
                )
                
                # Check if semantic retrieval correctly identifies these as low relevance
                # (sparse retrieval will match keywords, but semantic should be low)
                false_positives = 0
                for result in results:
                    # If score is high (>0.7), it's a false positive
                    if result.get('score', 0) > 0.7:
                        false_positives += 1
                
                # Allow up to 1 false positive out of 5
                passed = false_positives <= 1
                error_message = None if passed else f"Too many false positives: {false_positives}/5"
                
                logger.info(f"Keyword without content test: {false_positives} false positives")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.ADVERSARIAL,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["30.1", "54.5"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.ADVERSARIAL,
                passed=False,
                error_message=str(e),
                requirement_ids=["30.1", "54.5"]
            )

    def test_content_without_keywords(self) -> TestResult:
        """
        Test with relevant content but no CSF keywords (semantic retrieval should find it).
        
        Validates: Requirement 30.2, 54.1
        """
        test_id = "component_stress_content_without_keywords"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            from retrieval.embedding_engine import EmbeddingEngine
            from retrieval.vector_store import VectorStore
            
            # Create documents with relevant content but no CSF keywords
            relevant_docs = [
                "Our organization implements multi-factor authentication for all user accounts and enforces strong password policies with regular rotation requirements.",
                "We maintain comprehensive logs of all system activities and review them regularly to identify suspicious behavior patterns.",
                "Security patches are tested in a staging environment before deployment to production systems within 48 hours of release.",
                "All employees complete annual security awareness training covering phishing, social engineering, and data handling procedures.",
                "We conduct quarterly vulnerability assessments and penetration testing to identify and remediate security weaknesses."
            ]
            
            # Create vector store and add relevant documents
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine()
                
                embeddings = embedding_engine.generate_embeddings(relevant_docs)
                for i, (doc, emb) in enumerate(zip(relevant_docs, embeddings)):
                    vector_store.add_embedding(
                        chunk_id=f"chunk_{i}",
                        embedding=emb,
                        metadata={"text": doc}
                    )
                
                # Query for cybersecurity content
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                results = retriever.retrieve(
                    query="authentication and access control measures",
                    top_k=5
                )
                
                # Semantic retrieval should find relevant content
                # Check if we got results with reasonable scores
                passed = len(results) > 0 and any(r.get('score', 0) > 0.5 for r in results)
                error_message = None if passed else "Semantic retrieval failed to find relevant content without keywords"
                
                logger.info(f"Content without keywords test: found {len(results)} results")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.ADVERSARIAL,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["30.2", "54.1"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.ADVERSARIAL,
                passed=False,
                error_message=str(e),
                requirement_ids=["30.2", "54.1"]
            )
    
    def test_misleading_text(self) -> TestResult:
        """
        Test with intentionally misleading text.
        
        Validates: Requirement 30.3, 30.4
        """
        test_id = "component_stress_misleading_text"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            from retrieval.embedding_engine import EmbeddingEngine
            from retrieval.vector_store import VectorStore
            
            # Create intentionally misleading documents
            misleading_docs = [
                "We do not implement access controls. Anyone can access any system at any time without authentication.",
                "Our incident response plan is to ignore all security incidents and hope they go away.",
                "We never patch our systems because updates might break things. Security vulnerabilities are acceptable risks.",
                "Employee training is unnecessary. We assume everyone knows about cybersecurity best practices.",
                "We store all passwords in plain text files on shared network drives for easy access."
            ]
            
            # Create vector store and add misleading documents
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine()
                
                embeddings = embedding_engine.generate_embeddings(misleading_docs)
                for i, (doc, emb) in enumerate(zip(misleading_docs, embeddings)):
                    vector_store.add_embedding(
                        chunk_id=f"chunk_{i}",
                        embedding=emb,
                        metadata={"text": doc}
                    )
                
                # Query for positive security practices
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                results = retriever.retrieve(
                    query="access control implementation",
                    top_k=5
                )
                
                # Results should have low scores since content is negative/misleading
                high_score_count = sum(1 for r in results if r.get('score', 0) > 0.7)
                
                # Should not have many high-scoring misleading results
                passed = high_score_count <= 2
                error_message = None if passed else f"Too many high-scoring misleading results: {high_score_count}"
                
                logger.info(f"Misleading text test: {high_score_count} high-scoring results")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.ADVERSARIAL,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["30.3", "30.4"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.ADVERSARIAL,
                passed=False,
                error_message=str(e),
                requirement_ids=["30.3", "30.4"]
            )

    def test_keyword_stuffing(self) -> TestResult:
        """
        Test with keyword stuffing and spam (should not be fooled).
        
        Validates: Requirement 30.5, 54.2, 54.3, 54.4
        """
        test_id = "component_stress_keyword_stuffing"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.hybrid_retriever import HybridRetriever
            from retrieval.embedding_engine import EmbeddingEngine
            from retrieval.vector_store import VectorStore
            
            # Create documents with keyword stuffing
            stuffed_docs = [
                "access control " * 100 + "authentication " * 100 + "authorization " * 100,
                "IDENTIFY PROTECT DETECT RESPOND RECOVER " * 200,
                "cybersecurity security policy governance risk " * 150,
                "incident response vulnerability patch management " * 120,
                "encryption firewall intrusion detection " * 180
            ]
            
            # Also add one legitimate document
            legitimate_doc = "Our access control policy requires multi-factor authentication for all privileged accounts and implements role-based access control with least privilege principles."
            
            # Create vector store
            with tempfile.TemporaryDirectory() as tmpdir:
                vector_store = VectorStore(persist_directory=tmpdir)
                embedding_engine = EmbeddingEngine()
                
                # Add stuffed documents
                all_docs = stuffed_docs + [legitimate_doc]
                embeddings = embedding_engine.generate_embeddings(all_docs)
                for i, (doc, emb) in enumerate(zip(all_docs, embeddings)):
                    vector_store.add_embedding(
                        chunk_id=f"chunk_{i}",
                        embedding=emb,
                        metadata={"text": doc}
                    )
                
                # Query for access control
                retriever = HybridRetriever(
                    vector_store_dir=tmpdir,
                    reference_catalog_path="data/csf_reference_catalog.json"
                )
                
                results = retriever.retrieve(
                    query="access control policy",
                    top_k=5
                )
                
                # The legitimate document should rank higher than stuffed ones
                # Check if legitimate doc is in top 3
                legitimate_in_top_3 = False
                for i, result in enumerate(results[:3]):
                    if "multi-factor authentication" in result.get('text', ''):
                        legitimate_in_top_3 = True
                        break
                
                passed = legitimate_in_top_3
                error_message = None if passed else "Keyword stuffing fooled the retrieval system"
                
                logger.info(f"Keyword stuffing test: legitimate doc in top 3 = {legitimate_in_top_3}")
                
                return create_test_result(
                    test_id=test_id,
                    category=TestCategory.ADVERSARIAL,
                    passed=passed,
                    error_message=error_message,
                    requirement_ids=["30.5", "54.2", "54.3", "54.4"]
                )
                
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.ADVERSARIAL,
                passed=False,
                error_message=str(e),
                requirement_ids=["30.5", "54.2", "54.3", "54.4"]
            )

    # ========================================================================
    # Cross-Encoder Reranking Tests (Requirement 40)
    # ========================================================================
    
    def test_rerank_many_candidates(self) -> TestResult:
        """
        Test reranking 100+ candidates.
        
        Validates: Requirement 40.1
        """
        test_id = "component_stress_rerank_many_candidates"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.reranker import CrossEncoderReranker
            
            # Create reranker
            reranker = CrossEncoderReranker()
            
            # Generate 150 candidate documents
            candidates = [
                {
                    'text': f"Document {i} about cybersecurity policy and access control measures for system {i}",
                    'score': 0.5 + (i % 50) / 100.0  # Varying scores
                }
                for i in range(150)
            ]
            
            query = "access control policy implementation"
            
            # Measure reranking time
            start_time = time.time()
            reranked = reranker.rerank(query, candidates, top_k=100)
            end_time = time.time()
            
            duration = end_time - start_time
            
            # Should complete within reasonable time (< 30 seconds for 150 candidates)
            passed = duration < 30.0 and len(reranked) == 100
            error_message = None if passed else f"Reranking took {duration:.2f}s or returned {len(reranked)} results"
            
            logger.info(f"Reranked 150 candidates in {duration:.2f}s, returned {len(reranked)} results")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=passed,
                duration_seconds=duration,
                error_message=error_message,
                requirement_ids=["40.1"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.STRESS,
                passed=False,
                error_message=str(e),
                requirement_ids=["40.1"]
            )
    
    def test_rerank_identical_scores(self) -> TestResult:
        """
        Test reranking with identical scores (tie handling).
        
        Validates: Requirement 40.2
        """
        test_id = "component_stress_rerank_identical_scores"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.reranker import CrossEncoderReranker
            
            # Create reranker
            reranker = CrossEncoderReranker()
            
            # Generate candidates with identical scores
            candidates = [
                {
                    'text': f"Document {i} about access control and authentication",
                    'score': 0.75  # All identical
                }
                for i in range(20)
            ]
            
            query = "access control policy"
            
            # Rerank - should handle ties gracefully
            try:
                reranked = reranker.rerank(query, candidates, top_k=10)
                
                # Should return 10 results
                passed = len(reranked) == 10
                error_message = None if passed else f"Expected 10 results, got {len(reranked)}"
                
                logger.info(f"Reranked {len(candidates)} candidates with identical scores, returned {len(reranked)}")
                
            except Exception as e:
                passed = False
                error_message = f"Failed to handle identical scores: {e}"
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=passed,
                error_message=error_message,
                requirement_ids=["40.2"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                error_message=str(e),
                requirement_ids=["40.2"]
            )

    def test_rerank_long_text(self) -> TestResult:
        """
        Test reranking with extremely long text.
        
        Validates: Requirement 40.3
        """
        test_id = "component_stress_rerank_long_text"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.reranker import CrossEncoderReranker
            
            # Create reranker
            reranker = CrossEncoderReranker()
            
            # Generate candidates with extremely long text
            long_text = "This is a very long document about cybersecurity policy and access control. " * 1000  # ~10k words
            
            candidates = [
                {'text': long_text, 'score': 0.8},
                {'text': "Short document about access control", 'score': 0.7},
                {'text': long_text + " Additional content.", 'score': 0.75}
            ]
            
            query = "access control policy"
            
            # Rerank - should truncate long text appropriately
            try:
                reranked = reranker.rerank(query, candidates, top_k=3)
                
                # Should complete without errors
                passed = len(reranked) == 3
                error_message = None if passed else f"Expected 3 results, got {len(reranked)}"
                
                logger.info(f"Reranked candidates with long text, returned {len(reranked)} results")
                
            except Exception as e:
                passed = False
                error_message = f"Failed to handle long text: {e}"
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=passed,
                error_message=error_message,
                requirement_ids=["40.3"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                error_message=str(e),
                requirement_ids=["40.3"]
            )
    
    def test_rerank_relevance_improvement(self) -> TestResult:
        """
        Verify reranking improves relevance scores.
        
        Validates: Requirement 40.4, 40.5
        """
        test_id = "component_stress_rerank_relevance_improvement"
        logger.info(f"Starting {test_id}...")
        
        try:
            from retrieval.reranker import CrossEncoderReranker
            
            # Create reranker
            reranker = CrossEncoderReranker()
            
            # Create candidates where a highly relevant doc has low initial score
            candidates = [
                {'text': "Unrelated document about coffee machines", 'score': 0.9},
                {'text': "Another unrelated document about office supplies", 'score': 0.85},
                {'text': "Our access control policy implements role-based access control with multi-factor authentication for all privileged accounts", 'score': 0.6},
                {'text': "Random text about weather forecasts", 'score': 0.8},
                {'text': "Document about vacation policies", 'score': 0.75}
            ]
            
            query = "access control policy with multi-factor authentication"
            
            # Rerank
            reranked = reranker.rerank(query, candidates, top_k=5)
            
            # The relevant document (index 2) should move to top positions after reranking
            relevant_doc_text = "Our access control policy implements"
            relevant_in_top_2 = any(relevant_doc_text in r['text'] for r in reranked[:2])
            
            passed = relevant_in_top_2
            error_message = None if passed else "Reranking did not improve relevance - relevant doc not in top 2"
            
            logger.info(f"Reranking relevance improvement: relevant doc in top 2 = {relevant_in_top_2}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.ADVERSARIAL,
                passed=passed,
                error_message=error_message,
                requirement_ids=["40.4", "40.5"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.ADVERSARIAL,
                passed=False,
                error_message=str(e),
                requirement_ids=["40.4", "40.5"]
            )

    # ========================================================================
    # Stage A Scoring Edge Cases (Requirement 41)
    # ========================================================================
    
    def test_conflicting_scores(self) -> TestResult:
        """
        Test conflicting lexical/semantic scores.
        
        Validates: Requirement 41.1, 41.2
        """
        test_id = "component_stress_conflicting_scores"
        logger.info(f"Starting {test_id}...")
        
        try:
            from analysis.stage_a_scorer import StageAScorer
            
            # Create scorer
            scorer = StageAScorer()
            
            # Test case 1: High lexical, low semantic
            result1 = scorer.compute_coverage_score(
                lexical_score=1.0,
                semantic_score=0.0,
                subcategory_id="ID.AM-1"
            )
            
            # Test case 2: Low lexical, high semantic
            result2 = scorer.compute_coverage_score(
                lexical_score=0.0,
                semantic_score=1.0,
                subcategory_id="ID.AM-1"
            )
            
            # Both should produce valid classifications
            valid1 = result1['classification'] in ['Covered', 'Partial', 'Ambiguous', 'Gap']
            valid2 = result2['classification'] in ['Covered', 'Partial', 'Ambiguous', 'Gap']
            
            # Combined score should be reasonable (not just one or the other)
            combined1 = result1['combined_score']
            combined2 = result2['combined_score']
            
            # Combined scores should be between the extremes
            reasonable1 = 0.0 <= combined1 <= 1.0
            reasonable2 = 0.0 <= combined2 <= 1.0
            
            passed = valid1 and valid2 and reasonable1 and reasonable2
            error_message = None if passed else f"Invalid handling of conflicting scores: {result1}, {result2}"
            
            logger.info(f"Conflicting scores: lexical=1.0/semantic=0.0 -> {combined1:.2f}, lexical=0.0/semantic=1.0 -> {combined2:.2f}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=passed,
                error_message=error_message,
                requirement_ids=["41.1", "41.2"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                error_message=str(e),
                requirement_ids=["41.1", "41.2"]
            )
    
    def test_exact_threshold_scores(self) -> TestResult:
        """
        Test exact 0.5 scores at classification boundaries.
        
        Validates: Requirement 41.3
        """
        test_id = "component_stress_exact_threshold_scores"
        logger.info(f"Starting {test_id}...")
        
        try:
            from analysis.stage_a_scorer import StageAScorer
            
            # Create scorer
            scorer = StageAScorer()
            
            # Test exact 0.5 scores (both lexical and semantic)
            result = scorer.compute_coverage_score(
                lexical_score=0.5,
                semantic_score=0.5,
                subcategory_id="ID.AM-1"
            )
            
            # Should produce consistent classification
            classification = result['classification']
            combined_score = result['combined_score']
            
            # Run same test 10 times to verify consistency
            classifications = []
            for _ in range(10):
                r = scorer.compute_coverage_score(
                    lexical_score=0.5,
                    semantic_score=0.5,
                    subcategory_id="ID.AM-1"
                )
                classifications.append(r['classification'])
            
            # All classifications should be identical
            consistent = all(c == classifications[0] for c in classifications)
            
            passed = consistent and classification in ['Covered', 'Partial', 'Ambiguous', 'Gap']
            error_message = None if passed else f"Inconsistent classification at 0.5 threshold: {set(classifications)}"
            
            logger.info(f"Exact 0.5 scores: classification={classification}, consistent={consistent}")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=passed,
                error_message=error_message,
                requirement_ids=["41.3"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                error_message=str(e),
                requirement_ids=["41.3"]
            )

    def test_score_boundary_combinations(self) -> TestResult:
        """
        Test 100+ score combinations at classification boundaries.
        
        Validates: Requirement 41.4, 41.5
        """
        test_id = "component_stress_score_boundary_combinations"
        logger.info(f"Starting {test_id}...")
        
        try:
            from analysis.stage_a_scorer import StageAScorer
            
            # Create scorer
            scorer = StageAScorer()
            
            # Test score combinations at boundaries
            # Thresholds: Covered=0.8, Partial=0.5, Ambiguous=0.3
            boundary_scores = [0.0, 0.3, 0.5, 0.8, 1.0]
            
            test_cases = []
            for lex in boundary_scores:
                for sem in boundary_scores:
                    test_cases.append((lex, sem))
            
            # Add some near-boundary scores
            near_boundary = [0.29, 0.31, 0.49, 0.51, 0.79, 0.81]
            for lex in near_boundary:
                for sem in near_boundary:
                    test_cases.append((lex, sem))
            
            logger.info(f"Testing {len(test_cases)} score combinations...")
            
            results = []
            errors = []
            
            for lex_score, sem_score in test_cases:
                try:
                    result = scorer.compute_coverage_score(
                        lexical_score=lex_score,
                        semantic_score=sem_score,
                        subcategory_id="ID.AM-1"
                    )
                    
                    # Verify result is valid
                    if result['classification'] not in ['Covered', 'Partial', 'Ambiguous', 'Gap']:
                        errors.append(f"Invalid classification for lex={lex_score}, sem={sem_score}: {result['classification']}")
                    
                    if not (0.0 <= result['combined_score'] <= 1.0):
                        errors.append(f"Invalid combined score for lex={lex_score}, sem={sem_score}: {result['combined_score']}")
                    
                    results.append(result)
                    
                except Exception as e:
                    errors.append(f"Error for lex={lex_score}, sem={sem_score}: {e}")
            
            # Check for section heuristic false positives (Requirement 41.5)
            # Section heuristics should not cause false positives
            # This is validated by ensuring low scores don't get classified as Covered
            false_positives = 0
            for (lex, sem), result in zip(test_cases, results):
                if lex < 0.5 and sem < 0.5 and result['classification'] == 'Covered':
                    false_positives += 1
            
            passed = len(errors) == 0 and false_positives == 0
            error_message = None if passed else f"Errors: {errors[:5]}, False positives: {false_positives}"
            
            logger.info(f"Score boundary combinations: {len(results)} tested, {len(errors)} errors, {false_positives} false positives")
            
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=passed,
                error_message=error_message,
                requirement_ids=["41.4", "41.5"]
            )
            
        except Exception as e:
            logger.error(f"Test {test_id} failed: {e}", exc_info=True)
            return create_test_result(
                test_id=test_id,
                category=TestCategory.BOUNDARY,
                passed=False,
                error_message=str(e),
                requirement_ids=["41.4", "41.5"]
            )
