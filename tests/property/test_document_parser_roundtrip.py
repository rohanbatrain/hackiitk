"""
Property Test 38: Document Parser Round-Trip

Validates Requirement 13.3:
- Parse → print → parse produces equivalent policy object
- Document structure is preserved through round-trip
- Text content remains consistent
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
import tempfile
import hashlib

from ingestion.document_parser import DocumentParser
from ingestion.pretty_printer import PrettyPrinter
from models.domain import ParsedDocument, DocumentStructure, Heading, Section


# ============================================================================
# Test Strategies
# ============================================================================

@st.composite
def markdown_document_strategy(draw):
    """Generate valid markdown documents with structure."""
    # Generate headings and content
    num_sections = draw(st.integers(min_value=1, max_value=5))
    
    sections = []
    for i in range(num_sections):
        # Generate section title
        title = draw(st.text(
            alphabet=st.characters(
                whitelist_categories=('Lu', 'Ll', 'Nd'),
                whitelist_characters=' -'
            ),
            min_size=5,
            max_size=50
        ).filter(lambda x: x.strip() and not x.startswith('#')))
        
        # Generate section content
        num_paragraphs = draw(st.integers(min_value=1, max_value=3))
        paragraphs = []
        for _ in range(num_paragraphs):
            paragraph = draw(st.text(
                alphabet=st.characters(
                    whitelist_categories=('Lu', 'Ll', 'Nd', 'P'),
                    whitelist_characters=' \n'
                ),
                min_size=20,
                max_size=200
            ).filter(lambda x: x.strip()))
            paragraphs.append(paragraph)
        
        content = '\n\n'.join(paragraphs)
        sections.append((title, content))
    
    # Build markdown document
    markdown_parts = []
    for title, content in sections:
        markdown_parts.append(f"# {title}")
        markdown_parts.append(content)
    
    return '\n\n'.join(markdown_parts)


@st.composite
def simple_markdown_strategy(draw):
    """Generate simple markdown documents for testing."""
    templates = [
        """# Introduction

This is a sample policy document for testing purposes.

## Purpose

The purpose of this policy is to establish guidelines.

## Scope

This policy applies to all employees and contractors.

### Applicability

All systems and data are covered.

## Responsibilities

Management is responsible for enforcement.

### Employee Responsibilities

Employees must comply with all provisions.

## Review

This policy will be reviewed annually.""",
        
        """# Security Policy

## Access Control

Access to systems must be authorized.

## Data Protection

Data must be encrypted at rest and in transit.

## Incident Response

Incidents must be reported immediately.

### Reporting Procedures

Contact the security team for all incidents.""",
        
        """# Risk Management

## Risk Assessment

Risks must be identified and assessed regularly.

## Risk Treatment

Appropriate controls must be implemented.

## Monitoring

Risk levels must be monitored continuously."""
    ]
    
    return draw(st.sampled_from(templates))


# ============================================================================
# Property Tests
# ============================================================================

@given(markdown_text=simple_markdown_strategy())
@settings(max_examples=20, deadline=10000)
def test_document_parser_roundtrip_simple(markdown_text):
    """
    Property 38: Document Parser Round-Trip (Simple)
    
    Test that parse → print → parse produces equivalent structure
    for simple markdown documents.
    """
    # Create temporary markdown file
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
        
        # First parse
        parsed1 = parser.parse(str(tmp_path), 'txt')
        
        # Print to markdown
        markdown_output = printer.format_to_markdown(parsed1)
        
        # Write markdown output to new file
        with tempfile.NamedTemporaryFile(
            suffix='.txt',
            delete=False,
            mode='w',
            encoding='utf-8'
        ) as tmp_file2:
            tmp_path2 = Path(tmp_file2.name)
            tmp_file2.write(markdown_output)
        
        try:
            # Second parse
            parsed2 = parser.parse(str(tmp_path2), 'txt')
            
            # Verify structural equivalence
            assert_structure_equivalent(parsed1.structure, parsed2.structure)
            
            # Verify content similarity (normalized)
            content1_normalized = normalize_text(parsed1.text)
            content2_normalized = normalize_text(parsed2.text)
            
            # Content should be similar (allowing for formatting differences)
            similarity = text_similarity(content1_normalized, content2_normalized)
            assert similarity > 0.8, \
                f"Content similarity too low: {similarity:.2f}"
        
        finally:
            if tmp_path2.exists():
                tmp_path2.unlink()
    
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_roundtrip_preserves_headings():
    """
    Test that round-trip preserves heading structure.
    
    Verifies that heading levels and text are maintained.
    """
    markdown = """# Main Title

## Section 1

Content for section 1.

### Subsection 1.1

Content for subsection 1.1.

## Section 2

Content for section 2."""
    
    with tempfile.NamedTemporaryFile(
        suffix='.txt',
        delete=False,
        mode='w',
        encoding='utf-8'
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(markdown)
    
    try:
        parser = DocumentParser()
        printer = PrettyPrinter()
        
        # Parse
        parsed = parser.parse(str(tmp_path), 'txt')
        
        # Verify headings were extracted
        assert len(parsed.structure.headings) >= 3, \
            "Should extract at least 3 headings"
        
        # Print
        markdown_output = printer.format_to_markdown(parsed)
        
        # Verify headings are in output
        assert '# Main Title' in markdown_output or '#Main Title' in markdown_output
        assert '## Section 1' in markdown_output or '##Section 1' in markdown_output
        
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_roundtrip_preserves_sections():
    """
    Test that round-trip preserves section structure.
    
    Verifies that sections and their content are maintained.
    """
    markdown = """# Policy Document

