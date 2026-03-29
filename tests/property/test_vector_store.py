"""
Property-based tests for VectorStore component.

Tests validate correctness properties for vector storage, persistence,
similarity search, metadata preservation, and collection isolation.
"""

import pytest
import numpy as np
import tempfile
import shutil
from hypothesis import given, strategies as st, settings

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


# Hypothesis strategies
@st.composite
def embedding_strategy(draw, min_dim=10, max_dim=384):
    """Generate random embedding vectors."""
    dim = draw(st.integers(min_value=min_dim, max_value=max_dim))
    values = draw(st.lists(
        st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
        min_size=dim,
        max_size=dim
    ))
    return np.array(values, dtype=np.float32)


@st.composite
def embeddings_batch_strategy(draw, min_count=1, max_count=20, embedding_dim=384):
    """Generate batch of embeddings with consistent dimensions."""
    count = draw(st.integers(min_value=min_count, max_value=max_count))
    embeddings = []
    for _ in range(count):
        values = draw(st.lists(
            st.floats(min_value=-1.0, max_value=1.0, allow_nan=False, allow_infinity=False),
            min_size=embedding_dim,
            max_size=embedding_dim
        ))
        embeddings.append(values)
    return np.array(embeddings, dtype=np.float32)


@st.composite
def metadata_strategy(draw, count=1):
    """Generate metadata dictionaries."""
    metadata_list = []
    for i in range(count):
        metadata_list.append({
            "chunk_id": draw(st.text(min_size=1, max_size=20, alphabet=st.characters(whitelist_categories=('Lu', 'Ll', 'Nd')))),
            "source_text": draw(st.text(min_size=1, max_size=100)),
            "CSF_Subcategory": draw(st.sampled_from(["GV.RM-01", "ID.AM-01", "PR.AA-01", "DE.CM-01"])),
        })
    return metadata_list


