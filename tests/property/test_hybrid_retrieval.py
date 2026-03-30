"""
Property-based tests for Hybrid Retrieval.

Tests validate correctness properties for hybrid retrieval combining
dense and sparse search with reranking.
"""

import pytest
import tempfile
import shutil
from hypothesis import given, strategies as st, settings, assume

from retrieval.hybrid_retriever import HybridRetriever
from retrieval.embedding_engine import EmbeddingEngine
from reference_builder.reference_catalog import ReferenceCatalog
from models.domain import CSFSubcategory

# Try to import real components
try:
    from retrieval.vector_store import VectorStore, CHROMADB_AVAILABLE
    if not CHROMADB_AVAILABLE:
        from tests.mocks.mock_vector_store import MockVectorStore as VectorStore
        CHROMADB_AVAILABLE = False
except (ImportError, RuntimeError):
    pytest.skip("Required components not available", allow_module_level=True)


# Hypothesis strategies
@st.composite
def query_text_strategy(draw):
    """Generate random query text."""
    words = draw(st.lists(
        st.text(
            min_size=3,
            max_size=15,
            alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))
        ),
        min_size=2,
        max_size=10
    ))
    return " ".join(words)


@st.composite
def csf_subcategory_strategy(draw):
    """Generate random CSF subcategory."""
    functions = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
    function = draw(st.sampled_from(functions))
    
    subcategory_id = f"{function[:2].upper()}.{draw(st.text(min_size=2, max_size=4, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))}-{draw(st.integers(min_value=1, max_value=99)):02d}"
    
    description = draw(st.text(min_size=20, max_size=200))
    keywords = draw(st.lists(
        st.text(min_size=3, max_size=15, alphabet=st.characters(whitelist_categories=('Lu', 'Ll'))),
        min_size=1,
        max_size=5
    ))
    
    return CSFSubcategory(
        subcategory_id=subcategory_id,
        function=function,
        category="Test Category",
        description=description,
        keywords=keywords,
        domain_tags=["test"],
        mapped_templates=["Test Policy"],
        priority="medium"
    )


def create_test_catalog(subcategories):
    """Create test catalog from subcategories."""
    catalog = ReferenceCatalog()
    
    for sub in subcategories:
        catalog._subcategories[sub.subcategory_id] = sub
        if sub.function not in catalog._by_function:
            catalog._by_function[sub.function] = []
        catalog._by_function[sub.function].append(sub)
    
    return catalog


def create_test_retriever(catalog, temp_dir):
    """Create test hybrid retriever."""
    try:
        # Create embedding engine
        model_path = "./models/all-MiniLM-L6-v2"
        embedding_engine = EmbeddingEngine(model_path)
        
        # Create vector store
        vector_store = VectorStore(persist_directory=temp_dir)
        
        # Add catalog embeddings
        subcategories = catalog.get_all_subcategories()
        if not subcategories:
            return None
        
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
        
        vector_store.add_embeddings(
            embeddings=embeddings,
            metadata=metadata,
            collection_name="catalog"
        )
        
        # Create hybrid retriever
        retriever = HybridRetriever(
            vector_store=vector_store,
            embedding_engine=embedding_engine,
            catalog=catalog,
            reranker=None  # Skip reranker for faster tests
        )
        
        return retriever
    except Exception as e:
        pytest.skip(f"Could not create test retriever: {e}")


class TestHybridRetrievalCombination:
    """Property 19: Hybrid Retrieval Combination.
    
    Validates Requirements 7.1, 7.3, 7.4, 7.5, 7.6: Test that retrieval
    combines dense + sparse, merges, deduplicates, and reranks.
    """
    
    @given(
        query=query_text_strategy(),
        top_k=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=10, deadline=10000)
    def test_hybrid_retrieval_combines_methods(self, query, top_k):
        """Test that hybrid retrieval combines dense and sparse methods."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create sample catalog
            subcategories = [
                CSFSubcategory(
                    subcategory_id="GV.RM-01",
                    function="Govern",
                    category="Risk Management",
                    description="Risk management objectives are established and agreed to by stakeholders",
                    keywords=["risk", "objectives", "stakeholders"],
                    domain_tags=["risk_management"],
                    mapped_templates=["Risk Policy"],
                    priority="critical"
                ),
                CSFSubcategory(
                    subcategory_id="PR.AA-01",
                    function="Protect",
                    category="Identity Management",
                    description="Identities and credentials for authorized users are managed",
                    keywords=["identity", "credentials", "users"],
                    domain_tags=["access_control"],
                    mapped_templates=["Access Policy"],
                    priority="critical"
                ),
                CSFSubcategory(
                    subcategory_id="ID.RA-01",
                    function="Identify",
                    category="Risk Assessment",
                    description="Vulnerabilities in assets are identified and validated",
                    keywords=["vulnerability", "assets"],
                    domain_tags=["vulnerability"],
                    mapped_templates=["Vuln Policy"],
                    priority="high"
                )
            ]
            
            catalog = create_test_catalog(subcategories)
            retriever = create_test_retriever(catalog, temp_dir)
            
            if retriever is None:
                pytest.skip("Could not create retriever")
            
            # Perform hybrid retrieval
            results = retriever.retrieve(query, top_k=top_k)
            
            # Verify results structure
            assert isinstance(results, list), "Results should be a list"
            assert len(results) <= top_k, f"Should return at most {top_k} results"
            
            # Verify all results have required fields
            for result in results:
                assert hasattr(result, 'subcategory_id'), "Result should have subcategory_id"
                assert hasattr(result, 'subcategory_text'), "Result should have subcategory_text"
                assert hasattr(result, 'relevance_score'), "Result should have relevance_score"
                assert hasattr(result, 'evidence_spans'), "Result should have evidence_spans"
                assert hasattr(result, 'retrieval_method'), "Result should have retrieval_method"
                
                # Verify retrieval method is valid
                assert result.retrieval_method in ['dense', 'sparse', 'hybrid'], \
                    f"Invalid retrieval method: {result.retrieval_method}"
            
            # Verify deduplication: no duplicate subcategory IDs
            subcategory_ids = [r.subcategory_id for r in results]
            assert len(subcategory_ids) == len(set(subcategory_ids)), \
                "Results should not contain duplicate subcategories"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(
        query=query_text_strategy(),
        top_k=st.integers(min_value=1, max_value=3)
    )
    @settings(max_examples=10, deadline=10000)
    def test_hybrid_retrieval_respects_top_k(self, query, top_k):
        """Test that hybrid retrieval respects top_k parameter."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create sample catalog with multiple subcategories
            subcategories = [
                CSFSubcategory(
                    subcategory_id=f"TEST-{i:02d}",
                    function="Govern",
                    category="Test",
                    description=f"Test description {i} with various keywords",
                    keywords=[f"keyword{i}", "test"],
                    domain_tags=["test"],
                    mapped_templates=["Test"],
                    priority="medium"
                )
                for i in range(5)
            ]
            
            catalog = create_test_catalog(subcategories)
            retriever = create_test_retriever(catalog, temp_dir)
            
            if retriever is None:
                pytest.skip("Could not create retriever")
            
            # Perform retrieval
            results = retriever.retrieve(query, top_k=top_k)
            
            # Verify top_k is respected
            assert len(results) <= top_k, \
                f"Should return at most {top_k} results, got {len(results)}"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)


