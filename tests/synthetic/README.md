# Synthetic Test Documents

This directory contains synthetically generated test documents for stress testing and boundary testing of the Offline Policy Gap Analyzer.

## Purpose

Synthetic test documents provide controlled test cases with known characteristics for:
- Stress testing (1-100 pages)
- Extreme structural testing
- Multilingual testing (10+ languages)
- Intentional gap testing
- Performance profiling

## Document Categories

### 1. Stress Testing Documents (1-100 pages)
Documents of varying sizes for performance profiling and stress testing.
- **Files**: `stress_001_1page.md` through `stress_100_100pages.md`
- **Purpose**: Measure performance degradation with increasing document size
- **Characteristics**: Realistic policy content with varying CSF coverage

### 2. Extreme Structure Documents
Documents with unusual or extreme structural properties.
- **Files**: `structure_001_no_headings.md` through `structure_010_many_sections.md`
- **Purpose**: Validate parser robustness with edge case structures
- **Types**:
  - No headings (flat text)
  - Deep nesting (100+ levels)
  - Inconsistent hierarchy (H1 → H5 → H2)
  - Only tables (no prose)
  - Many headings (1000+)
  - Many sections (1000+)
  - Single continuous paragraph
  - Alternating tiny/huge paragraphs

### 3. Multilingual Documents (10+ languages)
Documents with diverse character sets and encodings.
- **Files**: `multilingual_001_chinese.md` through `multilingual_015_mixed.md`
- **Purpose**: Validate international document support
- **Languages**:
  - Chinese (Simplified and Traditional)
  - Arabic (RTL text)
  - Cyrillic (Russian)
  - Japanese (Hiragana, Katakana, Kanji)
  - Korean (Hangul)
  - Greek (mathematical symbols)
  - Hebrew (RTL text)
  - Thai
  - Hindi (Devanagari)
  - Emoji and special Unicode
  - Mixed multilingual

### 4. Intentional Gap Documents
Documents with specific CSF subcategories intentionally omitted.
- **Files**: `gap_001_zero_gaps.md` through `gap_050_all_gaps.md`
- **Purpose**: Validate gap detection accuracy with known gaps
- **Characteristics**:
  - Zero gaps (complete coverage)
  - Specific gaps (e.g., only ID.AM gaps)
  - Partial coverage (25 subcategories)
  - All gaps (zero coverage)
  - Boundary cases (exact threshold scores)

### 5. Performance Profiling Documents
Documents optimized for performance measurement.
- **Files**: `perf_001_baseline.md` through `perf_020_extreme.md`
- **Purpose**: Establish performance baselines and identify bottlenecks
- **Characteristics**:
  - Baseline (10 pages, 50% coverage)
  - Chunk-heavy (10,000+ chunks)
  - Keyword-dense (maximum CSF keywords)
  - Sparse (minimal CSF keywords)
  - Extreme size (100 pages, 500k words)

## Document Specifications

### Stress Testing Documents
| File | Pages | Words | Sections | Coverage | Purpose |
|------|-------|-------|----------|----------|---------|
| stress_001_1page.md | 1 | 500 | 3 | 50% | Minimum viable document |
| stress_010_10pages.md | 10 | 5,000 | 30 | 50% | Baseline document |
| stress_050_50pages.md | 50 | 25,000 | 150 | 50% | Medium document |
| stress_100_100pages.md | 100 | 50,000 | 300 | 50% | Maximum document |

### Extreme Structure Documents
| File | Structure Type | Description |
|------|----------------|-------------|
| structure_001_no_headings.md | No headings | Flat text with no section markers |
| structure_002_deep_nesting.md | Deep nesting | 100+ heading levels |
| structure_003_inconsistent.md | Inconsistent | H1 → H5 → H2 hierarchy |
| structure_004_only_tables.md | Only tables | No prose text, only tables |
| structure_005_many_headings.md | Many headings | 1000+ headings |
| structure_006_many_sections.md | Many sections | 1000+ sections |
| structure_007_single_paragraph.md | Single paragraph | No paragraph breaks |
| structure_008_alternating.md | Alternating | 1-word and 10k-word paragraphs |

