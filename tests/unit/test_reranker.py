"""
Unit tests for Reranker component.

Tests cross-encoder reranking functionality.
"""

import pytest
import numpy as np

try:
    from retrieval.reranker import Reranker, CROSS_ENCODER_AVAILABLE
    if not CROSS_ENCODER_AVAILABLE:
        pytest.skip(
            "CrossEncoder not available. Install sentence-transformers for full functionality.",
            allow_module_level=True
        )
except ImportError:
    pytest.skip(
        "Reranker module not available",
        allow_module_level=True
    )


@pytest.fixture
def sample_documents():
    """Sample documents for reranking."""
    return [
        "Risk management objectives are established and agreed to by organizational stakeholders",
        "Identities and credentials for authorized users are managed by the organization",
        "Vulnerabilities in assets are identified, validated, and recorded",
        "The confidentiality, integrity, and availability of data-at-rest are protected",
        "Networks and network services are monitored to find potentially adverse events"
    ]


@pytest.fixture
def sample_metadata():
    """Sample metadata for documents."""
    return [
        {'subcategory_id': 'GV.RM-01', 'function': 'Govern'},
        {'subcategory_id': 'PR.AA-01', 'function': 'Protect'},
        {'subcategory_id': 'ID.RA-01', 'function': 'Identify'},
        {'subcategory_id': 'PR.DS-01', 'function': 'Protect'},
        {'subcategory_id': 'DE.CM-01', 'function': 'Detect'}
    ]


@pytest.fixture
def reranker():
    """Create reranker instance."""
    try:
        return Reranker(model_path="cross-encoder/ms-marco-MiniLM-L-6-v2")
    except Exception as e:
        pytest.skip(f"Could not load reranker model: {e}")


class TestRerankerInitialization:
    """Test reranker initialization."""
    
    def test_initialization_with_default_model(self):
        """Test initialization with default model."""
        try:
            reranker = Reranker()
            assert reranker.model is not None
            assert reranker.model_path is not None
        except Exception as e:
            pytest.skip(f"Model not available: {e}")
    
    def test_initialization_with_custom_model(self):
        """Test initialization with custom model path."""
        try:
            reranker = Reranker(model_path="cross-encoder/ms-marco-MiniLM-L-6-v2")
            assert reranker.model is not None
        except Exception as e:
            pytest.skip(f"Model not available: {e}")


class TestReranking:
    """Test reranking functionality."""
    
    def test_rerank_returns_results(self, reranker, sample_documents, sample_metadata):
        """Test that reranking returns results."""
        query = "risk management objectives"
        results = reranker.rerank(
            query=query,
            documents=sample_documents,
            metadata=sample_metadata,
            top_k=3
        )
        
        assert len(results) <= 3
        assert all('document' in r for r in results)
        assert all('score' in r for r in results)
        assert all('metadata' in r for r in results)
        assert all('rank' in r for r in results)
    
    def test_rerank_respects_top_k(self, reranker, sample_documents, sample_metadata):
        """Test that top_k parameter is respected."""
        query = "security policy"
        
        for k in [1, 2, 3, 5]:
            results = reranker.rerank(
                query=query,
                documents=sample_documents,
                metadata=sample_metadata,
                top_k=k
            )
            assert len(results) <= k
    
    def test_rerank_improves_relevance(self, reranker, sample_documents, sample_metadata):
        """Test that reranking improves relevance ordering."""
        query = "vulnerability identification and validation"
        
        results = reranker.rerank(
            query=query,
            documents=sample_documents,
            metadata=sample_metadata,
            top_k=5
        )
        
        # The vulnerability document should rank highly
        assert len(results) > 0
        # Check that vulnerability-related document is in top results
        top_docs = [r['document'] for r in results[:2]]
        assert any('vulnerabilit' in doc.lower() for doc in top_docs)
    
    def test_rerank_scores_are_sorted(self, reranker, sample_documents, sample_metadata):
        """Test that results are sorted by score descending."""
        query = "data protection encryption"
        results = reranker.rerank(
            query=query,
            documents=sample_documents,
            metadata=sample_metadata,
            top_k=5
        )
        
        if len(results) > 1:
            scores = [r['score'] for r in results]
            assert scores == sorted(scores, reverse=True), \
                "Results should be sorted by score descending"
    
    def test_rerank_ranks_are_sequential(self, reranker, sample_documents, sample_metadata):
        """Test that result ranks are sequential starting from 0."""
        query = "network monitoring"
        results = reranker.rerank(
            query=query,
            documents=sample_documents,
            metadata=sample_metadata,
            top_k=5
        )
        
        ranks = [r['rank'] for r in results]
        assert ranks == list(range(len(results))), \
            "Ranks should be sequential starting from 0"
    
    def test_rerank_mismatched_lengths_raises_error(self, reranker):
        """Test that mismatched documents and metadata raise error."""
        documents = ["doc1", "doc2", "doc3"]
        metadata = [{"id": "1"}, {"id": "2"}]  # Wrong length
        
        with pytest.raises(ValueError, match="must match metadata count"):
            reranker.rerank("query", documents, metadata, top_k=3)
    
    def test_rerank_empty_documents_raises_error(self, reranker):
        """Test that empty documents list raises error."""
        with pytest.raises(ValueError, match="Cannot rerank empty"):
            reranker.rerank("query", [], [], top_k=3)
    
    def test_rerank_empty_query_raises_error(self, reranker, sample_documents, sample_metadata):
        """Test that empty query raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            reranker.rerank("", sample_documents, sample_metadata, top_k=3)


class TestScorePairs:
    """Test direct pair scoring functionality."""
    
    def test_score_pairs_returns_scores(self, reranker):
        """Test that scoring pairs returns score array."""
        pairs = [
            ("risk management", "Risk management objectives are established"),
            ("data protection", "The confidentiality of data-at-rest is protected"),
            ("network security", "Networks are monitored for adverse events")
        ]
        
        scores = reranker.score_pairs(pairs)
        
        assert isinstance(scores, np.ndarray)
        assert len(scores) == len(pairs)
        assert all(isinstance(s, (float, np.floating)) for s in scores)
    
    def test_score_pairs_empty_raises_error(self, reranker):
        """Test that empty pairs list raises error."""
        with pytest.raises(ValueError, match="Cannot score empty"):
            reranker.score_pairs([])
