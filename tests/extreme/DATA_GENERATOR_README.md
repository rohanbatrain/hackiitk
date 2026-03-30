# Test Data Generator

The Test Data Generator provides comprehensive test data generation capabilities for the extreme testing framework.

## Features

### 1. Synthetic Policy Documents
Generate policy documents with configurable characteristics:
- Customizable page count and word count
- Configurable CSF coverage percentage
- Optional CSF keyword inclusion
- Various structure types (normal, flat, deep, inconsistent)

### 2. Malicious PDF Files
Generate malicious PDFs for security testing:
- **javascript**: PDF with embedded JavaScript
- **malformed**: PDF with missing required elements
- **recursive**: PDF with circular object references
- **large_object**: PDF with extremely large embedded objects (10MB+)

### 3. Gap Policies
Generate policies with intentional gaps at specific CSF subcategories for testing gap detection accuracy.

### 4. Extreme Structures
Generate documents with extreme structural properties:
- **no_headings**: Document with no markdown headings
- **deep_nesting**: Document with 100+ nesting levels
- **inconsistent_hierarchy**: Document with inconsistent heading hierarchy (H1 → H5 → H2)
- **only_tables**: Document containing only markdown tables
- **many_headings**: Document with 1000+ headings
- **many_sections**: Document with 1000+ sections

### 5. Multilingual Documents
Generate documents with diverse character sets:
- **english**: Standard English text
- **chinese**: Chinese characters (安全, 政策, 系统, etc.)
- **arabic**: Arabic text with RTL directionality
- **cyrillic**: Cyrillic characters (безопасность, политика, etc.)
- **emoji**: Emoji characters (🔒, 🔐, 🛡️, etc.)
- **greek**: Greek mathematical symbols (α, β, γ, etc.)

### 6. Caching
Automatically cache generated test data for reuse:
- MD5-based cache keys
- Supports text, binary, and JSON content
- Configurable cache directory

## Usage

### Python API

```python
from tests.extreme.data_generator import TestDataGenerator, DocumentSpec

# Create generator
generator = TestDataGenerator()

# Generate synthetic policy document
spec = DocumentSpec(
    size_pages=10,
    words_per_page=500,
    sections_per_page=3,
    coverage_percentage=0.7,
    include_csf_keywords=True
)
document = generator.generate_policy_document(spec)

# Generate malicious PDF
pdf_content = generator.generate_malicious_pdf("javascript")

# Generate gap policy
gap_policy = generator.generate_gap_policy(["ID.AM-1", "ID.AM-2", "PR.AC-1"])

# Generate extreme structure
extreme_doc = generator.generate_extreme_structure("deep_nesting")

# Generate multilingual document
multilingual_doc = generator.generate_multilingual_document(["english", "chinese", "arabic"])

# Use caching
generator.save_to_cache("my_policy", document)
cached_doc = generator.load_from_cache("my_policy")
```

### Command Line Interface

```bash
# Generate policy document
python3 tests/extreme/data_generator.py \
    --type policy \
    --output test_policy.md \
    --pages 10 \
    --coverage 0.7

# Generate malicious PDF
python3 tests/extreme/data_generator.py \
    --type malicious \
    --output malicious.pdf \
    --attack javascript

# Generate gap policy
python3 tests/extreme/data_generator.py \
    --type gap \
    --output gap_policy.md \
    --gaps "ID.AM-1,ID.AM-2,PR.AC-1"

# Generate extreme structure
python3 tests/extreme/data_generator.py \
    --type structure \
    --output extreme.md \
    --structure deep_nesting

# Generate multilingual document
python3 tests/extreme/data_generator.py \
    --type multilingual \
    --output multilingual.md \
    --languages "english,chinese,arabic,cyrillic"
```

## Requirements Coverage

This implementation satisfies **Requirement 75: Test Data Generation Framework**:

1. ✅ **75.1**: Generate synthetic policy documents with configurable characteristics (size, structure, coverage)
2. ✅ **75.2**: Generate malicious PDF files for security testing
3. ✅ **75.3**: Generate documents with intentional gaps at specific CSF subcategories
4. ✅ **75.4**: Generate documents with extreme structural properties
5. ✅ **75.5**: Generate documents with diverse character sets and encodings
6. ✅ **75.6**: Provide a test data generation CLI for creating custom test cases

## Architecture

The TestDataGenerator class provides:
- **DocumentSpec**: Dataclass for specifying document generation parameters
- **CSF_SUBCATEGORIES**: List of all 49 CSF subcategories for gap generation
- **CSF_KEYWORDS**: Mapping of CSF functions to relevant keywords
- **Caching**: MD5-based caching system for generated test data
- **CLI**: Command-line interface for standalone test data generation

## Testing

The implementation includes comprehensive unit tests in `test_data_generator.py`:
- Policy document generation with various configurations
- All malicious PDF types
- Gap policy generation
- All extreme structure types
- Multilingual document generation
- Caching functionality

All tests pass successfully.

## Future Enhancements

Potential improvements for future iterations:
- Use a proper PDF library (PyPDF2, reportlab) for more realistic malicious PDFs
- Add more sophisticated CSF content generation with actual policy language
- Support for additional attack vectors (XSS, CSRF, etc.)
- More language support for multilingual documents
- Configurable randomness seed for reproducible test data
