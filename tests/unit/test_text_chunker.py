"""
Unit tests for text chunking component.
"""

import pytest
from ingestion.text_chunker import TextChunker
from models.domain import DocumentStructure, Section


def test_text_chunker_initialization():
    """Test TextChunker initializes with correct parameters."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    assert chunker.chunk_size == 512
    assert chunker.overlap == 50


def test_chunk_simple_text():
    """Test chunking simple text."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = "This is a simple test. " * 100  # Create text that needs chunking
    
    chunks = chunker.chunk(text, source_file="test.txt")
    
    assert len(chunks) > 0
    assert all(chunk.source_file == "test.txt" for chunk in chunks)
    assert all(chunk.chunk_id is not None for chunk in chunks)
    assert all(len(chunk.text) > 0 for chunk in chunks)


def test_chunk_size_constraint():
    """Test that chunks respect the size constraint."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = "Word " * 1000  # Create long text
    
    chunks = chunker.chunk(text, source_file="test.txt")
    
    for chunk in chunks:
        token_count = chunker._token_length(chunk.text)
        assert token_count <= 512, f"Chunk has {token_count} tokens, exceeds 512 limit"


def test_empty_text():
    """Test chunking empty text."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    
    chunks = chunker.chunk("", source_file="test.txt")
    assert chunks == []
    
    chunks = chunker.chunk("   ", source_file="test.txt")
    assert chunks == []


def test_chunk_metadata():
    """Test that chunks have complete metadata."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = "This is a test document with multiple sentences. " * 20
    
    chunks = chunker.chunk(text, source_file="policy.txt", page_number=1)
    
    for chunk in chunks:
        assert chunk.chunk_id is not None
        assert chunk.source_file == "policy.txt"
        assert chunk.page_number == 1
        assert chunk.start_pos >= 0
        assert chunk.end_pos > chunk.start_pos


def test_chunk_with_structure():
    """Test chunking with document structure."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    
    text = """# Introduction
This is the introduction section.

# Main Content
This is the main content section with more text.
"""
    
    # Create simple structure
    sections = [
        Section(
            title="Introduction",
            content="This is the introduction section.",
            start_pos=0,
            end_pos=50,
            subsections=[]
        ),
        Section(
            title="Main Content",
            content="This is the main content section with more text.",
            start_pos=50,
            end_pos=len(text),
            subsections=[]
        )
    ]
    
    structure = DocumentStructure(
        headings=[],
        sections=sections,
        paragraphs=[]
    )
    
    chunks = chunker.chunk(text, structure=structure, source_file="test.txt")
    
    assert len(chunks) > 0
    # At least some chunks should have section titles
    assert any(chunk.section_title is not None for chunk in chunks)


def test_chunk_id_uniqueness():
    """Test that chunk IDs are unique."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = "This is a test. " * 200
    
    chunks = chunker.chunk(text, source_file="test.txt")
    
    chunk_ids = [chunk.chunk_id for chunk in chunks]
    assert len(chunk_ids) == len(set(chunk_ids)), "Chunk IDs are not unique"


def test_token_length_estimation():
    """Test token length estimation."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    
    # Test with known text
    text = "word " * 100  # 100 words, ~500 characters
    token_count = chunker._token_length(text)
    
    # Should be approximately 125 tokens (500 chars / 4)
    assert 100 <= token_count <= 150


def test_chunk_with_boundaries():
    """Test chunking with explicit boundaries."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    
    text = "Section 1 content. " * 20 + "Section 2 content. " * 20
    boundaries = [0, 380, len(text)]  # Split at specific positions
    
    chunks = chunker.chunk_with_boundaries(text, boundaries, source_file="test.txt")
    
    assert len(chunks) > 0
    assert all(chunk.source_file == "test.txt" for chunk in chunks)
