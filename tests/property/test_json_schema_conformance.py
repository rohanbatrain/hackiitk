"""
Property test for JSON schema conformance.

Property 42: JSON Schema Conformance
Validates: Requirements 14.9

This test verifies that JSON output conforms to the documented schema with
all required fields, ensuring integration compatibility and testability.
"""

import json
import tempfile
from pathlib import Path
from datetime import datetime
from hypothesis import given, strategies as st
from jsonschema import ValidationError

from models.domain import GapAnalysisReport, GapDetail
from models.schemas import (
    validate_gap_analysis_report,
    GAP_ANALYSIS_REPORT_SCHEMA,
    is_valid_gap_analysis_report
)
from reporting.gap_report_generator import GapReportGenerator


# Strategy for generating valid CSF subcategory IDs matching the pattern
def csf_subcategory_id():
    """Generate valid CSF subcategory IDs matching pattern ^[A-Z]{2}\\.[A-Z]{2}-[0-9]{2}$"""
    functions = ['GV', 'ID', 'PR', 'DE', 'RS', 'RC']
    categories = ['RM', 'OV', 'SC', 'PO', 'AM', 'RA', 'IM', 'BE', 'DS', 'PS', 'AT', 'AA', 'IP', 'AE', 'CM', 'AN', 'MA', 'RP', 'CO']
    
    return st.tuples(
        st.sampled_from(functions),
        st.sampled_from(categories),
        st.integers(min_value=1, max_value=99)
    ).map(lambda x: f"{x[0]}.{x[1]}-{x[2]:02d}")


