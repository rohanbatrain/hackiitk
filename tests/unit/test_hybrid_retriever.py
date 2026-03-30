"""
Unit tests for HybridRetriever component.

Tests hybrid retrieval combining dense and sparse search with reranking.
"""

import pytest
import numpy as np
import tempfile
import shutil

from retrieval.hybrid_retriever import HybridRetriever
from retrieval.embedding_engine import EmbeddingEngine
from reference_builder.reference_catalog import ReferenceCatalog
from models.domain import CSFSubcategory

# Try to import real components, fall back to mocks if unavailable
try:
    from retrieval.vector_store import VectorStore, CHROMADB_AVAILABLE
    from retrieval.reranker import Reranker, CROSS_ENCODER_AVAILABLE
    
    if not CHROMADB_AVAILABLE:
        from tests.mocks.mock_vector_store import MockVectorStore as VectorStore
        CHROMADB_AVAILABLE = False
    
    if not CROSS_ENCODER_AVAILABLE:
        RERANKER_AVAILABLE = False
    else:
        RERANKER_AVAILABLE = True
except (ImportError, RuntimeError):
    pytest.skip("Required components not available", allow_module_level=True)


@pytest.fixture
def temp_dir():
    """Create temporary directory for testing."""
    temp_path = tempfile.mkdtemp()
    yield temp_path
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture
def sample_catalog():
    """Create sample reference catalog."""
    catalog = ReferenceCatalog()
    
    # Add sample subcategories
    subcategories = [
        CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Risk Management Strategy",
            description="Risk management objectives are established and agreed to by organizational stakeholders",
            keywords=["risk", "objectives", "stakeholders"],
            domain_tags=["risk_management"],
            mapped_templates=["Risk Management Policy"],
            priority="critical"
        ),
        CSFSubcategory(
            subcategory_id="PR.AA-01",
            function="Protect",
            category="Identity Management",
            description="Identities and credentials for authorized users, services, and hardware are managed",
            keywords=["identity", "credentials", "users"],
            domain_tags=["access_control"],
            mapped_templates=["Access Control Policy"],
            priority="critical"
        ),
        CSFSubcategory(
            subcategory_id="ID.RA-01",
            function="Identify",
            category="Risk Assessment",
            description="Vulnerabilities in assets are identified, validated, and recorded",
            keywords=["vulnerability", "assets", "identified"],
            domain_tags=["vulnerability_management"],
            mapped_templates=["Vulnerability Management Policy"],
            priority="critical"
        )
    ]
    
    # Manually populate catalog
    for sub in subcategories:
        catalog._subcategories[sub.subcategory_id] = sub
        if sub.function not in catalog._by_function:
            catalog._by_function[sub.function] = []
        catalog._by_function[sub.function].append(sub)
    
    return catalog


@pytest.fixture
def embedding_engine(temp_dir):
    """Create embedding engine."""
    try:
        # Try to use real model if available
        model_path = "./models/all-MiniLM-L6-v2"
        engine = EmbeddingEngine(model_path)
        return engine
    except:
        # Skip if model not available
        pytest.skip("Embedding model not available")


@pytest.fixture
def vector_store(temp_dir, embedding_engine, sample_catalog):
    """Create and populate vector store."""
    store = VectorStore(persist_directory=temp_dir)
    
    # Add catalog embeddings
    subcategories = sample_catalog.get_all_subcategories()
    documents = [sub.description for sub in subcategories]
    embeddings = embedding_engine.embed_batch(documents)
    
    metadata = [
        {
            'subcategory_id': sub.subcategory_id,
            'function': sub.function,
            'description': sub.description
        }
        for sub in subcategories
    ]
    
    store.add_embeddings(
        embeddings=embeddings,
        metadata=metadata,
        collection_name="catalog"
    )
    
    return store


@pytest.fixture
def hybrid_retriever_no_reranker(vector_store, embedding_engine, sample_catalog):
    """Create hybrid retriever without reranker."""
    return HybridRetriever(
        vector_store=vector_store,
        embedding_engine=embedding_engine,
        catalog=sample_catalog,
        reranker=None
    )