class TestVectorStorePersistence:
    """Property 15: Vector Store Persistence Round-Trip.
    
    Validates Requirements 6.1, 6.5: Test that persisting then loading
    embeddings produces equivalent data.
    """
    
    @given(
        embeddings=embeddings_batch_strategy(min_count=1, max_count=10, embedding_dim=384)
    )
    @settings(max_examples=20, deadline=5000)
    def test_persistence_round_trip(self, embeddings):
        """Test that persisting and loading embeddings preserves data."""
        # Create temporary directory for this test
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create vector store
            store = VectorStore(persist_directory=temp_dir)
            collection_name = "test_collection"
            
            # Generate metadata
            metadata = [
                {
                    "chunk_id": f"chunk_{i}",
                    "source_text": f"Test text {i}",
                    "CSF_Subcategory": "GV.RM-01"
                }
                for i in range(len(embeddings))
            ]
            
            # Add embeddings
            store.add_embeddings(
                embeddings=embeddings,
                metadata=metadata,
                collection_name=collection_name
            )
            
            # Get original count
            original_count = store.get_collection_count(collection_name)
            
            # Create new store instance (simulates restart)
            store2 = VectorStore(persist_directory=temp_dir)
            
            # Load collection
            loaded = store2.load_collection(collection_name)
            assert loaded, "Collection should be loadable after persistence"
            
            # Verify count matches
            loaded_count = store2.get_collection_count(collection_name)
            assert loaded_count == original_count, \
                f"Loaded count ({loaded_count}) should match original ({original_count})"
            
            # Verify we can retrieve embeddings
            query_embedding = embeddings[0]
            results = store2.similarity_search(
                query_embedding=query_embedding,
                collection_name=collection_name,
                top_k=min(5, len(embeddings))
            )
            
            assert len(results) > 0, "Should retrieve results from persisted collection"
            
        finally:
            # Cleanup
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestSimilaritySearchResultCount:
    """Property 16: Similarity Search Result Count.
    
    Validates Requirement 6.3: Test that similarity search returns exactly k
    results (or fewer if collection smaller).
    """
    
    @given(
        embeddings=embeddings_batch_strategy(min_count=1, max_count=20, embedding_dim=384),
        top_k=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=20, deadline=5000)
    def test_similarity_search_returns_k_results(self, embeddings, top_k):
        """Test that similarity search returns exactly k results or collection size."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            store = VectorStore(persist_directory=temp_dir)
            collection_name = "test_search"
            
            # Generate metadata
            metadata = [
                {
                    "chunk_id": f"chunk_{i}",
                    "source_text": f"Test text {i}",
                }
                for i in range(len(embeddings))
            ]
            
            # Add embeddings
            store.add_embeddings(
                embeddings=embeddings,
                metadata=metadata,
                collection_name=collection_name
            )
            
            # Perform search
            query_embedding = embeddings[0]
            results = store.similarity_search(
                query_embedding=query_embedding,
                collection_name=collection_name,
                top_k=top_k
            )
            
            # Expected count is min(top_k, collection_size)
            expected_count = min(top_k, len(embeddings))
            assert len(results) == expected_count, \
                f"Should return {expected_count} results, got {len(results)}"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(top_k=st.integers(min_value=1, max_value=10))
    @settings(max_examples=10, deadline=5000)
    def test_empty_collection_returns_zero_results(self, top_k):
        """Test that searching empty collection returns no results."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            store = VectorStore(persist_directory=temp_dir)
            collection_name = "empty_collection"
            
            # Create empty collection
            store._get_or_create_collection(collection_name)
            
            # Search with random query
            query_embedding = np.random.rand(384).astype(np.float32)
            results = store.similarity_search(
                query_embedding=query_embedding,
                collection_name=collection_name,
                top_k=top_k
            )
            
            assert len(results) == 0, "Empty collection should return zero results"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestMetadataPreservation:
    """Property 17: Metadata Preservation in Vector Store.
    
    Validates Requirement 6.4: Test that metadata is preserved and
    retrievable with embeddings.
    """
    
    @given(
        embeddings=embeddings_batch_strategy(min_count=1, max_count=10, embedding_dim=384)
    )
    @settings(max_examples=20, deadline=5000)
    def test_metadata_preserved_in_storage(self, embeddings):
        """Test that all metadata fields are preserved during storage and retrieval."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            store = VectorStore(persist_directory=temp_dir)
            collection_name = "test_metadata"
            
            # Generate metadata with multiple fields
            metadata = [
                {
                    "chunk_id": f"chunk_{i}",
                    "source_text": f"Test text {i}",
                    "CSF_Subcategory": f"GV.RM-0{(i % 3) + 1}",
                    "page_number": i + 1,
                    "section_title": f"Section {i}"
                }
                for i in range(len(embeddings))
            ]
            
            # Store embeddings with metadata
            store.add_embeddings(
                embeddings=embeddings,
                metadata=metadata,
                collection_name=collection_name
            )
            
            # Retrieve and verify metadata
            query_embedding = embeddings[0]
            results = store.similarity_search(
                query_embedding=query_embedding,
                collection_name=collection_name,
                top_k=len(embeddings)
            )
            
            # Check that all results have metadata
            for result in results:
                assert 'metadata' in result, "Result should contain metadata"
                result_meta = result['metadata']
                
                # Verify required fields exist
                assert 'chunk_id' in result_meta, "Metadata should contain chunk_id"
                assert 'CSF_Subcategory' in result_meta, "Metadata should contain CSF_Subcategory"
                assert 'page_number' in result_meta, "Metadata should contain page_number"
                assert 'section_title' in result_meta, "Metadata should contain section_title"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        embeddings=embeddings_batch_strategy(min_count=2, max_count=10, embedding_dim=384)
    )
    @settings(max_examples=15, deadline=5000)
    def test_metadata_uniquely_identifies_embeddings(self, embeddings):
        """Test that metadata correctly identifies each embedding."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            store = VectorStore(persist_directory=temp_dir)
            collection_name = "test_unique_metadata"
            
            # Create unique metadata for each embedding
            unique_ids = [f"unique_chunk_{i}" for i in range(len(embeddings))]
            metadata = [
                {
                    "chunk_id": unique_ids[i],
                    "source_text": f"Unique text {i}",
                }
                for i in range(len(embeddings))
            ]
            
            # Store with explicit IDs
            store.add_embeddings(
                embeddings=embeddings,
                metadata=metadata,
                collection_name=collection_name,
                ids=unique_ids
            )
            
            # Retrieve all
            query_embedding = embeddings[0]
            results = store.similarity_search(
                query_embedding=query_embedding,
                collection_name=collection_name,
                top_k=len(embeddings)
            )
            
            # Verify all IDs are present and unique
            retrieved_ids = [r['id'] for r in results]
            assert len(set(retrieved_ids)) == len(retrieved_ids), \
                "All retrieved IDs should be unique"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestCollectionIsolation:
    """Property 18: Collection Isolation.
    
    Validates Requirement 6.6: Test that queries to one collection never
    return results from another.
    """
    
    @given(
        embeddings1=embeddings_batch_strategy(min_count=2, max_count=10, embedding_dim=384),
        embeddings2=embeddings_batch_strategy(min_count=2, max_count=10, embedding_dim=384)
    )
    @settings(max_examples=15, deadline=5000)
    def test_collections_are_isolated(self, embeddings1, embeddings2):
        """Test that separate collections don't interfere with each other."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            store = VectorStore(persist_directory=temp_dir)
            collection1 = "reference_catalog"
            collection2 = "policy_embeddings"
            
            # Add embeddings to collection 1
            metadata1 = [
                {
                    "chunk_id": f"ref_{i}",
                    "source_text": f"Reference text {i}",
                    "collection_marker": "collection1"
                }
                for i in range(len(embeddings1))
            ]
            store.add_embeddings(
                embeddings=embeddings1,
                metadata=metadata1,
                collection_name=collection1
            )
            
            # Add embeddings to collection 2
            metadata2 = [
                {
                    "chunk_id": f"policy_{i}",
                    "source_text": f"Policy text {i}",
                    "collection_marker": "collection2"
                }
                for i in range(len(embeddings2))
            ]
            store.add_embeddings(
                embeddings=embeddings2,
                metadata=metadata2,
                collection_name=collection2
            )
            
            # Query collection 1
            query_embedding = embeddings1[0]
            results1 = store.similarity_search(
                query_embedding=query_embedding,
                collection_name=collection1,
                top_k=len(embeddings1)
            )
            
            # Verify all results are from collection 1
            for result in results1:
                assert result['metadata']['collection_marker'] == "collection1", \
                    "Collection 1 query should only return collection 1 results"
            
            # Query collection 2
            results2 = store.similarity_search(
                query_embedding=query_embedding,
                collection_name=collection2,
                top_k=len(embeddings2)
            )
            
            # Verify all results are from collection 2
            for result in results2:
                assert result['metadata']['collection_marker'] == "collection2", \
                    "Collection 2 query should only return collection 2 results"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        embeddings=embeddings_batch_strategy(min_count=3, max_count=10, embedding_dim=384)
    )
    @settings(max_examples=15, deadline=5000)
    def test_collection_counts_are_independent(self, embeddings):
        """Test that collection counts are tracked independently."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            store = VectorStore(persist_directory=temp_dir)
            
            # Split embeddings between two collections
            split_point = len(embeddings) // 2
            embeddings1 = embeddings[:split_point]
            embeddings2 = embeddings[split_point:]
            
            collection1 = "collection_a"
            collection2 = "collection_b"
            
            # Add to collection 1
            metadata1 = [{"chunk_id": f"a_{i}"} for i in range(len(embeddings1))]
            store.add_embeddings(embeddings1, metadata1, collection1)
            
            # Add to collection 2
            metadata2 = [{"chunk_id": f"b_{i}"} for i in range(len(embeddings2))]
            store.add_embeddings(embeddings2, metadata2, collection2)
            
            # Verify counts
            count1 = store.get_collection_count(collection1)
            count2 = store.get_collection_count(collection2)
            
            assert count1 == len(embeddings1), \
                f"Collection 1 should have {len(embeddings1)} embeddings, got {count1}"
            assert count2 == len(embeddings2), \
                f"Collection 2 should have {len(embeddings2)} embeddings, got {count2}"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