# Strategy for generating gap details that conform to schema
gap_detail_strategy = st.builds(
    GapDetail,
    subcategory_id=csf_subcategory_id(),
    subcategory_description=st.text(min_size=10, max_size=500, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    status=st.sampled_from(['partially_covered', 'missing']),
    evidence_quote=st.text(min_size=0, max_size=500, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    gap_explanation=st.text(min_size=10, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    severity=st.sampled_from(['critical', 'high', 'medium', 'low']),
    suggested_fix=st.text(min_size=10, max_size=1000, alphabet=st.characters(blacklist_categories=('Cs', 'Cc')))
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
    model_version=st.text(min_size=3, max_size=20, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
    embedding_model=st.just('all-MiniLM-L6-v2'),
    gaps=st.lists(gap_detail_strategy, min_size=0, max_size=15),
    covered_subcategories=st.lists(csf_subcategory_id(), min_size=0, max_size=30, unique=True),
    metadata=st.fixed_dictionaries({
        'prompt_version': st.text(min_size=3, max_size=20, alphabet=st.characters(blacklist_categories=('Cs', 'Cc'))),
        'config_hash': st.text(alphabet="0123456789abcdef", min_size=8, max_size=16),
        'retrieval_params': st.fixed_dictionaries({
            'top_k': st.integers(min_value=1, max_value=20),
            'temperature': st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False)
        })
    })
)


@given(report=gap_analysis_report_strategy)
def test_json_schema_conformance(report):
    """
    Property 42: JSON Schema Conformance
    
    Test that JSON output conforms to documented schema with all required fields.
    
    Property: For any valid GapAnalysisReport, the generated JSON output
    passes schema validation without errors.
    """
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "gap_analysis_report.json"
        
        # Generate JSON report
        generator.generate_json(report, str(json_path))
        
        # Load the generated JSON
        json_content = json_path.read_text(encoding='utf-8')
        json_data = json.loads(json_content)
        
        # Property 1: JSON must pass schema validation
        try:
            validate_gap_analysis_report(json_data)
        except ValidationError as e:
            raise AssertionError(f"JSON schema validation failed: {e.message}")
        
        # Property 2: All required top-level fields must be present
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
            assert field in json_data, f"Missing required field: {field}"
        
        # Property 3: Each gap must have all required fields
        gap_required_fields = [
            'subcategory_id',
            'description',
            'status',
            'evidence_quote',
            'gap_explanation',
            'severity',
            'suggested_fix'
        ]
        for i, gap in enumerate(json_data['gaps']):
            for field in gap_required_fields:
                assert field in gap, f"Gap {i} missing required field: {field}"
        
        # Property 4: Subcategory IDs must match pattern
        subcategory_pattern = r'^[A-Z]{2}\.[A-Z]{2}-[0-9]{2}$'
        import re
        pattern = re.compile(subcategory_pattern)
        
        for gap in json_data['gaps']:
            assert pattern.match(gap['subcategory_id']), \
                f"Invalid subcategory ID format: {gap['subcategory_id']}"
        
        for subcategory_id in json_data['covered_subcategories']:
            assert pattern.match(subcategory_id), \
                f"Invalid covered subcategory ID format: {subcategory_id}"
        
        # Property 5: Status must be valid enum value
        valid_statuses = ['partially_covered', 'missing']
        for gap in json_data['gaps']:
            assert gap['status'] in valid_statuses, \
                f"Invalid status: {gap['status']}"
        
        # Property 6: Severity must be valid enum value
        valid_severities = ['critical', 'high', 'medium', 'low']
        for gap in json_data['gaps']:
            assert gap['severity'] in valid_severities, \
                f"Invalid severity: {gap['severity']}"
        
        # Property 7: Metadata must contain required fields
        assert 'prompt_version' in json_data['metadata']
        assert 'config_hash' in json_data['metadata']
        assert 'retrieval_params' in json_data['metadata']


@given(report=gap_analysis_report_strategy)
def test_json_data_types(report):
    """
    Test that JSON output has correct data types for all fields.
    
    Property: For any GapAnalysisReport, the JSON output uses correct
    data types (strings, arrays, objects) as specified in the schema.
    """
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "report.json"
        generator.generate_json(report, str(json_path))
        
        json_data = json.loads(json_path.read_text(encoding='utf-8'))
        
        # Top-level type checks
        assert isinstance(json_data['analysis_date'], str)
        assert isinstance(json_data['input_file'], str)
        assert isinstance(json_data['input_file_hash'], str)
        assert isinstance(json_data['model_name'], str)
        assert isinstance(json_data['model_version'], str)
        assert isinstance(json_data['embedding_model'], str)
        assert isinstance(json_data['gaps'], list)
        assert isinstance(json_data['covered_subcategories'], list)
        assert isinstance(json_data['metadata'], dict)
        
        # Gap field type checks
        for gap in json_data['gaps']:
            assert isinstance(gap['subcategory_id'], str)
            assert isinstance(gap['description'], str)
            assert isinstance(gap['status'], str)
            assert isinstance(gap['evidence_quote'], str)
            assert isinstance(gap['gap_explanation'], str)
            assert isinstance(gap['severity'], str)
            assert isinstance(gap['suggested_fix'], str)
        
        # Covered subcategories type check
        for subcategory_id in json_data['covered_subcategories']:
            assert isinstance(subcategory_id, str)


@given(report=gap_analysis_report_strategy)
def test_json_no_additional_properties(report):
    """
    Test that JSON output does not contain additional properties.
    
    Property: For any GapAnalysisReport, the JSON output contains only
    the fields defined in the schema (additionalProperties: false).
    """
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "report.json"
        generator.generate_json(report, str(json_path))
        
        json_data = json.loads(json_path.read_text(encoding='utf-8'))
        
        # Top-level allowed fields
        allowed_top_level = {
            'analysis_date',
            'input_file',
            'input_file_hash',
            'model_name',
            'model_version',
            'embedding_model',
            'gaps',
            'covered_subcategories',
            'metadata'
        }
        
        actual_top_level = set(json_data.keys())
        extra_fields = actual_top_level - allowed_top_level
        assert not extra_fields, f"Unexpected top-level fields: {extra_fields}"
        
        # Gap allowed fields
        allowed_gap_fields = {
            'subcategory_id',
            'description',
            'status',
            'evidence_quote',
            'gap_explanation',
            'severity',
            'suggested_fix'
        }
        
        for i, gap in enumerate(json_data['gaps']):
            actual_gap_fields = set(gap.keys())
            extra_gap_fields = actual_gap_fields - allowed_gap_fields
            assert not extra_gap_fields, \
                f"Gap {i} has unexpected fields: {extra_gap_fields}"


def test_schema_validation_helper_functions():
    """
    Test that schema validation helper functions work correctly.
    
    Property: The is_valid_gap_analysis_report function correctly identifies
    valid and invalid reports.
    """
    # Valid report
    valid_report_data = {
        "analysis_date": "2024-01-15T10:30:00",
        "input_file": "test_policy.pdf",
        "input_file_hash": "a" * 64,
        "model_name": "Qwen2.5-3B-Instruct",
        "model_version": "Q4_K_M",
        "embedding_model": "all-MiniLM-L6-v2",
        "gaps": [
            {
                "subcategory_id": "GV.RM-01",
                "description": "Test description",
                "status": "missing",
                "evidence_quote": "",
                "gap_explanation": "Test explanation",
                "severity": "high",
                "suggested_fix": "Test fix"
            }
        ],
        "covered_subcategories": ["ID.AM-01"],
        "metadata": {
            "prompt_version": "v1.0",
            "config_hash": "abc123",
            "retrieval_params": {"top_k": 5}
        }
    }
    
    assert is_valid_gap_analysis_report(valid_report_data), \
        "Valid report should pass validation"
    
    # Invalid report - missing required field
    invalid_report_data = valid_report_data.copy()
    del invalid_report_data['model_name']
    
    assert not is_valid_gap_analysis_report(invalid_report_data), \
        "Invalid report should fail validation"
    
    # Invalid report - wrong status enum
    invalid_report_data2 = valid_report_data.copy()
    invalid_report_data2['gaps'] = [
        {
            "subcategory_id": "GV.RM-01",
            "description": "Test",
            "status": "invalid_status",
            "evidence_quote": "",
            "gap_explanation": "Test",
            "severity": "high",
            "suggested_fix": "Test"
        }
    ]
    
    assert not is_valid_gap_analysis_report(invalid_report_data2), \
        "Report with invalid enum should fail validation"


def test_datetime_format():
    """
    Test that datetime is formatted correctly in ISO 8601 format.
    
    Property: The analysis_date field in JSON output is a valid ISO 8601
    datetime string.
    """
    from datetime import datetime as dt
    
    report = GapAnalysisReport(
        analysis_date=dt(2024, 3, 15, 14, 30, 45),
        input_file="test.pdf",
        input_file_hash="a" * 64,
        model_name="Qwen2.5-3B-Instruct",
        model_version="Q4_K_M",
        embedding_model="all-MiniLM-L6-v2",
        gaps=[],
        covered_subcategories=[],
        metadata={'prompt_version': 'v1.0', 'config_hash': 'abc', 'retrieval_params': {}}
    )
    
    generator = GapReportGenerator()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        json_path = Path(tmpdir) / "report.json"
        generator.generate_json(report, str(json_path))
        
        json_data = json.loads(json_path.read_text(encoding='utf-8'))
        
        # Should be ISO 8601 format
        assert 'T' in json_data['analysis_date'], \
            "Datetime should be in ISO 8601 format with T separator"
        
        # Should be parseable back to datetime
        parsed_dt = dt.fromisoformat(json_data['analysis_date'])
        assert parsed_dt.year == 2024
        assert parsed_dt.month == 3
        assert parsed_dt.day == 15


if __name__ == "__main__":
    # Run tests manually for debugging
    import sys
    from hypothesis import settings, Verbosity
    
    print("Running property tests for JSON schema conformance...")
    
    with settings(verbosity=Verbosity.verbose, max_examples=20):
        test_json_schema_conformance()
        test_json_data_types()
        test_json_no_additional_properties()
    
    test_schema_validation_helper_functions()
    test_datetime_format()
    
    print("All tests passed!")
