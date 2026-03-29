"""
JSON schemas for output validation.

This module defines JSON schemas for gap analysis reports and implementation
roadmaps, along with validation functions to ensure output conformance.
"""

from typing import Dict, Any, List
from jsonschema import validate, ValidationError, Draft7Validator


# JSON Schema for Gap Detail
GAP_DETAIL_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "subcategory_id": {
            "type": "string",
            "description": "CSF subcategory identifier (e.g., 'GV.RM-01')",
            "pattern": "^[A-Z]{2}\\.[A-Z]{2}-[0-9]{2}$"
        },
        "description": {
            "type": "string",
            "description": "Full NIST CSF subcategory description text"
        },
        "status": {
            "type": "string",
            "enum": ["partially_covered", "missing"],
            "description": "Gap status indicating coverage level"
        },
        "evidence_quote": {
            "type": "string",
            "description": "Relevant text from policy (empty string if missing)"
        },
        "gap_explanation": {
            "type": "string",
            "description": "Explanation of what is missing or inadequate"
        },
        "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"],
            "description": "Gap severity level"
        },
        "suggested_fix": {
            "type": "string",
            "description": "Suggested policy language to address the gap"
        }
    },
    "required": [
        "subcategory_id",
        "description",
        "status",
        "evidence_quote",
        "gap_explanation",
        "severity",
        "suggested_fix"
    ],
    "additionalProperties": False
}


# JSON Schema for Gap Analysis Report
GAP_ANALYSIS_REPORT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "analysis_date": {
            "type": "string",
            "format": "date-time",
            "description": "Timestamp of analysis execution"
        },
        "input_file": {
            "type": "string",
            "description": "Path to analyzed policy document"
        },
        "input_file_hash": {
            "type": "string",
            "description": "SHA-256 hash of input file for traceability"
        },
        "model_name": {
            "type": "string",
            "description": "LLM model name used for analysis"
        },
        "model_version": {
            "type": "string",
            "description": "LLM model version/quantization"
        },
        "embedding_model": {
            "type": "string",
            "description": "Embedding model name"
        },
        "gaps": {
            "type": "array",
            "items": GAP_DETAIL_SCHEMA,
            "description": "List of identified gaps"
        },
        "covered_subcategories": {
            "type": "array",
            "items": {
                "type": "string",
                "pattern": "^[A-Z]{2}\\.[A-Z]{2}-[0-9]{2}$"
            },
            "description": "List of CSF subcategory IDs that are covered"
        },
        "metadata": {
            "type": "object",
            "properties": {
                "prompt_version": {
                    "type": "string",
                    "description": "Version of prompt templates used"
                },
                "config_hash": {
                    "type": "string",
                    "description": "Hash of configuration parameters"
                },
                "retrieval_params": {
                    "type": "object",
                    "description": "Retrieval configuration parameters"
                }
            },
            "description": "Additional metadata about the analysis"
        }
    },
    "required": [
        "analysis_date",
        "input_file",
        "input_file_hash",
        "model_name",
        "model_version",
        "embedding_model",
        "gaps",
        "covered_subcategories",
        "metadata"
    ],
    "additionalProperties": False
}


# JSON Schema for Action Item
ACTION_ITEM_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "action_id": {
            "type": "string",
            "description": "Unique action identifier"
        },
        "timeframe": {
            "type": "string",
            "enum": ["immediate", "near_term", "medium_term"],
            "description": "Implementation timeframe"
        },
        "severity": {
            "type": "string",
            "enum": ["critical", "high", "medium", "low"],
            "description": "Gap severity this addresses"
        },
        "effort": {
            "type": "string",
            "enum": ["low", "medium", "high"],
            "description": "Implementation effort estimate"
        },
        "csf_subcategory": {
            "type": "string",
            "pattern": "^[A-Z]{2}\\.[A-Z]{2}-[0-9]{2}$",
            "description": "CSF subcategory ID being addressed"
        },
        "policy_section": {
            "type": "string",
            "description": "Policy section requiring changes"
        },
        "description": {
            "type": "string",
            "description": "Action description"
        },
        "technical_steps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of technical implementation steps"
        },
        "administrative_steps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of administrative/policy steps"
        },
        "physical_steps": {
            "type": "array",
            "items": {"type": "string"},
            "description": "List of physical security steps"
        }
    },
    "required": [
        "action_id",
        "timeframe",
        "severity",
        "effort",
        "csf_subcategory",
        "policy_section",
        "description",
        "technical_steps",
        "administrative_steps",
        "physical_steps"
    ],
    "additionalProperties": False
}


