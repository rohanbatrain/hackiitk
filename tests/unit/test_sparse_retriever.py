"""
Unit tests for SparseRetriever component.

Tests BM25-based keyword retrieval functionality.
"""

import pytest
from retrieval.sparse_retriever import SparseRetriever


@pytest.fixture
def sample_documents():
    """Sample CSF subcategory descriptions for testing."""
    return [
        "Risk management objectives are established and agreed to by organizational stakeholders",
        "Identities and credentials for authorized users, services, and hardware are managed by the organization",
        "Vulnerabilities in assets are identified, validated, and recorded",
        "The confidentiality, integrity, and availability of data-at-rest are protected",
        "Networks and network services are monitored to find potentially adverse events"
    ]


@pytest.fixture
def sample_metadata():
    """Sample metadata for documents."""
    return [
        {'subcategory_id': 'GV.RM-01', 'function': 'Govern', 'keywords': ['risk', 'objectives']},
        {'subcategory_id': 'PR.AA-01', 'function': 'Protect', 'keywords': ['identity', 'credentials']},
        {'subcategory_id': 'ID.RA-01', 'function': 'Identify', 'keywords': ['vulnerability', 'assets']},
        {'subcategory_id': 'PR.DS-01', 'function': 'Protect', 'keywords': ['data', 'encryption']},
        {'subcategory_id': 'DE.CM-01', 'function': 'Detect', 'keywords': ['monitoring', 'network']}
    ]


@pytest.fixture
def indexed_retriever(sample_documents, sample_metadata):
    """Create and return indexed sparse retriever."""
    retriever = SparseRetriever()
    retriever.index_documents(sample_documents, sample_metadata)
    return retriever


class TestSparseRetrieverInitialization:
    """Test sparse retriever initialization."""
    
    def test_initialization(self):
        """Test basic initialization."""
        retriever = SparseRetriever()
        assert retriever.corpus == []
        assert retriever.corpus_metadata == []
        assert retriever.bm25 is None
        assert not retriever.is_indexed()


class TestIndexing:
    """Test document indexing."""
    
    def test_index_documents_basic(self, sample_documents, sample_metadata):
        """Test basic document indexing."""
        retriever = SparseRetriever()
        retriever.index_documents(sample_documents, sample_metadata)
        
        assert retriever.is_indexed()
        assert retriever.get_corpus_size() == len(sample_documents)
        assert retriever.bm25 is not None
    
    def test_index_documents_mismatched_lengths_raises_error(self):
        """Test that mismatched documents and metadata raise error."""
        retriever = SparseRetriever()
        documents = ["doc1", "doc2", "doc3"]
        metadata = [{"id": "1"}, {"id": "2"}]  # Wrong length
        
        with pytest.raises(ValueError, match="must match metadata count"):
            retriever.index_documents(documents, metadata)
    
    def test_index_empty_documents_raises_error(self):
        """Test that indexing empty list raises error."""
        retriever = SparseRetriever()
        
        with pytest.raises(ValueError, match="Cannot index empty"):
            retriever.index_documents([], [])


class TestRetrieval:
    """Test BM25 retrieval functionality."""
    
    def test_retrieve_returns_results(self, indexed_retriever):
        """Test that retrieval returns results."""
        query = "risk management objectives"
        results = indexed_retriever.retrieve(query, top_k=3)
        
        assert len(results) <= 3
        assert all('document' in r for r in results)
        assert all('score' in r for r in results)
        assert all('metadata' in r for r in results)
        assert all('rank' in r for r in results)
    
    def test_retrieve_keyword_matching(self, indexed_retriever):
        """Test that BM25 finds exact keyword matches."""
        # Query with specific keywords
        query = "vulnerability assets identified"
        results = indexed_retriever.retrieve(query, top_k=5)
        
        # The vulnerability document should rank highly
        assert len(results) > 0
        top_result = results[0]
        assert 'vulnerability' in top_result['document'].lower() or \
               'vulnerabilities' in top_result['document'].lower()
    
    def test_retrieve_respects_top_k(self, indexed_retriever):
        """Test that top_k parameter is respected."""
        query = "security policy management"
        
        for k in [1, 2, 3, 5]:
            results = indexed_retriever.retrieve(query, top_k=k)
            assert len(results) <= k
    
    def test_retrieve_without_indexing_raises_error(self):
        """Test that retrieval without indexing raises error."""
        retriever = SparseRetriever()
        
        with pytest.raises(RuntimeError, match="must be indexed"):
            retriever.retrieve("test query", top_k=5)
    
    def test_retrieve_empty_query_raises_error(self, indexed_retriever):
        """Test that empty query raises error."""
        with pytest.raises(ValueError, match="cannot be empty"):
            indexed_retriever.retrieve("", top_k=5)
    
    def test_retrieve_scores_are_sorted(self, indexed_retriever):
        """Test that results are sorted by score descending."""
        query = "risk management security"
        results = indexed_retriever.retrieve(query, top_k=5)
        
        if len(results) > 1:
            scores = [r['score'] for r in results]
            assert scores == sorted(scores, reverse=True), \
                "Results should be sorted by score descending"
    
    def test_retrieve_ranks_are_sequential(self, indexed_retriever):
        """Test that result ranks are sequential starting from 0."""
        query = "data protection encryption"
        results = indexed_retriever.retrieve(query, top_k=5)
        
        ranks = [r['rank'] for r in results]
        assert ranks == list(range(len(results))), \
            "Ranks should be sequential starting from 0"


class TestCorpusManagement:
    """Test corpus management functionality."""
    
    def test_get_corpus_size(self, indexed_retriever):
        """Test getting corpus size."""
        size = indexed_retriever.get_corpus_size()
        assert size == 5
    
    def test_get_corpus_size_empty(self):
        """Test corpus size for unindexed retriever."""
        retriever = SparseRetriever()
        assert retriever.get_corpus_size() == 0
