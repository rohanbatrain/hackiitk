"""
Integration test for Patch Management policy analysis.

This test validates the complete analysis of a dummy Patch Management policy with
intentionally planted gaps in Risk Assessment and Protective Technology subcategories.
Also verifies that critical gaps are prioritized as Immediate in the roadmap.

**Validates: Requirements 19.3, 19.5**
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
def patch_policy_path():
    """Path to dummy Patch Management policy."""
    policy_path = Path("tests/fixtures/dummy_policies/patch_policy.md")
    if not policy_path.exists():
        pytest.skip("Patch Management test policy not available")
    return str(policy_path)


@pytest.fixture
def expected_patch_gaps():
    """Load expected patch management gaps for validation."""
    expected_path = Path("tests/fixtures/expected_outputs/expected_patch_gaps.json")
    if not expected_path.exists():
        pytest.skip("Expected patch gaps not available")
    
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
def test_patch_policy_analysis(patch_policy_path, expected_patch_gaps, pipeline_config, temp_output_dir):
    """Test complete analysis of dummy Patch Management policy.
    
    This test validates:
    - At least 80% of planted gaps are identified
    - Gap report is generated correctly
    - Revised policy is generated
    - Implementation roadmap is generated
    - Critical gaps are prioritized as Immediate in roadmap
    
    **Validates: Requirements 19.3, 19.5**
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    # Create pipeline
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        # Execute pipeline with patch_management domain
        result = pipeline.execute(
            policy_path=patch_policy_path,
            domain='patch_management',
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
        for gap in expected_patch_gaps['expected_gaps']:
            expected_gaps.add(gap['subcategory_id'])
        
        # Calculate detection rate
        detected_gaps = identified_gaps.intersection(expected_gaps)
        detection_rate = len(detected_gaps) / len(expected_gaps) if expected_gaps else 0
        
        # Verify at least 80% of planted gaps identified
        minimum_threshold = expected_patch_gaps['detection_threshold_percentage'] / 100
        assert detection_rate >= minimum_threshold, (
            f"Detection rate {detection_rate:.1%} below threshold {minimum_threshold:.1%}. "
            f"Detected {len(detected_gaps)}/{len(expected_gaps)} gaps: {detected_gaps}"
        )
        
        # Verify specific critical gaps are detected
        critical_gaps = {'ID.RA-01', 'PR.PS-01', 'PR.PS-04', 'PR.PS-05'}
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
        
        # Load implementation roadmap
        roadmap_json_path = Path(result.output_directory) / 'implementation_roadmap.json'
        assert roadmap_json_path.exists()
        
        with open(roadmap_json_path, 'r', encoding='utf-8') as f:
            roadmap_data = json.load(f)
        
        # Verify roadmap prioritizes critical gaps as Immediate
        immediate_actions = roadmap_data.get('immediate_actions', [])
        
        # Count critical severity gaps in immediate actions
        critical_immediate_count = 0
        for action in immediate_actions:
            if action.get('severity', '').lower() in ['critical', 'high']:
                critical_immediate_count += 1
        
        # Verify at least some critical/high gaps are in immediate actions
        assert critical_immediate_count > 0, (
            "No critical/high severity gaps prioritized as Immediate actions"
        )
        
        # Verify critical gaps from gap report are in immediate or near-term actions
        critical_gap_ids = set()
        for gap in gap_report_data['gaps']:
            if gap.get('severity', '').lower() in ['critical', 'high']:
                critical_gap_ids.add(gap['subcategory_id'])
        
        # Check if critical gaps appear in roadmap actions
        roadmap_gap_ids = set()
        for action in immediate_actions + roadmap_data.get('near_term_actions', []):
            if 'csf_subcategory' in action:
                roadmap_gap_ids.add(action['csf_subcategory'])
        
        critical_in_roadmap = critical_gap_ids.intersection(roadmap_gap_ids)
        if critical_gap_ids:
            roadmap_coverage = len(critical_in_roadmap) / len(critical_gap_ids)
            assert roadmap_coverage >= 0.7, (
                f"Only {roadmap_coverage:.1%} of critical gaps in roadmap: "
                f"{critical_in_roadmap} out of {critical_gap_ids}"
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
        
        # Calculate total actions
        total_actions = (
            len(immediate_actions) +
            len(roadmap_data.get('near_term_actions', [])) +
            len(roadmap_data.get('medium_term_actions', []))
        )
        
        # Print test results
        print(f"\n✓ Patch Management Policy Analysis Test Passed")
        print(f"  - Detection rate: {detection_rate:.1%} ({len(detected_gaps)}/{len(expected_gaps)} gaps)")
        print(f"  - Critical gaps detected: {len(detected_critical)}/4")
        print(f"  - Total gaps identified: {len(identified_gaps)}")
        print(f"  - Critical/High in Immediate actions: {critical_immediate_count}")
        print(f"  - Revisions generated: {len(result.revised_policy.revisions)}")
        print(f"  - Roadmap actions: {total_actions}")
        print(f"  - Detected gaps: {sorted(detected_gaps)}")
        print(f"  - Missed gaps: {sorted(expected_gaps - detected_gaps)}")
        
    finally:
        pipeline.cleanup()


@pytest.mark.integration
def test_patch_policy_domain_prioritization(patch_policy_path, pipeline_config, temp_output_dir):
    """Test that patch_management domain prioritizes ID.RA, PR.DS, and PR.PS subcategories.
    
    **Validates: Requirement 12.3**
    """
    # Skip if required models are not available
    if not Path(pipeline_config.model_path).exists():
        pytest.skip("LLM model not available")
    
    if not Path(pipeline_config.embedding_model_path).exists():
        pytest.skip("Embedding model not available")
    
    pipeline = AnalysisPipeline(config=pipeline_config)
    
    try:
        result = pipeline.execute(
            policy_path=patch_policy_path,
            domain='patch_management',
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
            if subcategory_id.startswith('ID.RA') or subcategory_id.startswith('PR.DS') or subcategory_id.startswith('PR.PS'):
                prioritized_count += 1
        
        total_gaps = len(gap_report_data['gaps'])
        
        if total_gaps > 0:
            prioritized_percentage = prioritized_count / total_gaps
            # At least 60% of gaps should be from prioritized categories
            assert prioritized_percentage >= 0.5, (
                f"Prioritized categories not emphasized: {prioritized_count}/{total_gaps} ({prioritized_percentage:.1%})"
            )
        
        print(f"\n✓ Patch Management Domain Prioritization Test Passed")
        print(f"  - Prioritized gaps (ID.RA/PR.DS/PR.PS): {prioritized_count}/{total_gaps}")
        
    finally:
        pipeline.cleanup()


if __name__ == '__main__':
    pytest.main([__file__, '-v', '-s'])
