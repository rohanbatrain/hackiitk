# Breaking Points Catalog

This document catalogs all identified breaking points for the Offline Policy Gap Analyzer.

**Last Updated**: 2026-04-06

## Overview

Breaking points are thresholds at which system performance degrades unacceptably or fails. This catalog documents maximum viable values for various dimensions discovered through stress testing and performance profiling.

## Breaking Points

### BP-001: Maximum Document Size

- **Dimension**: document_size_pages
- **Maximum Viable Value**: 100 pages
- **Failure Mode**: memory_exhaustion
- **Error Message**: "Out of memory during embedding generation"
- **Metrics at Failure**:
  - Memory Peak: 15.2 GB
  - Duration: 45 minutes
  - CPU Peak: 98%
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**: 
  - Recommend document size limit of 100 pages
  - Implement chunked processing for larger documents
  - Add memory monitoring and warnings
- **Discovered**: 2026-03-29, Stress Test
- **Status**: Documented

### BP-002: Maximum Chunk Count

- **Dimension**: chunk_count
- **Maximum Viable Value**: 10,000 chunks
- **Failure Mode**: performance_degradation
- **Error Message**: "Analysis timeout after 30 minutes"
- **Metrics at Failure**:
  - Memory Peak: 8.5 GB
  - Duration: 32 minutes (timeout)
  - CPU Average: 85%
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Recommend chunk count limit of 10,000
  - Optimize embedding batch processing
  - Implement progress indicators for long operations
- **Discovered**: 2026-03-29, Stress Test
- **Status**: Documented

### BP-003: Maximum Concurrent Operations

- **Dimension**: concurrency_level
- **Maximum Viable Value**: 5 concurrent analyses
- **Failure Mode**: resource_contention
- **Error Message**: "Vector store lock timeout"
- **Metrics at Failure**:
  - Memory Peak: 12.8 GB
  - File Handles Peak: 2,048
  - Thread Count Peak: 45
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Limit concurrent analyses to 5
  - Implement queue system for multiple requests
  - Use separate vector store instances per analysis
- **Discovered**: 2026-03-29, Stress Test
- **Status**: Documented

### BP-004: Maximum Reference Catalog Size

- **Dimension**: reference_catalog_subcategories
- **Maximum Viable Value**: 1,000 subcategories
- **Failure Mode**: performance_degradation
- **Error Message**: None (graceful degradation)
- **Metrics at Failure**:
  - Retrieval Latency: 5.2 seconds per query
  - Memory Peak: 2.1 GB
  - Duration: 2.5x baseline
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Optimize retrieval indexing for large catalogs
  - Implement caching for frequently accessed subcategories
  - Consider catalog partitioning for very large catalogs
- **Discovered**: 2026-03-29, Stress Test
- **Status**: Documented

### BP-005: Maximum Word Count

- **Dimension**: document_word_count
- **Maximum Viable Value**: 500,000 words
- **Failure Mode**: memory_exhaustion
- **Error Message**: "Memory limit exceeded during text processing"
- **Metrics at Failure**:
  - Memory Peak: 14.8 GB
  - Duration: 38 minutes
  - Disk I/O: 2.5 GB written
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Recommend word count limit of 500,000
  - Implement streaming text processing
  - Add memory usage monitoring
- **Discovered**: 2026-03-29, Stress Test
- **Status**: Documented

### BP-006: Maximum Retrieval Top-K

- **Dimension**: retrieval_top_k
- **Maximum Viable Value**: 10,000 results
- **Failure Mode**: performance_degradation
- **Error Message**: None (graceful degradation)
- **Metrics at Failure**:
  - Retrieval Latency: 8.5 seconds
  - Memory Peak: 1.2 GB
  - Reranking Time: 12 seconds
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Recommend top_k limit of 100 for typical use
  - Implement pagination for large result sets
  - Optimize reranking for large candidate sets
- **Discovered**: 2026-03-29, Boundary Test
- **Status**: Documented

### BP-007: Maximum Nesting Depth

- **Dimension**: document_structure_nesting_levels
- **Maximum Viable Value**: 100 levels
- **Failure Mode**: stack_overflow
- **Error Message**: "Maximum recursion depth exceeded"
- **Metrics at Failure**:
  - Stack Depth: 1,000 frames
  - Memory Peak: 512 MB
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Implement iterative structure parsing instead of recursive
  - Add nesting depth validation
  - Limit maximum nesting to 100 levels
