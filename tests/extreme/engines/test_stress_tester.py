"""
Tests for StressTester

This module contains comprehensive tests for the StressTester class.
"""

import pytest
import time
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock

from tests.extreme.engines.stress_tester import StressTester, StressTestConfig
from tests.extreme.config import TestConfig
from tests.extreme.models import TestStatus, Metrics
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator


# Check if ChromaDB is available
def is_chromadb_available():
    """Check if ChromaDB is available."""
    try:
        from retrieval.vector_store import VectorStore
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            VectorStore(persist_directory=tmpdir)
        return True
    except (RuntimeError, ImportError):
        return False


CHROMADB_AVAILABLE = is_chromadb_available()
requires_chromadb = pytest.mark.skipif(
    not CHROMADB_AVAILABLE,
    reason="ChromaDB not available (NumPy 2.0 compatibility issue)"
)


@pytest.fixture
def test_config():
    """Create test configuration."""
    return TestConfig(
        categories=['stress'],
        requirements=[],
        concurrency=5,
        timeout_seconds=3600,
        output_dir='test_outputs/stress_tests',
        baseline_dir='test_outputs/baselines',
        oracle_dir='tests/extreme/oracles',
        test_data_dir='test_outputs/test_data',
        verbose=True,
        fail_fast=False
    )


@pytest.fixture
def metrics_collector():
    """Create metrics collector."""
    return MetricsCollector()


@pytest.fixture
def test_data_generator():
    """Create test data generator."""
    return TestDataGenerator(cache_dir=Path('test_outputs/test_data'))


@pytest.fixture
def stress_tester(test_config, metrics_collector, test_data_generator):
    """Create stress tester instance."""
    return StressTester(
        config=test_config,
        metrics_collector=metrics_collector,
        test_data_generator=test_data_generator
    )



class TestStressTesterInitialization:
    """Test StressTester initialization."""
    
    def test_initialization(self, stress_tester):
        """Test that StressTester initializes correctly."""
        assert stress_tester is not None
        assert stress_tester.metrics_collector is not None
        assert stress_tester.test_data_generator is not None
        assert stress_tester.stress_config is not None
        assert isinstance(stress_tester.stress_config, StressTestConfig)
    
    def test_stress_config_defaults(self, stress_tester):
        """Test that stress config has correct defaults."""
        config = stress_tester.stress_config
        assert config.max_document_pages == 100
        assert config.max_words == 500000
        assert config.max_chunks == 10000
        assert config.max_catalog_size == 1000
        assert config.max_concurrency == 5
        assert config.resource_leak_iterations == 10
        assert 'document_size' in config.breaking_point_dimensions
        assert 'chunk_count' in config.breaking_point_dimensions
        assert 'concurrency' in config.breaking_point_dimensions
        assert 'catalog_size' in config.breaking_point_dimensions


class TestMaximumDocumentSize:
    """Test maximum document size stress testing."""
    
    @pytest.mark.slow
    def test_maximum_document_size_generation(self, stress_tester):
        """Test that maximum-size document can be generated."""
        # This test just verifies document generation works
        from tests.extreme.data_generator import DocumentSpec
        
        spec = DocumentSpec(
            size_pages=10,  # Use smaller size for testing
            words_per_page=500,
            sections_per_page=3,
            coverage_percentage=0.5,
            include_csf_keywords=True
        )
        
        document = stress_tester.test_data_generator.generate_policy_document(spec)
        
        assert document is not None
        assert len(document) > 0
        assert "Section" in document
    
    @pytest.mark.slow
    @pytest.mark.integration
    @requires_chromadb
    def test_maximum_document_size_full(self, stress_tester):
        """Test full maximum document size stress test."""
        # This is a full integration test - mark as slow
        result = stress_tester.test_maximum_document_size()
        
        assert result is not None
        assert result.test_id == "stress_7.1_maximum_document_size"
        assert result.category == "stress"
        # Status could be PASS or FAIL depending on system resources
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
        assert result.duration_seconds > 0


class TestReferenceCatalogScale:
    """Test reference catalog scale stress testing."""
    
    @pytest.mark.slow
    @pytest.mark.integration
    @requires_chromadb
    def test_reference_catalog_scale(self, stress_tester):
        """Test reference catalog scale stress test."""
        result = stress_tester.test_reference_catalog_scale()
        
        assert result is not None
        assert result.test_id == "stress_7.1_reference_catalog_scale"
        assert result.category == "stress"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
        assert result.duration_seconds > 0