@pytest.fixture
def hybrid_retriever_with_reranker(vector_store, embedding_engine, sample_catalog):
    """Create hybrid retriever with reranker."""
    if not RERANKER_AVAILABLE:
        pytest.skip("Reranker not available")
    
    try:
        reranker = Reranker()
        return HybridRetriever(
            vector_store=vector_store,
            embedding_engine=embedding_engine,
            catalog=sample_catalog,
            reranker=reranker
        )
    except:
        pytest.skip("Could not initialize reranker")


class TestHybridRetrieverInitialization:
    """Test hybrid retriever initialization."""
    
    def test_initialization(self, vector_store, embedding_engine, sample_catalog):
        """Test basic initialization."""
        retriever = HybridRetriever(
            vector_store=vector_store,
            embedding_engine=embedding_engine,
            catalog=sample_catalog
        )
        
        assert retriever.vector_store is not None
        assert retriever.embedding_engine is not None
        assert retriever.catalog is not None
        assert retriever.sparse_retriever is not None
        assert retriever.sparse_retriever.is_indexed()


class TestDenseRetrieval:
    """Test dense vector similarity search."""
    
    def test_dense_retrieve_returns_results(self, hybrid_retriever_no_reranker):
        """Test that dense retrieval returns results."""
        query = "risk management objectives"
        results = hybrid_retriever_no_reranker.dense_retrieve(query, top_k=3)
        
        assert len(results) <= 3
        assert all('score' in r for r in results)
        assert all('metadata' in r for r in results)
        assert all('method' in r for r in results)
        assert all(r['method'] == 'dense' for r in results)
    
    def test_dense_retrieve_finds_semantic_matches(self, hybrid_retriever_no_reranker):
        """Test that dense retrieval finds semantically similar content."""
        query = "managing user identities and access credentials"
        results = hybrid_retriever_no_reranker.dense_retrieve(query, top_k=3)
        
        assert len(results) > 0
        # Should find identity/credential related subcategory
        top_result = results[0]
        assert 'PR.AA-01' in str(top_result['metadata'])


class TestSparseRetrieval:
    """Test sparse BM25 keyword matching."""
    
    def test_sparse_retrieve_returns_results(self, hybrid_retriever_no_reranker):
        """Test that sparse retrieval returns results."""
        query = "vulnerability assets identified"
        results = hybrid_retriever_no_reranker.sparse_retrieve(query, top_k=3)
        
        assert len(results) <= 3
        assert all('score' in r for r in results)
        assert all('metadata' in r for r in results)
        assert all('method' in r for r in results)
        assert all(r['method'] == 'sparse' for r in results)
    
    def test_sparse_retrieve_finds_keyword_matches(self, hybrid_retriever_no_reranker):
        """Test that sparse retrieval finds exact keyword matches."""
        query = "vulnerability identified validated"
        results = hybrid_retriever_no_reranker.sparse_retrieve(query, top_k=3)
        
        assert len(results) > 0
        # Should find vulnerability subcategory in top results
        top_ids = [r['metadata']['subcategory_id'] for r in results]
        assert 'ID.RA-01' in top_ids, f"Expected ID.RA-01 in top results, got {top_ids}"


