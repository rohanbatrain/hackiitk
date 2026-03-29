"""
Text chunking component for the Offline Policy Gap Analyzer.

This module implements intelligent text chunking that segments documents into
embedding-compatible chunks while preserving semantic boundaries and context.
"""

import hashlib
from typing import List, Optional
from langchain_text_splitters import RecursiveCharacterTextSplitter

from models.domain import TextChunk, DocumentStructure, Section


class TextChunker:
    """
    Segments documents into overlapping chunks for embedding generation.
    
    Uses structure-aware splitting to prefer boundaries at headings and
    paragraphs, and preserves complete sentences when possible.
    """
    
    def __init__(self, chunk_size: int = 512, overlap: int = 50):
        """
        Initialize text chunker with size and overlap parameters.
        
        Args:
            chunk_size: Maximum tokens per chunk (default: 512)
            overlap: Token overlap between consecutive chunks (default: 50)
        """
        self.chunk_size = chunk_size
        self.overlap = overlap
        
        # Convert token counts to approximate character counts
        # Using 4 characters per token as estimation
        chunk_size_chars = chunk_size * 4
        overlap_chars = overlap * 4
        
        # Initialize LangChain's RecursiveCharacterTextSplitter
        # This splitter tries to split on structural boundaries in order:
        # 1. Markdown headings (# )
        # 2. Double newlines (paragraphs)
        # 3. Single newlines
        # 4. Sentence terminators with space
        # 5. Spaces (word boundaries)
        # 6. Characters (last resort)
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size_chars,
            chunk_overlap=overlap_chars,
            length_function=len,  # Use character length
            separators=["\n# ", "\n## ", "\n### ", "\n\n", "\n", ". ", "! ", "? ", "; ", ", ", " ", ""],
            keep_separator=True,
            is_separator_regex=False
        )
    
    def _token_length(self, text: str) -> int:
        """
        Estimate token count for text.
        
        Uses simple heuristic: ~4 characters per token for English text.
        This approximation is sufficient for chunking purposes.
        
        Args:
            text: Text to measure
            
        Returns:
            Estimated token count
        """
        return len(text) // 4
    
    def _generate_chunk_id(self, text: str, source_file: str, index: int) -> str:
        """
        Generate unique chunk identifier.
        
        Args:
            text: Chunk text content
            source_file: Source document path
            index: Chunk index in sequence
            
        Returns:
            Unique chunk ID (hash-based)
        """
        content = f"{source_file}:{index}:{text[:50]}"
        return hashlib.md5(content.encode()).hexdigest()[:16]
    
    def _find_section_for_position(self, position: int, 
                                   structure: DocumentStructure) -> Optional[str]:
        """
        Find section title for a given text position.
        
        Args:
            position: Character position in document
            structure: Document structure with sections
            
        Returns:
            Section title if found, None otherwise
        """
        if not structure or not structure.sections:
            return None
        
        # Search through sections recursively
        def search_sections(sections: List[Section]) -> Optional[str]:
            for section in sections:
                if section.start_pos <= position < section.end_pos:
                    # Check subsections first (more specific)
                    if section.subsections:
                        subsection_title = search_sections(section.subsections)
                        if subsection_title:
                            return subsection_title
                    return section.title
            return None
        
        return search_sections(structure.sections)
    
    def _clean_chunk_boundaries(self, chunk_text: str) -> str:
        """
        Clean chunk boundaries to avoid mid-word splits while preserving sentence terminators.
        
        Args:
            chunk_text: Raw chunk text
            
        Returns:
            Cleaned chunk text with proper boundaries
        """
        text = chunk_text.strip()
        
        if not text:
            return text
        
        # If chunk already ends with sentence terminator, it's perfect
        if text[-1] in ['.', '!', '?']:
            return text
        
        # If chunk ends with other punctuation or whitespace, it's acceptable
        if text[-1] in ['\n', ' ', ';', ':', ',']:
            return text.rstrip()
        
        # If chunk ends with a letter, we need to find a better boundary
        if text and text[-1].isalnum():
            # Strategy 1: Try to find the last sentence terminator (best option)
            # Look back up to 100 characters to find a sentence boundary
            search_limit = max(0, len(text) - 100)
            for i in range(len(text) - 1, search_limit, -1):
                if text[i] in ['.', '!', '?']:
                    # Include the terminator and any trailing whitespace
                    return text[:i+1]
            
            # Strategy 2: If no sentence terminator, find the last word boundary
            # Look back up to 50 characters
            search_limit = max(0, len(text) - 50)
            for i in range(len(text) - 1, search_limit, -1):
                if text[i] in [' ', '\n']:
                    # Truncate at the space, removing trailing whitespace
                    return text[:i].rstrip()
            
            # Strategy 3: If still no good boundary found, find any punctuation
            search_limit = max(0, len(text) - 50)
            for i in range(len(text) - 1, search_limit, -1):
                if text[i] in [',', ';', ':']:
                    return text[:i+1]
        
        # If all else fails, return as-is (very rare edge case)
        return text
    
    def chunk(self, text: str, structure: Optional[DocumentStructure] = None,
              source_file: str = "", page_number: Optional[int] = None) -> List[TextChunk]:
        """
        Segment text into overlapping chunks with metadata.
        
        Uses structure-aware splitting to prefer boundaries at headings and
        paragraphs. Preserves complete sentences when possible.
        
        Args:
            text: Full document text to chunk
            structure: Optional document structure for boundary awareness
            source_file: Path to source document
            page_number: Optional page number for single-page chunking
            
        Returns:
            List of TextChunk objects with text and metadata
        """
        if not text or not text.strip():
            return []
        
        # Use LangChain's splitter for structure-aware chunking
        text_chunks = self.splitter.split_text(text)
        
        # Convert to TextChunk objects with metadata
        chunks = []
        current_pos = 0
        
        for idx, chunk_text in enumerate(text_chunks):
            # Find the position of this chunk in the original text
            # Account for potential whitespace variations
            chunk_start = text.find(chunk_text.strip(), current_pos)
            if chunk_start == -1:
                # Fallback: use current position
                chunk_start = current_pos
            
            chunk_end = chunk_start + len(chunk_text)
            
            # Find section title for this chunk
            section_title = None
            if structure:
                section_title = self._find_section_for_position(chunk_start, structure)
            
            # Generate unique chunk ID
            chunk_id = self._generate_chunk_id(chunk_text, source_file, idx)
            
            # Clean chunk boundaries to avoid mid-word splits
            cleaned_text = self._clean_chunk_boundaries(chunk_text)
            
            # Create TextChunk object
            chunk = TextChunk(
                text=cleaned_text,
                chunk_id=chunk_id,
                source_file=source_file,
                start_pos=chunk_start,
                end_pos=chunk_end,
                page_number=page_number,
                section_title=section_title,
                embedding=None  # Will be populated by embedding engine
            )
            
            chunks.append(chunk)
            current_pos = chunk_end
        
        return chunks
    
    def chunk_with_boundaries(self, text: str, boundaries: List[int],
                             source_file: str = "") -> List[TextChunk]:
        """
        Chunk text preferring specified boundary positions.
        
        This method allows explicit control over chunk boundaries for
        special cases like preserving CSF subcategory descriptions.
        
        Args:
            text: Full document text to chunk
            boundaries: List of character positions to prefer as boundaries
            source_file: Path to source document
            
        Returns:
            List of TextChunk objects
        """
        if not text or not text.strip():
            return []
        
        if not boundaries:
            # Fall back to standard chunking
            return self.chunk(text, source_file=source_file)
        
        # Sort boundaries
        boundaries = sorted(set([0] + boundaries + [len(text)]))
        
        chunks = []
        chunk_idx = 0
        
        for i in range(len(boundaries) - 1):
            start = boundaries[i]
            end = boundaries[i + 1]
            
            segment = text[start:end]
            
            # If segment is too large, use standard chunking on it
            if self._token_length(segment) > self.chunk_size:
                sub_chunks = self.chunk(segment, source_file=source_file)
                chunks.extend(sub_chunks)
                chunk_idx += len(sub_chunks)
            else:
                # Create single chunk for this segment
                chunk_id = self._generate_chunk_id(segment, source_file, chunk_idx)
                chunk = TextChunk(
                    text=segment.strip(),
                    chunk_id=chunk_id,
                    source_file=source_file,
                    start_pos=start,
                    end_pos=end,
                    page_number=None,
                    section_title=None,
                    embedding=None
                )
                chunks.append(chunk)
                chunk_idx += 1
        
        return chunks
