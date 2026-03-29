"""
Unit tests for the Embedding Engine component.

Tests verify performance characteristics, CPU-only operation,
and memory usage constraints.
"""

import pytest
import numpy as np
import time
import psutil
import os
from retrieval.embedding_engine import EmbeddingEngine


# Test configuration
EMBEDDING_MODEL_PATH = "./models/all-MiniLM-L6-v2"


@pytest.fixture(scope="module")
def embedding_engine():
    """Create embedding engine instance for testing."""
    if not os.path.exists(EMBEDDING_MODEL_PATH):
        pytest.skip(f"Embedding model not found at {EMBEDDING_MODEL_PATH}")
    return EmbeddingEngine(EMBEDDING_MODEL_PATH)


def test_model_loading():
    """Test that model loads successfully from local path."""
    if not os.path.exists(EMBEDDING_MODEL_PATH):
        pytest.skip(f"Embedding model not found at {EMBEDDING_MODEL_PATH}")
    
    engine = EmbeddingEngine(EMBEDDING_MODEL_PATH)
    assert engine.model is not None
    assert engine.dimensions == 384
    assert engine.model_path == EMBEDDING_MODEL_PATH


def test_model_loading_invalid_path():
    """Test that invalid model path raises appropriate error."""
    with pytest.raises(FileNotFoundError) as exc_info:
        EmbeddingEngine("/invalid/path/to/model")
    
    assert "Model path not found" in str(exc_info.value)
    assert "download_models.py" in str(exc_info.value)


def test_single_text_embedding(embedding_engine):
    """Test embedding generation for single text."""
    text = "This is a test policy document about cybersecurity."
    embedding = embedding_engine.embed_text(text)
    
    assert isinstance(embedding, np.ndarray)
    assert embedding.shape == (384,)
    assert embedding.dtype in [np.float32, np.float64]
    
    # Verify embedding is normalized (L2 norm should be ~1.0)
    norm = np.linalg.norm(embedding)
    assert 0.99 <= norm <= 1.01, f"Embedding not normalized: norm={norm}"


def test_empty_text_rejection(embedding_engine):
    """Test that empty text raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        embedding_engine.embed_text("")
    assert "empty text" in str(exc_info.value).lower()
    
    with pytest.raises(ValueError) as exc_info:
        embedding_engine.embed_text("   ")
    assert "empty text" in str(exc_info.value).lower()


def test_batch_embedding(embedding_engine):
    """Test batch embedding generation."""
    texts = [
        "First policy document about access control.",
        "Second document covering incident response.",
        "Third document on risk management.",
        "Fourth document about data protection."
    ]
    
    embeddings = embedding_engine.embed_batch(texts)
    
    assert isinstance(embeddings, np.ndarray)
    assert embeddings.shape == (4, 384)
    
    # Verify each embedding is normalized
    for i, embedding in enumerate(embeddings):
        norm = np.linalg.norm(embedding)
        assert 0.99 <= norm <= 1.01, f"Embedding {i} not normalized: norm={norm}"


def test_empty_batch_rejection(embedding_engine):
    """Test that empty batch raises ValueError."""
    with pytest.raises(ValueError) as exc_info:
        embedding_engine.embed_batch([])
    assert "empty" in str(exc_info.value).lower()
    
    with pytest.raises(ValueError) as exc_info:
        embedding_engine.embed_batch(["", "  ", "\n"])
    assert "empty" in str(exc_info.value).lower()


def test_batch_processing_efficiency(embedding_engine):
    """
    Test batch processing efficiency (100+ chunks per minute).
    Requirements: 5.6, 5.7
    """
    # Generate 100 test chunks
    chunks = [
        f"This is test chunk number {i} containing policy text about cybersecurity controls."
        for i in range(100)
    ]
    
    # Measure batch processing time
    start_time = time.time()
    embeddings = embedding_engine.embed_batch(chunks)
    elapsed_time = time.time() - start_time
    
    # Verify all embeddings generated
    assert embeddings.shape == (100, 384)
    
    # Verify processing rate (100 chunks per minute = 1.67 per second)
    # Allow 60 seconds for 100 chunks (conservative for CI environments)
    assert elapsed_time < 60, \
        f"Batch processing too slow: {elapsed_time:.2f}s for 100 chunks"
    
    chunks_per_minute = (100 / elapsed_time) * 60
    print(f"\nBatch processing rate: {chunks_per_minute:.1f} chunks/minute")
    assert chunks_per_minute >= 100, \
        f"Processing rate {chunks_per_minute:.1f} chunks/min below requirement of 100/min"


def test_cpu_only_operation(embedding_engine):
    """
    Test CPU-only operation (no GPU required).
    Requirements: 5.6
    """
    # Verify model is on CPU device
    assert embedding_engine.model.device.type == 'cpu', \
        "Model should be on CPU device"
    
    # Generate embedding and verify it works on CPU
    text = "Test text for CPU operation verification."
    embedding = embedding_engine.embed_text(text)
    
    assert embedding.shape == (384,)


def test_memory_usage_bounds(embedding_engine):
    """
    Test memory usage stays within bounds during batch processing.
    Requirements: 5.7
    """
    # Get initial memory usage
    process = psutil.Process()
    initial_memory_mb = process.memory_info().rss / 1024 / 1024
    
    # Process a large batch
    large_batch = [
        f"Policy text chunk {i} " * 50  # ~50 words per chunk
        for i in range(200)
    ]
    
    embeddings = embedding_engine.embed_batch(large_batch)
    
    # Get peak memory usage
    peak_memory_mb = process.memory_info().rss / 1024 / 1024
    memory_increase_mb = peak_memory_mb - initial_memory_mb
    
    # Verify embeddings generated correctly
    assert embeddings.shape == (200, 384)
    
    # Memory increase should be reasonable (< 500MB for 200 chunks)
    # This is conservative for consumer hardware
    print(f"\nMemory increase: {memory_increase_mb:.1f} MB")
    assert memory_increase_mb < 500, \
        f"Memory usage too high: {memory_increase_mb:.1f} MB increase"


def test_verify_offline_method(embedding_engine):
    """Test the verify_offline method."""
    result = embedding_engine.verify_offline()
    assert result is True, "verify_offline should return True for properly loaded model"


def test_embedding_consistency(embedding_engine):
    """Test that same text produces same embedding."""
    text = "Consistent policy text for testing."
    
    embedding1 = embedding_engine.embed_text(text)
    embedding2 = embedding_engine.embed_text(text)
    
    # Embeddings should be identical (or very close due to floating point)
    assert np.allclose(embedding1, embedding2, atol=1e-6), \
        "Same text should produce consistent embeddings"


def test_batch_vs_single_consistency(embedding_engine):
    """Test that batch and single embedding produce same results."""
    texts = [
        "First test text.",
        "Second test text.",
        "Third test text."
    ]
    
    # Generate embeddings individually
    single_embeddings = np.array([
        embedding_engine.embed_text(text) for text in texts
    ])
    
    # Generate embeddings in batch
    batch_embeddings = embedding_engine.embed_batch(texts)
    
    # Results should be very close
    assert np.allclose(single_embeddings, batch_embeddings, atol=1e-5), \
        "Batch and single embedding should produce consistent results"
