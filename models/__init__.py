"""
Data models module.

This module defines all data structures used throughout the system
including documents, chunks, embeddings, gaps, and reports.
"""

__version__ = "0.1.0"

# Export schema validation functions for convenience
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

__all__ = [
    "validate_gap_detail",
    "validate_gap_analysis_report",
    "validate_action_item",
    "validate_implementation_roadmap",
    "is_valid_gap_analysis_report",
    "is_valid_implementation_roadmap",
    "get_schema_errors",
    "GAP_DETAIL_SCHEMA",
    "GAP_ANALYSIS_REPORT_SCHEMA",
    "ACTION_ITEM_SCHEMA",
    "IMPLEMENTATION_ROADMAP_SCHEMA"
]

