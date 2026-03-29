"""
Pretty Printer for the Offline Policy Gap Analyzer.

This module provides the PrettyPrinter class for formatting parsed policy
documents back to markdown format, enabling round-trip testing of the parser.
"""

import logging
from typing import Optional

from models.domain import (
    ParsedDocument,
    DocumentStructure,
    Heading,
    Section,
)


logger = logging.getLogger(__name__)


class PrettyPrinter:
    """
    Formatter for converting parsed policy documents back to markdown.
    
    Preserves document structure including headings, sections, and paragraphs
    while formatting with proper markdown syntax.
    """
    
    def __init__(self):
        """Initialize the PrettyPrinter."""
        self.logger = logging.getLogger(__name__)
    
    def format_to_markdown(self, parsed_doc: ParsedDocument) -> str:
        """
        Format a parsed document back to markdown.
        
        Args:
            parsed_doc: ParsedDocument with text and structure
            
        Returns:
            Markdown-formatted string representation of the document
        """
        if not parsed_doc.structure:
            # If no structure, return plain text
            return parsed_doc.text
        
        # Build markdown from structure
        markdown_parts = []
        
        # Format sections with their headings
        if parsed_doc.structure.sections:
            # Find corresponding heading levels for sections
            heading_map = {h.text: h.level for h in parsed_doc.structure.headings}
            
            for section in parsed_doc.structure.sections:
                # Get the heading level from the heading map
                level = heading_map.get(section.title, 1)
                markdown_parts.append(self._format_section(section, level=level))
        else:
            # Fallback: use headings and text
            markdown_parts.append(self._format_from_headings(
                parsed_doc.text,
                parsed_doc.structure
            ))
        
        return '\n\n'.join(markdown_parts)
    
    def _format_section(self, section: Section, level: int = 1) -> str:
        """
        Format a section with its heading and content.
        
        Args:
            section: Section to format
            level: Heading level (1-6)
            
        Returns:
            Markdown-formatted section
        """
        parts = []
        
        # Add heading
        heading_prefix = '#' * min(level, 6)
        parts.append(f"{heading_prefix} {section.title}")
        
        # Add content (if not empty)
        content = section.content.strip()
        if content:
            parts.append(content)
        
        # Add subsections recursively
        for subsection in section.subsections:
            parts.append(self._format_section(subsection, level + 1))
        
        return '\n\n'.join(parts)
    
    def _format_from_headings(
        self,
        text: str,
        structure: DocumentStructure
    ) -> str:
        """
        Format document using headings and text positions.
        
        This is a fallback when sections are not available.
        
        Args:
            text: Full document text
            structure: Document structure with headings
            
        Returns:
            Markdown-formatted document
        """
        if not structure.headings:
            return text
        
        parts = []
        headings = sorted(structure.headings, key=lambda h: h.start_pos)
        
        for i, heading in enumerate(headings):
            # Add heading
            heading_prefix = '#' * min(heading.level, 6)
            parts.append(f"{heading_prefix} {heading.text}")
            
            # Add content between this heading and next
            content_start = heading.end_pos
            if i + 1 < len(headings):
                content_end = headings[i + 1].start_pos
            else:
                content_end = len(text)
            
            content = text[content_start:content_end].strip()
            if content:
                parts.append(content)
        
        return '\n\n'.join(parts)
