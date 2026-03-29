"""
Property Test 44: Operation Logging

Validates Requirements 15.5, 15.6:
- All major operations are logged with timestamps
- Logs include component name and context
- Logs are written to output directory
"""

import pytest
from hypothesis import given, strategies as st, settings
from pathlib import Path
import tempfile
import logging
from datetime import datetime
import re
import time

from utils.logger import OperationLogger, setup_logging, get_logger


# ============================================================================
# Test Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_logging():
    """Cleanup logging handlers before and after each test."""
    # Cleanup before test
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)
    
    yield
    
    # Cleanup after test
    root_logger = logging.getLogger()
    for handler in root_logger.handlers[:]:
        handler.close()
        root_logger.removeHandler(handler)


# ============================================================================
# Test Strategies
# ============================================================================

@st.composite
def operation_strategy(draw):
    """Generate operation scenarios."""
    component = draw(st.sampled_from([
        'document_parser',
        'embedding_engine',
        'retrieval_engine',
        'llm_runtime',
        'gap_analysis_engine'
    ]))
    
    operation = draw(st.sampled_from([
        'parsing',
        'embedding',
        'retrieval',
        'generation',
        'analysis'
    ]))
    
    status = draw(st.sampled_from(['started', 'completed', 'failed']))
    
    return {
        'component': component,
        'operation': operation,
        'status': status
    }


# ============================================================================
# Property Tests
# ============================================================================

@given(operation=operation_strategy())
@settings(max_examples=50, deadline=5000)
def test_all_operations_logged_with_timestamps(operation):
    """
    Property 44: Operation Logging
    
    Test that all major operations:
    1. Are logged with timestamps
    2. Include component name
    3. Include operation context
    4. Are written to log file
    """
    component = operation['component']
    op_name = operation['operation']
    status = operation['status']
    
    # Create temporary output directory
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        
        # Setup logging
        logger = OperationLogger(
            output_dir=output_dir,
            log_level='INFO',
            console_output=False
        )
        
        # Log operation
        context = {'test_key': 'test_value', 'status': status}
        
        if status == 'started':
            logger.log_operation_start(component, op_name, context)
        elif status == 'completed':
            logger.log_operation_complete(component, op_name, duration_seconds=1.5, context=context)
        elif status == 'failed':
            error = Exception(f"Test error in {op_name}")
            logger.log_operation_error(component, op_name, error, context)
        
        # Close logger to flush
        logger.close()
        
        # Find log file
        log_files = list(output_dir.glob('analysis_*.log'))
        assert len(log_files) > 0, "Log file should be created"
        
        log_file = log_files[0]
        log_content = log_file.read_text()
        
        # Verify timestamp format: [YYYY-MM-DD HH:MM:SS.mmm]
        timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]'
        assert re.search(timestamp_pattern, log_content), \
            "Log should contain timestamp in correct format"
        
        # Verify component name is included
        assert component in log_content, \
            f"Log should contain component name: {component}"
        
        # Verify operation name is included
        assert op_name in log_content, \
            f"Log should contain operation name: {op_name}"
        
        # Verify log level is included
        if status == 'failed':
            assert 'ERROR' in log_content, "Failed operations should log as ERROR"
        else:
            assert 'INFO' in log_content, "Operations should log as INFO"


def test_parsing_operation_logging():
    """
    Test that parsing operations are logged with all required details.
    
    Verifies Requirements 15.5, 15.6 for parsing operations.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        logger = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        
        # Log parsing operations
        logger.log_parsing('test_policy.pdf', 'pdf', 'started')
        logger.log_parsing('test_policy.pdf', 'pdf', 'completed', page_count=25)
        logger.log_parsing('bad_policy.pdf', 'pdf', 'failed', error='Corrupted file')
        
        logger.close()
        
        # Read log file
        log_files = list(output_dir.glob('analysis_*.log'))
        assert len(log_files) == 1
        
        log_content = log_files[0].read_text()
        
        # Verify all parsing operations logged
        assert 'Parsing document: test_policy.pdf' in log_content
        assert 'Parsed 25 pages' in log_content
        assert 'Failed to parse bad_policy.pdf' in log_content
        assert 'Corrupted file' in log_content
        
        # Verify timestamps present
        timestamp_pattern = r'\[\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3}\]'
        timestamps = re.findall(timestamp_pattern, log_content)
        assert len(timestamps) >= 3, "Should have timestamps for all log entries"


def test_embedding_operation_logging():
    """
    Test that embedding operations are logged with performance metrics.
    
    Verifies Requirements 15.5, 15.6 for embedding operations.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        logger = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        
        # Log embedding operations
        logger.log_embedding('started', chunk_count=100)
        logger.log_embedding('completed', chunk_count=100, duration_seconds=2.5)
        logger.log_embedding('failed', chunk_count=50, error='Model not loaded')
        
        logger.close()
        
        # Read log file
        log_files = list(output_dir.glob('analysis_*.log'))
        log_content = log_files[0].read_text()
        
        # Verify embedding operations logged
        assert 'Generating embeddings for 100 chunks' in log_content
        assert 'Generated 100 embeddings' in log_content
        assert '2.5' in log_content  # Duration
        assert 'chunks/sec' in log_content  # Rate calculation
        assert 'Failed to generate embeddings' in log_content
        assert 'Model not loaded' in log_content


