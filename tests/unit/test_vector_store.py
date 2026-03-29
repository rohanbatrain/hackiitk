"""
Unit tests for VectorStore component.

Tests basic functionality of vector storage, retrieval, and persistence.
"""

import pytest
import numpy as np
import tempfile
import shutil
import sys

# Try to import real VectorStore, fall back to mock if unavailable
try:
    from retrieval.vector_store import VectorStore, CHROMADB_AVAILABLE
    if not CHROMADB_AVAILABLE:
        raise ImportError("ChromaDB not available")
except (ImportError, RuntimeError):
    from tests.mocks.mock_vector_store import MockVectorStore as VectorStore
    CHROMADB_AVAILABLE = False
    pytest.skip(
        "ChromaDB not available (requires Python < 3.14). Using mock for basic validation.",
        allow_module_level=True
    )


@pytest.fixture
def temp_vector_store():
    """Create temporary vector store for testing."""
    temp_dir = tempfile.mkdtemp()
    store = VectorStore(persist_directory=temp_dir)
    yield store
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_embeddings():
    """Generate sample embeddings for testing."""
    return np.random.rand(5, 384).astype(np.float32)


@pytest.fixture
def sample_metadata():
    """Generate sample metadata for testing."""
    return [
        {
            "chunk_id": f"chunk_{i}",
            "source_text": f"Sample text {i}",
            "CSF_Subcategory": "GV.RM-01",
            "page_number": i + 1
        }
        for i in range(5)
    ]


class TestVectorStoreInitialization:
    """Test vector store initialization."""
    
    def test_initialization_creates_directory(self):
        """Test that initialization creates persist directory."""
        temp_dir = tempfile.mkdtemp()
        test_dir = f"{temp_dir}/test_store"
        
        try:
            store = VectorStore(persist_directory=test_dir)
            assert store.persist_directory == test_dir
            import os
            assert os.path.exists(test_dir)
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_initialization_with_existing_directory(self, temp_vector_store):
        """Test initialization with existing directory."""
        assert temp_vector_store.client is not None
        assert temp_vector_store.collections == {}