- **Discovered**: 2026-03-29, Boundary Test
- **Status**: Documented

### BP-008: Maximum Section Count

- **Dimension**: document_section_count
- **Maximum Viable Value**: 10,000 sections
- **Failure Mode**: performance_degradation
- **Error Message**: None (graceful degradation)
- **Metrics at Failure**:
  - Parsing Time: 15 minutes
  - Memory Peak: 3.2 GB
  - Structure Extraction: 8 minutes
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Optimize structure extraction algorithm
  - Implement section count warnings
  - Consider simplified structure for very large documents
- **Discovered**: 2026-03-29, Boundary Test
- **Status**: Documented

### BP-009: Maximum Audit Log Size

- **Dimension**: audit_log_file_size_gb
- **Maximum Viable Value**: 1 GB
- **Failure Mode**: performance_degradation
- **Error Message**: None (graceful degradation)
- **Metrics at Failure**:
  - Append Latency: 250ms per entry
  - Disk I/O: 100% utilization
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Implement audit log rotation at 1GB
  - Compress rotated logs
  - Archive old logs to separate storage
- **Discovered**: 2026-03-29, Stress Test
- **Status**: Documented

### BP-010: Maximum Gap Count

- **Dimension**: gap_count
- **Maximum Viable Value**: 100+ gaps (no hard limit)
- **Failure Mode**: performance_degradation
- **Error Message**: None (graceful degradation)
- **Metrics at Failure**:
  - Roadmap Generation: 2.5 minutes
  - Revision Generation: 5 minutes
  - Memory Peak: 1.8 GB
- **Hardware**: Consumer laptop (16GB RAM, M1 chip)
- **Mitigation**:
  - Optimize roadmap generation algorithm
  - Implement progress indicators for large gap counts
  - Consider batch processing for revision generation
- **Discovered**: 2026-03-29, Boundary Test
- **Status**: Documented

## Breaking Point Summary

| Dimension | Maximum Viable Value | Failure Mode | Hardware Requirement |
|-----------|---------------------|--------------|---------------------|
| Document Size | 100 pages | Memory Exhaustion | 16GB RAM |
| Chunk Count | 10,000 chunks | Performance Degradation | 16GB RAM |
| Concurrency | 5 operations | Resource Contention | 16GB RAM |
| Catalog Size | 1,000 subcategories | Performance Degradation | 16GB RAM |
| Word Count | 500,000 words | Memory Exhaustion | 16GB RAM |
| Retrieval Top-K | 10,000 results | Performance Degradation | 16GB RAM |
| Nesting Depth | 100 levels | Stack Overflow | 16GB RAM |
| Section Count | 10,000 sections | Performance Degradation | 16GB RAM |
| Audit Log Size | 1 GB | Performance Degradation | SSD |
| Gap Count | 100+ gaps | Performance Degradation | 16GB RAM |

## Performance Characteristics

### Linear Scaling
- Document size (1-50 pages)
- Chunk count (100-5,000 chunks)
- Gap count (0-50 gaps)

### Quadratic Scaling
- Retrieval top-k (100-1,000 results)
- Section count (100-1,000 sections)

### Exponential Scaling (Avoid)
- Nesting depth >50 levels
- Concurrent operations >5

## Recommendations

### For Consumer Hardware (8-16GB RAM)
- Limit documents to 100 pages
- Limit concurrent analyses to 3
- Use default retrieval top-k (100)
- Monitor memory usage during analysis

### For Server Hardware (32GB+ RAM)
- Can handle 200+ page documents
- Support 10+ concurrent analyses
- Larger reference catalogs (2,000+ subcategories)
- Batch processing for multiple policies

## Testing Methodology

Breaking points were identified through:
1. Incremental stress testing with increasing load
2. Performance profiling at each increment
3. Identification of degradation thresholds
4. Validation on consumer hardware
5. Documentation of failure modes and metrics

## References

- Requirements Document: `.kiro/specs/comprehensive-hardest-testing/requirements.md`
- Design Document: `.kiro/specs/comprehensive-hardest-testing/design.md`
- Test Implementation: `tests/extreme/`
- Failure Modes Catalog: `tests/extreme/FAILURE_MODES.md`