# JSON Schema for Implementation Roadmap
IMPLEMENTATION_ROADMAP_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "properties": {
        "roadmap_date": {
            "type": "string",
            "format": "date-time",
            "description": "Timestamp of roadmap generation"
        },
        "policy_analyzed": {
            "type": "string",
            "description": "Path to analyzed policy document"
        },
        "immediate_actions": {
            "type": "array",
            "items": ACTION_ITEM_SCHEMA,
            "description": "Actions for 0-3 months (Critical/High severity)"
        },
        "near_term_actions": {
            "type": "array",
            "items": ACTION_ITEM_SCHEMA,
            "description": "Actions for 3-6 months (Medium severity)"
        },
        "medium_term_actions": {
            "type": "array",
            "items": ACTION_ITEM_SCHEMA,
            "description": "Actions for 6-12 months (Low severity)"
        },
        "metadata": {
            "type": "object",
            "description": "Additional metadata about roadmap generation"
        }
    },
    "required": [
        "roadmap_date",
        "policy_analyzed",
        "immediate_actions",
        "near_term_actions",
        "medium_term_actions",
        "metadata"
    ],
    "additionalProperties": False
}


def validate_gap_detail(gap_detail: Dict[str, Any]) -> None:
    """
    Validate a gap detail object against the schema.
    
    Args:
        gap_detail: Dictionary representing a gap detail
        
    Raises:
        ValidationError: If the gap detail does not conform to schema
    """
    validate(instance=gap_detail, schema=GAP_DETAIL_SCHEMA)


def validate_gap_analysis_report(report: Dict[str, Any]) -> None:
    """
    Validate a gap analysis report against the schema.
    
    Args:
        report: Dictionary representing a gap analysis report
        
    Raises:
        ValidationError: If the report does not conform to schema
    """
    validate(instance=report, schema=GAP_ANALYSIS_REPORT_SCHEMA)


def validate_action_item(action_item: Dict[str, Any]) -> None:
    """
    Validate an action item against the schema.
    
    Args:
        action_item: Dictionary representing an action item
        
    Raises:
        ValidationError: If the action item does not conform to schema
    """
    validate(instance=action_item, schema=ACTION_ITEM_SCHEMA)


def validate_implementation_roadmap(roadmap: Dict[str, Any]) -> None:
    """
    Validate an implementation roadmap against the schema.
    
    Args:
        roadmap: Dictionary representing an implementation roadmap
        
    Raises:
        ValidationError: If the roadmap does not conform to schema
    """
    validate(instance=roadmap, schema=IMPLEMENTATION_ROADMAP_SCHEMA)


def get_schema_errors(data: Dict[str, Any], schema: Dict[str, Any]) -> List[str]:
    """
    Get a list of validation errors for data against a schema.
    
    Args:
        data: Dictionary to validate
        schema: JSON schema to validate against
        
    Returns:
        List of error messages (empty if valid)
    """
    validator = Draft7Validator(schema)
    errors = []
    for error in validator.iter_errors(data):
        errors.append(f"{'.'.join(str(p) for p in error.path)}: {error.message}")
    return errors


def is_valid_gap_analysis_report(report: Dict[str, Any]) -> bool:
    """
    Check if a gap analysis report is valid.
    
    Args:
        report: Dictionary representing a gap analysis report
        
    Returns:
        True if valid, False otherwise
    """
    try:
        validate_gap_analysis_report(report)
        return True
    except ValidationError:
        return False


def is_valid_implementation_roadmap(roadmap: Dict[str, Any]) -> bool:
    """
    Check if an implementation roadmap is valid.
    
    Args:
        roadmap: Dictionary representing an implementation roadmap
        
    Returns:
        True if valid, False otherwise
    """
    try:
        validate_implementation_roadmap(roadmap)
        return True
    except ValidationError:
        return False
