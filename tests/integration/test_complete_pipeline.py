"""
Integration test for complete analysis pipeline.

This test validates the end-to-end workflow from policy document input
through gap analysis, policy revision, roadmap generation, and output creation.

**Validates: All requirements**
"""

import pytest
import os
from pathlib import Path
import json
import tempfile
import shutil

from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig


@pytest.fixture
def temp_output_dir():
    """Create temporary output directory for tests."""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def sample_policy_path():
    """Path to sample policy for testing."""
    # Use a simple test policy
    test_policy_dir = Path("tests/fixtures/dummy_policies")
    
    # Check if test policies exist
    if not test_policy_dir.exists():
        pytest.skip("Test policy fixtures not available")
    
    # Look for any available test policy
    for policy_file in test_policy_dir.glob("*.pdf"):
        return str(policy_file)
    
    for policy_file in test_policy_dir.glob("*.txt"):
        return str(policy_file)
    
    pytest.skip("No test policy files found")


@pytest.fixture
def pipeline_config(temp_output_dir):
    """Create pipeline configuration for testing."""
    config_dict = {
        'chunk_size': 512,
        'overlap': 50,
        'top_k': 5,
        'temperature': 0.1,
        'max_tokens': 512,
        'model_name': 'qwen2.5-3b-instruct',
        'model_path': 'models/llm/qwen2.5-3b-instruct-q4_k_m.gguf',
        'embedding_model_path': 'models/embeddings/all-MiniLM-L6-v2',
        'reranker_model_path': 'models/reranker/cross-encoder-ms-marco-MiniLM-L-6-v2',
        'vector_store_path': os.path.join(temp_output_dir, 'vector_store'),
        'catalog_path': 'data/reference_catalog.json',
        'cis_guide_path': 'data/cis_guide.pdf',
        'output_dir': temp_output_dir,
        'audit_dir': os.path.join(temp_output_dir, 'audit_logs')
    }
    
    return PipelineConfig(config_dict)