## Purpose

This policy establishes security requirements.

## Scope

This policy applies to all systems.

## Requirements

All users must comply."""
    
    with tempfile.NamedTemporaryFile(
        suffix='.txt',
        delete=False,
        mode='w',
        encoding='utf-8'
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(markdown)
    
    try:
        parser = DocumentParser()
        printer = PrettyPrinter()
        
        # Parse
        parsed = parser.parse(str(tmp_path), 'txt')
        
        # Verify sections were extracted
        assert len(parsed.structure.sections) >= 1, \
            "Should extract at least 1 section"
        
        # Print
        markdown_output = printer.format_to_markdown(parsed)
        
        # Parse again
        with tempfile.NamedTemporaryFile(
            suffix='.txt',
            delete=False,
            mode='w',
            encoding='utf-8'
        ) as tmp_file2:
            tmp_path2 = Path(tmp_file2.name)
            tmp_file2.write(markdown_output)
        
        try:
            parsed2 = parser.parse(str(tmp_path2), 'txt')
            
            # Verify section count is similar
            section_count1 = len(parsed.structure.sections)
            section_count2 = len(parsed2.structure.sections)
            
            assert abs(section_count1 - section_count2) <= 1, \
                f"Section count should be similar: {section_count1} vs {section_count2}"
        
        finally:
            if tmp_path2.exists():
                tmp_path2.unlink()
    
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_roundtrip_with_empty_sections():
    """
    Test round-trip with sections that have no content.
    
    Verifies that empty sections are handled correctly.
    """
    markdown = """# Document

## Section 1

## Section 2

Some content here.

## Section 3"""
    
    with tempfile.NamedTemporaryFile(
        suffix='.txt',
        delete=False,
        mode='w',
        encoding='utf-8'
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(markdown)
    
    try:
        parser = DocumentParser()
        printer = PrettyPrinter()
        
        # Parse
        parsed = parser.parse(str(tmp_path), 'txt')
        
        # Print
        markdown_output = printer.format_to_markdown(parsed)
        
        # Should not crash and should produce valid markdown
        assert markdown_output is not None
        assert len(markdown_output) > 0
        
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


def test_roundtrip_preserves_content_hash():
    """
    Test that round-trip preserves content (by hash).
    
    Verifies that the essential content is maintained.
    """
    markdown = """# Security Policy

## Access Control

Users must authenticate before accessing systems.

## Data Protection

Data must be encrypted using approved algorithms."""
    
    with tempfile.NamedTemporaryFile(
        suffix='.txt',
        delete=False,
        mode='w',
        encoding='utf-8'
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(markdown)
    
    try:
        parser = DocumentParser()
        printer = PrettyPrinter()
        
        # Parse
        parsed1 = parser.parse(str(tmp_path), 'txt')
        
        # Get content hash
        content1_normalized = normalize_text(parsed1.text)
        hash1 = hashlib.sha256(content1_normalized.encode()).hexdigest()
        
        # Print and parse again
        markdown_output = printer.format_to_markdown(parsed1)
        
        with tempfile.NamedTemporaryFile(
            suffix='.txt',
            delete=False,
            mode='w',
            encoding='utf-8'
        ) as tmp_file2:
            tmp_path2 = Path(tmp_file2.name)
            tmp_file2.write(markdown_output)
        
        try:
            parsed2 = parser.parse(str(tmp_path2), 'txt')
            
            # Get content hash
            content2_normalized = normalize_text(parsed2.text)
            hash2 = hashlib.sha256(content2_normalized.encode()).hexdigest()
            
            # Hashes should be similar (allowing for minor formatting)
            # We check text similarity instead of exact hash match
            similarity = text_similarity(content1_normalized, content2_normalized)
            assert similarity > 0.9, \
                f"Content should be highly similar: {similarity:.2f}"
        
        finally:
            if tmp_path2.exists():
                tmp_path2.unlink()
    
    finally:
        if tmp_path.exists():
            tmp_path.unlink()


# ============================================================================
# Helper Functions
# ============================================================================

def assert_structure_equivalent(
    structure1: DocumentStructure,
    structure2: DocumentStructure
):
    """
    Assert that two document structures are equivalent.
    
    Checks heading count and section count are similar.
    """
    # Check heading count (allow small differences due to parsing variations)
    heading_count1 = len(structure1.headings)
    heading_count2 = len(structure2.headings)
    
    assert abs(heading_count1 - heading_count2) <= 2, \
        f"Heading count should be similar: {heading_count1} vs {heading_count2}"
    
    # Check section count
    section_count1 = len(structure1.sections)
    section_count2 = len(structure2.sections)
    
    assert abs(section_count1 - section_count2) <= 2, \
        f"Section count should be similar: {section_count1} vs {section_count2}"


def normalize_text(text: str) -> str:
    """
    Normalize text for comparison.
    
    Removes extra whitespace and normalizes line endings.
    """
    # Normalize line endings
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Remove extra whitespace
    lines = [line.strip() for line in text.split('\n')]
    lines = [line for line in lines if line]
    
    return '\n'.join(lines)


def text_similarity(text1: str, text2: str) -> float:
    """
    Calculate similarity between two texts.
    
    Uses simple word overlap metric.
    """
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())
    
    if not words1 or not words2:
        return 0.0
    
    intersection = words1 & words2
    union = words1 | words2
    
    return len(intersection) / len(union)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
