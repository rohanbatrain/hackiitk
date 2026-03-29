"""
Property-based tests for Reference Catalog.

Tests universal properties of the reference catalog including completeness,
persistence round-trip, and query consistency.

**Validates: Requirements 3.2, 3.3, 3.4, 3.6, 13.4**
"""

import json
import tempfile
from pathlib import Path

import pytest
from hypothesis import given, strategies as st, settings

from models.domain import CSFSubcategory
from reference_builder.reference_catalog import ReferenceCatalog


# ============================================================================
# Property 6: Reference Catalog Completeness
# **Validates: Requirements 3.2, 3.3, 3.6**
# ============================================================================


@settings(max_examples=10)  # Reduced since building catalog is deterministic
@given(st.just(None))  # Dummy strategy since catalog building is deterministic
def test_property_6_catalog_completeness(dummy):
    """
    Feature: offline-policy-gap-analyzer
    Property 6: Reference Catalog Completeness
    
    For any Reference_Catalog built from the CIS guide, all 49 NIST CSF 2.0
    subcategories shall be present, and each subcategory shall contain all
    required fields: CSF_Function, Category, Subcategory_ID, Description,
    Keywords, Domain_Tags, and Mapped_Templates.
    
    **Validates: Requirements 3.2, 3.3, 3.6**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy CIS guide file
        guide_path = Path(tmpdir) / "cis_guide.pdf"
        guide_path.touch()
        
        # Build catalog
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Property: Catalog contains exactly 49 subcategories
        all_subcategories = catalog.get_all_subcategories()
        assert len(all_subcategories) == 49, \
            f"Expected 49 subcategories, got {len(all_subcategories)}"
        
        # Property: Each subcategory has all required fields
        required_fields = [
            "subcategory_id", "function", "category", "description",
            "keywords", "domain_tags", "mapped_templates", "priority"
        ]
        
        for subcategory in all_subcategories:
            # Check field presence
            assert hasattr(subcategory, "subcategory_id")
            assert hasattr(subcategory, "function")
            assert hasattr(subcategory, "category")
            assert hasattr(subcategory, "description")
            assert hasattr(subcategory, "keywords")
            assert hasattr(subcategory, "domain_tags")
            assert hasattr(subcategory, "mapped_templates")
            assert hasattr(subcategory, "priority")
            
            # Check field values are non-empty
            assert subcategory.subcategory_id, \
                "subcategory_id must be non-empty"
            assert subcategory.function, \
                f"function must be non-empty for {subcategory.subcategory_id}"
            assert subcategory.category, \
                f"category must be non-empty for {subcategory.subcategory_id}"
            assert subcategory.description, \
                f"description must be non-empty for {subcategory.subcategory_id}"
            assert len(subcategory.keywords) > 0, \
                f"keywords must be non-empty for {subcategory.subcategory_id}"
            assert len(subcategory.domain_tags) > 0, \
                f"domain_tags must be non-empty for {subcategory.subcategory_id}"
            assert len(subcategory.mapped_templates) > 0, \
                f"mapped_templates must be non-empty for {subcategory.subcategory_id}"
            assert subcategory.priority in ["critical", "high", "medium", "low"], \
                f"Invalid priority for {subcategory.subcategory_id}: {subcategory.priority}"
        
        # Property: All 6 CSF functions are represented
        functions = set(sub.function for sub in all_subcategories)
        expected_functions = {"Govern", "Identify", "Protect", "Detect", "Respond", "Recover"}
        assert functions == expected_functions, \
            f"Expected functions {expected_functions}, got {functions}"
        
        # Property: Subcategory IDs are unique
        subcategory_ids = [sub.subcategory_id for sub in all_subcategories]
        assert len(subcategory_ids) == len(set(subcategory_ids)), \
            "Subcategory IDs must be unique"


# ============================================================================
# Property 7: Reference Catalog Persistence Round-Trip
# **Validates: Requirements 3.4, 13.4**
# ============================================================================


@settings(max_examples=10)  # Reduced since persistence is deterministic
@given(st.just(None))  # Dummy strategy since catalog is deterministic
def test_property_7_catalog_persistence_roundtrip(dummy):
    """
    Feature: offline-policy-gap-analyzer
    Property 7: Reference Catalog Persistence Round-Trip
    
    For any Reference_Catalog, serializing to JSON then deserializing shall
    produce an equivalent catalog structure with all subcategories and fields
    preserved.
    
    **Validates: Requirements 3.4, 13.4**
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Create dummy CIS guide and build catalog
        guide_path = tmpdir_path / "cis_guide.pdf"
        guide_path.touch()
        
        catalog1 = ReferenceCatalog()
        catalog1.build_from_cis_guide(str(guide_path))
        
        # Persist to JSON
        json_path = tmpdir_path / "catalog.json"
        catalog1.persist(str(json_path))
        
        # Load into new catalog
        catalog2 = ReferenceCatalog()
        catalog2.load(str(json_path))
        
        # Property: Same number of subcategories
        subs1 = catalog1.get_all_subcategories()
        subs2 = catalog2.get_all_subcategories()
        assert len(subs1) == len(subs2), \
            f"Subcategory count mismatch: {len(subs1)} vs {len(subs2)}"
        
        # Property: All subcategories preserved with same IDs
        ids1 = sorted([sub.subcategory_id for sub in subs1])
        ids2 = sorted([sub.subcategory_id for sub in subs2])
        assert ids1 == ids2, "Subcategory IDs not preserved"
        
        # Property: Each subcategory's fields are preserved
        for sub_id in ids1:
            sub1 = catalog1.get_subcategory(sub_id)
            sub2 = catalog2.get_subcategory(sub_id)
            
            assert sub1.subcategory_id == sub2.subcategory_id
            assert sub1.function == sub2.function
            assert sub1.category == sub2.category
            assert sub1.description == sub2.description
            assert sub1.keywords == sub2.keywords
            assert sub1.domain_tags == sub2.domain_tags
            assert sub1.mapped_templates == sub2.mapped_templates
            assert sub1.priority == sub2.priority
        
        # Property: Function-based queries return same results
        for function in ["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"]:
            func_subs1 = catalog1.get_by_function(function)
            func_subs2 = catalog2.get_by_function(function)
            
            ids1 = sorted([sub.subcategory_id for sub in func_subs1])
            ids2 = sorted([sub.subcategory_id for sub in func_subs2])
            assert ids1 == ids2, f"Function query mismatch for {function}"
        
        # Property: Domain-based queries return same results
        # Get all unique domains from catalog1
        all_domains = set()
        for sub in subs1:
            all_domains.update(sub.domain_tags)
        
        for domain in all_domains:
            domain_subs1 = catalog1.get_by_domain(domain)
            domain_subs2 = catalog2.get_by_domain(domain)
            
            ids1 = sorted([sub.subcategory_id for sub in domain_subs1])
            ids2 = sorted([sub.subcategory_id for sub in domain_subs2])
            assert ids1 == ids2, f"Domain query mismatch for {domain}"


