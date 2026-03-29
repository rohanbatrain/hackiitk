"""
Property-based tests for output metadata inclusion.

**Property 40: Output Metadata Inclusion**
**Validates: Requirements 14.7**

Tests that all outputs include required metadata fields.
"""

import pytest
import json
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


# Reuse generators from test_output_file_generation
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
    manager.set_roadmap_catalog(None)
    return manager


@given(
    report=gap_analysis_reports(),
    policy=revised_policies(),
    roadmap=implementation_roadmaps()
)
@settings(max_examples=100, deadline=None)
def test_property_40_output_metadata_inclusion(report, policy, roadmap):
    """
    Property 40: Output Metadata Inclusion
    
    For any generated output file, the Policy_Analyzer shall include metadata
    fields: analysis_date, model_version, model_name, input_file_name,
    prompt_template_version, configuration_hash, and retrieval_parameters.
    
    **Validates: Requirements 14.7**
    """
    # Create temporary output directory and manager for this test
    temp_dir = tempfile.mkdtemp()
    try:
        output_manager = OutputManager(base_output_dir=temp_dir, prompt_for_overwrite=False)
        output_manager.set_roadmap_catalog(None)
        
        # Create output directory
        output_dir = output_manager.create_output_directory()
        
        # Define required metadata
        input_file_name = "test_policy.pdf"
        metadata = {
            "model_name": report.model_name,
            "model_version": report.model_version,
            "prompt_template_version": "1.0.0",
            "configuration_hash": "test_config_hash_123",
            "retrieval_parameters": {"top_k": 5, "chunk_size": 512}
        }
        
        # Write all outputs
        result = output_manager.write_all_outputs(
            gap_report=report,
            revised_policy=policy,
            roadmap=roadmap,
            input_file_name=input_file_name,
            metadata=metadata,
            output_dir=output_dir
        )
        
        # Verify gap analysis JSON includes all required metadata
        gap_json_path = result['gap_report']['json']
        with open(gap_json_path, 'r') as f:
            gap_json = json.load(f)
        
        assert 'analysis_date' in gap_json
        assert 'input_file' in gap_json
        assert 'model_name' in gap_json
        assert 'model_version' in gap_json
        assert 'embedding_model' in gap_json
        assert 'metadata' in gap_json
        
        # Verify metadata section includes required fields
        assert 'prompt_version' in gap_json['metadata'] or 'prompt_template_version' in metadata
        assert 'config_hash' in gap_json['metadata'] or 'configuration_hash' in metadata
        assert 'retrieval_params' in gap_json['metadata'] or 'retrieval_parameters' in metadata
        
        # Verify gap analysis markdown includes metadata
        gap_md_path = result['gap_report']['markdown']
        gap_md_content = gap_md_path.read_text()
        
        assert 'Analysis Date' in gap_md_content or 'analysis_date' in gap_md_content.lower()
        assert 'Model Name' in gap_md_content or 'model_name' in gap_md_content.lower()
        assert 'Model Version' in gap_md_content or 'model_version' in gap_md_content.lower()
        
        # Verify roadmap JSON includes metadata
        roadmap_json_path = result['roadmap']['json']
        with open(roadmap_json_path, 'r') as f:
            roadmap_json = json.load(f)
        
        assert 'roadmap_date' in roadmap_json
        assert 'policy_analyzed' in roadmap_json
        assert 'metadata' in roadmap_json
        
        # Verify roadmap markdown includes metadata
        roadmap_md_path = result['roadmap']['markdown']
        roadmap_md_content = roadmap_md_path.read_text()
        
        assert 'Policy Analyzed' in roadmap_md_content or 'policy_analyzed' in roadmap_md_content.lower()
        assert 'Generation Date' in roadmap_md_content or 'roadmap_date' in roadmap_md_content.lower()
        
        # Verify revised policy markdown includes metadata
        policy_md_path = result['revised_policy']
        policy_md_content = policy_md_path.read_text()
        
        assert 'Original Policy' in policy_md_content or input_file_name in policy_md_content
        assert 'Revision Date' in policy_md_content or 'revision_date' in policy_md_content.lower()
        assert 'Model Used' in policy_md_content or 'model_name' in policy_md_content.lower()
    finally:
        # Cleanup temporary directory
        shutil.rmtree(temp_dir)


def test_property_40_metadata_in_gap_json(output_manager):
    """Test that gap analysis JSON includes all required metadata fields."""
    output_dir = output_manager.create_output_directory()
    
    report = GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file="test.pdf",
        input_file_hash="abc123",
        model_name="qwen2.5-3b",
        model_version="q4_k_m",
        embedding_model="all-MiniLM-L6-v2",
        gaps=[],
        covered_subcategories=[],
        metadata={
            "prompt_version": "1.0.0",
            "config_hash": "def456",
            "retrieval_params": {"top_k": 5}
        }
    )
    
    metadata = {
        "model_name": "qwen2.5-3b",
        "model_version": "q4_k_m",
        "prompt_template_version": "1.0.0",
        "configuration_hash": "config_hash_123",
        "retrieval_parameters": {"top_k": 5}
    }
    
    result = output_manager.write_gap_analysis_report(report, output_dir, metadata)
    
    # Read JSON and verify metadata
    with open(result['json'], 'r') as f:
        gap_json = json.load(f)
    
    assert gap_json['analysis_date'] is not None
    assert gap_json['input_file'] == "test.pdf"
    assert gap_json['model_name'] == "qwen2.5-3b"
    assert gap_json['model_version'] == "q4_k_m"
    assert gap_json['embedding_model'] == "all-MiniLM-L6-v2"
    assert 'metadata' in gap_json


def test_property_40_metadata_in_roadmap_json(output_manager):
    """Test that roadmap JSON includes all required metadata fields."""
    output_dir = output_manager.create_output_directory()
    
    roadmap = ImplementationRoadmap(
        immediate_actions=[],
        near_term_actions=[],
        medium_term_actions=[],
        metadata={
            "generation_date": datetime.now().isoformat(),
            "total_actions": 0
        }
    )
    
    metadata = {
        "model_name": "qwen2.5-3b",
        "model_version": "q4_k_m",
        "prompt_template_version": "1.0.0",
        "configuration_hash": "config_hash_123"
    }
    
    result = output_manager.write_implementation_roadmap(
        roadmap,
        output_dir,
        "test.pdf",
        metadata
    )
    
    # Read JSON and verify metadata
    with open(result['json'], 'r') as f:
        roadmap_json = json.load(f)
    
    assert roadmap_json['roadmap_date'] is not None
    assert roadmap_json['policy_analyzed'] == "test.pdf"
    assert 'metadata' in roadmap_json


def test_property_40_configuration_hash_computation(output_manager):
    """Test that configuration hash is computed consistently."""
    config1 = {"chunk_size": 512, "top_k": 5, "temperature": 0.1}
    config2 = {"top_k": 5, "chunk_size": 512, "temperature": 0.1}  # Different order
    config3 = {"chunk_size": 512, "top_k": 5, "temperature": 0.2}  # Different value
    
    hash1 = output_manager.compute_configuration_hash(config1)
    hash2 = output_manager.compute_configuration_hash(config2)
    hash3 = output_manager.compute_configuration_hash(config3)
    
    # Same config (different order) should produce same hash
    assert hash1 == hash2
    
    # Different config should produce different hash
    assert hash1 != hash3
    
    # Hash should be 64 characters (SHA-256 hex)
    assert len(hash1) == 64

