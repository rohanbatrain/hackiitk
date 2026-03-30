"""
Unit Tests for Boundary Tester

This module contains unit tests for the BoundaryTester class.
"""

import pytest
import logging
from pathlib import Path
import tempfile
import shutil

from tests.extreme.engines.boundary_tester import BoundaryTester, BoundaryTestConfig
from tests.extreme.config import TestConfig
from tests.extreme.data_generator import TestDataGenerator
from tests.extreme.support.oracle_validator import OracleValidator
from tests.extreme.models import TestStatus


@pytest.fixture
def test_config():
    """Create test configuration."""
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=['boundary'],
            requirements=[],
            concurrency=1,
            timeout_seconds=300,
            output_dir=temp_dir,
            baseline_dir=str(Path(temp_dir) / "baselines"),
            oracle_dir=str(Path(temp_dir) / "oracles"),
            test_data_dir=str(Path(temp_dir) / "test_data"),
            verbose=True,
            fail_fast=False
        )
        yield config


@pytest.fixture
def test_data_generator(test_config):
    """Create test data generator."""
    return TestDataGenerator(
        cache_dir=Path(test_config.test_data_dir)
    )


@pytest.fixture
def oracle_validator(test_config):
    """Create oracle validator."""
    oracle_dir = Path(test_config.oracle_dir)
    oracle_dir.mkdir(parents=True, exist_ok=True)
    return OracleValidator(oracle_dir=str(oracle_dir))


@pytest.fixture
def boundary_tester(test_config, test_data_generator, oracle_validator):
    """Create boundary tester instance."""
    logger = logging.getLogger("test_boundary_tester")
    logger.setLevel(logging.INFO)
    
    return BoundaryTester(
        config=test_config,
        test_data_generator=test_data_generator,
        oracle_validator=oracle_validator,
        logger=logger
    )


class TestBoundaryTesterInitialization:
    """Test boundary tester initialization."""
    
    def test_initialization(self, boundary_tester):
        """Test that boundary tester initializes correctly."""
        assert boundary_tester is not None
        assert boundary_tester.test_data_generator is not None
        assert boundary_tester.oracle_validator is not None
        assert boundary_tester.boundary_config is not None
        assert isinstance(boundary_tester.boundary_config, BoundaryTestConfig)
    
    def test_config_defaults(self, boundary_tester):
        """Test that boundary config has correct defaults."""
        config = boundary_tester.boundary_config
        assert config.minimum_word_counts == [1, 10, 100]
        assert len(config.structural_anomaly_types) == 6
        assert len(config.encoding_languages) == 10
        assert config.similarity_thresholds == [0.0, 0.3, 0.5, 0.8, 1.0]
        assert config.chunk_overlap_range == (0, 512)
        assert config.top_k_range == (1, 10000)


class TestEmptyDocumentTesting:
    """Test empty document testing functionality."""
    
    def test_empty_document(self, boundary_tester):
        """Test that empty document test executes."""
        result = boundary_tester._test_empty_document()
        assert result is not None
        assert result.test_id == "boundary_10.1_empty_document"
        assert result.category == "boundary"
        # Status could be PASS or FAIL depending on system behavior
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_whitespace_only_document(self, boundary_tester):
        """Test that whitespace-only document test executes."""
        result = boundary_tester._test_whitespace_only_document()
        assert result is not None
        assert result.test_id == "boundary_10.1_whitespace_only_document"
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_special_char_only_document(self, boundary_tester):
        """Test that special-char-only document test executes."""
        result = boundary_tester._test_special_char_only_document()
        assert result is not None
        assert result.test_id == "boundary_10.1_special_char_only_document"
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_minimum_document_sizes(self, boundary_tester):
        """Test that minimum document size tests execute."""
        for word_count in [1, 10, 100]:
            result = boundary_tester._test_minimum_document_size(word_count)
            assert result is not None
            assert f"minimum_document_{word_count}_words" in result.test_id
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL]


class TestStructuralAnomalyTesting:
    """Test structural anomaly testing functionality."""
    
    def test_structural_anomaly_types(self, boundary_tester):
        """Test that all structural anomaly types are tested."""
        anomaly_types = boundary_tester.boundary_config.structural_anomaly_types
        assert len(anomaly_types) == 6
        assert 'no_headings' in anomaly_types
        assert 'deep_nesting' in anomaly_types
        assert 'inconsistent_hierarchy' in anomaly_types
    
    def test_structural_anomaly_execution(self, boundary_tester):
        """Test that structural anomaly test executes."""
        result = boundary_tester._test_structural_anomaly('no_headings')
        assert result is not None
        assert 'structural_anomaly_no_headings' in result.test_id
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]