def test_retrieval_operation_logging():
    """
    Test that retrieval operations are logged with query context.
    
    Verifies Requirements 15.5, 15.6 for retrieval operations.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        logger = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        
        # Log retrieval operations
        query = "risk management policy requirements"
        logger.log_retrieval(query, 'started')
        logger.log_retrieval(query, 'completed', result_count=5, retrieval_method='hybrid')
        logger.log_retrieval(query, 'failed', error='Vector store unavailable')
        
        logger.close()
        
        # Read log file
        log_files = list(output_dir.glob('analysis_*.log'))
        log_content = log_files[0].read_text()
        
        # Verify retrieval operations logged
        assert 'Retrieving results for query' in log_content
        assert 'risk management' in log_content
        assert 'Retrieved 5 results' in log_content
        assert 'hybrid' in log_content
        assert 'Failed to retrieve results' in log_content
        assert 'Vector store unavailable' in log_content


def test_generation_operation_logging():
    """
    Test that LLM generation operations are logged with performance metrics.
    
    Verifies Requirements 15.5, 15.6 for generation operations.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        logger = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        
        # Log generation operations
        logger.log_generation('gap_analysis', 'started')
        logger.log_generation('gap_analysis', 'completed', token_count=512, duration_seconds=25.6)
        logger.log_generation('policy_revision', 'failed', error='Context too long')
        
        logger.close()
        
        # Read log file
        log_files = list(output_dir.glob('analysis_*.log'))
        log_content = log_files[0].read_text()
        
        # Verify generation operations logged
        assert 'Starting LLM generation: gap_analysis' in log_content
        assert 'Generated 512 tokens' in log_content
        assert '25.6' in log_content  # Duration
        assert 'tokens/sec' in log_content  # Rate calculation
        assert 'Failed LLM generation for policy_revision' in log_content
        assert 'Context too long' in log_content


