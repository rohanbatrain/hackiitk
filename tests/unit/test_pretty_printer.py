"""
Unit tests for the PrettyPrinter component.

Tests the formatting of parsed documents back to markdown.
"""

import pytest
from pathlib import Path
import tempfile

from ingestion.document_parser import DocumentParser
from ingestion.pretty_printer import PrettyPrinter
from models.domain import (
    ParsedDocument,
    DocumentStructure,
    Heading,
    Section,
)


def test_format_simple_document():
    """Test formatting a simple document with headings and content."""
    # Create a simple parsed document
    structure = DocumentStructure(
        headings=[
            Heading(level=1, text="Title", start_pos=0, end_pos=5),
            Heading(level=2, text="Section", start_pos=6, end_pos=13),
        ],
        sections=[
            Section(
                title="Title",
                content="",
                start_pos=0,
                end_pos=5,
                subsections=[]
            ),
            Section(
                title="Section",
                content="Some content here.",
                start_pos=6,
                end_pos=30,
                subsections=[]
            ),
        ],
        paragraphs=[]
    )
    
    parsed_doc = ParsedDocument(
        text="Title\nSection\nSome content here.",
        file_path="test.txt",
        file_type="txt",
        page_count=1,
        structure=structure,
        metadata={}
    )
    
    printer = PrettyPrinter()
    markdown = printer.format_to_markdown(parsed_doc)
    
    # Verify markdown output
    assert "# Title" in markdown
    assert "## Section" in markdown
    assert "Some content here." in markdown


def test_format_nested_sections():
    """Test formatting document with nested sections."""
    structure = DocumentStructure(
        headings=[
            Heading(level=1, text="Main", start_pos=0, end_pos=4),
            Heading(level=2, text="Sub1", start_pos=5, end_pos=9),
            Heading(level=3, text="Sub2", start_pos=10, end_pos=14),
        ],
        sections=[
            Section(
                title="Main",
                content="Main content",
                start_pos=0,
                end_pos=20,
                subsections=[
                    Section(
                        title="Sub1",
                        content="Sub1 content",
                        start_pos=5,
                        end_pos=15,
                        subsections=[
                            Section(
                                title="Sub2",
                                content="Sub2 content",
                                start_pos=10,
                                end_pos=14,
                                subsections=[]
                            )
                        ]
                    )
                ]
            ),
        ],
        paragraphs=[]
    )
    
    parsed_doc = ParsedDocument(
        text="Main\nSub1\nSub2",
        file_path="test.txt",
        file_type="txt",
        page_count=1,
        structure=structure,
        metadata={}
    )
    
    printer = PrettyPrinter()
    markdown = printer.format_to_markdown(parsed_doc)
    
    # Verify heading levels are preserved
    assert "# Main" in markdown
    assert "## Sub1" in markdown
    assert "### Sub2" in markdown


def test_format_document_without_structure():
    """Test formatting document with no structure (fallback to plain text)."""
    parsed_doc = ParsedDocument(
        text="Plain text document",
        file_path="test.txt",
        file_type="txt",
        page_count=1,
        structure=None,
        metadata={}
    )
    
    printer = PrettyPrinter()
    markdown = printer.format_to_markdown(parsed_doc)
    
    # Should return plain text
    assert markdown == "Plain text document"


def test_format_empty_sections():
    """Test formatting document with empty sections."""
    structure = DocumentStructure(
        headings=[
            Heading(level=1, text="Empty", start_pos=0, end_pos=5),
        ],
        sections=[
            Section(
                title="Empty",
                content="",
                start_pos=0,
                end_pos=5,
                subsections=[]
            ),
        ],
        paragraphs=[]
    )
    
    parsed_doc = ParsedDocument(
        text="Empty",
        file_path="test.txt",
        file_type="txt",
        page_count=1,
        structure=structure,
        metadata={}
    )
    
    printer = PrettyPrinter()
    markdown = printer.format_to_markdown(parsed_doc)
    
    # Should include heading even if content is empty
    assert "# Empty" in markdown


def test_roundtrip_with_real_parser():
    """Test round-trip with actual DocumentParser."""
    markdown_text = """# Security Policy

## Access Control

Users must authenticate before accessing systems.

### Authentication Methods

Multiple authentication methods are supported.

## Data Protection

Data must be encrypted at rest and in transit."""
    
    # Create temporary file
    with tempfile.NamedTemporaryFile(
        suffix='.txt',
        delete=False,
        mode='w',
        encoding='utf-8'
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(markdown_text)
    
    try:
        parser = DocumentParser()
        printer = PrettyPrinter()
        
        # Parse
        parsed = parser.parse(str(tmp_path), 'txt')
        
        # Format back to markdown
        markdown_output = printer.format_to_markdown(parsed)
        
        # Verify key elements are present
        assert "# Security Policy" in markdown_output or "#Security Policy" in markdown_output
        assert "## Access Control" in markdown_output or "##Access Control" in markdown_output
        assert "### Authentication Methods" in markdown_output or "###Authentication Methods" in markdown_output
        assert "authenticate" in markdown_output
        assert "encrypted" in markdown_output
        
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_format_preserves_content():
    """Test that formatting preserves content text."""
    content = "This is important policy content that must be preserved."
    
    structure = DocumentStructure(
        headings=[
            Heading(level=1, text="Policy", start_pos=0, end_pos=6),
        ],
        sections=[
            Section(
                title="Policy",
                content=content,
                start_pos=0,
                end_pos=len(content),
                subsections=[]
            ),
        ],
        paragraphs=[]
    )
    
    parsed_doc = ParsedDocument(
        text=f"Policy\n{content}",
        file_path="test.txt",
        file_type="txt",
        page_count=1,
        structure=structure,
        metadata={}
    )
    
    printer = PrettyPrinter()
    markdown = printer.format_to_markdown(parsed_doc)
    
    # Verify content is preserved
    assert content in markdown


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
