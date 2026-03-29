# Domain Models

This module contains the core domain data models for the Offline Policy Gap Analyzer.

## Overview

All models are implemented as Python dataclasses with comprehensive type hints and docstrings. They support serialization for JSON output and persistence as required by the system design.

## Implemented Models

### Document Processing Models

1. **ParsedDocument** - Represents a parsed policy document with text, metadata, and structure
2. **DocumentStructure** - Hierarchical structure of a document with headings and sections
3. **Heading** - Document heading with level and position information
4. **Section** - Document section with hierarchical subsections
5. **Paragraph** - Document paragraph (deprecated, use Section instead)
6. **TextChunk** - Text chunk with metadata for embedding and retrieval

### Reference Catalog Models

7. **CSFSubcategory** - NIST CSF 2.0 subcategory from reference catalog with keywords and domain tags

### Retrieval Models

8. **RetrievalResult** - Result from hybrid retrieval combining dense and sparse search
9. **CoverageAssessment** - Stage A deterministic coverage assessment with scores

### Analysis Models

10. **GapDetail** - Detailed gap information from Stage B analysis
11. **GapAnalysisReport** - Complete gap analysis output with metadata

### Revision Models

12. **Revision** - Single policy revision addressing a gap
13. **RevisedPolicy** - Revised policy document with all revisions and warning

### Roadmap Models

14. **ActionItem** - Implementation roadmap action item with steps
15. **ImplementationRoadmap** - Prioritized implementation plan

### Audit Models

16. **AuditLogEntry** - Immutable audit log entry for compliance traceability

## Usage

```python
from models.domain import ParsedDocument, CSFSubcategory, GapAnalysisReport

# Create a parsed document
doc = ParsedDocument(
    text="Policy text...",
    file_path="/path/to/policy.pdf",
    file_type="pdf",
    page_count=10,
    structure=DocumentStructure(headings=[], sections=[]),
    metadata={"author": "Security Team"}
)

# Create a CSF subcategory
subcategory = CSFSubcategory(
    subcategory_id="GV.RM-01",
    function="Govern",
    category="Risk Management Strategy",
    description="Risk management objectives are established...",
    keywords=["risk", "management", "objectives"],
    domain_tags=["isms", "risk_management"],
    mapped_templates=["Risk Management Policy"],
    priority="high"
)
```

## Type Hints

All models use comprehensive type hints:
- `str` for text fields
- `int` for numeric fields
- `float` for scores and measurements
- `List[T]` for collections
- `Dict` for metadata and configuration
- `Optional[T]` for nullable fields
- `datetime` for timestamps
- `Any` for flexible fields (e.g., numpy arrays)

## Serialization

All models are dataclasses and can be easily serialized to JSON using standard libraries:

```python
from dataclasses import asdict
import json

gap_report = GapAnalysisReport(...)
report_dict = asdict(gap_report)
json_output = json.dumps(report_dict, default=str)
```

## Validation

Models include docstrings describing field constraints and expected values. Additional validation logic should be implemented in the component classes that use these models.

### JSON Schema Validation

The `models/schemas.py` module provides JSON schemas and validation functions for output files:

```python
from models.schemas import (
    validate_gap_analysis_report,
    validate_implementation_roadmap,
    GAP_ANALYSIS_REPORT_SCHEMA,
    IMPLEMENTATION_ROADMAP_SCHEMA
)

# Validate a gap analysis report
report_dict = {
    "analysis_date": "2024-01-15T10:30:00Z",
    "input_file": "/path/to/policy.pdf",
    "input_file_hash": "abc123",
    "model_name": "qwen3-8b",
    "model_version": "q4_0",
    "embedding_model": "all-MiniLM-L6-v2",
    "gaps": [...],
    "covered_subcategories": ["ID.AM-01"],
    "metadata": {}
}

validate_gap_analysis_report(report_dict)  # Raises ValidationError if invalid

# Check validity without raising exceptions
from models.schemas import is_valid_gap_analysis_report
if is_valid_gap_analysis_report(report_dict):
    print("Report is valid")

# Get detailed error messages
from models.schemas import get_schema_errors
errors = get_schema_errors(report_dict, GAP_ANALYSIS_REPORT_SCHEMA)
for error in errors:
    print(f"Validation error: {error}")
```

**Available Schemas:**
- `GAP_DETAIL_SCHEMA` - Individual gap detail structure
- `GAP_ANALYSIS_REPORT_SCHEMA` - Complete gap analysis report
- `ACTION_ITEM_SCHEMA` - Individual action item structure
- `IMPLEMENTATION_ROADMAP_SCHEMA` - Complete implementation roadmap

**Validation Functions:**
- `validate_gap_detail(gap_detail)` - Validate gap detail, raises ValidationError
- `validate_gap_analysis_report(report)` - Validate gap report, raises ValidationError
- `validate_action_item(action_item)` - Validate action item, raises ValidationError
- `validate_implementation_roadmap(roadmap)` - Validate roadmap, raises ValidationError
- `is_valid_gap_analysis_report(report)` - Returns True/False
- `is_valid_implementation_roadmap(roadmap)` - Returns True/False
- `get_schema_errors(data, schema)` - Returns list of error messages

## Testing

See `scripts/verify_domain_models.py` for a verification script that instantiates all models.

Unit tests are available in `tests/unit/test_domain_models.py`.