def test_analysis_stage_logging():
    """
    Test that gap analysis stages are logged with results.
    
    Verifies Requirements 15.5, 15.6 for analysis operations.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        logger = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        
        # Log analysis stages
        logger.log_analysis_stage('stage_a', 'started', subcategory_count=49)
        logger.log_analysis_stage('stage_a', 'completed', subcategory_count=49, gap_count=12)
        logger.log_analysis_stage('stage_b', 'started', subcategory_count=12)
        logger.log_analysis_stage('stage_b', 'completed', subcategory_count=12, gap_count=8)
        
        logger.close()
        
        # Read log file
        log_files = list(output_dir.glob('analysis_*.log'))
        log_content = log_files[0].read_text()
        
        # Verify analysis stages logged
        assert 'Starting stage_a analysis for 49 subcategories' in log_content
        assert 'Completed stage_a analysis: 12 gaps identified' in log_content
        assert 'Starting stage_b analysis for 12 subcategories' in log_content
        assert 'Completed stage_b analysis: 8 gaps identified' in log_content


@given(
    log_level=st.sampled_from(['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']),
    console_output=st.booleans()
)
@settings(max_examples=20)
def test_logging_configuration_options(log_level, console_output):
    """
    Property: Logging configuration options work correctly.
    
    Verifies that different log levels and output options are respected.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        
        logger = OperationLogger(
            output_dir=output_dir,
            log_level=log_level,
            console_output=console_output
        )
        
        # Log at different levels
        component_logger = logger.get_logger('test_component')
        component_logger.debug('Debug message')
        component_logger.info('Info message')
        component_logger.warning('Warning message')
        component_logger.error('Error message')
        component_logger.critical('Critical message')
        
        logger.close()
        
        # Verify log file created
        log_files = list(output_dir.glob('analysis_*.log'))
        assert len(log_files) == 1, "Log file should be created"
        
        log_content = log_files[0].read_text()
        
        # Verify log level filtering
        level_hierarchy = ['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
        min_level_index = level_hierarchy.index(log_level)
        
        for i, level in enumerate(level_hierarchy):
            message = f'{level.capitalize()} message'
            if i >= min_level_index:
                # Should be logged
                assert message in log_content, \
                    f"{level} message should be logged with log_level={log_level}"
            else:
                # Should not be logged
                assert message not in log_content, \
                    f"{level} message should not be logged with log_level={log_level}"


def test_timestamp_ordering():
    """
    Test that log entries maintain chronological order.
    
    Verifies that timestamps increase monotonically.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        logger = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        
        # Log multiple operations with small delays
        for i in range(5):
            logger.log_operation_start('test_component', f'operation_{i}')
            time.sleep(0.01)  # Small delay to ensure different timestamps
        
        logger.close()
        
        # Read log file
        log_files = list(output_dir.glob('analysis_*.log'))
        log_content = log_files[0].read_text()
        
        # Extract timestamps
        timestamp_pattern = r'\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}\.\d{3})\]'
        timestamps = re.findall(timestamp_pattern, log_content)
        
        assert len(timestamps) >= 5, "Should have at least 5 timestamps"
        
        # Verify chronological order
        for i in range(len(timestamps) - 1):
            t1 = datetime.strptime(timestamps[i], '%Y-%m-%d %H:%M:%S.%f')
            t2 = datetime.strptime(timestamps[i + 1], '%Y-%m-%d %H:%M:%S.%f')
            assert t1 <= t2, "Timestamps should be in chronological order"


def test_component_name_in_logs():
    """
    Test that component names are included in all log entries.
    
    Verifies Requirement 15.6 for component context.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        logger = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        
        components = [
            'document_parser',
            'embedding_engine',
            'retrieval_engine',
            'llm_runtime',
            'gap_analysis_engine'
        ]
        
        # Log from each component
        for component in components:
            logger.log_operation_start(component, f'test_operation')
        
        logger.close()
        
        # Read log file
        log_files = list(output_dir.glob('analysis_*.log'))
        log_content = log_files[0].read_text()
        
        # Verify all component names present
        for component in components:
            assert component in log_content, \
                f"Component name '{component}' should be in logs"


def test_log_file_naming_convention():
    """
    Test that log files follow naming convention with timestamp.
    
    Verifies that log files are uniquely named with timestamps.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        
        # Create multiple loggers
        logger1 = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        logger1.log_operation_start('test', 'op1')
        logger1.close()
        
        time.sleep(1.1)  # Ensure different timestamp
        
        logger2 = OperationLogger(output_dir=output_dir, log_level='INFO', console_output=False)
        logger2.log_operation_start('test', 'op2')
        logger2.close()
        
        # Verify log files
        log_files = list(output_dir.glob('analysis_*.log'))
        assert len(log_files) == 2, "Should have 2 separate log files"
        
        # Verify naming pattern: analysis_YYYYMMDD_HHMMSS.log
        for log_file in log_files:
            assert log_file.name.startswith('analysis_'), \
                "Log file should start with 'analysis_'"
            assert log_file.name.endswith('.log'), \
                "Log file should end with '.log'"
            
            # Extract timestamp part
            timestamp_part = log_file.stem.replace('analysis_', '')
            assert len(timestamp_part) == 15, \
                "Timestamp should be in format YYYYMMDD_HHMMSS"


def test_global_logger_setup():
    """
    Test that global logger setup works correctly.
    
    Verifies that setup_logging and get_logger functions work.
    """
    with tempfile.TemporaryDirectory() as tmp_dir:
        output_dir = Path(tmp_dir)
        
        # Setup global logger
        global_logger = setup_logging(output_dir=output_dir, log_level='INFO')
        
        # Get component logger
        component_logger = get_logger('test_component')
        component_logger.info('Test message from global logger')
        
        global_logger.close()
        
        # Verify log file created
        log_files = list(output_dir.glob('analysis_*.log'))
        assert len(log_files) == 1
        
        log_content = log_files[0].read_text()
        assert 'Test message from global logger' in log_content
        assert 'test_component' in log_content


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
