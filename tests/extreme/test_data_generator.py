"""
Unit tests for TestDataGenerator

This module tests the test data generation capabilities to ensure
all generation methods work correctly.
"""

import pytest
from pathlib import Path
import tempfile
import shutil

from tests.extreme.data_generator import TestDataGenerator, DocumentSpec


class TestDataGeneratorTests:
    """Test suite for TestDataGenerator."""
    
    @pytest.fixture
    def generator(self):
        """Create a test data generator with temporary cache directory."""
        temp_dir = Path(tempfile.mkdtemp())
        gen = TestDataGenerator(cache_dir=temp_dir)
        yield gen
        # Cleanup
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
    
    def test_generate_policy_document_basic(self, generator):
        """Test basic policy document generation."""
        spec = DocumentSpec(size_pages=2, words_per_page=100, sections_per_page=2)
        document = generator.generate_policy_document(spec)
        
        assert document is not None
        assert len(document) > 0
        assert "# Cybersecurity Policy Document" in document
        assert "## Section" in document
    
    def test_generate_policy_document_with_coverage(self, generator):
        """Test policy document generation with specific coverage."""
        spec = DocumentSpec(
            size_pages=5,
            words_per_page=200,
            sections_per_page=3,
            coverage_percentage=0.7,
            include_csf_keywords=True
        )
        document = generator.generate_policy_document(spec)
        
        assert document is not None
        assert len(document) > 0
        # Should contain some CSF references
        assert any(csf in document for csf in ["ID.", "PR."])
    
    def test_generate_malicious_pdf_javascript(self, generator):
        """Test malicious PDF generation with JavaScript."""
        pdf_content = generator.generate_malicious_pdf("javascript")
        
        assert pdf_content is not None
        assert len(pdf_content) > 0
        assert b"%PDF" in pdf_content
        assert b"JavaScript" in pdf_content
    
    def test_generate_malicious_pdf_malformed(self, generator):
        """Test malformed PDF generation."""
        pdf_content = generator.generate_malicious_pdf("malformed")
        
        assert pdf_content is not None
        assert len(pdf_content) > 0
        assert b"%PDF" in pdf_content
    
    def test_generate_malicious_pdf_recursive(self, generator):
        """Test recursive PDF generation."""
        pdf_content = generator.generate_malicious_pdf("recursive")
        
        assert pdf_content is not None
        assert len(pdf_content) > 0
        assert b"%PDF" in pdf_content
    
    def test_generate_malicious_pdf_large_object(self, generator):
        """Test large object PDF generation."""
        pdf_content = generator.generate_malicious_pdf("large_object")
        
        assert pdf_content is not None
        assert len(pdf_content) > 1000000  # Should be > 1MB
        assert b"%PDF" in pdf_content
    
    def test_generate_gap_policy(self, generator):
        """Test gap policy generation."""
        gap_subcategories = ["ID.AM-1", "ID.AM-2", "PR.AC-1"]
        document = generator.generate_gap_policy(gap_subcategories)
        
        assert document is not None
        assert len(document) > 0
        assert "# Cybersecurity Policy Document" in document
        # Should not contain gap subcategories
        for gap in gap_subcategories:
            assert gap not in document
    
    def test_generate_extreme_structure_no_headings(self, generator):
        """Test document generation with no headings."""
        document = generator.generate_extreme_structure("no_headings")
        
        assert document is not None
        assert len(document) > 0
        # Should not contain markdown headings
        assert not any(line.startswith("#") for line in document.split("\n"))
    
    def test_generate_extreme_structure_deep_nesting(self, generator):
        """Test document generation with deep nesting."""
        document = generator.generate_extreme_structure("deep_nesting")
        
        assert document is not None
        assert len(document) > 0
        # Should contain many heading levels
        assert "# Level" in document or "## Level" in document
    
    def test_generate_extreme_structure_inconsistent_hierarchy(self, generator):
        """Test document generation with inconsistent hierarchy."""
        document = generator.generate_extreme_structure("inconsistent_hierarchy")
        
        assert document is not None
        assert len(document) > 0
        # Should contain various heading levels
        assert "#" in document
    
    def test_generate_extreme_structure_only_tables(self, generator):
        """Test document generation with only tables."""
        document = generator.generate_extreme_structure("only_tables")
        
        assert document is not None
        assert len(document) > 0
        # Should contain table markers
        assert "|" in document
        assert "---" in document
    
    def test_generate_extreme_structure_many_headings(self, generator):
        """Test document generation with many headings."""
        document = generator.generate_extreme_structure("many_headings")
        
        assert document is not None
        assert len(document) > 0
        # Should contain many headings
        heading_count = sum(1 for line in document.split("\n") if line.startswith("#"))
        assert heading_count >= 100
    
    def test_generate_extreme_structure_many_sections(self, generator):
        """Test document generation with many sections."""
        document = generator.generate_extreme_structure("many_sections")
        
        assert document is not None
        assert len(document) > 0
        # Should contain many sections
        section_count = document.count("## Section")
        assert section_count >= 100
    
    def test_generate_multilingual_document(self, generator):
        """Test multilingual document generation."""
        languages = ["english", "chinese", "arabic", "cyrillic"]
        document = generator.generate_multilingual_document(languages)
        
        assert document is not None
        assert len(document) > 0
        assert "# Multilingual Cybersecurity Policy" in document
        # Should contain sections for each language
        for lang in languages:
            assert lang.title() in document
    
    def test_cache_save_and_load_text(self, generator):
        """Test caching text content."""
        key = "test_policy_1"
        content = "# Test Policy\n\nThis is a test policy document."
        
        # Save to cache
        filepath = generator.save_to_cache(key, content)
        assert filepath.exists()
        
        # Load from cache
        loaded_content = generator.load_from_cache(key)
        assert loaded_content == content
    
    def test_cache_save_and_load_bytes(self, generator):
        """Test caching binary content."""
        key = "test_pdf_1"
        content = b"%PDF-1.4\nTest PDF content"
        
        # Save to cache
        filepath = generator.save_to_cache(key, content)
        assert filepath.exists()
        
        # Load from cache
        loaded_content = generator.load_from_cache(key)
        assert loaded_content == content
    
    def test_invalid_attack_type(self, generator):
        """Test that invalid attack type raises error."""
        with pytest.raises(ValueError):
            generator.generate_malicious_pdf("invalid_type")
    
    def test_invalid_structure_type(self, generator):
        """Test that invalid structure type raises error."""
        with pytest.raises(ValueError):
            generator.generate_extreme_structure("invalid_type")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