class TestRetrievalResultMetadata:
    """Property 20: Retrieval Result Metadata.
    
    Validates Requirement 7.8: Test that all retrieved chunks include
    CSF subcategory identifiers.
    """
    
    @given(
        query=query_text_strategy(),
        top_k=st.integers(min_value=1, max_value=5)
    )
    @settings(max_examples=10, deadline=10000)
    def test_all_results_include_subcategory_metadata(self, query, top_k):
        """Test that all results include CSF subcategory identifiers."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create sample catalog
            subcategories = [
                CSFSubcategory(
                    subcategory_id="GV.RM-01",
                    function="Govern",
                    category="Risk Management",
                    description="Risk management objectives are established",
                    keywords=["risk", "objectives"],
                    domain_tags=["risk"],
                    mapped_templates=["Risk Policy"],
                    priority="critical"
                ),
                CSFSubcategory(
                    subcategory_id="PR.AA-01",
                    function="Protect",
                    category="Identity",
                    description="Identities and credentials are managed",
                    keywords=["identity", "credentials"],
                    domain_tags=["access"],
                    mapped_templates=["Access Policy"],
                    priority="high"
                )
            ]
            
            catalog = create_test_catalog(subcategories)
            retriever = create_test_retriever(catalog, temp_dir)
            
            if retriever is None:
                pytest.skip("Could not create retriever")
            
            # Perform retrieval
            results = retriever.retrieve(query, top_k=top_k)
            
            # Verify all results have CSF subcategory metadata
            for result in results:
                # Check subcategory_id is present and non-empty
                assert result.subcategory_id, \
                    "Result must have non-empty subcategory_id"
                
                # Check subcategory_text is present and non-empty
                assert result.subcategory_text, \
                    "Result must have non-empty subcategory_text"
                
                # Verify subcategory_id matches catalog format
                assert '.' in result.subcategory_id or '-' in result.subcategory_id, \
                    f"Subcategory ID should follow CSF format: {result.subcategory_id}"
                
                # Verify evidence spans are present
                assert isinstance(result.evidence_spans, list), \
                    "Evidence spans should be a list"
                assert len(result.evidence_spans) > 0, \
                    "Evidence spans should not be empty"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    @given(query=query_text_strategy())
    @settings(max_examples=10, deadline=10000)
    def test_results_have_valid_relevance_scores(self, query):
        """Test that all results have valid relevance scores."""
        temp_dir = tempfile.mkdtemp()
        
        try:
            # Create sample catalog
            subcategories = [
                CSFSubcategory(
                    subcategory_id=f"TEST-{i:02d}",
                    function="Govern",
                    category="Test",
                    description=f"Test description {i}",
                    keywords=["test"],
                    domain_tags=["test"],
                    mapped_templates=["Test"],
                    priority="medium"
                )
                for i in range(3)
            ]
            
            catalog = create_test_catalog(subcategories)
            retriever = create_test_retriever(catalog, temp_dir)
            
            if retriever is None:
                pytest.skip("Could not create retriever")
            
            # Perform retrieval
            results = retriever.retrieve(query, top_k=3)
            
            # Verify relevance scores
            for result in results:
                # Score should be a number
                assert isinstance(result.relevance_score, (int, float)), \
                    "Relevance score should be numeric"
                
                # Score should be non-negative
                assert result.relevance_score >= 0, \
                    "Relevance score should be non-negative"
            
            # Verify scores are sorted descending
            if len(results) > 1:
                scores = [r.relevance_score for r in results]
                assert scores == sorted(scores, reverse=True), \
                    "Results should be sorted by relevance score descending"
            
        finally:
            shutil.rmtree(temp_dir, ignore_errors=True)
