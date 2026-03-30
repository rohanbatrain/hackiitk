"""
Tests for Component Stress Tester

Validates component-specific stress testing functionality.
"""

import pytest
import tempfile
from pathlib import Path

from tests.extreme.engines.component_stress_tester import (
    ComponentStressTester,
    ComponentStressConfig
)
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.data_generator import TestDataGenerator


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def component_tester(temp_output_dir):
    """Create component stress tester instance."""
    config = ComponentStressConfig(
        sequential_searches=100,  # Reduced for testing
        concurrent_searches=10,
        max_top_k=100,
        embedding_sizes=[100, 500],
        output_file_count=10,
        audit_log_entries=100,
        concurrent_audit_writes=10
    )
    
    metrics = MetricsCollector()
    data_gen = TestDataGenerator()
    
    return ComponentStressTester(
        config=config,
        metrics_collector=metrics,
        data_generator=data_gen,
        output_dir=temp_output_dir
    )


def test_component_tester_initialization(component_tester):
    """Test component tester initializes correctly."""
    assert component_tester is not None
    assert component_tester.config.sequential_searches == 100
    assert component_tester.config.concurrent_searches == 10


def test_sequential_similarity_searches(component_tester):
    """Test sequential similarity searches."""
    result = component_tester.test_sequential_similarity_searches()
    
    assert result is not None
    assert result.test_id == "component_stress_sequential_searches"
    assert "44.1" in result.requirement_id


def test_concurrent_similarity_searches(component_tester):
    """Test concurrent similarity searches."""
    result = component_tester.test_concurrent_similarity_searches()
    
    assert result is not None
    assert result.test_id == "component_stress_concurrent_searches"
    assert "44.2" in result.requirement_id


def test_large_top_k(component_tester):
    """Test large top_k values."""
    result = component_tester.test_large_top_k()
    
    assert result is not None
    assert result.test_id == "component_stress_large_top_k"
    assert "44.3" in result.requirement_id


def test_query_latency_scaling(component_tester):
    """Test query latency scaling."""
    result = component_tester.test_query_latency_scaling()
    
    assert result is not None
    assert result.test_id == "component_stress_query_latency_scaling"
    assert "44.4" in result.requirement_id
    assert "44.5" in result.requirement_id



def test_dense_retrieval_failure(component_tester):
    """Test dense retrieval failure fallback."""
    result = component_tester.test_dense_retrieval_failure()
    
    assert result is not None
    assert result.test_id == "component_stress_dense_retrieval_failure"
    assert "45.1" in result.requirement_id


def test_sparse_retrieval_failure(component_tester):
    """Test sparse retrieval failure fallback."""
    result = component_tester.test_sparse_retrieval_failure()
    
    assert result is not None
    assert result.test_id == "component_stress_sparse_retrieval_failure"
    assert "45.2" in result.requirement_id


def test_reranking_failure(component_tester):
    """Test reranking failure fallback."""
    result = component_tester.test_reranking_failure()
    
    assert result is not None
    assert result.test_id == "component_stress_reranking_failure"
    assert "45.3" in result.requirement_id


def test_empty_result_handling(component_tester):
    """Test empty result handling."""
    result = component_tester.test_empty_result_handling()
    
    assert result is not None
    assert result.test_id == "component_stress_empty_result_handling"
    assert "45.4" in result.requirement_id
    assert "45.5" in result.requirement_id


def test_keyword_without_content(component_tester):
    """Test keywords without relevant content."""
    result = component_tester.test_keyword_without_content()
    
    assert result is not None
    assert result.test_id == "component_stress_keyword_without_content"
    assert "30.1" in result.requirement_id
    assert "54.5" in result.requirement_id


def test_content_without_keywords(component_tester):
    """Test relevant content without keywords."""
    result = component_tester.test_content_without_keywords()
    
    assert result is not None
    assert result.test_id == "component_stress_content_without_keywords"
    assert "30.2" in result.requirement_id
    assert "54.1" in result.requirement_id


def test_misleading_text(component_tester):
    """Test intentionally misleading text."""
    result = component_tester.test_misleading_text()
    
    assert result is not None
    assert result.test_id == "component_stress_misleading_text"
    assert "30.3" in result.requirement_id
    assert "30.4" in result.requirement_id


def test_keyword_stuffing(component_tester):
    """Test keyword stuffing and spam."""
    result = component_tester.test_keyword_stuffing()
    
    assert result is not None
    assert result.test_id == "component_stress_keyword_stuffing"
    assert "30.5" in result.requirement_id


def test_rerank_many_candidates(component_tester):
    """Test reranking many candidates."""
    result = component_tester.test_rerank_many_candidates()
    
    assert result is not None
    assert result.test_id == "component_stress_rerank_many_candidates"
    assert "40.1" in result.requirement_id


def test_rerank_identical_scores(component_tester):
    """Test reranking with identical scores."""
    result = component_tester.test_rerank_identical_scores()
    
    assert result is not None
    assert result.test_id == "component_stress_rerank_identical_scores"
    assert "40.2" in result.requirement_id


def test_rerank_long_text(component_tester):
    """Test reranking with long text."""
    result = component_tester.test_rerank_long_text()
    
    assert result is not None
    assert result.test_id == "component_stress_rerank_long_text"
    assert "40.3" in result.requirement_id


def test_rerank_relevance_improvement(component_tester):
    """Test reranking improves relevance."""
    result = component_tester.test_rerank_relevance_improvement()
    
    assert result is not None
    assert result.test_id == "component_stress_rerank_relevance_improvement"
    assert "40.4" in result.requirement_id
    assert "40.5" in result.requirement_id


def test_conflicting_scores(component_tester):
    """Test conflicting lexical/semantic scores."""
    result = component_tester.test_conflicting_scores()
    
    assert result is not None
    assert result.test_id == "component_stress_conflicting_scores"
    assert "41.1" in result.requirement_id
    assert "41.2" in result.requirement_id


def test_exact_threshold_scores(component_tester):
    """Test exact threshold scores."""
    result = component_tester.test_exact_threshold_scores()
    
    assert result is not None
    assert result.test_id == "component_stress_exact_threshold_scores"
    assert "41.3" in result.requirement_id


def test_score_boundary_combinations(component_tester):
    """Test score boundary combinations."""
    result = component_tester.test_score_boundary_combinations()
    
    assert result is not None
    assert result.test_id == "component_stress_score_boundary_combinations"
    assert "41.4" in result.requirement_id
    assert "41.5" in result.requirement_id


def test_run_all_tests(component_tester):
    """Test running all component stress tests."""
    results = component_tester.run_tests()
    
    assert len(results) > 0
    assert all(r.test_id is not None for r in results)
    assert all(r.category is not None for r in results)
