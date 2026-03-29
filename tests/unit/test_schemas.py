"""
Unit tests for JSON schema validation.

Tests validate that the JSON schemas correctly enforce structure and data types
for gap analysis reports and implementation roadmaps.
"""

import pytest
from jsonschema import ValidationError
from models.schemas import (
    validate_gap_detail,
    validate_gap_analysis_report,
    validate_action_item,
    validate_implementation_roadmap,
    is_valid_gap_analysis_report,
    is_valid_implementation_roadmap,
    get_schema_errors,
    GAP_DETAIL_SCHEMA,
    GAP_ANALYSIS_REPORT_SCHEMA,
    ACTION_ITEM_SCHEMA,
    IMPLEMENTATION_ROADMAP_SCHEMA
)


class TestGapDetailSchema:
    """Tests for gap detail schema validation."""
    
    def test_valid_gap_detail(self):
        """Valid gap detail should pass validation."""
        gap_detail = {
            "subcategory_id": "GV.RM-01",
            "description": "Risk management processes are established",
            "status": "missing",
            "evidence_quote": "",
            "gap_explanation": "No risk management process documented",
            "severity": "critical",
            "suggested_fix": "Establish formal risk management process"
        }
        validate_gap_detail(gap_detail)  # Should not raise
    
    def test_invalid_subcategory_id_format(self):
        """Invalid subcategory ID format should fail validation."""
        gap_detail = {
            "subcategory_id": "INVALID",
            "description": "Test",
            "status": "missing",
            "evidence_quote": "",
            "gap_explanation": "Test",
            "severity": "low",
            "suggested_fix": "Test"
        }
        with pytest.raises(ValidationError):
            validate_gap_detail(gap_detail)
    
    def test_invalid_status_value(self):
        """Invalid status value should fail validation."""
        gap_detail = {
            "subcategory_id": "GV.RM-01",
            "description": "Test",
            "status": "invalid_status",
            "evidence_quote": "",
            "gap_explanation": "Test",
            "severity": "low",
            "suggested_fix": "Test"
        }
        with pytest.raises(ValidationError):
            validate_gap_detail(gap_detail)
    
    def test_missing_required_field(self):
        """Missing required field should fail validation."""
        gap_detail = {
            "subcategory_id": "GV.RM-01",
            "description": "Test",
            "status": "missing"
            # Missing other required fields
        }
        with pytest.raises(ValidationError):
            validate_gap_detail(gap_detail)


class TestGapAnalysisReportSchema:
    """Tests for gap analysis report schema validation."""
    
    def test_valid_gap_analysis_report(self):
        """Valid gap analysis report should pass validation."""
        report = {
            "analysis_date": "2024-01-15T10:30:00Z",
            "input_file": "/path/to/policy.pdf",
            "input_file_hash": "abc123def456",
            "model_name": "qwen3-8b",
            "model_version": "q4_0",
            "embedding_model": "all-MiniLM-L6-v2",
            "gaps": [
                {
                    "subcategory_id": "GV.RM-01",
                    "description": "Risk management processes",
                    "status": "missing",
                    "evidence_quote": "",
                    "gap_explanation": "No process documented",
                    "severity": "critical",
                    "suggested_fix": "Establish process"
                }
            ],
            "covered_subcategories": ["ID.AM-01", "PR.DS-01"],
            "metadata": {
                "prompt_version": "1.0",
                "config_hash": "xyz789",
                "retrieval_params": {"top_k": 5}
            }
        }
        validate_gap_analysis_report(report)  # Should not raise
        assert is_valid_gap_analysis_report(report) is True
    
    def test_invalid_covered_subcategory_format(self):
        """Invalid covered subcategory format should fail validation."""
        report = {
            "analysis_date": "2024-01-15T10:30:00Z",
            "input_file": "/path/to/policy.pdf",
            "input_file_hash": "abc123",
            "model_name": "qwen3-8b",
            "model_version": "q4_0",
            "embedding_model": "all-MiniLM-L6-v2",
            "gaps": [],
            "covered_subcategories": ["INVALID_FORMAT"],
            "metadata": {}
        }
        assert is_valid_gap_analysis_report(report) is False


class TestActionItemSchema:
    """Tests for action item schema validation."""
    
    def test_valid_action_item(self):
        """Valid action item should pass validation."""
        action_item = {
            "action_id": "ACT-001",
            "timeframe": "immediate",
            "severity": "critical",
            "effort": "high",
            "csf_subcategory": "GV.RM-01",
            "policy_section": "Risk Management",
            "description": "Establish risk management process",
            "technical_steps": ["Deploy risk tool"],
            "administrative_steps": ["Create policy"],
            "physical_steps": []
        }
        validate_action_item(action_item)  # Should not raise
    
    def test_invalid_timeframe(self):
        """Invalid timeframe should fail validation."""
        action_item = {
            "action_id": "ACT-001",
            "timeframe": "invalid_timeframe",
            "severity": "critical",
            "effort": "high",
            "csf_subcategory": "GV.RM-01",
            "policy_section": "Risk Management",
            "description": "Test",
            "technical_steps": [],
            "administrative_steps": [],
            "physical_steps": []
        }
        with pytest.raises(ValidationError):
            validate_action_item(action_item)


class TestImplementationRoadmapSchema:
    """Tests for implementation roadmap schema validation."""
    
    def test_valid_implementation_roadmap(self):
        """Valid implementation roadmap should pass validation."""
        roadmap = {
            "roadmap_date": "2024-01-15T10:30:00Z",
            "policy_analyzed": "/path/to/policy.pdf",
            "immediate_actions": [
                {
                    "action_id": "ACT-001",
                    "timeframe": "immediate",
                    "severity": "critical",
                    "effort": "high",
                    "csf_subcategory": "GV.RM-01",
                    "policy_section": "Risk Management",
                    "description": "Establish process",
                    "technical_steps": [],
                    "administrative_steps": [],
                    "physical_steps": []
                }
            ],
            "near_term_actions": [],
            "medium_term_actions": [],
            "metadata": {
                "analysis_date": "2024-01-15T10:30:00Z",
                "input_file": "/path/to/policy.pdf",
                "model_name": "qwen3-8b",
                "model_version": "q4_0"
            }
        }
        validate_implementation_roadmap(roadmap)  # Should not raise
        assert is_valid_implementation_roadmap(roadmap) is True
    
    def test_missing_required_actions_field(self):
        """Missing required actions field should fail validation."""
        roadmap = {
            "immediate_actions": [],
            "near_term_actions": [],
            # Missing medium_term_actions
            "metadata": {}
        }
        assert is_valid_implementation_roadmap(roadmap) is False


class TestSchemaErrorReporting:
    """Tests for schema error reporting utilities."""
    
    def test_get_schema_errors_returns_list(self):
        """get_schema_errors should return list of error messages."""
        invalid_gap = {
            "subcategory_id": "INVALID",
            "status": "invalid_status"
        }
        errors = get_schema_errors(invalid_gap, GAP_DETAIL_SCHEMA)
        assert isinstance(errors, list)
        assert len(errors) > 0
    
    def test_get_schema_errors_empty_for_valid(self):
        """get_schema_errors should return empty list for valid data."""
        valid_gap = {
            "subcategory_id": "GV.RM-01",
            "description": "Test",
            "status": "missing",
            "evidence_quote": "",
            "gap_explanation": "Test",
            "severity": "low",
            "suggested_fix": "Test"
        }
        errors = get_schema_errors(valid_gap, GAP_DETAIL_SCHEMA)
        assert errors == []
