"""
Property Test: Unknown Domain Fallback

**Property 37: Unknown Domain Fallback**
**Validates: Requirements 12.6**

This property test verifies that when a policy domain cannot be determined
or is unknown, the system evaluates against all CSF functions rather than
failing or returning an empty result.
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from analysis.domain_mapper import DomainMapper
from reference_builder.reference_catalog import ReferenceCatalog


class TestUnknownDomainFallback:
    """Property tests for unknown domain fallback behavior."""
    
    @pytest.fixture
    def catalog(self):
        """Create reference catalog with all CSF subcategories."""
        catalog = ReferenceCatalog()
        # Build catalog from hardcoded subcategories
        catalog._subcategories = {}
        catalog._by_function = {}
        catalog._by_domain = {}
        
        # Load the hardcoded subcategories
        subcategories = catalog._get_nist_csf_subcategories()
        
        for subcategory in subcategories:
            catalog._subcategories[subcategory.subcategory_id] = subcategory
            
            # Index by function
            if subcategory.function not in catalog._by_function:
                catalog._by_function[subcategory.function] = []
            catalog._by_function[subcategory.function].append(subcategory)
            
            # Index by domain tags
            for domain in subcategory.domain_tags:
                if domain not in catalog._by_domain:
                    catalog._by_domain[domain] = []
                catalog._by_domain[domain].append(subcategory)
        
        return catalog
    
    @pytest.fixture
    def mapper(self, catalog):
        """Create domain mapper with catalog."""
        return DomainMapper(catalog)
    
    def test_none_domain_returns_all_subcategories(self, mapper, catalog):
        """Property: None domain returns all CSF subcategories.
        
        Validates Requirement 12.6:
        Where policy type cannot be determined, evaluate against all CSF functions.
        """
        # Get subcategories with None domain
        subcategories, warning = mapper.get_prioritized_subcategories(None)
        
        # Get all subcategories from catalog
        all_subcategories = catalog.get_all_subcategories()
        
        # Verify same count
        assert len(subcategories) == len(all_subcategories), (
            f"None domain should return all {len(all_subcategories)} subcategories, "
            f"but got {len(subcategories)}"
        )
        
        # Verify all subcategory IDs match
        returned_ids = {s.subcategory_id for s in subcategories}
        expected_ids = {s.subcategory_id for s in all_subcategories}
        
        assert returned_ids == expected_ids, (
            "None domain should return exactly the same subcategories as catalog.get_all_subcategories()"
        )
        
        # Verify no warning for None domain
        assert warning is None, "None domain should not have a warning"
    
    @given(unknown_domain=st.text(min_size=1, max_size=50).filter(
        lambda x: x not in ['isms', 'risk_management', 'patch_management', 'data_privacy']
    ))
    @settings(max_examples=50, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_unknown_domain_returns_all_subcategories(self, mapper, catalog, unknown_domain):
        """Property: Unknown domain returns all CSF subcategories.
        
        Validates Requirement 12.6:
        Where policy type cannot be determined, evaluate against all CSF functions.
        
        Tests with randomly generated domain names that are not in the supported list.
        """
        # Get subcategories with unknown domain
        subcategories, warning = mapper.get_prioritized_subcategories(unknown_domain)
        
        # Get all subcategories from catalog
        all_subcategories = catalog.get_all_subcategories()
        
        # Verify same count
        assert len(subcategories) == len(all_subcategories), (
            f"Unknown domain '{unknown_domain}' should return all {len(all_subcategories)} subcategories, "
            f"but got {len(subcategories)}"
        )
        
        # Verify all subcategory IDs match
        returned_ids = {s.subcategory_id for s in subcategories}
        expected_ids = {s.subcategory_id for s in all_subcategories}
        
        assert returned_ids == expected_ids, (
            f"Unknown domain '{unknown_domain}' should return exactly the same subcategories "
            f"as catalog.get_all_subcategories()"
        )
        
        # Verify no warning for unknown domain
        assert warning is None, f"Unknown domain '{unknown_domain}' should not have a warning"
    
    def test_unknown_domain_includes_all_functions(self, mapper):
        """Property: Unknown domain includes subcategories from all CSF functions.
        
        Verifies that the fallback behavior includes subcategories from all six
        CSF functions: Govern, Identify, Protect, Detect, Respond, Recover.
        """
        # Get subcategories with unknown domain
        subcategories, warning = mapper.get_prioritized_subcategories('unknown_domain_xyz')
        
        # Extract functions
        functions = {s.function for s in subcategories}
        
        # Verify all six CSF functions are represented
        expected_functions = {'Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover'}
        
        assert functions == expected_functions, (
            f"Unknown domain should include all CSF functions, "
            f"expected {expected_functions}, got {functions}"
        )
    
    def test_empty_string_domain_returns_all_subcategories(self, mapper, catalog):
        """Property: Empty string domain returns all CSF subcategories.
        
        Validates that empty string is treated as unknown domain.
        """
        # Get subcategories with empty string domain
        subcategories, warning = mapper.get_prioritized_subcategories('')
        
        # Get all subcategories from catalog
        all_subcategories = catalog.get_all_subcategories()
        
        # Verify same count
        assert len(subcategories) == len(all_subcategories), (
            f"Empty string domain should return all {len(all_subcategories)} subcategories, "
            f"but got {len(subcategories)}"
        )
        
        # Verify no warning
        assert warning is None, "Empty string domain should not have a warning"
    
    def test_unknown_domain_returns_valid_subcategories(self, mapper):
        """Property: Unknown domain returns valid CSFSubcategory objects.
        
        Verifies that the fallback behavior returns properly structured
        subcategory objects with all required fields.
        """
        # Get subcategories with unknown domain
        subcategories, warning = mapper.get_prioritized_subcategories('completely_unknown')
        
        # Verify non-empty result
        assert len(subcategories) > 0, (
            "Unknown domain should return at least one subcategory"
        )
        
        # Verify all are valid CSFSubcategory objects
        for subcat in subcategories:
            assert hasattr(subcat, 'subcategory_id'), (
                "Each subcategory should have subcategory_id"
            )
            assert hasattr(subcat, 'function'), (
                "Each subcategory should have function"
            )
            assert hasattr(subcat, 'category'), (
                "Each subcategory should have category"
            )
            assert hasattr(subcat, 'description'), (
                "Each subcategory should have description"
            )
            assert hasattr(subcat, 'keywords'), (
                "Each subcategory should have keywords"
            )
            assert hasattr(subcat, 'domain_tags'), (
                "Each subcategory should have domain_tags"
            )
            assert hasattr(subcat, 'priority'), (
                "Each subcategory should have priority"
            )
            
            # Verify non-empty required fields
            assert subcat.subcategory_id, "subcategory_id should not be empty"
            assert subcat.function, "function should not be empty"
            assert subcat.category, "category should not be empty"
            assert subcat.description, "description should not be empty"
    
    def test_case_sensitivity_of_unknown_domains(self, mapper, catalog):
        """Property: Domain matching is case-sensitive for unknown domains.
        
        Verifies that variations in case for known domains are treated as unknown.
        """
        # Test uppercase variation of known domain
        subcategories_upper, _ = mapper.get_prioritized_subcategories('ISMS')
        all_subcategories = catalog.get_all_subcategories()
        
        # Should return all subcategories (fallback behavior)
        assert len(subcategories_upper) == len(all_subcategories), (
            "Uppercase 'ISMS' should be treated as unknown and return all subcategories"
        )
        
        # Test mixed case variation
        subcategories_mixed, _ = mapper.get_prioritized_subcategories('Risk_Management')
        
        # Should return all subcategories (fallback behavior)
        assert len(subcategories_mixed) == len(all_subcategories), (
            "Mixed case 'Risk_Management' should be treated as unknown and return all subcategories"
        )
