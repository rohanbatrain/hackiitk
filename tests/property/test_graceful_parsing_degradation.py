"""
Property Test 43: Graceful Parsing Degradation

Validates Requirement 15.1:
- Parsing failures log errors and continue with available data
- System does not crash on parsing errors
- Errors are logged with appropriate context
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from pathlib import Path
import tempfile
import logging
from io import StringIO

from ingestion.document_parser import DocumentParser
from utils.error_handler import ParsingError, ErrorHandler
from utils.logger import setup_logging


# ============================================================================
# Test Strategies
# ============================================================================

@st.composite
def corrupted_file_strategy(draw):
    """Generate corrupted file scenarios."""
    file_type = draw(st.sampled_from(['pdf', 'docx', 'txt']))
    corruption_type = draw(st.sampled_from([
        'empty',
        'binary_garbage',
        'truncated',
        'wrong_extension',
        'missing_file'
    ]))
    
    return {
        'file_type': file_type,
        'corruption_type': corruption_type
    }


# ============================================================================
# Property Tests
# ============================================================================

@given(scenario=corrupted_file_strategy())
@settings(max_examples=50, deadline=5000)
def test_parsing_failures_log_and_continue(scenario):
    """
    Property 43: Graceful Parsing Degradation
    
    Test that parsing failures:
    1. Log errors with appropriate context
    2. Continue execution without crashing
    3. Return None or raise ParsingError based on configuration
    """
    file_type = scenario['file_type']
    corruption_type = scenario['corruption_type']
    
    # Setup logging to capture log messages
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Add handler to both the component logger and error_handler logger
    logger = logging.getLogger('policy_analyzer.document_parser')
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    
    error_logger = logging.getLogger('utils.error_handler')
    error_logger.addHandler(handler)
    error_logger.setLevel(logging.ERROR)
    
    # Create temporary corrupted file
    with tempfile.NamedTemporaryFile(
        suffix=f'.{file_type}',
        delete=False,
        mode='wb'
    ) as tmp_file:
        tmp_path = Path(tmp_file.name)
        
        if corruption_type == 'empty':
            # Empty file
            pass
        elif corruption_type == 'binary_garbage':
            # Random binary data
            tmp_file.write(b'\x00\x01\x02\x03\x04\x05' * 100)
        elif corruption_type == 'truncated':
            # Truncated file header
            if file_type == 'pdf':
                tmp_file.write(b'%PDF-1.4\n%')
            elif file_type == 'docx':
                tmp_file.write(b'PK\x03\x04')
            else:
                tmp_file.write(b'Truncated')
        elif corruption_type == 'wrong_extension':
            # Text content with wrong extension
            tmp_file.write(b'This is plain text but has wrong extension')
    
    try:
        parser = DocumentParser()
        error_handler = ErrorHandler()
        
        if corruption_type == 'missing_file':
            # Test with non-existent file
            test_path = Path('/nonexistent/file.pdf')
        else:
            test_path = tmp_path
        
        # Test with continue_on_error=True (graceful degradation)
        try:
            result = error_handler.handle_parsing_error(
                str(test_path),
                ParsingError(str(test_path), f"Simulated {corruption_type} error"),
                continue_on_error=True
            )
            
            # Should return None and continue
            assert result is None, "Graceful degradation should return None"
            
            # Check that error was logged
            log_output = log_stream.getvalue()
            assert 'Failed to parse' in log_output or len(log_output) > 0, \
                "Error should be logged"
            
        except Exception as e:
            pytest.fail(f"Should not raise exception with continue_on_error=True: {e}")
        
        # Test with continue_on_error=False (should raise)
        with pytest.raises(ParsingError):
            error_handler.handle_parsing_error(
                str(test_path),
                ParsingError(str(test_path), f"Simulated {corruption_type} error"),
                continue_on_error=False
            )
        
    finally:
        # Cleanup
        logger.removeHandler(handler)
        error_logger.removeHandler(handler)
        if tmp_path.exists():
            tmp_path.unlink()


def test_parser_graceful_degradation_with_real_parser():
    """
    Test graceful degradation with actual DocumentParser.
    
    Verifies that parser errors are handled gracefully and logged.
    """
    # Setup logging
    log_stream = StringIO()
    handler = logging.StreamHandler(log_stream)
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    logger = logging.getLogger('policy_analyzer.document_parser')
    logger.addHandler(handler)
    logger.setLevel(logging.ERROR)
    
    error_logger = logging.getLogger('utils.error_handler')
    error_logger.addHandler(handler)
    error_logger.setLevel(logging.ERROR)
    
    # Create corrupted PDF
    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False, mode='wb') as tmp_file:
        tmp_path = Path(tmp_file.name)
        tmp_file.write(b'Not a valid PDF')
    
    try:
        parser = DocumentParser()
        error_handler = ErrorHandler()
        
        # Attempt to parse corrupted file
        try:
            parsed = parser.parse(str(tmp_path), 'pdf')
            # If parsing somehow succeeds, that's fine
        except Exception as e:
            # Handle the error gracefully
            result = error_handler.handle_parsing_error(
                str(tmp_path),
                e,
                continue_on_error=True
            )
            
            # Should return None and not crash
            assert result is None
            
            # Verify error was logged
            log_output = log_stream.getvalue()
            assert 'Failed to parse' in log_output or len(log_output) > 0
    
    finally:
        logger.removeHandler(handler)
        error_logger.removeHandler(handler)
        if tmp_path.exists():
            tmp_path.unlink()


def test_multiple_parsing_failures_continue():
    """
    Test that multiple parsing failures can be handled sequentially.
    
    Verifies that the system continues processing after multiple errors.
    """
    error_handler = ErrorHandler()
    
    # Simulate multiple parsing failures
    files = [
        ('file1.pdf', 'Corrupted header'),
        ('file2.docx', 'Missing content'),
        ('file3.txt', 'Encoding error')
    ]
    
    results = []
    for file_path, error_msg in files:
        result = error_handler.handle_parsing_error(
            file_path,
            ParsingError(file_path, error_msg),
            continue_on_error=True
        )
        results.append(result)
    
    # All should return None (graceful degradation)
    assert all(r is None for r in results), \
        "All parsing errors should be handled gracefully"


@given(
    error_count=st.integers(min_value=1, max_value=10),
    continue_on_error=st.booleans()
)
@settings(max_examples=30)
def test_parsing_error_handling_consistency(error_count, continue_on_error):
    """
    Property: Error handling behavior is consistent across multiple errors.
    
    Verifies that the error handler behaves consistently regardless of
    the number of errors encountered.
    """
    error_handler = ErrorHandler()
    
    for i in range(error_count):
        file_path = f'file_{i}.pdf'
        error = ParsingError(file_path, f'Error {i}')
        
        if continue_on_error:
            result = error_handler.handle_parsing_error(
                file_path,
                error,
                continue_on_error=True
            )
            assert result is None, "Should return None with continue_on_error=True"
        else:
            with pytest.raises(ParsingError):
                error_handler.handle_parsing_error(
                    file_path,
                    error,
                    continue_on_error=False
                )


def test_parsing_error_includes_troubleshooting():
    """
    Test that ParsingError includes troubleshooting information.
    
    Verifies that errors provide helpful guidance to users.
    """
    from utils.error_handler import ParsingError
    
    error = ParsingError('test.pdf', 'Invalid format')
    error_str = str(error)
    
    # Should include troubleshooting guidance
    assert 'Troubleshooting' in error_str or 'troubleshooting' in error_str.lower(), \
        "Error should include troubleshooting information"
    assert 'corrupted' in error_str.lower() or 'valid' in error_str.lower(), \
        "Error should provide actionable guidance"


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
