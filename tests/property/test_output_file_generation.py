"""
Property-based tests for output file generation.

**Property 39: Output File Generation**
**Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6**

Tests that all required output files are generated in timestamped directory.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st, settings

from reporting.output_manager import OutputManager
from models.domain import (
    GapAnalysisReport,
    GapDetail,
    RevisedPolicy,
    Revision,
    ImplementationRoadmap,
    ActionItem
)
from reference_builder.reference_catalog import ReferenceCatalog


# Test data generators
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
    gaps = draw(st.lists(gap_details(), min_size=0, max_size=10))
    covered = draw(st.lists(
        st.sampled_from(["GV.OC-01", "GV.RM-02", "ID.AM-02"]),
        min_size=0,
        max_size=5
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


@st.composite
def revisions(draw):
    """Generate random revisions."""
    return Revision(
        section=draw(st.text(min_size=5, max_size=50)),
        gap_addressed=draw(st.sampled_from(["GV.RM-01", "PR.AA-01"])),
        original_clause=draw(st.text(min_size=0, max_size=200)),
        revised_clause=draw(st.text(min_size=10, max_size=200)),
        revision_type=draw(st.sampled_from(["injection", "strengthening"]))
    )


@st.composite
def revised_policies(draw):
    """Generate random revised policies."""
    revision_list = draw(st.lists(revisions(), min_size=0, max_size=10))
    
    return RevisedPolicy(
        original_text=draw(st.text(min_size=50, max_size=500)),
        revised_text=draw(st.text(min_size=50, max_size=500)),
        revisions=revision_list,
        warning="IMPORTANT: This is AI-generated and requires review.",
        metadata={"revision_count": len(revision_list)}
    )


@st.composite
def action_items(draw):
    """Generate random action items."""
    timeframe = draw(st.sampled_from(["immediate", "near_term", "medium_term"]))
    severity = draw(st.sampled_from(["critical", "high", "medium", "low"]))
    
    return ActionItem(
        action_id=f"ACT-{draw(st.integers(min_value=1, max_value=999))}",
        timeframe=timeframe,
        severity=severity,
        effort=draw(st.sampled_from(["low", "medium", "high"])),
        csf_subcategory=draw(st.sampled_from(["GV.RM-01", "PR.AA-01"])),
        policy_section=draw(st.text(min_size=5, max_size=50)),
        description=draw(st.text(min_size=10, max_size=200)),
        technical_steps=draw(st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=5)),
        administrative_steps=draw(st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=5)),
        physical_steps=draw(st.lists(st.text(min_size=10, max_size=100), min_size=0, max_size=5))
    )


@st.composite
def implementation_roadmaps(draw):
    """Generate random implementation roadmaps."""
    immediate = draw(st.lists(action_items(), min_size=0, max_size=5))
    near_term = draw(st.lists(action_items(), min_size=0, max_size=5))
    medium_term = draw(st.lists(action_items(), min_size=0, max_size=5))
    
    return ImplementationRoadmap(
        immediate_actions=immediate,
        near_term_actions=near_term,
        medium_term_actions=medium_term,
        metadata={
            "generation_date": datetime.now().isoformat(),
            "total_actions": len(immediate) + len(near_term) + len(medium_term)
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
    # Set a mock catalog (not needed for file generation tests)
    manager.set_roadmap_catalog(None)
    return manager


@given(
    report=gap_analysis_reports(),
    policy=revised_policies(),
    roadmap=implementation_roadmaps()
)
@settings(max_examples=100, deadline=None)
def test_property_39_output_file_generation(report, policy, roadmap):
    """
    Property 39: Output File Generation
    
    For any completed analysis, the Policy_Analyzer shall generate all required
    output files: gap_analysis_report.md, gap_analysis_report.json,
    revised_policy.md, implementation_roadmap.md, and implementation_roadmap.json
    in a timestamped output directory.
    
    **Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6**
    """
    # Create temporary output directory and manager for this test
    temp_dir = tempfile.mkdtemp()
    try:
        output_manager = OutputManager(base_output_dir=temp_dir, prompt_for_overwrite=False)
        output_manager.set_roadmap_catalog(None)
        
        # Create timestamped output directory
        output_dir = output_manager.create_output_directory()
        
        # Verify directory was created with timestamp format
        assert output_dir.exists()
        assert output_dir.is_dir()
        assert output_dir.name.startswith("analysis_")
        
        # Write all outputs
        input_file_name = "test_policy.pdf"
        metadata = {
            "model_name": report.model_name,
            "model_version": report.model_version,
            "prompt_template_version": "1.0.0",
            "configuration_hash": "test_hash"
        }
        
        result = output_manager.write_all_outputs(
            gap_report=report,
            revised_policy=policy,
            roadmap=roadmap,
            input_file_name=input_file_name,
            metadata=metadata,
            output_dir=output_dir
        )
        
        # Verify all required files exist
        assert (output_dir / "gap_analysis_report.md").exists()
        assert (output_dir / "gap_analysis_report.json").exists()
        assert (output_dir / "revised_policy.md").exists()
        assert (output_dir / "implementation_roadmap.md").exists()
        assert (output_dir / "implementation_roadmap.json").exists()
        
        # Verify result structure
        assert 'output_dir' in result
        assert 'gap_report' in result
        assert 'revised_policy' in result
        assert 'roadmap' in result
        
        # Verify gap report paths
        assert 'markdown' in result['gap_report']
        assert 'json' in result['gap_report']
        assert result['gap_report']['markdown'].exists()
        assert result['gap_report']['json'].exists()
        
        # Verify roadmap paths
        assert 'markdown' in result['roadmap']
        assert 'json' in result['roadmap']
        assert result['roadmap']['markdown'].exists()
        assert result['roadmap']['json'].exists()
        
        # Verify revised policy path
        assert result['revised_policy'].exists()
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir)


def test_property_39_timestamped_directory_format(output_manager):
    """Test that output directory has correct timestamp format."""
    timestamp = datetime(2024, 1, 15, 10, 30, 45)
    output_dir = output_manager.create_output_directory(timestamp)
    
    # Verify format: analysis_YYYYMMDD_HHMMSS
    assert output_dir.name == "analysis_20240115_103045"
    assert output_dir.exists()


def test_property_39_multiple_analyses_separate_directories(output_manager):
    """Test that multiple analyses create separate directories."""
    dir1 = output_manager.create_output_directory(datetime(2024, 1, 15, 10, 0, 0))
    dir2 = output_manager.create_output_directory(datetime(2024, 1, 15, 11, 0, 0))
    
    assert dir1 != dir2
    assert dir1.exists()
    assert dir2.exists()

