"""
Property Test: Domain-Specific CSF Prioritization

**Property 36: Domain-Specific CSF Prioritization**
**Validates: Requirements 12.1, 12.2, 12.3, 12.4**

This property test verifies that each policy domain correctly prioritizes
the appropriate CSF subcategories:
- ISMS domain → Govern (GV) function subcategories
- Risk Management domain → GV.RM, GV.OV, ID.RA subcategories
- Patch Management domain → ID.RA, PR.DS, PR.PS subcategories
- Data Privacy domain → PR.AA, PR.DS, PR.AT subcategories
"""

import pytest
from hypothesis import given, strategies as st, settings, HealthCheck

from analysis.domain_mapper import DomainMapper
from reference_builder.reference_catalog import ReferenceCatalog


class TestDomainSpecificPrioritization:
    """Property tests for domain-specific CSF prioritization."""
    
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
    
    def test_isms_domain_prioritizes_govern_function(self, mapper):
        """Property: ISMS domain prioritizes all Govern (GV) function subcategories.
        
        Validates Requirement 12.1:
        When analyzing an ISMS policy, prioritize Govern (GV) function subcategories.
        """
        # Get prioritized subcategories for ISMS domain
        subcategories, warning = mapper.get_prioritized_subcategories('isms')
        
        # Extract subcategory IDs
        subcategory_ids = [s.subcategory_id for s in subcategories]
        
        # Verify all returned subcategories are from Govern function
        for subcat in subcategories:
            assert subcat.function == 'Govern', (
                f"ISMS domain should only prioritize Govern function, "
                f"but got {subcat.function} for {subcat.subcategory_id}"
            )
        
        # Verify all GV subcategories are included
        expected_gv_ids = [
            'GV.OC-01', 'GV.OC-02', 'GV.OC-03',
            'GV.OV-01', 'GV.OV-02',
            'GV.RM-01', 'GV.RM-02', 'GV.RM-03',
            'GV.SC-01', 'GV.SC-02',
            'GV.RR-01', 'GV.RR-02',
            'GV.PO-01', 'GV.PO-02'
        ]
        
        for expected_id in expected_gv_ids:
            assert expected_id in subcategory_ids, (
                f"ISMS domain should include {expected_id}"
            )
        
        # Verify no warning for ISMS domain
        assert warning is None, "ISMS domain should not have a warning"
    
    def test_risk_management_domain_prioritizes_correct_subcategories(self, mapper):
        """Property: Risk Management domain prioritizes GV.RM, GV.OV, and ID.RA.
        
        Validates Requirement 12.2:
        When analyzing a Risk Management policy, prioritize GV.RM, GV.OV,
        and ID.RA subcategories.
        """
        # Get prioritized subcategories for Risk Management domain
        subcategories, warning = mapper.get_prioritized_subcategories('risk_management')
        
        # Extract subcategory IDs
        subcategory_ids = [s.subcategory_id for s in subcategories]
        
        # Expected subcategories for Risk Management
        expected_ids = [
            'GV.RM-01', 'GV.RM-02', 'GV.RM-03',  # Risk Management Strategy
            'GV.OV-01',  # Oversight
            'ID.RA-01', 'ID.RA-02', 'ID.RA-03', 'ID.RA-04', 'ID.RA-05'  # Risk Assessment
        ]
        
        # Verify all expected subcategories are included
        for expected_id in expected_ids:
            assert expected_id in subcategory_ids, (
                f"Risk Management domain should include {expected_id}"
            )
        
        # Verify no warning for Risk Management domain
        assert warning is None, "Risk Management domain should not have a warning"
    
    def test_patch_management_domain_prioritizes_correct_subcategories(self, mapper):
        """Property: Patch Management domain prioritizes ID.RA, PR.DS, and PR.PS.
        
        Validates Requirement 12.3:
        When analyzing a Patch Management policy, prioritize ID.RA, PR.DS,
        and PR.PS subcategories.
        """
        # Get prioritized subcategories for Patch Management domain
        subcategories, warning = mapper.get_prioritized_subcategories('patch_management')
        
        # Extract subcategory IDs
        subcategory_ids = [s.subcategory_id for s in subcategories]
        
        # Expected subcategories for Patch Management
        expected_ids = [
            'ID.RA-01',  # Vulnerability identification
            'PR.DS-01', 'PR.DS-02',  # Data Security
            'PR.PS-01', 'PR.PS-02'  # Platform Security (patching)
        ]
        
        # Verify all expected subcategories are included
        for expected_id in expected_ids:
            assert expected_id in subcategory_ids, (
                f"Patch Management domain should include {expected_id}"
            )
        
        # Verify no warning for Patch Management domain
        assert warning is None, "Patch Management domain should not have a warning"
    
    def test_data_privacy_domain_prioritizes_correct_subcategories(self, mapper):
        """Property: Data Privacy domain prioritizes PR.AA, PR.DS, and PR.AT.
        
        Validates Requirement 12.4:
        When analyzing a Data Privacy policy, prioritize PR.AA, PR.DS,
        and PR.AT subcategories.
        """
        # Get prioritized subcategories for Data Privacy domain
        subcategories, warning = mapper.get_prioritized_subcategories('data_privacy')
        
        # Extract subcategory IDs
        subcategory_ids = [s.subcategory_id for s in subcategories]
        
        # Expected subcategories for Data Privacy
        expected_ids = [
            'PR.AA-01', 'PR.AA-02', 'PR.AA-03', 'PR.AA-05',  # Access Control
            'PR.DS-01', 'PR.DS-02',  # Data Security
            'PR.AT-01'  # Awareness and Training
        ]
        
        # Verify all expected subcategories are included
        for expected_id in expected_ids:
            assert expected_id in subcategory_ids, (
                f"Data Privacy domain should include {expected_id}"
            )
        
        # Verify warning is present for Data Privacy domain
        assert warning is not None, (
            "Data Privacy domain should include privacy framework limitation warning"
        )
        assert "NIST CSF 2.0" in warning, (
            "Warning should mention NIST CSF 2.0"
        )
        assert "privacy framework" in warning.lower(), (
            "Warning should mention privacy framework limitation"
        )
    
    @given(domain=st.sampled_from(['isms', 'risk_management', 'patch_management', 'data_privacy']))
    @settings(max_examples=20, deadline=None, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_all_domains_return_valid_subcategories(self, mapper, domain):
        """Property: All supported domains return non-empty valid subcategories.
        
        Verifies that:
        1. Each domain returns at least one subcategory
        2. All returned subcategories are valid CSFSubcategory objects
        3. All subcategory IDs are properly formatted
        """
        subcategories, warning = mapper.get_prioritized_subcategories(domain)
        
        # Verify non-empty result
        assert len(subcategories) > 0, (
            f"Domain '{domain}' should return at least one subcategory"
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
            
            # Verify ID format (e.g., GV.RM-01)
            assert '.' in subcat.subcategory_id, (
                f"Subcategory ID should contain '.': {subcat.subcategory_id}"
            )
            assert '-' in subcat.subcategory_id, (
                f"Subcategory ID should contain '-': {subcat.subcategory_id}"
            )
    
    def test_supported_domains_list(self, mapper):
        """Property: Mapper provides list of supported domains."""
        supported = mapper.get_supported_domains()
        
        # Verify expected domains are present
        expected_domains = ['isms', 'risk_management', 'patch_management', 'data_privacy']
        for domain in expected_domains:
            assert domain in supported, (
                f"Domain '{domain}' should be in supported domains list"
            )
    
    def test_domain_descriptions_available(self, mapper):
        """Property: Each supported domain has a human-readable description."""
        supported = mapper.get_supported_domains()
        
        for domain in supported:
            description = mapper.get_domain_description(domain)
            assert description is not None, (
                f"Domain '{domain}' should have a description"
            )
            assert len(description) > 0, (
                f"Domain '{domain}' description should not be empty"
            )
