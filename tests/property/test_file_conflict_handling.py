"""
Property-based tests for file conflict handling.

**Property 41: File Conflict Handling**
**Validates: Requirements 14.8**

Tests that existing files trigger overwrite confirmation or unique filename generation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings
from unittest.mock import patch

from reporting.output_manager import OutputManager
from models.domain import (
    GapAnalysisReport,
    GapDetail,
    RevisedPolicy,
    Revision,
    ImplementationRoadmap,
    ActionItem
)


# Reuse generators
@st.composite
def gap_details(draw):
    """Generate random gap details."""
    subcategory_id = draw(st.sampled_from([
        "GV.RM-01", "GV.SC-02", "ID.AM-01", "PR.AA-01", "DE.CM-01"
    ]))
    status = draw(st.sampled_from(["missing", "partially_covered"]))
    severity = draw(st.sampled_from(["critical", "high", "medium", "low"]))
    
    return GapDetail(
        subcategory_id=subcategory_id,
        subcategory_description=f"Description for {subcategory_id}",
        status=status,
        evidence_quote=draw(st.text(min_size=0, max_size=200)),
        gap_explanation=draw(st.text(min_size=10, max_size=200)),
        severity=severity,
        suggested_fix=draw(st.text(min_size=10, max_size=200))
    )


@st.composite
def gap_analysis_reports(draw):
    """Generate random gap analysis reports."""
    gaps = draw(st.lists(gap_details(), min_size=0, max_size=5))
    covered = draw(st.lists(
        st.sampled_from(["GV.OC-01", "GV.RM-02", "ID.AM-02"]),
        min_size=0,
        max_size=3
    ))
    
    return GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file=draw(st.text(min_size=5, max_size=50)),
        input_file_hash=draw(st.text(min_size=64, max_size=64)),
        model_name=draw(st.sampled_from(["qwen2.5-3b", "phi-3.5-mini"])),
        model_version=draw(st.sampled_from(["q4_k_m", "q8_0"])),
        embedding_model="all-MiniLM-L6-v2",
        gaps=gaps,
        covered_subcategories=covered,
        metadata={
            "prompt_version": "1.0.0",
            "config_hash": "abc123",
            "retrieval_params": {"top_k": 5}
        }
    )


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


@pytest.fixture
def output_manager(temp_output_dir):
    """Create output manager with temporary directory."""
    manager = OutputManager(base_output_dir=temp_output_dir, prompt_for_overwrite=False)
    manager.set_roadmap_catalog(None)
    return manager


@given(report=gap_analysis_reports())
@settings(max_examples=50, deadline=None)
def test_property_41_file_conflict_unique_filename(report):
    """
    Property 41: File Conflict Handling
    
    For any analysis run where output files already exist at the target location,
    the Policy_Analyzer shall either prompt for overwrite confirmation or generate
    unique filenames to avoid data loss.
    
    This test verifies unique filename generation (no prompt).
    
    **Validates: Requirements 14.8**
    """
    # Create temporary output directory and manager for this test
    temp_dir = tempfile.mkdtemp()
    try:
        output_manager = OutputManager(base_output_dir=temp_dir, prompt_for_overwrite=False)
        output_manager.set_roadmap_catalog(None)
        
        output_dir = output_manager.create_output_directory()
        
        # Write gap analysis report first time
        result1 = output_manager.write_gap_analysis_report(report, output_dir)
        
        # Verify files exist
        assert result1['markdown'].exists()
        assert result1['json'].exists()
        
        # Write gap analysis report second time (should generate unique filenames)
        result2 = output_manager.write_gap_analysis_report(report, output_dir)
        
        # Verify new files were created with unique names
        assert result2['markdown'].exists()
        assert result2['json'].exists()
        
        # Verify filenames are different
        assert result1['markdown'] != result2['markdown']
        assert result1['json'] != result2['json']
        
        # Verify both sets of files exist (no overwrite)
        assert result1['markdown'].exists()
        assert result1['json'].exists()
        assert result2['markdown'].exists()
        assert result2['json'].exists()
        
        # Verify unique filename format (should have _1, _2, etc.)
        assert '_1' in result2['markdown'].name or result2['markdown'].name != result1['markdown'].name
        assert '_1' in result2['json'].name or result2['json'].name != result1['json'].name
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir)


def test_property_41_unique_filename_generation(output_manager):
    """Test that unique filenames are generated with incrementing counters."""
    output_dir = output_manager.create_output_directory()
    
    # Create initial file
    test_file = output_dir / "test_file.txt"
    test_file.write_text("original")
    
    # Generate unique filename
    unique_file = output_manager._generate_unique_filename(test_file)
    
    # Verify unique filename has counter
    assert unique_file.name == "test_file_1.txt"
    assert not unique_file.exists()
    
    # Create the unique file
    unique_file.write_text("first unique")
    
    # Generate another unique filename
    unique_file2 = output_manager._generate_unique_filename(test_file)
    
    # Verify counter incremented
    assert unique_file2.name == "test_file_2.txt"
    assert not unique_file2.exists()


def test_property_41_handle_file_conflict_no_conflict(output_manager):
    """Test that handle_file_conflict returns original path when no conflict."""
    output_dir = output_manager.create_output_directory()
    test_file = output_dir / "nonexistent.txt"
    
    result = output_manager.handle_file_conflict(test_file, prompt_user=False)
    
    # Should return original path since file doesn't exist
    assert result == test_file


def test_property_41_handle_file_conflict_with_conflict(output_manager):
    """Test that handle_file_conflict generates unique name when conflict exists."""
    output_dir = output_manager.create_output_directory()
    test_file = output_dir / "existing.txt"
    test_file.write_text("original content")
    
    result = output_manager.handle_file_conflict(test_file, prompt_user=False)
    
    # Should return unique path since file exists
    assert result != test_file
    assert result.name == "existing_1.txt"
    assert not result.exists()  # Unique file not created yet


@patch('builtins.input', return_value='y')
def test_property_41_handle_file_conflict_user_confirms_overwrite(mock_input, output_manager):
    """Test that user can confirm overwrite when prompted."""
    # Create manager with prompting enabled
    manager = OutputManager(
        base_output_dir=output_manager.base_output_dir,
        prompt_for_overwrite=True
    )
    
    output_dir = manager.create_output_directory()
    test_file = output_dir / "existing.txt"
    test_file.write_text("original content")
    
    result = manager.handle_file_conflict(test_file, prompt_user=True)
    
    # Should return original path since user confirmed overwrite
    assert result == test_file
    mock_input.assert_called_once()


@patch('builtins.input', return_value='n')
def test_property_41_handle_file_conflict_user_declines_overwrite(mock_input, output_manager):
    """Test that unique filename is generated when user declines overwrite."""
    # Create manager with prompting enabled
    manager = OutputManager(
        base_output_dir=output_manager.base_output_dir,
        prompt_for_overwrite=True
    )
    
    output_dir = manager.create_output_directory()
    test_file = output_dir / "existing.txt"
    test_file.write_text("original content")
    
    result = manager.handle_file_conflict(test_file, prompt_user=True)
    
    # Should return unique path since user declined overwrite
    assert result != test_file
    assert result.name == "existing_1.txt"
    mock_input.assert_called_once()


def test_property_41_multiple_conflicts_increment_counter(output_manager):
    """Test that multiple conflicts increment counter correctly."""
    output_dir = output_manager.create_output_directory()
    
    # Create original and first unique file
    test_file = output_dir / "test.txt"
    test_file.write_text("original")
    
    unique1 = output_dir / "test_1.txt"
    unique1.write_text("first")
    
    unique2 = output_dir / "test_2.txt"
    unique2.write_text("second")
    
    # Generate next unique filename
    result = output_manager._generate_unique_filename(test_file)
    
    # Should skip to _3 since _1 and _2 exist
    assert result.name == "test_3.txt"
    assert not result.exists()


def test_property_41_preserves_file_extension(output_manager):
    """Test that unique filename generation preserves file extension."""
    output_dir = output_manager.create_output_directory()
    
    # Test various extensions
    for ext in ['.txt', '.md', '.json', '.pdf']:
        test_file = output_dir / f"test{ext}"
        test_file.write_text("content")
        
        unique = output_manager._generate_unique_filename(test_file)
        
        assert unique.suffix == ext
        assert unique.stem == "test_1"


def test_property_41_all_outputs_handle_conflicts(output_manager):
    """Test that all output methods handle file conflicts."""
    output_dir = output_manager.create_output_directory()
    
    # Create minimal test data
    report = GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file="test.pdf",
        input_file_hash="abc123",
        model_name="qwen2.5-3b",
        model_version="q4_k_m",
        embedding_model="all-MiniLM-L6-v2",
        gaps=[],
        covered_subcategories=[],
        metadata={}
    )
    
    policy = RevisedPolicy(
        original_text="original",
        revised_text="revised",
        revisions=[],
        warning="warning",
        metadata={}
    )
    
    roadmap = ImplementationRoadmap(
        immediate_actions=[],
        near_term_actions=[],
        medium_term_actions=[],
        metadata={}
    )
    
    # Write outputs first time
    result1 = output_manager.write_all_outputs(
        gap_report=report,
        revised_policy=policy,
        roadmap=roadmap,
        input_file_name="test.pdf",
        output_dir=output_dir
    )
    
    # Write outputs second time (should generate unique filenames)
    result2 = output_manager.write_all_outputs(
        gap_report=report,
        revised_policy=policy,
        roadmap=roadmap,
        input_file_name="test.pdf",
        output_dir=output_dir
    )
    
    # Verify all files from both runs exist
    assert result1['gap_report']['markdown'].exists()
    assert result1['gap_report']['json'].exists()
    assert result1['revised_policy'].exists()
    assert result1['roadmap']['markdown'].exists()
    assert result1['roadmap']['json'].exists()
    
    assert result2['gap_report']['markdown'].exists()
    assert result2['gap_report']['json'].exists()
    assert result2['revised_policy'].exists()
    assert result2['roadmap']['markdown'].exists()
    assert result2['roadmap']['json'].exists()
    
    # Verify filenames are different
    assert result1['gap_report']['markdown'] != result2['gap_report']['markdown']
    assert result1['gap_report']['json'] != result2['gap_report']['json']
    assert result1['revised_policy'] != result2['revised_policy']
    assert result1['roadmap']['markdown'] != result2['roadmap']['markdown']
    assert result1['roadmap']['json'] != result2['roadmap']['json']