# ============================================================================
# Additional Property Tests for Query Consistency
# ============================================================================


@settings(max_examples=20)
@given(
    function=st.sampled_from(["Govern", "Identify", "Protect", "Detect", "Respond", "Recover"])
)
def test_property_function_query_consistency(function):
    """
    Property: Function queries return consistent results.
    
    For any CSF function, querying the catalog multiple times shall return
    the same set of subcategories in a consistent order.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        guide_path = Path(tmpdir) / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Query multiple times
        result1 = catalog.get_by_function(function)
        result2 = catalog.get_by_function(function)
        
        # Property: Results are consistent
        ids1 = [sub.subcategory_id for sub in result1]
        ids2 = [sub.subcategory_id for sub in result2]
        assert ids1 == ids2, "Function query results must be consistent"


@settings(max_examples=20)
@given(
    subcategory_id=st.sampled_from([
        "GV.RM-01", "GV.OV-01", "ID.RA-01", "PR.AA-01",
        "PR.DS-01", "DE.CM-01", "RS.MA-01", "RC.RP-01"
    ])
)
def test_property_subcategory_retrieval_idempotent(subcategory_id):
    """
    Property: Subcategory retrieval is idempotent.
    
    For any subcategory ID, retrieving the subcategory multiple times shall
    return the same object with identical field values.
    """
    with tempfile.TemporaryDirectory() as tmpdir:
        guide_path = Path(tmpdir) / "cis_guide.pdf"
        guide_path.touch()
        
        catalog = ReferenceCatalog()
        catalog.build_from_cis_guide(str(guide_path))
        
        # Retrieve multiple times
        sub1 = catalog.get_subcategory(subcategory_id)
        sub2 = catalog.get_subcategory(subcategory_id)
        
        # Property: Results are identical
        if sub1 is not None and sub2 is not None:
            assert sub1.subcategory_id == sub2.subcategory_id
            assert sub1.function == sub2.function
            assert sub1.category == sub2.category
            assert sub1.description == sub2.description
            assert sub1.keywords == sub2.keywords
            assert sub1.domain_tags == sub2.domain_tags
            assert sub1.priority == sub2.priority