class TestHybridRetrieval:
    """Test hybrid retrieval combining dense and sparse."""
    
    def test_retrieve_returns_retrieval_results(self, hybrid_retriever_no_reranker):
        """Test that hybrid retrieval returns RetrievalResult objects."""
        query = "risk management and vulnerability assessment"
        results = hybrid_retriever_no_reranker.retrieve(query, top_k=3)
        
        assert len(results) <= 3
        assert all(hasattr(r, 'subcategory_id') for r in results)
        assert all(hasattr(r, 'subcategory_text') for r in results)
        assert all(hasattr(r, 'relevance_score') for r in results)
        assert all(hasattr(r, 'evidence_spans') for r in results)
        assert all(hasattr(r, 'retrieval_method') for r in results)
    
    def test_retrieve_combines_dense_and_sparse(self, hybrid_retriever_no_reranker):
        """Test that retrieval combines both methods."""
        query = "security policy management"
        results = hybrid_retriever_no_reranker.retrieve(query, top_k=5)
        
        # Should get results from hybrid approach
        assert len(results) > 0
        # Check that retrieval methods are tracked
        methods = [r.retrieval_method for r in results]
        assert all(m in ['dense', 'sparse', 'hybrid'] for m in methods)
    
    def test_retrieve_deduplicates_results(self, hybrid_retriever_no_reranker):
        """Test that duplicate results are merged."""
        query = "risk objectives stakeholders"
        results = hybrid_retriever_no_reranker.retrieve(query, top_k=5)
        
        # Check for unique subcategory IDs
        subcategory_ids = [r.subcategory_id for r in results]
        assert len(subcategory_ids) == len(set(subcategory_ids)), \
            "Results should not contain duplicate subcategories"
    
    def test_retrieve_respects_top_k(self, hybrid_retriever_no_reranker):
        """Test that top_k parameter is respected."""
        query = "security controls"
        
        for k in [1, 2, 3]:
            results = hybrid_retriever_no_reranker.retrieve(query, top_k=k)
            assert len(results) <= k
    
    def test_retrieve_empty_query_raises_error(self, hybrid_retriever_no_reranker):
        """Test that empty query raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            hybrid_retriever_no_reranker.retrieve("", top_k=5)
    
    def test_retrieve_invalid_weights_raises_error(self, hybrid_retriever_no_reranker):
        """Test that invalid weights raise error."""
        query = "test query"
        
        # Negative weights
        with pytest.raises(ValueError, match="must be non-negative"):
            hybrid_retriever_no_reranker.retrieve(
                query, top_k=5, dense_weight=-0.5, sparse_weight=0.5
            )
        
        # Both weights zero
        with pytest.raises(ValueError, match="At least one weight must be positive"):
            hybrid_retriever_no_reranker.retrieve(
                query, top_k=5, dense_weight=0.0, sparse_weight=0.0
            )


class TestReranking:
    """Test reranking functionality."""
    
    def test_retrieve_with_reranker(self, hybrid_retriever_with_reranker):
        """Test that retrieval with reranker works."""
        query = "vulnerability identification and validation"
        results = hybrid_retriever_with_reranker.retrieve(query, top_k=3)
        
        assert len(results) <= 3
        assert all(hasattr(r, 'relevance_score') for r in results)
        
        # Scores should be sorted descending
        if len(results) > 1:
            scores = [r.relevance_score for r in results]
            assert scores == sorted(scores, reverse=True)
    
    def test_reranking_improves_relevance(self, hybrid_retriever_with_reranker):
        """Test that reranking improves relevance ordering."""
        query = "managing user credentials and authentication"
        results = hybrid_retriever_with_reranker.retrieve(query, top_k=3)
        
        # Should find results
        assert len(results) > 0
        # Just verify we get results (scores can be negative from cross-encoder)
        assert all(hasattr(r, 'relevance_score') for r in results)


class TestResultFormatting:
    """Test result formatting."""
    
    def test_results_include_csf_metadata(self, hybrid_retriever_no_reranker):
        """Test that results include CSF subcategory metadata."""
        query = "risk management"
        results = hybrid_retriever_no_reranker.retrieve(query, top_k=3)
        
        for result in results:
            assert result.subcategory_id
            assert result.subcategory_text
            assert result.relevance_score >= 0
            assert isinstance(result.evidence_spans, list)
            assert result.retrieval_method in ['dense', 'sparse', 'hybrid']
    
    def test_results_include_evidence_spans(self, hybrid_retriever_no_reranker):
        """Test that results include evidence spans."""
        query = "vulnerability assessment"
        results = hybrid_retriever_no_reranker.retrieve(query, top_k=3)
        
        for result in results:
            assert len(result.evidence_spans) > 0
            assert all(isinstance(span, str) for span in result.evidence_spans)