class TestConcurrentOperations:
    """Test concurrent operation stress testing."""
    
    @requires_chromadb
    def test_concurrent_operations_config(self, stress_tester):
        """Test that concurrent operations can be configured."""
        # Test with small concurrency for unit test
        result = stress_tester.test_concurrent_operations(concurrency=2)
        
        assert result is not None
        assert "concurrent_operations" in result.test_id
        assert result.category == "stress"
        assert result.duration_seconds > 0
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_concurrent_operations_full(self, stress_tester):
        """Test full concurrent operations stress test."""
        result = stress_tester.test_concurrent_operations(concurrency=5)
        
        assert result is not None
        assert result.category == "stress"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]


class TestResourceLeaks:
    """Test resource leak detection."""
    
    @requires_chromadb
    def test_resource_leaks_small_iterations(self, stress_tester):
        """Test resource leak detection with small iteration count."""
        # Use small iteration count for unit test
        result = stress_tester.test_resource_leaks(iterations=2)
        
        assert result is not None
        assert "resource_leaks" in result.test_id
        assert result.category == "stress"
        assert result.duration_seconds > 0
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_resource_leaks_full(self, stress_tester):
        """Test full resource leak detection."""
        result = stress_tester.test_resource_leaks(iterations=10)
        
        assert result is not None
        assert result.category == "stress"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
        
        # If test passed, no resource leaks should be detected
        if result.status == TestStatus.PASS:
            assert result.error_message is None


class TestBreakingPointIdentification:
    """Test breaking point identification."""
    
    def test_identify_breaking_point_document_size(self, stress_tester):
        """Test breaking point identification for document size."""
        result = stress_tester.identify_breaking_point('document_size')
        
        assert result is not None
        assert "breaking_point_document_size" in result.test_id
        assert result.category == "stress"
        
        # Check that breaking point was recorded
        assert len(stress_tester.breaking_points) > 0
        bp = stress_tester.breaking_points[-1]
        assert bp.dimension == 'document_size'
        assert bp.maximum_viable_value is not None
    
    def test_identify_breaking_point_chunk_count(self, stress_tester):
        """Test breaking point identification for chunk count."""
        result = stress_tester.identify_breaking_point('chunk_count')
        
        assert result is not None
        assert "breaking_point_chunk_count" in result.test_id
        
        # Check that breaking point was recorded
        bp = [bp for bp in stress_tester.breaking_points if bp.dimension == 'chunk_count']
        assert len(bp) > 0
        assert "10000+" in bp[0].maximum_viable_value
    
    def test_identify_breaking_point_concurrency(self, stress_tester):
        """Test breaking point identification for concurrency."""
        result = stress_tester.identify_breaking_point('concurrency')
        
        assert result is not None
        assert "breaking_point_concurrency" in result.test_id
    
    def test_identify_breaking_point_catalog_size(self, stress_tester):
        """Test breaking point identification for catalog size."""
        result = stress_tester.identify_breaking_point('catalog_size')
        
        assert result is not None
        assert "breaking_point_catalog_size" in result.test_id
    
    def test_identify_breaking_point_unsupported_dimension(self, stress_tester):
        """Test that unsupported dimension returns None."""
        result = stress_tester.identify_breaking_point('unsupported_dimension')
        
        assert result is None


class TestRunAllTests:
    """Test running all stress tests."""
    
    @pytest.mark.slow
    @pytest.mark.integration
    def test_run_all_tests(self, stress_tester):
        """Test running all stress tests."""
        results = stress_tester.run_tests()
        
        assert results is not None
        assert len(results) > 0
        
        # Should have results for all test categories
        test_ids = [r.test_id for r in results]
        
        # Check for key tests
        assert any("maximum_document_size" in tid for tid in test_ids)
        assert any("concurrent_operations" in tid for tid in test_ids)
        assert any("resource_leaks" in tid for tid in test_ids)
        assert any("breaking_point" in tid for tid in test_ids)
        
        # All results should have valid status
        for result in results:
            assert result.status in [TestStatus.PASS, TestStatus.FAIL, TestStatus.SKIP, TestStatus.ERROR]
            assert result.duration_seconds >= 0
            assert result.category == "stress"


class TestMetricsCollection:
    """Test metrics collection during stress tests."""
    
    def test_metrics_collected_for_tests(self, stress_tester):
        """Test that metrics are collected for stress tests."""
        # Run a simple test
        result = stress_tester.test_resource_leaks(iterations=1)
        
        # Check that metrics were collected
        if result.status == TestStatus.PASS:
            assert result.metrics is not None
            assert result.metrics.duration_seconds > 0
            assert result.metrics.memory_peak_mb >= 0
            assert result.metrics.cpu_peak_percent >= 0


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
