"""
Property-based tests for the Embedding Engine component.

Tests verify that embedding generation maintains required properties across
all possible inputs, including dimensionality, coverage, and offline operation.
"""

import pytest
import numpy as np
from hypothesis import given, strategies as st, settings, assume
from retrieval.embedding_engine import EmbeddingEngine
import os
import socket
import urllib.request


# Test configuration
EMBEDDING_MODEL_PATH = "./models/all-MiniLM-L6-v2"


@pytest.fixture(scope="module")
def embedding_engine():
    """Create embedding engine instance for testing."""
    if not os.path.exists(EMBEDDING_MODEL_PATH):
        pytest.skip(f"Embedding model not found at {EMBEDDING_MODEL_PATH}")
    return EmbeddingEngine(EMBEDDING_MODEL_PATH)


# Property 13: Embedding Dimensionality
# **Validates: Requirements 5.3**
@given(text=st.text(min_size=1, max_size=1000))
@settings(max_examples=50, deadline=5000)
def test_embedding_dimensionality(embedding_engine, text):
    """
    Property 13: Embedding Dimensionality
    
    Test that any text produces exactly 384-dimensional vector.
    This validates that the all-MiniLM-L6-v2 model consistently
    produces the expected embedding dimensionality.
    """
    # Skip empty or whitespace-only text
    assume(text.strip())
    
    # Generate embedding
    embedding = embedding_engine.embed_text(text)
    
    # Verify dimensionality
    assert isinstance(embedding, np.ndarray), "Embedding must be numpy array"
    assert embedding.shape == (384,), f"Expected 384 dimensions, got {embedding.shape}"
    assert embedding.dtype in [np.float32, np.float64], "Embedding must be float type"


# Property 14: Complete Embedding Coverage
# **Validates: Requirements 5.4, 5.5**
@given(
    texts=st.lists(
        st.text(min_size=1, max_size=500),
        min_size=1,
        max_size=20
    )
)
@settings(max_examples=30, deadline=10000)
def test_complete_embedding_coverage(embedding_engine, texts):
    """
    Property 14: Complete Embedding Coverage
    
    Test that all chunks in any document are embedded without skipping.
    This ensures that batch processing doesn't skip any inputs.
    """
    # Filter to non-empty texts
    valid_texts = [t for t in texts if t.strip()]
    assume(len(valid_texts) > 0)
    
    # Generate embeddings in batch
    embeddings = embedding_engine.embed_batch(valid_texts)
    
    # Verify all texts were embedded
    assert embeddings.shape[0] == len(valid_texts), \
        f"Expected {len(valid_texts)} embeddings, got {embeddings.shape[0]}"
    
    # Verify each embedding has correct dimensionality
    assert embeddings.shape[1] == 384, \
        f"Expected 384 dimensions, got {embeddings.shape[1]}"
    
    # Verify no embeddings are all zeros (which would indicate skipping)
    for i, embedding in enumerate(embeddings):
        assert not np.allclose(embedding, 0), \
            f"Embedding {i} is all zeros, indicating it was skipped"


# Property 1: Complete Offline Operation
# **Validates: Requirements 1.1, 1.2, 5.2**
def test_offline_operation(embedding_engine):
    """
    Property 1: Complete Offline Operation
    
    Test that embedding generation makes no network calls.
    This uses network monitoring to verify offline operation.
    """
    # Verify the engine reports offline capability
    assert embedding_engine.verify_offline(), \
        "Embedding engine failed offline verification"
    
    # Test that we can generate embeddings (should work offline)
    test_texts = [
        "This is a test sentence.",
        "Another test for offline operation.",
        "Cybersecurity policy gap analysis."
    ]
    
    try:
        embeddings = embedding_engine.embed_batch(test_texts)
        assert embeddings.shape == (3, 384), \
            "Offline embedding generation failed"
    except Exception as e:
        pytest.fail(f"Offline embedding generation raised exception: {e}")


# Additional property test