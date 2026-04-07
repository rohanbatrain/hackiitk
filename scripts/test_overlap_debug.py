from ingestion.text_chunker import TextChunker

chunker = TextChunker(chunk_size=512, overlap=50)
text = "This is a test sentence. " * 200  # Create long text

chunks = chunker.chunk(text, source_file="test.txt")

print(f"Number of chunks: {len(chunks)}")
if len(chunks) >= 2:
    chunk1 = chunks[0].text
    chunk2 = chunks[1].text
    
    print(f"\nChunk 1 length: {len(chunk1)} chars, {chunker._token_length(chunk1)} tokens")
    print(f"Chunk 2 length: {len(chunk2)} chars, {chunker._token_length(chunk2)} tokens")
    
    print(f"\nChunk 1 ends with: ...{chunk1[-50:]}")
    print(f"Chunk 2 starts with: {chunk2[:50]}...")
    
    # Check for overlap
    for length in [200, 150, 100, 50, 25]:
        chunk1_end = chunk1[-length:]
        if chunk1_end in chunk2:
            overlap_tokens = chunker._token_length(chunk1_end)
            print(f"\nOverlap found at {length} chars: {overlap_tokens} tokens")
            break
    else:
        print("\nNo overlap found")
