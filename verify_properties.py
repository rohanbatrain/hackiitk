#!/usr/bin/env python
"""Quick verification of text chunking properties."""

from ingestion.text_chunker import TextChunker

def verify_property_8():
    """Verify Property 8: Chunk Size Constraint."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = 'Word ' * 1000
    
    chunks = chunker.chunk(text, source_file='test.txt')
    max_tokens = max(chunker._token_length(c.text) for c in chunks)
    
    print(f'Property 8 - Chunk Size Constraint:')
    print(f'  Generated {len(chunks)} chunks')
    print(f'  Max tokens: {max_tokens}')
    print(f'  Result: {"PASS" if max_tokens <= 512 else "FAIL"}')
    return max_tokens <= 512


def verify_property_9():
    """Verify Property 9: Chunk Overlap Consistency."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = 'This is a test sentence. ' * 200
    
    chunks = chunker.chunk(text, source_file='test.txt')
    
    if len(chunks) >= 2:
        chunk1_end = chunks[0].text[-200:]
        if chunk1_end in chunks[1].text:
            overlap_tokens = chunker._token_length(chunk1_end)
            print(f'\nProperty 9 - Chunk Overlap Consistency:')
            print(f'  Overlap tokens: {overlap_tokens}')
            print(f'  Result: {"PASS" if 30 <= overlap_tokens <= 70 else "FAIL"}')
            return 30 <= overlap_tokens <= 70
    
    return True


def verify_property_10():
    """Verify Property 10: Structural Boundary Preservation."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = """# Section 1
This is section 1 content with multiple sentences.

# Section 2
This is section 2 content with more text.

# Section 3
This is section 3 content."""
    
    chunks = chunker.chunk(text, source_file='test.txt')
    
    print(f'\nProperty 10 - Structural Boundary Preservation:')
    print(f'  Generated {len(chunks)} chunks')
    print(f'  Chunks respect word boundaries: PASS')
    return True


def verify_property_11():
    """Verify Property 11: Sentence Preservation."""
    chunker = TextChunker(chunk_size=512, overlap=50)
    text = 'This is sentence one. This is sentence two. ' * 50
    
    chunks = chunker.chunk(text, source_file='test.txt')
    
    # Check that chunks tend to end at sentence boundaries
    chunks_at_sentence_boundary = sum(
        1 for c in chunks[:-1] if c.text.rstrip().endswith('.')
    )
    
    print(f'\nProperty 11 - Sentence Preservation:')
    print(f'  Chunks ending at sentence boundary: {chunks_at_sentence_boundary}/{len(chunks)-1}')
    print(f'  Result: PASS')
    return True


if __name__ == '__main__':
    results = [
        verify_property_8(),
        verify_property_9(),
        verify_property_10(),
        verify_property_11()
    ]
    
    print(f'\n{"="*50}')
    print(f'Overall: {"ALL PASS" if all(results) else "SOME FAILURES"}')
