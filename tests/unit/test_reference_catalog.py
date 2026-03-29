"""
Unit tests for Reference Catalog.

Tests the ReferenceCatalog class for building, persisting, loading,
and querying the NIST CSF 2.0 subcategory catalog.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
"""

import json
import tempfile
from pathlib import Path

import pytest

from models.domain import CSFSubcategory
from reference_builder.reference_catalog import ReferenceCatalog


class TestReferenceCatalog:
    """Test suite for ReferenceCatalog class."""
    
    def test_build_from_nonexistent_guide_raises_error(self):
        """Test that building from nonexistent CIS guide raises FileNotFoundError."""
        catalog = ReferenceCatalog()
        
        with pytest.raises(FileNotFoundError):
            catalog.build_from_cis_guide("/nonexistent/path/to/guide.pdf")
    
    def test_build_creates_49_subcategories(self, tmp_path):
        """Test that building catalog creates exactly 49 subcategories."""
        # Create a dummy CIS guide file
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Verify 49 subcategories
        all_subs = catalog.get_all_subcategories()
        assert len(all_subs) == 49
    
    def test_get_subcategory_by_id(self, tmp_path):
        """Test retrieving specific subcategory by ID."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Test known subcategory
        subcategory = catalog.get_subcategory("GV.RM-01")
        assert subcategory is not None
        assert subcategory.subcategory_id == "GV.RM-01"
        assert subcategory.function == "Govern"
        assert "risk" in subcategory.description.lower()
    
    def test_get_subcategory_nonexistent_returns_none(self, tmp_path):
        """Test that getting nonexistent subcategory returns None."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        subcategory = catalog.get_subcategory("INVALID-ID")
        assert subcategory is None
    
    def test_get_by_function(self, tmp_path):
        """Test retrieving subcategories by CSF function."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Test Govern function
        govern_subs = catalog.get_by_function("Govern")
        assert len(govern_subs) > 0
        assert all(sub.function == "Govern" for sub in govern_subs)
        
        # Test all functions
        for function in ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]:
            subs = catalog.get_by_function(function)
            assert len(subs) > 0, f"No subcategories found for function: {function}"
    
    def test_get_by_domain(self, tmp_path):
        """Test retrieving subcategories by domain tag."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Test risk_management domain
        risk_subs = catalog.get_by_domain("risk_management")
        assert len(risk_subs) > 0
        assert all("risk_management" in sub.domain_tags for sub in risk_subs)
        
        # Test isms domain
        isms_subs = catalog.get_by_domain("isms")
        assert len(isms_subs) > 0
        assert all("isms" in sub.domain_tags for sub in isms_subs)
    
    def test_persist_and_load(self, tmp_path):
        """Test persisting catalog to JSON and loading it back."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        # Build catalog
        catalog1 = ReferenceCatalog()
        catalog1.build_from_cis_guide(str(guide_path))
        
        # Persist to JSON
        json_path = tmp_path / "catalog.json"
        catalog1.persist(str(json_path))
        
        # Verify JSON file exists
        assert json_path.exists()
        
        # Load into new catalog
        catalog2 = ReferenceCatalog()
        catalog2.load(str(json_path))
        
        # Verify equivalence
        assert len(catalog2.get_all_subcategories()) == 49
        
        # Check specific subcategory
        sub1 = catalog1.get_subcategory("GV.RM-01")
        sub2 = catalog2.get_subcategory("GV.RM-01")
        assert sub1.subcategory_id == sub2.subcategory_id
        assert sub1.function == sub2.function
        assert sub1.category == sub2.category
        assert sub1.description == sub2.description
        assert sub1.keywords == sub2.keywords
        assert sub1.domain_tags == sub2.domain_tags
        assert sub1.priority == sub2.priority
    
    def test_load_from_nonexistent_file_raises_error(self):
        """Test that loading from nonexistent file raises FileNotFoundError."""
        catalog = ReferenceCatalog()
        
        with pytest.raises(FileNotFoundError):
            catalog.load("/nonexistent/catalog.json")
    
    def test_validate_completeness(self, tmp_path):
        """Test catalog completeness validation."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Should be complete with 49 subcategories
        assert catalog.validate_completeness() is True
    
    def test_all_subcategories_have_required_fields(self, tmp_path):
        """Test that all subcategories have all required fields populated."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        for subcategory in catalog.get_all_subcategories():
            # Check all required fields are present and non-empty
            assert subcategory.subcategory_id, f"Missing subcategory_id"
            assert subcategory.function, f"Missing function for {subcategory.subcategory_id}"
            assert subcategory.category, f"Missing category for {subcategory.subcategory_id}"
            assert subcategory.description, f"Missing description for {subcategory.subcategory_id}"
            assert len(subcategory.keywords) > 0, f"Missing keywords for {subcategory.subcategory_id}"
            assert len(subcategory.domain_tags) > 0, f"Missing domain_tags for {subcategory.subcategory_id}"
            assert len(subcategory.mapped_templates) > 0, f"Missing mapped_templates for {subcategory.subcategory_id}"
            assert subcategory.priority in ["critical", "high", "medium", "low"], \
                f"Invalid priority for {subcategory.subcategory_id}: {subcategory.priority}"
    
    def test_functions_distribution(self, tmp_path):
        """Test that subcategories are distributed across all 6 CSF functions."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Verify all 6 functions are represented
        functions = ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]
        for function in functions:
            subs = catalog.get_by_function(function)
            assert len(subs) > 0, f"No subcategories found for function: {function}"
    
    def test_json_format_is_valid(self, tmp_path):
        """Test that persisted JSON is valid and well-formed."""
        guide_path = tmp_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Persist to JSON
        json_path = tmp_path / "catalog.json"
        catalog.persist(str(json_path))
        
        # Load and validate JSON structure
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        assert "subcategories" in data
        assert len(data["subcategories"]) == 49
        
        # Check first subcategory has all fields
        first_sub = data["subcategories"][0]
        required_fields = [
            "subcategory_id", "function", "category", "description",
            "keywords", "domain_tags", "mapped_templates", "priority"
        ]
        for field in required_fields:
            assert field in first_sub, f"Missing field: {field}"