@pytest.mark.integration
@pytest.mark.slow
def test_complete_pipeline_execution(sample_policy_path, pipeline_config, temp_output_dir):
    """Test end-to-end pipeline execution with sample policy.
    
    This test validates:
    - Pipeline initialization
    - Document parsing
    - Gap analysis execution
    - Policy revision generation
    - Roadmap generation
    - Output file creation
    - Audit log creation
    
    **Validates: All requirements**
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    # Create pipeline
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        # Execute pipeline
        result = pipeline.execute(
            policy_path=sample_policy_path,
            domain=None,  # Auto-detect
            output_dir=temp_output_dir
        )
        
        # Verify result structure
        assert result is not None
        assert result.gap_report is not None
        assert result.revised_policy is not None
        assert result.roadmap is not None
        assert result.output_directory is not None
        assert result.duration_seconds > 0
        
        # Verify gap report
        assert hasattr(result.gap_report, 'gaps')
        assert hasattr(result.gap_report, 'covered_subcategories')
        assert hasattr(result.gap_report, 'metadata')
        
        # Verify revised policy
        assert hasattr(result.revised_policy, 'original_text')
        assert hasattr(result.revised_policy, 'revised_text')
        assert hasattr(result.revised_policy, 'revisions')
        assert hasattr(result.revised_policy, 'warning')
        
        # Verify roadmap
        assert hasattr(result.roadmap, 'immediate_actions')
        assert hasattr(result.roadmap, 'near_term_actions')
        assert hasattr(result.roadmap, 'medium_term_actions')
        
        # Verify output directory exists
        output_dir = Path(result.output_directory)
        assert output_dir.exists()
        assert output_dir.is_dir()
        
        # Verify output files exist
        expected_files = [
            'gap_analysis_report.md',
            'gap_analysis_report.json',
            'revised_policy.md',
            'implementation_roadmap.md',
            'implementation_roadmap.json'
        ]
        
        for filename in expected_files:
            file_path = output_dir / filename
            assert file_path.exists(), f"Missing output file: {filename}"
            assert file_path.stat().st_size > 0, f"Empty output file: {filename}"
        
        # Verify gap report JSON structure
        gap_report_json_path = output_dir / 'gap_analysis_report.json'
        with open(gap_report_json_path, 'r', encoding='utf-8') as f:
            gap_report_data = json.load(f)
        
        assert 'analysis_date' in gap_report_data
        assert 'input_file' in gap_report_data
        assert 'model_name' in gap_report_data
        assert 'gaps' in gap_report_data
        assert isinstance(gap_report_data['gaps'], list)
        
        # Verify roadmap JSON structure
        roadmap_json_path = output_dir / 'implementation_roadmap.json'
        with open(roadmap_json_path, 'r', encoding='utf-8') as f:
            roadmap_data = json.load(f)
        
        assert 'roadmap_date' in roadmap_data
        assert 'immediate_actions' in roadmap_data
        assert 'near_term_actions' in roadmap_data
        assert 'medium_term_actions' in roadmap_data
        assert isinstance(roadmap_data['immediate_actions'], list)
        
        # Verify audit log created
        audit_dir = Path(pipeline_config.audit_dir)
        assert audit_dir.exists()
        
        audit_files = list(audit_dir.glob('audit_*.json'))
        assert len(audit_files) > 0, "No audit log files created"
        
        # Verify audit log content
        audit_file = audit_files[0]
        with open(audit_file, 'r', encoding='utf-8') as f:
            audit_data = json.load(f)
        
        assert 'timestamp' in audit_data
        assert 'input_file_path' in audit_data
        assert 'input_file_hash' in audit_data
        assert 'model_name' in audit_data
        assert 'output_directory' in audit_data
        assert 'analysis_duration_seconds' in audit_data
        
        print(f"\n✓ Pipeline execution successful")
        print(f"  - Gaps identified: {len(result.gap_report.gaps)}")
        print(f"  - Subcategories covered: {len(result.gap_report.covered_subcategories)}")
        print(f"  - Revisions generated: {len(result.revised_policy.revisions)}")
        print(f"  - Immediate actions: {len(result.roadmap.immediate_actions)}")
        print(f"  - Duration: {result.duration_seconds:.2f} seconds")
        print(f"  - Output directory: {result.output_directory}")
        
    finally:
        # Cleanup pipeline resources
        pipeline.cleanup()


@pytest.mark.integration
def test_pipeline_initialization(pipeline_config):
    """Test pipeline resource initialization.
    
    Validates that all components are properly initialized.
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        # Initialize resources
        pipeline.initialize_resources()
        
        # Verify components are initialized
        assert pipeline.document_parser is not None
        assert pipeline.text_chunker is not None
        assert pipeline.catalog is not None
        assert pipeline.embedding_engine is not None
        assert pipeline.vector_store is not None
        assert pipeline.hybrid_retriever is not None
        assert pipeline.llm_runtime is not None
        assert pipeline.gap_analysis_engine is not None
        assert pipeline.policy_revision_engine is not None
        assert pipeline.roadmap_generator is not None
        assert pipeline.gap_report_generator is not None
        assert pipeline.audit_logger is not None
        
        # Verify catalog has subcategories
        assert len(pipeline.catalog.get_all_subcategories()) > 0
        
        print(f"\n✓ Pipeline initialization successful")
        print(f"  - Reference catalog: {len(pipeline.catalog.get_all_subcategories())} subcategories")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
def test_pipeline_error_handling(pipeline_config):
    """Test pipeline error handling for invalid inputs."""
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    # Test with non-existent file
    with pytest.raises(Exception):
        pipeline.execute(
            policy_path="nonexistent_file.pdf",
            domain=None
        )


@pytest.mark.integration
def test_pipeline_with_domain_prioritization(sample_policy_path, pipeline_config, temp_output_dir):
    """Test pipeline with domain-specific prioritization."""
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        # Execute with ISMS domain
        result = pipeline.execute(
            policy_path=sample_policy_path,
            domain='isms',
            output_dir=temp_output_dir
        )
        
        # Verify result
        assert result is not None
        assert result.gap_report is not None
        
        # Verify domain metadata
        assert 'domain' in result.gap_report.metadata
        assert result.gap_report.metadata['domain'] == 'isms'
        
        print(f"\n✓ Domain prioritization successful")
        print(f"  - Domain: isms")
        print(f"  - Gaps identified: {len(result.gap_report.gaps)}")
        
    finally:
        pipeline.cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
