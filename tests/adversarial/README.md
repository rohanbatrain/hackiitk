# Adversarial Test Samples

This directory contains malicious PDF samples for security testing of the Offline Policy Gap Analyzer.

## Purpose

Adversarial test samples validate that the system properly handles malicious inputs and security attacks. These samples test:
- Input sanitization
- PDF parsing robustness
- Security boundary enforcement
- Graceful error handling

## Attack Types

### 1. Embedded JavaScript (JS)
PDFs containing embedded JavaScript that attempts to execute code when opened.
- **Files**: `malicious_001_javascript.pdf` through `malicious_005_javascript.pdf`
- **Attack Vector**: JavaScript execution in PDF viewer
- **Expected Behavior**: Document parser should reject or sanitize JavaScript content

### 2. Malformed Structure
PDFs with intentionally corrupted or invalid structure.
- **Files**: `malicious_006_malformed.pdf` through `malicious_010_malformed.pdf`
- **Attack Vector**: Parser crashes or undefined behavior
- **Expected Behavior**: Parser should detect malformation and return descriptive error

### 3. Recursive References
PDFs with circular object references that could cause infinite loops.
- **Files**: `malicious_011_recursive.pdf` through `malicious_015_recursive.pdf`
- **Attack Vector**: Infinite loop or stack overflow
- **Expected Behavior**: Parser should detect recursion and prevent infinite loops

### 4. Large Embedded Objects
PDFs with extremely large embedded objects (10MB+ streams).
- **Files**: `malicious_016_large_object.pdf` through `malicious_020_large_object.pdf`
- **Attack Vector**: Memory exhaustion
- **Expected Behavior**: Parser should enforce memory limits and reject oversized objects

### 5. Mixed Attack Vectors
PDFs combining multiple attack types.
- **Files**: `malicious_021_mixed.pdf` through `malicious_024_mixed.pdf`
- **Attack Vector**: Multiple simultaneous attacks
- **Expected Behavior**: Parser should handle all attack vectors gracefully

## Sample Metadata

Each malicious sample is documented with:
- **Attack Type**: Primary attack vector
- **Severity**: Low, Medium, High, Critical
- **Source**: Where the attack pattern was sourced from
- **CVE References**: Related CVE identifiers if applicable
- **Expected Behavior**: How the system should handle this sample

## Testing Guidelines

When testing with adversarial samples:

1. **Isolation**: Run tests in isolated environment
2. **Monitoring**: Monitor for crashes, hangs, or resource exhaustion
3. **Validation**: Verify error messages are descriptive and actionable
4. **Cleanup**: Ensure no partial artifacts remain after failures
5. **Logging**: Verify all security events are logged

## Requirements

Adversarial testing addresses:
- Requirement 8.1: Test with embedded JavaScript PDFs
- Requirement 8.2: Test with malformed structure PDFs
- Requirement 8.3: Test with recursive reference PDFs
- Requirement 8.4: Test with large embedded object PDFs
- Requirement 8.5: Test with 20+ malicious PDF samples

## Maintenance

Update adversarial samples when:
- New attack vectors are discovered
- Security vulnerabilities are reported
- PDF parsing library is updated
- New security research is published

## Safety Notice

⚠️ **WARNING**: These files contain intentionally malicious content. Do not open them with standard PDF viewers. Use only for automated testing in isolated environments.

## Sample Inventory

| File | Attack Type | Severity | Description |
|------|-------------|----------|-------------|
| malicious_001_javascript.pdf | JavaScript | High | Basic JavaScript alert |
| malicious_002_javascript.pdf | JavaScript | High | JavaScript with app.launchURL |
| malicious_003_javascript.pdf | JavaScript | Critical | JavaScript with file system access |
| malicious_004_javascript.pdf | JavaScript | High | JavaScript with network access |
| malicious_005_javascript.pdf | JavaScript | Medium | Obfuscated JavaScript |
| malicious_006_malformed.pdf | Malformed | Medium | Missing required objects |
| malicious_007_malformed.pdf | Malformed | Medium | Invalid xref table |
| malicious_008_malformed.pdf | Malformed | High | Corrupted stream data |
| malicious_009_malformed.pdf | Malformed | Medium | Invalid PDF header |
| malicious_010_malformed.pdf | Malformed | High | Truncated file |
| malicious_011_recursive.pdf | Recursive | High | Self-referencing catalog |
| malicious_012_recursive.pdf | Recursive | High | Circular page tree |
| malicious_013_recursive.pdf | Recursive | Critical | Deep recursion (1000+ levels) |
| malicious_014_recursive.pdf | Recursive | High | Mutual object references |
| malicious_015_recursive.pdf | Recursive | Medium | Indirect recursion |
| malicious_016_large_object.pdf | Large Object | High | 10MB embedded stream |
| malicious_017_large_object.pdf | Large Object | Critical | 100MB embedded image |
| malicious_018_large_object.pdf | Large Object | High | 50MB compressed stream |
| malicious_019_large_object.pdf | Large Object | Medium | Multiple 5MB objects |
| malicious_020_large_object.pdf | Large Object | High | 20MB font data |
| malicious_021_mixed.pdf | Mixed | Critical | JavaScript + Recursion |
| malicious_022_mixed.pdf | Mixed | Critical | Malformed + Large Object |
| malicious_023_mixed.pdf | Mixed | Critical | JavaScript + Large Object |
| malicious_024_mixed.pdf | Mixed | Critical | All attack vectors combined |

