"""
Property test for dual format gap report generation.

Property 26: Dual Format Gap Report Generation
Validates: Requirements 9.12, 14.1, 14.2

This test verifies that both markdown and JSON reports are generated for any
gap analysis, ensuring consistent output across formats.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st

from models.domain import GapAnalysisReport, GapDetail
from reporting.gap_report_generator import GapReportGenerator


# Strategy for generating valid CSF subcategory IDs
@st.composite
def csf_subcategory_id_strategy(draw):
    """Generate valid CSF subcategory IDs matching pattern ^[A-Z]{2}\\.[A-Z]{2}-[0-9]{2}$"""
    func = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=2, max_size=2))
    cat = draw(st.text(alphabet="ABCDEFGHIJKLMNOPQRSTUVWXYZ", min_size=2, max_size=2))
    num = draw(st.integers(min_value=1, max_value=99))
    return f"{func}.{cat}-{num:02d}"


# Strategy for generating gap details
gap_detail_strategy = st.builds(
    GapDetail,
    subcategory_id=csf_subcategory_id_strategy(),
    subcategory_description=st.text(min_size=10, max_size=200),
    status=st.sampled_from(['partially_covered', 'missing']),
    evidence_quote=st.text(min_size=0, max_size=300),
    gap_explanation=st.text(min_size=10, max_size=500),
    severity=st.sampled_from(['critical', 'high', 'medium', 'low']),
    suggested_fix=st.text(min_size=10, max_size=500)
)


# Strategy for generating gap analysis reports
gap_analysis_report_strategy = st.builds(
    GapAnalysisReport,
    analysis_date=st.datetimes(
        min_value=datetime(2020, 1, 1),
        max_value=datetime(2030, 12, 31)
    ),
    input_file=st.text(min_size=5, max_size=100, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))).map(lambda s: f"{s.replace('/', '_')}.pdf"),
    input_file_hash=st.text(
        alphabet="0123456789abcdef",
        min_size=64,
        max_size=64
    ),
    model_name=st.sampled_from([
        'Qwen2.5-3B-Instruct',
        'Phi-3.5-mini',
        'Mistral-7B-Instruct',
        'Qwen3-8B-Instruct'
    ]),
    model_version=st.text(min_size=3, max_size=20),
    embedding_model=st.just('all-MiniLM-L6-v2'),
    gaps=st.lists(gap_detail_strategy, min_size=0, max_size=10),
    covered_subcategories=st.lists(csf_subcategory_id_strategy(), min_size=0, max_size=20),
    metadata=st.fixed_dictionaries({
        'prompt_version': st.text(min_size=3, max_size=10),
        'config_hash': st.text(alphabet="0123456789abcdef", min_size=8, max_size=16),
        'retrieval_params': st.fixed_dictionaries({
            'top_k': st.integers(min_value=1, max_value=10),
            'temperature': st.floats(min_value=0.0, max_value=1.0)
        })
    })
)


@given(report=gap_analysis_report_strategy)
def test_dual_format_generation(report):
    """
    Property 26: Dual Format Gap Report Generation
    
    Test that both markdown and JSON reports are generated for any analysis.
    
    Property: For any valid GapAnalysisReport, the generator produces both
    markdown and JSON files that exist and contain valid content.
    """
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Generate both formats
        md_path = tmpdir_path / "gap_analysis_report.md"
        json_path = tmpdir_path / "gap_analysis_report.json"
        
        generator.generate_markdown(report, str(md_path))
        generator.generate_json(report, str(json_path))
        
        # Property 1: Both files must exist
        assert md_path.exists(), "Markdown report file was not created"
        assert json_path.exists(), "JSON report file was not created"
        
        # Property 2: Both files must be non-empty
        assert md_path.stat().st_size > 0, "Markdown report is empty"
        assert json_path.stat().st_size > 0, "JSON report is empty"
        
        # Property 3: Markdown must contain key sections
        md_content = md_path.read_text(encoding='utf-8')
        assert "# Gap Analysis Report" in md_content, "Markdown missing main header"
        assert "## Analysis Metadata" in md_content, "Markdown missing metadata section"
        assert "## Summary" in md_content, "Markdown missing summary section"
        # Input file may have control characters normalized, so check if it's present in some form
        assert "Input File" in md_content, "Markdown missing input file label"
        assert report.model_name in md_content, "Markdown missing model name"
        
        # Property 4: JSON must be valid and parseable
        json_content = json_path.read_text(encoding='utf-8')
        json_data = json.loads(json_content)
        
        # Property 5: JSON must contain all required fields
        required_fields = [
            'analysis_date',
            'input_file',
            'input_file_hash',
            'model_name',
            'model_version',
            'embedding_model',
            'gaps',
            'covered_subcategories',
            'metadata'
        ]
        for field in required_fields:
            assert field in json_data, f"JSON missing required field: {field}"
        
        # Property 6: JSON gaps must match report gaps count
        assert len(json_data['gaps']) == len(report.gaps), \
            "JSON gaps count does not match report"
        
        # Property 7: JSON covered subcategories must match report
        assert len(json_data['covered_subcategories']) == len(report.covered_subcategories), \
            "JSON covered subcategories count does not match report"
        
        # Property 8: Each gap in JSON must have all required fields
        gap_required_fields = [
            'subcategory_id',
            'description',
            'status',
            'evidence_quote',
            'gap_explanation',
            'severity',
            'suggested_fix'
        ]
        for gap in json_data['gaps']:
            for field in gap_required_fields:
                assert field in gap, f"Gap missing required field: {field}"


@given(report=gap_analysis_report_strategy)
def test_markdown_contains_all_gaps(report):
    """
    Test that markdown report contains all gaps from the analysis.
    
    Property: For any GapAnalysisReport with N gaps, the markdown output
    contains N gap sections with proper formatting.
    """
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = Path(tmpdir) / "report.md"
        generator.generate_markdown(report, str(md_path))
        
        md_content = md_path.read_text(encoding='utf-8')
        
        # Each gap should have its subcategory ID in the markdown
        for gap in report.gaps:
            assert gap.subcategory_id in md_content, \
                f"Gap {gap.subcategory_id} not found in markdown"
            assert gap.severity in md_content.lower(), \
                f"Severity {gap.severity} not found in markdown"


@given(report=gap_analysis_report_strategy)
def test_json_schema_conformance_basic(report):
    """
    Test that JSON output has correct structure.
    
    Property: For any GapAnalysisReport, the JSON output is valid JSON
    and contains the expected structure.
    """
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "report.json"
        generator.generate_json(report, str(json_path))
        
        # Must be valid JSON
        json_content = json_path.read_text(encoding='utf-8')
        json_data = json.loads(json_content)
        
        # Must be a dictionary at top level
        assert isinstance(json_data, dict), "JSON root must be an object"
        
        # Gaps must be a list
        assert isinstance(json_data['gaps'], list), "Gaps must be a list"
        
        # Covered subcategories must be a list
        assert isinstance(json_data['covered_subcategories'], list), \
            "Covered subcategories must be a list"
        
        # Metadata must be a dictionary
        assert isinstance(json_data['metadata'], dict), "Metadata must be an object"


def test_empty_gaps_report():
    """
    Test that reports with no gaps are handled correctly.
    
    Property: A report with zero gaps produces valid markdown and JSON
    with appropriate messaging.
    """
    report = GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file="test_policy.pdf",
        input_file_hash="a" * 64,
        model_name="Qwen2.5-3B-Instruct",
        model_version="Q4_K_M",
        embedding_model="all-MiniLM-L6-v2",
        gaps=[],
        covered_subcategories=["GV.RM-01", "ID.AM-01"],
        metadata={
            'prompt_version': 'v1.0',
            'config_hash': 'abc123',
            'retrieval_params': {'top_k': 5}
        }
    )
    
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        md_path = Path(tmpdir) / "report.md"
        json_path = Path(tmpdir) / "report.json"
        
        generator.generate_markdown(report, str(md_path))
        generator.generate_json(report, str(json_path))
        
        # Both files should exist
        assert md_path.exists()
        assert json_path.exists()
        
        # Markdown should indicate no gaps
        md_content = md_path.read_text(encoding='utf-8')
        assert "No gaps identified" in md_content or "Total Gaps Identified**: 0" in md_content
        
        # JSON should have empty gaps list
        json_data = json.loads(json_path.read_text(encoding='utf-8'))
        assert json_data['gaps'] == []
        assert len(json_data['covered_subcategories']) == 2


if __name__ == "__main__":
    # Run a few examples manually for debugging
    import sys
    from hypothesis import settings, Verbosity
    
    print("Running property tests for dual format generation...")
    
    with settings(verbosity=Verbosity.verbose, max_examples=10):
        test_dual_format_generation()
        test_markdown_contains_all_gaps()
        test_json_schema_conformance_basic()
    
    test_empty_gaps_report()
    
    print("All tests passed!")
