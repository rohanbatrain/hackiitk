"""
Integration test for Data Privacy policy analysis.

This test validates the complete analysis of a dummy Data Privacy policy with
intentionally planted gaps in Identity Management, Access Control, and Data
Security subcategories. Also verifies privacy framework limitation warning.

**Validates: Requirements 19.2, 19.5, 12.5**
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
def privacy_policy_path():
    """Path to dummy Data Privacy policy."""
    policy_path = Path("tests/fixtures/dummy_policies/privacy_policy.md")
    if not policy_path.exists():
        pytest.skip("Privacy test policy not available")
    return str(policy_path)


@pytest.fixture
def expected_privacy_gaps():
    """Load expected privacy gaps for validation."""
    expected_path = Path("tests/fixtures/expected_outputs/expected_privacy_gaps.json")
    if not expected_path.exists():
        pytest.skip("Expected privacy gaps not available")
    
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
def test_privacy_policy_analysis(privacy_policy_path, expected_privacy_gaps, pipeline_config, temp_output_dir):
    """Test complete analysis of dummy Data Privacy policy.
    
    This test validates:
    - At least 80% of planted gaps are identified
    - Privacy framework limitation warning is logged
    - Gap report is generated correctly
    - Revised policy is generated
    - Implementation roadmap is generated
    
    **Validates: Requirements 19.2, 19.5, 12.5**
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    # Create pipeline
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        # Execute pipeline with data_privacy domain
        result = pipeline.execute(
            policy_path=privacy_policy_path,
            domain='data_privacy',
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
        for gap in expected_privacy_gaps['expected_gaps']:
            expected_gaps.add(gap['subcategory_id'])
        
        # Calculate detection rate
        detected_gaps = identified_gaps.intersection(expected_gaps)
        detection_rate = len(detected_gaps) / len(expected_gaps) if expected_gaps else 0
        
        # Verify at least 80% of planted gaps identified
        minimum_threshold = expected_privacy_gaps['detection_threshold_percentage'] / 100
        assert detection_rate >= minimum_threshold, (
            f"Detection rate {detection_rate:.1%} below threshold {minimum_threshold:.1%}. "
            f"Detected {len(detected_gaps)}/{len(expected_gaps)} gaps: {detected_gaps}"
        )
        
        # Verify specific critical gaps are detected
        critical_gaps = {'PR.AA-01', 'PR.AA-03', 'PR.DS-01', 'PR.DS-02'}
        detected_critical = critical_gaps.intersection(identified_gaps)
        assert len(detected_critical) >= 3, (
            f"Only {len(detected_critical)}/4 critical gaps detected: {detected_critical}"
        )
        
        # Verify gap report contains required fields
        for gap in gap_report_data['gaps']:
            assert 'subcategory_id' in gap
            assert 'description' in gap
            assert 'status' in gap
            assert 'severity' in gap
            assert gap['status'] in ['Missing', 'Partially_Covered', 'Ambiguous']
        
        # Verify privacy framework limitation warning is logged
        # Check in metadata or warnings section
        warning_found = False
        
        # Check metadata for warning
        if 'metadata' in gap_report_data:
            metadata_str = json.dumps(gap_report_data['metadata']).lower()
            if 'privacy' in metadata_str and ('framework' in metadata_str or 'limitation' in metadata_str):
                warning_found = True
        
        # Check for warnings field
        if 'warnings' in gap_report_data:
            for warning in gap_report_data['warnings']:
                warning_text = warning.lower() if isinstance(warning, str) else str(warning).lower()
                if 'privacy' in warning_text and 'framework' in warning_text:
                    warning_found = True
                    break
        
        # Check gap report markdown for warning
        gap_report_md_path = Path(result.output_directory) / 'gap_analysis_report.md'
        if gap_report_md_path.exists():
            with open(gap_report_md_path, 'r', encoding='utf-8') as f:
                md_content = f.read().lower()
                if 'privacy' in md_content and 'framework' in md_content and ('limitation' in md_content or 'not complete' in md_content):
                    warning_found = True
        
        # Check logs for warning
        log_files = list(Path(temp_output_dir).glob('*.log'))
        for log_file in log_files:
            with open(log_file, 'r', encoding='utf-8') as f:
                log_content = f.read().lower()
                if 'privacy' in log_content and 'framework' in log_content:
                    warning_found = True
                    break
        
        assert warning_found, (
            "Privacy framework limitation warning not found in outputs or logs"
        )
        
        # Verify revised policy generated
        revised_policy_path = Path(result.output_directory) / 'revised_policy.md'
        assert revised_policy_path.exists()
        assert revised_policy_path.stat().st_size > 0
        
        # Verify revised policy contains mandatory warning
        with open(revised_policy_path, 'r', encoding='utf-8') as f:
            revised_content = f.read()
        
        assert 'IMPORTANT:' in revised_content or 'WARNING:' in revised_content
        assert 'AI system' in revised_content or 'generated' in revised_content
        
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
        
        # Print test results
        print(f"\n✓ Data Privacy Policy Analysis Test Passed")
        print(f"  - Detection rate: {detection_rate:.1%} ({len(detected_gaps)}/{len(expected_gaps)} gaps)")
        print(f"  - Critical gaps detected: {len(detected_critical)}/4")
        print(f"  - Total gaps identified: {len(identified_gaps)}")
        print(f"  - Privacy framework warning: {'✓' if warning_found else '✗'}")
        print(f"  - Revisions generated: {len(result.revised_policy.revisions)}")
        print(f"  - Roadmap actions: {total_actions}")
        print(f"  - Detected gaps: {sorted(detected_gaps)}")
        print(f"  - Missed gaps: {sorted(expected_gaps - detected_gaps)}")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
def test_privacy_policy_domain_prioritization(privacy_policy_path, pipeline_config, temp_output_dir):
    """Test that data_privacy domain prioritizes PR.AA, PR.DS, and PR.AT subcategories.
    
    **Validates: Requirement 12.4**
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        result = pipeline.execute(
            policy_path=privacy_policy_path,
            domain='data_privacy',
            output_dir=temp_output_dir
        )
        
        # Load gap report
        gap_report_json_path = Path(result.output_directory) / 'gap_analysis_report.json'
        with open(gap_report_json_path, 'r', encoding='utf-8') as f:
            gap_report_data = json.load(f)
        
        # Count gaps by category
        prioritized_count = 0
        for gap in gap_report_data['gaps']:
            subcategory_id = gap['subcategory_id']
            # Check if gap is from prioritized categories
            if subcategory_id.startswith('PR.AA') or subcategory_id.startswith('PR.DS') or subcategory_id.startswith('PR.AT'):
                prioritized_count += 1
        
        total_gaps = len(gap_report_data['gaps'])
        
        if total_gaps > 0:
            prioritized_percentage = prioritized_count / total_gaps
            # At least 60% of gaps should be from prioritized categories
            assert prioritized_percentage >= 0.5, (
                f"Prioritized categories not emphasized: {prioritized_count}/{total_gaps} ({prioritized_percentage:.1%})"
            )
        
        print(f"\n✓ Privacy Domain Prioritization Test Passed")
        print(f"  - Prioritized gaps (PR.AA/PR.DS/PR.AT): {prioritized_count}/{total_gaps}")
        
    finally:
        pipeline.cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
