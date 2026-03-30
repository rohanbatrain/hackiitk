"""
Unit tests for AdversarialTester

This module tests the AdversarialTester class to ensure it correctly
validates security boundaries with malicious inputs and attack vectors.
"""

import pytest
import logging
from pathlib import Path
import tempfile
import shutil

from tests.extreme.engines.adversarial_tester import AdversarialTester, AdversarialTestConfig
from tests.extreme.config import TestConfig
from tests.extreme.data_generator import TestDataGenerator
from tests.extreme.models import TestStatus


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
    with tempfile.TemporaryDirectory() as temp_dir:
        config = TestConfig(
            categories=['adversarial'],
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
        cache_dir=Path(test_config.test_data_dir),
        logger=logging.getLogger("test_data_generator")
    )


@pytest.fixture
def adversarial_tester(test_config, test_data_generator):
    """Create adversarial tester instance."""
    return AdversarialTester(
        config=test_config,
        test_data_generator=test_data_generator,
        logger=logging.getLogger("adversarial_tester")
    )


def test_adversarial_tester_initialization(adversarial_tester):
    """Test AdversarialTester initialization."""
    assert adversarial_tester is not None
    assert adversarial_tester.test_data_generator is not None
    assert adversarial_tester.adversarial_config is not None
    assert isinstance(adversarial_tester.adversarial_config, AdversarialTestConfig)


@requires_chromadb
def test_malicious_pdfs(adversarial_tester):
    """Test malicious PDF handling."""
    result = adversarial_tester.test_malicious_pdfs()
    
    assert result is not None
    assert result.test_id == "adversarial_9.1_malicious_pdfs"
    assert result.category == "adversarial"
    # Test should pass (malicious PDFs rejected or sanitized)
    assert result.status in [TestStatus.PASS, TestStatus.SKIP]


@requires_chromadb
def test_buffer_overflow(adversarial_tester):
    """Test buffer overflow protection."""
    result = adversarial_tester.test_buffer_overflow()
    
    assert result is not None
    assert result.test_id == "adversarial_9.2_buffer_overflow"
    assert result.category == "adversarial"
    # Test should pass (buffer overflows handled)
    assert result.status in [TestStatus.PASS, TestStatus.SKIP]


@requires_chromadb
def test_encoding_attacks(adversarial_tester):
    """Test encoding attack handling."""
    result = adversarial_tester.test_encoding_attacks()
    
    assert result is not None
    assert result.test_id == "adversarial_9.3_encoding_attacks"
    assert result.category == "adversarial"
    # Test should pass (encoding attacks handled)
    assert result.status in [TestStatus.PASS, TestStatus.SKIP]


@requires_chromadb
def test_path_traversal(adversarial_tester):
    """Test path traversal protection."""
    result = adversarial_tester.test_path_traversal()
    
    assert result is not None
    assert result.test_id == "adversarial_9.4_path_traversal"
    assert result.category == "adversarial"
    # Test should pass (path traversal blocked)
    assert result.status in [TestStatus.PASS, TestStatus.SKIP]


@requires_chromadb
def test_prompt_injection(adversarial_tester):
    """Test prompt injection resistance."""
    result = adversarial_tester.test_prompt_injection()
    
    assert result is not None
    assert result.test_id == "adversarial_9.5_prompt_injection"
    assert result.category == "adversarial"
    # Test should pass (prompt injections blocked)
    assert result.status in [TestStatus.PASS, TestStatus.SKIP]


@requires_chromadb
def test_chunking_boundary_attacks(adversarial_tester):
    """Test chunking boundary attack handling."""
    result = adversarial_tester.test_chunking_boundary_attacks()
    
    assert result is not None
    assert result.test_id == "adversarial_9.6_chunking_boundary_attacks"
    assert result.category == "adversarial"
    # Test should pass (chunking attacks handled)
    assert result.status in [TestStatus.PASS, TestStatus.SKIP]


def test_run_all_tests(adversarial_tester):
    """Test running all adversarial tests."""
    results = adversarial_tester.run_tests()
    
    assert results is not None
    assert len(results) == 6  # 6 test methods
    
    # Verify all tests executed
    test_ids = [r.test_id for r in results]
    assert "adversarial_9.1_malicious_pdfs" in test_ids
    assert "adversarial_9.2_buffer_overflow" in test_ids
    assert "adversarial_9.3_encoding_attacks" in test_ids
    assert "adversarial_9.4_path_traversal" in test_ids
    assert "adversarial_9.5_prompt_injection" in test_ids
    assert "adversarial_9.6_chunking_boundary_attacks" in test_ids


def test_adversarial_config():
    """Test AdversarialTestConfig."""
    config = AdversarialTestConfig()
    
    assert config.malicious_pdf_count == 20
    assert config.buffer_overflow_sizes is not None
    assert len(config.buffer_overflow_sizes) == 3
    assert config.encoding_attack_count == 15
    assert config.path_traversal_patterns == 10
    assert config.prompt_injection_patterns == 15
    assert config.stage_b_injection_patterns == 25


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