### Multilingual Documents
| File | Language | Script | Purpose |
|------|----------|--------|---------|
| multilingual_001_chinese.md | Chinese | Simplified Chinese | CJK character handling |
| multilingual_002_arabic.md | Arabic | Arabic script | RTL text handling |
| multilingual_003_cyrillic.md | Cyrillic | Cyrillic script | Non-Latin alphabet |
| multilingual_004_japanese.md | Japanese | Hiragana/Katakana/Kanji | Mixed scripts |
| multilingual_005_korean.md | Korean | Hangul | Korean characters |
| multilingual_006_greek.md | Greek | Greek alphabet | Mathematical symbols |
| multilingual_007_hebrew.md | Hebrew | Hebrew script | RTL text |
| multilingual_008_thai.md | Thai | Thai script | Complex diacritics |
| multilingual_009_hindi.md | Hindi | Devanagari | Indic script |
| multilingual_010_emoji.md | Emoji | Unicode emoji | Special characters |
| multilingual_011_mixed.md | Mixed | Multiple scripts | Multilingual document |

### Intentional Gap Documents
| File | Gap Count | Coverage | Purpose |
|------|-----------|----------|---------|
| gap_001_zero_gaps.md | 0 | 100% | Complete coverage validation |
| gap_025_half_gaps.md | 25 | 50% | Partial coverage validation |
| gap_049_all_gaps.md | 49 | 0% | Zero coverage validation |
| gap_boundary_covered.md | Varies | Exact 0.8 | Boundary threshold testing |
| gap_boundary_partial.md | Varies | Exact 0.5 | Boundary threshold testing |
| gap_boundary_ambiguous.md | Varies | Exact 0.3 | Boundary threshold testing |

## Generation

Synthetic documents are generated using the `TestDataGenerator` class from `tests/extreme/data_generator.py`.

### Generate Custom Documents

```bash
# Generate a 50-page policy with 70% coverage
python tests/extreme/data_generator.py --type policy --output tests/synthetic/custom.md --pages 50 --coverage 0.7

# Generate a document with specific gaps
python tests/extreme/data_generator.py --type gap --output tests/synthetic/custom_gaps.md --gaps "ID.AM-1,ID.AM-2,PR.AC-1"

# Generate an extreme structure document
python tests/extreme/data_generator.py --type structure --output tests/synthetic/custom_structure.md --structure deep_nesting

# Generate a multilingual document
python tests/extreme/data_generator.py --type multilingual --output tests/synthetic/custom_multilingual.md --languages "chinese,arabic,emoji"
```

### Batch Generation

Use the provided script to generate all synthetic documents:

```bash
python tests/synthetic/generate_synthetic_documents.py
```

This will create:
- 20 stress testing documents (1, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100 pages)
- 10 extreme structure documents
- 15 multilingual documents
- 50 intentional gap documents
- 20 performance profiling documents

Total: 115+ synthetic documents

## Caching

Generated documents are cached in `test_outputs/test_data/` to avoid regeneration. To regenerate:

```bash
# Clear cache
rm -rf test_outputs/test_data/

# Regenerate all documents
python tests/synthetic/generate_synthetic_documents.py
```

## Requirements

Synthetic document generation addresses:
- Requirement 75.1: Generate documents for stress testing (1-100 pages)
- Requirement 75.3: Generate documents with extreme structures
- Requirement 75.4: Generate multilingual documents (10+ languages)
- Requirement 75.5: Generate documents with intentional gaps
- Requirement 75.6: Cache generated documents for reuse

## Validation

Synthetic documents are validated to ensure:
- Correct size (page count, word count)
- Correct structure (heading hierarchy, section count)
- Correct coverage (expected gaps match actual gaps)
- Correct encoding (no mojibake, proper character rendering)
- Parseable by document parser

## Maintenance

Update synthetic documents when:
- Reference catalog is updated
- New CSF subcategories are added
- New languages need to be tested
- New structural edge cases are discovered
- Performance baselines need to be refreshed

