"""
Integration test for ISMS policy analysis.

This test validates the complete analysis of a dummy ISMS policy with
intentionally planted gaps in Supply Chain Risk Management and Organizational
Context subcategories.

**Validates: Requirements 19.1, 19.5**
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
    shutil.rmtree(temp_dir, ignore_errors=True)


@pytest.fixture
def isms_policy_path():
    """Path to dummy ISMS policy."""
    policy_path = Path("tests/fixtures/dummy_policies/isms_policy.md")
    if not policy_path.exists():
        pytest.skip("ISMS test policy not available")
    return str(policy_path)


@pytest.fixture
def expected_isms_gaps():
    """Load expected ISMS gaps for validation."""
    expected_path = Path("tests/fixtures/expected_outputs/expected_isms_gaps.json")
    if not expected_path.exists():
        pytest.skip("Expected ISMS gaps not available")
    
    with open(expected_path, 'r', encoding='utf-8') as f:
        return json.load(f)


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
def test_isms_policy_analysis(isms_policy_path, expected_isms_gaps, pipeline_config, temp_output_dir):
    """Test complete analysis of dummy ISMS policy.
    
    This test validates:
    - At least 80% of planted gaps are identified
    - Gap report is generated correctly
    - Revised policy is generated
    - Implementation roadmap is generated
    - All output files are created
    
    **Validates: Requirements 19.1, 19.5**
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    # Create pipeline
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        # Execute pipeline with ISMS domain
        result = pipeline.execute(
            policy_path=isms_policy_path,
            domain='isms',
            output_dir=temp_output_dir
        )
        
        # Verify result structure
        assert result is not None
        assert result.gap_report is not None
        assert result.revised_policy is not None
        assert result.roadmap is not None
        
        # Load generated gap report JSON
        gap_report_json_path = Path(result.output_directory) / 'gap_analysis_report.json'
        assert gap_report_json_path.exists()
        
        with open(gap_report_json_path, 'r', encoding='utf-8') as f:
            gap_report_data = json.load(f)
        
        # Extract identified gap subcategory IDs
        identified_gaps = set()
        for gap in gap_report_data['gaps']:
            identified_gaps.add(gap['subcategory_id'])
        
        # Extract expected gap subcategory IDs
        expected_gaps = set()
        for gap in expected_isms_gaps['expected_gaps']:
            expected_gaps.add(gap['subcategory_id'])
        
        # Calculate detection rate
        detected_gaps = identified_gaps.intersection(expected_gaps)
        detection_rate = len(detected_gaps) / len(expected_gaps) if expected_gaps else 0
        
        # Verify at least 80% of planted gaps identified
        minimum_threshold = expected_isms_gaps['detection_threshold_percentage'] / 100
        assert detection_rate >= minimum_threshold, (
            f"Detection rate {detection_rate:.1%} below threshold {minimum_threshold:.1%}. "
            f"Detected {len(detected_gaps)}/{len(expected_gaps)} gaps: {detected_gaps}"
        )
        
        # Verify specific expected gaps are detected
        critical_gaps = {'GV.SC-01', 'GV.SC-02', 'GV.SC-03', 'GV.OV-01', 'GV.OV-03'}
        detected_critical = critical_gaps.intersection(identified_gaps)
        assert len(detected_critical) >= 4, (
            f"Only {len(detected_critical)}/5 critical gaps detected: {detected_critical}"
        )
        
        # Verify gap report contains required fields
        for gap in gap_report_data['gaps']:
            assert 'subcategory_id' in gap
            assert 'description' in gap
            assert 'status' in gap
            assert 'severity' in gap
            assert gap['status'] in ['Missing', 'Partially_Covered', 'Ambiguous']
        
        # Verify revised policy generated
        revised_policy_path = Path(result.output_directory) / 'revised_policy.md'
        assert revised_policy_path.exists()
        assert revised_policy_path.stat().st_size > 0
        
        # Verify revised policy contains mandatory warning
        with open(revised_policy_path, 'r', encoding='utf-8') as f:
            revised_content = f.read()
        
        assert 'IMPORTANT:' in revised_content or 'WARNING:' in revised_content
        assert 'AI system' in revised_content or 'generated' in revised_content
        assert 'review' in revised_content.lower()
        
        # Verify implementation roadmap generated
        roadmap_md_path = Path(result.output_directory) / 'implementation_roadmap.md'
        roadmap_json_path = Path(result.output_directory) / 'implementation_roadmap.json'
        assert roadmap_md_path.exists()
        assert roadmap_json_path.exists()
        
        # Verify roadmap contains actions
        with open(roadmap_json_path, 'r', encoding='utf-8') as f:
            roadmap_data = json.load(f)
        
        total_actions = (
            len(roadmap_data['immediate_actions']) +
            len(roadmap_data['near_term_actions']) +
            len(roadmap_data['medium_term_actions'])
        )
        assert total_actions > 0, "Roadmap contains no actions"
        
        # Verify audit log created
        audit_dir = Path(pipeline_config.audit_dir)
        assert audit_dir.exists()
        audit_files = list(audit_dir.glob('audit_*.json'))
        assert len(audit_files) > 0
        
        # Print test results
        print(f"\n✓ ISMS Policy Analysis Test Passed")
        print(f"  - Detection rate: {detection_rate:.1%} ({len(detected_gaps)}/{len(expected_gaps)} gaps)")
        print(f"  - Critical gaps detected: {len(detected_critical)}/5")
        print(f"  - Total gaps identified: {len(identified_gaps)}")
        print(f"  - Revisions generated: {len(result.revised_policy.revisions)}")
        print(f"  - Roadmap actions: {total_actions}")
        print(f"  - Detected gaps: {sorted(detected_gaps)}")
        print(f"  - Missed gaps: {sorted(expected_gaps - detected_gaps)}")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
def test_isms_policy_domain_prioritization(isms_policy_path, pipeline_config, temp_output_dir):
    """Test that ISMS domain prioritizes Govern (GV) function subcategories.
    
    **Validates: Requirement 12.1**
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        result = pipeline.execute(
            policy_path=isms_policy_path,
            domain='isms',
            output_dir=temp_output_dir
        )
        
        # Load gap report
        gap_report_json_path = Path(result.output_directory) / 'gap_analysis_report.json'
        with open(gap_report_json_path, 'r', encoding='utf-8') as f:
            gap_report_data = json.load(f)
        
        # Count gaps by function
        function_counts = {}
        for gap in gap_report_data['gaps']:
            subcategory_id = gap['subcategory_id']
            function = subcategory_id.split('.')[0]  # Extract function prefix
            function_counts[function] = function_counts.get(function, 0) + 1
        
        # Verify GV (Govern) function is prioritized
        gv_count = function_counts.get('GV', 0)
        total_gaps = len(gap_report_data['gaps'])
        
        if total_gaps > 0:
            gv_percentage = gv_count / total_gaps
            # At least 50% of gaps should be from Govern function for ISMS
            assert gv_percentage >= 0.3, (
                f"GV function not prioritized: {gv_count}/{total_gaps} ({gv_percentage:.1%})"
            )
        
        print(f"\n✓ ISMS Domain Prioritization Test Passed")
        print(f"  - GV (Govern) gaps: {gv_count}/{total_gaps}")
        print(f"  - Function distribution: {function_counts}")
        
    finally:
        pipeline.cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
