"""
Unit Tests for Embedding and Vector Store Stress Tester

Tests the EmbeddingVectorStoreStressTester class to ensure all test methods
work correctly and handle edge cases properly.
"""

import os
import sys
import pytest
import tempfile
import numpy as np
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from tests.extreme.engines.embedding_vector_store_stress_tester import (
    EmbeddingVectorStoreStressTester,
    EmbeddingVectorStoreConfig,
    create_test_result
)
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator
from tests.extreme.models import TestStatus


@pytest.fixture
def config():
    """Create test configuration."""
    return EmbeddingVectorStoreConfig(
        sequential_searches=100,  # Reduced for testing
        concurrent_searches=10,
        max_top_k=100,
        embedding_test_sizes=[10, 50],
        large_chunk_count=100
    )


@pytest.fixture
def metrics_collector():
    """Create metrics collector."""
    return MetricsCollector()


@pytest.fixture
def data_generator():
    """Create data generator."""
    return TestDataGenerator()


@pytest.fixture
def output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def tester(config, metrics_collector, data_generator, output_dir):
    """Create tester instance."""
    return EmbeddingVectorStoreStressTester(
        config=config,
        metrics_collector=metrics_collector,
        data_generator=data_generator,
        output_dir=output_dir
    )



class TestEmbeddingVectorStoreStressTester:
    """Test suite for EmbeddingVectorStoreStressTester."""
    
    def test_initialization(self, tester, output_dir):
        """Test tester initialization."""
        assert tester.config is not None
        assert tester.metrics is not None
        assert tester.data_gen is not None
        assert tester.output_dir == Path(output_dir)
        assert tester.output_dir.exists()
    
    def test_create_test_result_pass(self):
        """Test creating a passing test result."""
        result = create_test_result(
            test_id="test_1",
            category="stress",
            passed=True,
            requirement_ids=["27.1", "27.2"],
            duration_seconds=1.5
        )
        
        assert result.test_id == "test_1"
        assert result.category == "stress"
        assert result.status == TestStatus.PASS
        assert result.requirement_id == "27.1,27.2"
        assert result.duration_seconds == 1.5
        assert result.error_message is None
    
    def test_create_test_result_fail(self):
        """Test creating a failing test result."""
        result = create_test_result(
            test_id="test_2",
            category="chaos",
            passed=False,
            requirement_ids=["51.1"],
            error_message="Test failed"
        )
        
        assert result.test_id == "test_2"
        assert result.status == TestStatus.FAIL
        assert result.error_message == "Test failed"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_embedding_quality_large_batch(self, tester):
        """Test embedding quality validation with large batch."""
        result = tester.test_embedding_quality_large_batch()
        
        assert result is not None
        assert result.test_id == "embedding_quality_large_batch"
        assert result.requirement_id == "27.1"
        # Result may pass or fail depending on model availability
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_embedding_empty_strings(self, tester):
        """Test embedding with empty strings."""
        result = tester.test_embedding_empty_strings()
        
        assert result is not None
        assert result.test_id == "embedding_empty_strings"
        assert result.requirement_id == "27.2"
        # Should pass if empty strings are correctly rejected
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_embedding_extremely_long_text(self, tester):
        """Test embedding with extremely long text."""
        result = tester.test_embedding_extremely_long_text()
        
        assert result is not None
        assert result.test_id == "embedding_extremely_long_text"
        assert result.requirement_id == "27.3"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_embedding_dimensionality_consistency(self, tester):
        """Test embedding dimensionality consistency."""
        result = tester.test_embedding_dimensionality_consistency()
        
        assert result is not None
        assert result.test_id == "embedding_dimensionality_consistency"
        assert result.requirement_id == "27.4"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_embedding_similarity_score_range(self, tester):
        """Test embedding similarity score range."""
        result = tester.test_embedding_similarity_score_range()
        
        assert result is not None
        assert result.test_id == "embedding_similarity_score_range"
        assert result.requirement_id == "27.5"
    
    def test_embedding_nan_values(self, tester):
        """Test embedding with NaN values."""
        result = tester.test_embedding_nan_values()
        
        assert result is not None
        assert result.test_id == "embedding_nan_values"
        assert result.requirement_id == "51.1"
    
    def test_embedding_infinite_values(self, tester):
        """Test embedding with infinite values."""
        result = tester.test_embedding_infinite_values()
        
        assert result is not None
        assert result.test_id == "embedding_infinite_values"
        assert result.requirement_id == "51.2"
    
    def test_embedding_incorrect_dimensionality(self, tester):
        """Test embedding with incorrect dimensionality."""
        result = tester.test_embedding_incorrect_dimensionality()
        
        assert result is not None
        assert result.test_id == "embedding_incorrect_dimensionality"
        assert result.requirement_id == "51.3"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_embedding_all_zeros(self, tester):
        """Test embedding with all zeros."""
        result = tester.test_embedding_all_zeros()
        
        assert result is not None
        assert result.test_id == "embedding_all_zeros"
        assert result.requirement_id == "51.4"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_sequential_similarity_searches(self, tester):
        """Test sequential similarity searches."""
        result = tester.test_sequential_similarity_searches()
        
        assert result is not None
        assert result.test_id == "vector_store_sequential_searches"
        assert result.requirement_id == "44.1"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_concurrent_similarity_searches(self, tester):
        """Test concurrent similarity searches."""
        result = tester.test_concurrent_similarity_searches()
        
        assert result is not None
        assert result.test_id == "vector_store_concurrent_searches"
        assert result.requirement_id == "44.2"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_large_top_k(self, tester):
        """Test large top_k values."""
        result = tester.test_large_top_k()
        
        assert result is not None
        assert result.test_id == "vector_store_large_top_k"
        assert result.requirement_id == "44.3"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_query_latency_scaling(self, tester):
        """Test query latency scaling."""
        result = tester.test_query_latency_scaling()
        
        assert result is not None
        assert result.test_id == "vector_store_query_latency_scaling"
        assert result.requirement_id == "44.4"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_search_accuracy_with_size(self, tester):
        """Test search accuracy with increasing collection size."""
        result = tester.test_search_accuracy_with_size()
        
        assert result is not None
        assert result.test_id == "vector_store_search_accuracy_scaling"
        assert result.requirement_id == "44.5"
    
    @pytest.mark.skipif(
        not os.path.exists("models/all-MiniLM-L6-v2"),
        reason="Embedding model not available"
    )
    def test_run_tests(self, tester):
        """Test running all tests."""
        results = tester.run_tests()
        
        assert len(results) > 0
        assert all(hasattr(r, 'test_id') for r in results)
        assert all(hasattr(r, 'status') for r in results)
        assert all(hasattr(r, 'requirement_id') for r in results)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
