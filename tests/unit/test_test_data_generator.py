"""
Unit Tests for TestDataGenerator

Tests document generation with various specifications, malicious PDF generation,
gap policy generation, extreme structure generation, and multilingual document generation.

**Validates: Task 32.1**
"""

import pytest
from pathlib import Path
from tests.extreme.data_generator import TestDataGenerator, DocumentSpec


class TestTestDataGenerator:
    """Unit tests for TestDataGenerator component."""
    
    @pytest.fixture
    def generator(self, tmp_path):
        """Create TestDataGenerator instance with temporary cache directory."""
        return TestDataGenerator(cache_dir=tmp_path / "test_cache")
    
    # Test document generation with various specifications
    
    def test_generate_policy_document_basic(self, generator):
        """Test basic policy document generation."""
        spec = DocumentSpec(
            size_pages=5,
            words_per_page=100,
            sections_per_page=2,
            coverage_percentage=0.5
        )
        
        document = generator.generate_policy_document(spec)
        
        assert isinstance(document, str)
        assert len(document) > 0
        assert "# Cybersecurity Policy Document" in document
        assert "## Executive Summary" in document
    
    def test_generate_policy_document_with_csf_keywords(self, generator):
        """Test document generation includes CSF keywords when specified."""
        spec = DocumentSpec(
            size_pages=3,
            words_per_page=200,
            sections_per_page=3,
            coverage_percentage=0.8,
            include_csf_keywords=True
        )
        
        document = generator.generate_policy_document(spec)
        
        # Should contain some CSF-related content
        assert any(keyword in document.lower() for keyword in 
                  ["asset", "governance", "risk", "access", "security"])
    
    def test_generate_policy_document_without_csf_keywords(self, generator):
        """Test document generation without CSF keywords."""
        spec = DocumentSpec(
            size_pages=2,
            words_per_page=100,
            sections_per_page=2,
            coverage_percentage=0.5,
            include_csf_keywords=False
        )
        
        document = generator.generate_policy_document(spec)
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_policy_document_zero_coverage(self, generator):
        """Test document generation with zero coverage."""
        spec = DocumentSpec(
            size_pages=2,
            words_per_page=100,
            sections_per_page=2,
            coverage_percentage=0.0
        )
        
        document = generator.generate_policy_document(spec)
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_policy_document_full_coverage(self, generator):
        """Test document generation with full coverage."""
        spec = DocumentSpec(
            size_pages=10,
            words_per_page=500,
            sections_per_page=3,
            coverage_percentage=1.0
        )
        
        document = generator.generate_policy_document(spec)
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_policy_document_structure_types(self, generator):
        """Test document generation with different structure types."""
        structure_types = ["normal", "flat", "deep", "inconsistent"]
        
        for structure_type in structure_types:
            spec = DocumentSpec(
                size_pages=3,
                words_per_page=100,
                sections_per_page=2,
                structure_type=structure_type
            )
            
            document = generator.generate_policy_document(spec)
            
            assert isinstance(document, str)
            assert len(document) > 0
    
    # Test malicious PDF generation
    
    def test_generate_malicious_pdf_javascript(self, generator):
        """Test malicious PDF generation with embedded JavaScript."""
        pdf_content = generator.generate_malicious_pdf("javascript")
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert b"%PDF" in pdf_content
        assert b"JavaScript" in pdf_content
    
    def test_generate_malicious_pdf_malformed(self, generator):
        """Test malicious PDF generation with malformed structure."""
        pdf_content = generator.generate_malicious_pdf("malformed")
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert b"%PDF" in pdf_content
    
    def test_generate_malicious_pdf_recursive(self, generator):
        """Test malicious PDF generation with recursive references."""
        pdf_content = generator.generate_malicious_pdf("recursive")
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 0
        assert b"%PDF" in pdf_content
    
    def test_generate_malicious_pdf_large_object(self, generator):
        """Test malicious PDF generation with large embedded object."""
        pdf_content = generator.generate_malicious_pdf("large_object")
        
        assert isinstance(pdf_content, bytes)
        assert len(pdf_content) > 1000000  # Should be > 1MB
        assert b"%PDF" in pdf_content
    
    def test_generate_malicious_pdf_invalid_type(self, generator):
        """Test malicious PDF generation with invalid attack type."""
        with pytest.raises(ValueError, match="Unknown attack type"):
            generator.generate_malicious_pdf("invalid_type")
    
    # Test gap policy generation
    
    def test_generate_gap_policy_with_specific_gaps(self, generator):
        """Test gap policy generation with specific gap subcategories."""
        gap_subcategories = ["ID.AM-1", "ID.AM-2", "PR.AC-1", "PR.AC-2"]
        
        document = generator.generate_gap_policy(gap_subcategories)
        
        assert isinstance(document, str)
        assert len(document) > 0
        assert "# Cybersecurity Policy Document" in document
        
        # Gap subcategories should NOT be mentioned
        for gap in gap_subcategories:
            assert gap not in document
    
    def test_generate_gap_policy_no_gaps(self, generator):
        """Test gap policy generation with no gaps (full coverage)."""
        document = generator.generate_gap_policy([])
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_gap_policy_all_gaps(self, generator):
        """Test gap policy generation with all subcategories as gaps."""
        all_subcategories = generator.CSF_SUBCATEGORIES.copy()
        
        document = generator.generate_gap_policy(all_subcategories)
        
        assert isinstance(document, str)
        # Should be minimal since all are gaps
        assert "# Cybersecurity Policy Document" in document
    
    # Test extreme structure generation
    
    def test_generate_extreme_structure_no_headings(self, generator):
        """Test extreme structure generation with no headings."""
        document = generator.generate_extreme_structure("no_headings")
        
        assert isinstance(document, str)
        assert len(document) > 0
        # Should not contain markdown headings
        assert not any(line.startswith("#") for line in document.split("\n"))
    
    def test_generate_extreme_structure_deep_nesting(self, generator):
        """Test extreme structure generation with deep nesting."""
        document = generator.generate_extreme_structure("deep_nesting")
        
        assert isinstance(document, str)
        assert len(document) > 0
        # Should contain many heading levels
        assert "# Level" in document or "## Level" in document
    
    def test_generate_extreme_structure_inconsistent_hierarchy(self, generator):
        """Test extreme structure generation with inconsistent hierarchy."""
        document = generator.generate_extreme_structure("inconsistent_hierarchy")
        
        assert isinstance(document, str)
        assert len(document) > 0
        # Should contain various heading levels
        assert "#" in document
    
    def test_generate_extreme_structure_only_tables(self, generator):
        """Test extreme structure generation with only tables."""
        document = generator.generate_extreme_structure("only_tables")
        
        assert isinstance(document, str)
        assert len(document) > 0
        # Should contain table markers
        assert "|" in document
    
    def test_generate_extreme_structure_many_headings(self, generator):
        """Test extreme structure generation with many headings."""
        document = generator.generate_extreme_structure("many_headings")
        
        assert isinstance(document, str)
        assert len(document) > 0
        # Should contain many headings
        heading_count = sum(1 for line in document.split("\n") if line.startswith("#"))
        assert heading_count > 100
    
    def test_generate_extreme_structure_many_sections(self, generator):
        """Test extreme structure generation with many sections."""
        document = generator.generate_extreme_structure("many_sections")
        
        assert isinstance(document, str)
        assert len(document) > 0
        # Should contain many sections
        assert "## Section" in document
    
    def test_generate_extreme_structure_invalid_type(self, generator):
        """Test extreme structure generation with invalid type."""
        with pytest.raises(ValueError, match="Unknown structure type"):
            generator.generate_extreme_structure("invalid_type")
    
    # Test multilingual document generation
    
    def test_generate_multilingual_document_chinese(self, generator):
        """Test multilingual document generation with Chinese."""
        document = generator.generate_multilingual_document(["chinese"])
        
        assert isinstance(document, str)
        assert len(document) > 0
        assert "# Multilingual Cybersecurity Policy" in document
    
    def test_generate_multilingual_document_arabic(self, generator):
        """Test multilingual document generation with Arabic."""
        document = generator.generate_multilingual_document(["arabic"])
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_multilingual_document_cyrillic(self, generator):
        """Test multilingual document generation with Cyrillic."""
        document = generator.generate_multilingual_document(["cyrillic"])
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_multilingual_document_emoji(self, generator):
        """Test multilingual document generation with emoji."""
        document = generator.generate_multilingual_document(["emoji"])
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_multilingual_document_greek(self, generator):
        """Test multilingual document generation with Greek symbols."""
        document = generator.generate_multilingual_document(["greek"])
        
        assert isinstance(document, str)
        assert len(document) > 0
    
    def test_generate_multilingual_document_multiple_languages(self, generator):
        """Test multilingual document generation with multiple languages."""
        languages = ["chinese", "arabic", "cyrillic", "emoji", "greek"]
        
        document = generator.generate_multilingual_document(languages)
        
        assert isinstance(document, str)
        assert len(document) > 0
        # Should have sections for each language
        for lang in languages:
            assert lang.title() in document
    
    # Test caching functionality
    
    def test_save_to_cache_string(self, generator):
        """Test saving string content to cache."""
        content = "Test policy document content"
        key = "test_policy_1"
        
        filepath = generator.save_to_cache(key, content)
        
        assert filepath.exists()
        assert filepath.suffix == ".md"
        assert filepath.read_text() == content
    
    def test_save_to_cache_bytes(self, generator):
        """Test saving bytes content to cache."""
        content = b"%PDF-1.4\nTest PDF content"
        key = "test_pdf_1"
        
        filepath = generator.save_to_cache(key, content)
        
        assert filepath.exists()
        assert filepath.suffix == ".pdf"
        assert filepath.read_bytes() == content
    
    def test_save_to_cache_json(self, generator):
        """Test saving JSON content to cache."""
        content = {"test": "data", "value": 123}
        key = "test_json_1"
        
        filepath = generator.save_to_cache(key, content)
        
        assert filepath.exists()
        assert filepath.suffix == ".json"
    
    def test_load_from_cache_existing(self, generator):
        """Test loading existing content from cache."""
        content = "Cached policy document"
        key = "test_cached_policy"
        
        # Save first
        generator.save_to_cache(key, content)
        
        # Load
        loaded_content = generator.load_from_cache(key)
        
        assert loaded_content == content
    
    def test_load_from_cache_nonexistent(self, generator):
        """Test loading nonexistent content from cache."""
        loaded_content = generator.load_from_cache("nonexistent_key")
        
        assert loaded_content is None