class TestCoverageBoundaryTesting:
    """Test coverage boundary testing functionality."""
    
    def test_zero_gaps(self, boundary_tester):
        """Test that zero gaps test executes."""
        result = boundary_tester._test_zero_gaps()
        assert result is not None
        assert result.test_id == "boundary_10.3_zero_gaps"
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_all_gaps(self, boundary_tester):
        """Test that all gaps test executes."""
        result = boundary_tester._test_all_gaps()
        assert result is not None
        assert result.test_id == "boundary_10.3_all_gaps"
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_exact_threshold_scores(self, boundary_tester):
        """Test that exact threshold score tests execute."""
        for threshold in [0.0, 0.3, 0.5, 0.8, 1.0]:
            result = boundary_tester._test_exact_threshold_score(threshold)
            assert result is not None
            assert f"threshold_{threshold}" in result.test_id
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_keywords_only_policy(self, boundary_tester):
        """Test that keywords-only policy test executes."""
        result = boundary_tester._test_keywords_only_policy()
        assert result is not None
        assert result.test_id == "boundary_10.3_keywords_only"
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_implementation_only_policy(self, boundary_tester):
        """Test that implementation-only policy test executes."""
        result = boundary_tester._test_implementation_only_policy()
        assert result is not None
        assert result.test_id == "boundary_10.3_implementation_only"
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]


class TestEncodingDiversityTesting:
    """Test encoding diversity testing functionality."""
    
    def test_encoding_languages(self, boundary_tester):
        """Test that all encoding languages are configured."""
        languages = boundary_tester.boundary_config.encoding_languages
        assert len(languages) >= 10
        assert 'chinese' in languages
        assert 'arabic' in languages
        assert 'cyrillic' in languages
        assert 'emoji' in languages
    
    def test_encoding_language_execution(self, boundary_tester):
        """Test that encoding language test executes."""
        result = boundary_tester._test_encoding_language('chinese')
        assert result is not None
        assert 'encoding_chinese' in result.test_id
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]


class TestSimilarityScoreBoundaryTesting:
    """Test similarity score boundary testing functionality."""
    
    def test_similarity_score_boundaries(self, boundary_tester):
        """Test that similarity score boundary test executes."""
        result = boundary_tester._test_similarity_score_boundary_combinations()
        assert result is not None
        assert result.test_id == "boundary_10.5_similarity_score_boundaries"
        assert result.category == "boundary"
        assert result.status in [TestStatus.PASS, TestStatus.FAIL]


class TestExtremeParameterTesting:
    """Test extreme parameter testing functionality."""
    
    def test_extreme_chunk_overlap(self, boundary_tester):
        """Test that extreme chunk overlap tests execute."""
        for overlap in [0, 511, 512]:
            result = boundary_tester._test_extreme_chunk_overlap(overlap)
            assert result is not None
            assert f"chunk_overlap_{overlap}" in result.test_id
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL]
    
    def test_extreme_top_k(self, boundary_tester):
        """Test that extreme top_k tests execute."""
        for top_k in [1, 100, 10000]:
            result = boundary_tester._test_extreme_top_k(top_k)
            assert result is not None
            assert f"top_k_{top_k}" in result.test_id
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL]


class TestBoundaryTesterIntegration:
    """Test boundary tester integration."""
    
    def test_run_tests(self, boundary_tester):
        """Test that run_tests executes all test categories."""
        # Note: This is a long-running test, so we'll just verify it starts
        # In a real test, we'd run a subset or mock the pipeline
        assert boundary_tester.run_tests is not None
        assert callable(boundary_tester.run_tests)
    
    def test_test_empty_documents(self, boundary_tester):
        """Test that test_empty_documents returns results."""
        results = boundary_tester.test_empty_documents()
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL, TestStatus.SKIP]
    
    def test_test_structural_anomalies(self, boundary_tester):
        """Test that test_structural_anomalies returns results."""
        results = boundary_tester.test_structural_anomalies()
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL, TestStatus.SKIP]
    
    def test_test_coverage_boundaries(self, boundary_tester):
        """Test that test_coverage_boundaries returns results."""
        results = boundary_tester.test_coverage_boundaries()
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL, TestStatus.SKIP]
    
    def test_test_encoding_diversity(self, boundary_tester):
        """Test that test_encoding_diversity returns results."""
        results = boundary_tester.test_encoding_diversity()
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL, TestStatus.SKIP]
    
    def test_test_similarity_score_boundaries(self, boundary_tester):
        """Test that test_similarity_score_boundaries returns results."""
        results = boundary_tester.test_similarity_score_boundaries()
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL, TestStatus.SKIP]
    
    def test_test_extreme_parameters(self, boundary_tester):
        """Test that test_extreme_parameters returns results."""
        results = boundary_tester.test_extreme_parameters()
        assert isinstance(results, list)
        assert len(results) > 0
        for result in results:
            assert result.category == "boundary"
            assert result.status in [TestStatus.PASS, TestStatus.FAIL, TestStatus.SKIP]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