class TestAddEmbeddings:
    """Test adding embeddings to vector store."""
    
    def test_add_embeddings_basic(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test basic embedding addition."""
        temp_vector_store.add_embeddings(
            embeddings=sample_embeddings,
            metadata=sample_metadata,
            collection_name="test_collection"
        )
        
        count = temp_vector_store.get_collection_count("test_collection")
        assert count == len(sample_embeddings)
    
    def test_add_embeddings_with_custom_ids(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test adding embeddings with custom IDs."""
        custom_ids = [f"custom_id_{i}" for i in range(len(sample_embeddings))]
        
        temp_vector_store.add_embeddings(
            embeddings=sample_embeddings,
            metadata=sample_metadata,
            collection_name="test_collection",
            ids=custom_ids
        )
        
        # Verify by searching
        results = temp_vector_store.similarity_search(
            query_embedding=sample_embeddings[0],
            collection_name="test_collection",
            top_k=5
        )
        
        retrieved_ids = [r['id'] for r in results]
        assert all(rid in custom_ids for rid in retrieved_ids)
    
    def test_add_embeddings_mismatched_lengths_raises_error(self, temp_vector_store):
        """Test that mismatched embeddings and metadata lengths raise error."""
        embeddings = np.random.rand(5, 384).astype(np.float32)
        metadata = [{"chunk_id": f"chunk_{i}"} for i in range(3)]  # Wrong length
        
        with pytest.raises(ValueError, match="must match metadata count"):
            temp_vector_store.add_embeddings(
                embeddings=embeddings,
                metadata=metadata,
                collection_name="test_collection"
            )


class TestSimilaritySearch:
    """Test similarity search functionality."""
    
    def test_similarity_search_returns_results(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test that similarity search returns results."""
        temp_vector_store.add_embeddings(
            embeddings=sample_embeddings,
            metadata=sample_metadata,
            collection_name="test_collection"
        )
        
        query_embedding = sample_embeddings[0]
        results = temp_vector_store.similarity_search(
            query_embedding=query_embedding,
            collection_name="test_collection",
            top_k=3
        )
        
        assert len(results) == 3
        assert all('id' in r for r in results)
        assert all('distance' in r for r in results)
        assert all('metadata' in r for r in results)
    
    def test_similarity_search_respects_top_k(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test that top_k parameter is respected."""
        temp_vector_store.add_embeddings(
            embeddings=sample_embeddings,
            metadata=sample_metadata,
            collection_name="test_collection"
        )
        
        query_embedding = sample_embeddings[0]
        
        for k in [1, 2, 3, 5]:
            results = temp_vector_store.similarity_search(
                query_embedding=query_embedding,
                collection_name="test_collection",
                top_k=k
            )
            assert len(results) == k
    
    def test_similarity_search_nonexistent_collection_raises_error(self, temp_vector_store):
        """Test that searching nonexistent collection raises error."""
        query_embedding = np.random.rand(384).astype(np.float32)
        
        with pytest.raises(ValueError, match="does not exist"):
            temp_vector_store.similarity_search(
                query_embedding=query_embedding,
                collection_name="nonexistent",
                top_k=5
            )
    
    def test_similarity_search_empty_collection(self, temp_vector_store):
        """Test searching empty collection returns empty results."""
        # Create empty collection
        temp_vector_store._get_or_create_collection("empty_collection")
        
        query_embedding = np.random.rand(384).astype(np.float32)
        results = temp_vector_store.similarity_search(
            query_embedding=query_embedding,
            collection_name="empty_collection",
            top_k=5
        )
        
        assert len(results) == 0


class TestCollectionManagement:
    """Test collection management operations."""
    
    def test_load_collection_existing(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test loading existing collection."""
        # Add data to collection
        temp_vector_store.add_embeddings(
            embeddings=sample_embeddings,
            metadata=sample_metadata,
            collection_name="test_collection"
        )
        
        # Clear collections dict to simulate fresh load
        temp_vector_store.collections = {}
        
        # Load collection
        loaded = temp_vector_store.load_collection("test_collection")
        assert loaded is True
        assert "test_collection" in temp_vector_store.collections
    
    def test_load_collection_nonexistent(self, temp_vector_store):
        """Test loading nonexistent collection returns False."""
        loaded = temp_vector_store.load_collection("nonexistent")
        assert loaded is False
    
    def test_list_collections(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test listing all collections."""
        # Create multiple collections
        for i in range(3):
            temp_vector_store.add_embeddings(
                embeddings=sample_embeddings,
                metadata=sample_metadata,
                collection_name=f"collection_{i}"
            )
        
        collections = temp_vector_store.list_collections()
        assert len(collections) == 3
        assert all(f"collection_{i}" in collections for i in range(3))
    
    def test_get_collection_count(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test getting collection count."""
        temp_vector_store.add_embeddings(
            embeddings=sample_embeddings,
            metadata=sample_metadata,
            collection_name="test_collection"
        )
        
        count = temp_vector_store.get_collection_count("test_collection")
        assert count == len(sample_embeddings)
    
    def test_get_collection_count_nonexistent(self, temp_vector_store):
        """Test getting count of nonexistent collection returns 0."""
        count = temp_vector_store.get_collection_count("nonexistent")
        assert count == 0
    
    def test_delete_collection(self, temp_vector_store, sample_embeddings, sample_metadata):
        """Test deleting a collection."""
        temp_vector_store.add_embeddings(
            embeddings=sample_embeddings,
            metadata=sample_metadata,
            collection_name="test_collection"
        )
        
        # Verify collection exists
        assert temp_vector_store.get_collection_count("test_collection") > 0
        
        # Delete collection
        temp_vector_store.delete_collection("test_collection")
        
        # Verify collection is gone
        assert temp_vector_store.get_collection_count("test_collection") == 0


class TestPersistence:
    """Test persistence functionality."""
    
    def test_persistence_across_instances(self, sample_embeddings, sample_metadata):
        """Test that data persists across vector store instances."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create first instance and add data
            store1 = VectorStore(persist_directory=temp_dir)
            store1.add_embeddings(
                embeddings=sample_embeddings,
                metadata=sample_metadata,
                collection_name="persistent_collection"
            )
            
            original_count = store1.get_collection_count("persistent_collection")
            
            # Create second instance (simulates restart)
            store2 = VectorStore(persist_directory=temp_dir)
            loaded = store2.load_collection("persistent_collection")
            
            assert loaded is True
            loaded_count = store2.get_collection_count("persistent_collection")
            assert loaded_count == original_count
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
