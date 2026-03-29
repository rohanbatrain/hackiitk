"""
Operation logging for the Offline Policy Gap Analyzer.

This module provides structured logging with timestamps, severity levels,
and component context for all major operations.
"""

import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime
import json


# ============================================================================
# Log Levels and Configuration
# ============================================================================

LOG_LEVELS = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO,
    'WARNING': logging.WARNING,
    'ERROR': logging.ERROR,
    'CRITICAL': logging.CRITICAL
}


# ============================================================================
# Custom Formatter with Component Context
# ============================================================================

class ComponentFormatter(logging.Formatter):
    """Custom formatter that includes component name and context."""
    
    def __init__(self, include_component: bool = True):
        """
        Initialize formatter.
        
        Args:
            include_component: Whether to include component name in output
        """
        self.include_component = include_component
        super().__init__()
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Format log record with timestamp, level, component, and message.
        
        Args:
            record: Log record to format
        
        Returns:
            Formatted log string
        """
        timestamp = datetime.fromtimestamp(record.created).strftime('%Y-%m-%d %H:%M:%S.%f')[:-3]
        level = record.levelname
        
        # Extract component name from logger name
        component = record.name.split('.')[-1] if '.' in record.name else record.name
        
        # Get context if available
        context = getattr(record, 'context', None)
        
        if self.include_component:
            if context:
                return f"[{timestamp}] {level:8s} [{component:20s}] {record.getMessage()} | {context}"
            else:
                return f"[{timestamp}] {level:8s} [{component:20s}] {record.getMessage()}"
        else:
            if context:
                return f"[{timestamp}] {level:8s} {record.getMessage()} | {context}"
            else:
                return f"[{timestamp}] {level:8s} {record.getMessage()}"


# ============================================================================
# Structured Logger
# ============================================================================

class OperationLogger:
    """
    Structured logger for Policy Analyzer operations.
    
    Logs all major operations with timestamps, component context,
    and writes to both console and file.
    """
    
    def __init__(
        self,
        output_dir: Optional[Path] = None,
        log_level: str = 'INFO',
        console_output: bool = True
    ):
        """
        Initialize operation logger.
        
        Args:
            output_dir: Directory for log files (None for console only)
            log_level: Minimum log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
            console_output: Whether to output to console
        """
        self.output_dir = output_dir
        self.log_level = LOG_LEVELS.get(log_level.upper(), logging.INFO)
        self.console_output = console_output
        self.log_file = None
        
        # Create output directory if specified
        if self.output_dir:
            self.output_dir.mkdir(parents=True, exist_ok=True)
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            self.log_file = self.output_dir / f"analysis_{timestamp}.log"
        
        # Configure root logger
        self._configure_logging()
    
    def _configure_logging(self) -> None:
        """Configure logging handlers and formatters."""
        root_logger = logging.getLogger()
        root_logger.setLevel(self.log_level)
        
        # Remove existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = ComponentFormatter(include_component=True)
        
        # Console handler
        if self.console_output:
            console_handler = logging.StreamHandler(sys.stdout)
            console_handler.setLevel(self.log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # File handler
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file, mode='a', encoding='utf-8')
            file_handler.setLevel(self.log_level)
            file_handler.setFormatter(formatter)
            root_logger.addHandler(file_handler)
    
    def get_logger(self, component_name: str) -> logging.Logger:
        """
        Get logger for specific component.
        
        Args:
            component_name: Name of component (e.g., 'document_parser', 'embedding_engine')
        
        Returns:
            Logger instance for component
        """
        return logging.getLogger(f"policy_analyzer.{component_name}")
    
    def log_operation_start(
        self,
        component: str,
        operation: str,
        context: Optional[dict] = None
    ) -> None:
        """
        Log the start of a major operation.
        
        Args:
            component: Component name
            operation: Operation description
            context: Optional context dictionary
        """
        logger = self.get_logger(component)
        context_str = json.dumps(context) if context else ""
        logger.info(f"Starting: {operation}", extra={'context': context_str})
    
    def log_operation_complete(
        self,
        component: str,
        operation: str,
        duration_seconds: Optional[float] = None,
        context: Optional[dict] = None
    ) -> None:
        """
        Log the completion of a major operation.
        
        Args:
            component: Component name
            operation: Operation description
            duration_seconds: Optional operation duration
            context: Optional context dictionary
        """
        logger = self.get_logger(component)
        
        if duration_seconds is not None:
            message = f"Completed: {operation} (duration: {duration_seconds:.2f}s)"
        else:
            message = f"Completed: {operation}"
        
        context_str = json.dumps(context) if context else ""
        logger.info(message, extra={'context': context_str})
    
    def log_operation_error(
        self,
        component: str,
        operation: str,
        error: Exception,
        context: Optional[dict] = None
    ) -> None:
        """
        Log an operation error.
        
        Args:
            component: Component name
            operation: Operation description
            error: Exception that occurred
            context: Optional context dictionary
        """
        logger = self.get_logger(component)
        context_str = json.dumps(context) if context else ""
        logger.error(
            f"Error in {operation}: {type(error).__name__}: {error}",
            extra={'context': context_str},
            exc_info=True
        )
    
    def log_parsing(
        self,
        file_path: str,
        file_type: str,
        status: str,
        page_count: Optional[int] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log document parsing operation.
        
        Args:
            file_path: Path to document
            file_type: Document type (pdf, docx, txt)
            status: Status (started, completed, failed)
            page_count: Number of pages parsed
            error: Error message if failed
        """
        logger = self.get_logger('document_parser')
        
        context = {
            'file_path': file_path,
            'file_type': file_type,
            'page_count': page_count
        }
        
        if status == 'started':
            logger.info(f"Parsing document: {file_path}", extra={'context': json.dumps(context)})
        elif status == 'completed':
            logger.info(
                f"Parsed {page_count} pages from {file_path}",
                extra={'context': json.dumps(context)}
            )
        elif status == 'failed':
            context['error'] = error
            logger.error(
                f"Failed to parse {file_path}: {error}",
                extra={'context': json.dumps(context)}
            )
    
    def log_embedding(
        self,
        status: str,
        chunk_count: Optional[int] = None,
        duration_seconds: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log embedding generation operation.
        
        Args:
            status: Status (started, completed, failed)
            chunk_count: Number of chunks embedded
            duration_seconds: Operation duration
            error: Error message if failed
        """
        logger = self.get_logger('embedding_engine')
        
        context = {
            'chunk_count': chunk_count,
            'duration_seconds': duration_seconds
        }
        
        if status == 'started':
            logger.info(f"Generating embeddings for {chunk_count} chunks")
        elif status == 'completed':
            rate = chunk_count / duration_seconds if duration_seconds and duration_seconds > 0 else 0
            logger.info(
                f"Generated {chunk_count} embeddings in {duration_seconds:.2f}s ({rate:.1f} chunks/sec)",
                extra={'context': json.dumps(context)}
            )
        elif status == 'failed':
            context['error'] = error
            logger.error(
                f"Failed to generate embeddings: {error}",
                extra={'context': json.dumps(context)}
            )
    
    def log_retrieval(
        self,
        query: str,
        status: str,
        result_count: Optional[int] = None,
        retrieval_method: Optional[str] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log retrieval operation.
        
        Args:
            query: Query text (truncated for logging)
            status: Status (started, completed, failed)
            result_count: Number of results retrieved
            retrieval_method: Method used (dense, sparse, hybrid)
            error: Error message if failed
        """
        logger = self.get_logger('retrieval_engine')
        
        query_preview = query[:100] + '...' if len(query) > 100 else query
        context = {
            'query_preview': query_preview,
            'result_count': result_count,
            'retrieval_method': retrieval_method
        }
        
        if status == 'started':
            logger.info(f"Retrieving results for query: {query_preview}")
        elif status == 'completed':
            logger.info(
                f"Retrieved {result_count} results using {retrieval_method}",
                extra={'context': json.dumps(context)}
            )
        elif status == 'failed':
            context['error'] = error
            logger.error(
                f"Failed to retrieve results: {error}",
                extra={'context': json.dumps(context)}
            )
    
    def log_generation(
        self,
        operation: str,
        status: str,
        token_count: Optional[int] = None,
        duration_seconds: Optional[float] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log LLM generation operation.
        
        Args:
            operation: Operation type (gap_analysis, policy_revision, roadmap)
            status: Status (started, completed, failed)
            token_count: Number of tokens generated
            duration_seconds: Operation duration
            error: Error message if failed
        """
        logger = self.get_logger('llm_runtime')
        
        context = {
            'operation': operation,
            'token_count': token_count,
            'duration_seconds': duration_seconds
        }
        
        if status == 'started':
            logger.info(f"Starting LLM generation: {operation}")
        elif status == 'completed':
            rate = token_count / duration_seconds if duration_seconds and duration_seconds > 0 else 0
            logger.info(
                f"Generated {token_count} tokens for {operation} in {duration_seconds:.2f}s ({rate:.1f} tokens/sec)",
                extra={'context': json.dumps(context)}
            )
        elif status == 'failed':
            context['error'] = error
            logger.error(
                f"Failed LLM generation for {operation}: {error}",
                extra={'context': json.dumps(context)}
            )
    
    def log_analysis_stage(
        self,
        stage: str,
        status: str,
        subcategory_count: Optional[int] = None,
        gap_count: Optional[int] = None,
        error: Optional[str] = None
    ) -> None:
        """
        Log gap analysis stage.
        
        Args:
            stage: Stage name (stage_a, stage_b)
            status: Status (started, completed, failed)
            subcategory_count: Number of subcategories processed
            gap_count: Number of gaps identified
            error: Error message if failed
        """
        logger = self.get_logger('gap_analysis_engine')
        
        context = {
            'stage': stage,
            'subcategory_count': subcategory_count,
            'gap_count': gap_count
        }
        
        if status == 'started':
            logger.info(f"Starting {stage} analysis for {subcategory_count} subcategories")
        elif status == 'completed':
            logger.info(
                f"Completed {stage} analysis: {gap_count} gaps identified",
                extra={'context': json.dumps(context)}
            )
        elif status == 'failed':
            context['error'] = error
            logger.error(
                f"Failed {stage} analysis: {error}",
                extra={'context': json.dumps(context)}
            )
    
    def close(self) -> None:
        """Close all logging handlers."""
        root_logger = logging.getLogger()
        for handler in root_logger.handlers[:]:
            handler.flush()  # Flush before closing
            handler.close()
            root_logger.removeHandler(handler)


# ============================================================================
# Global Logger Instance
# ============================================================================

_global_logger: Optional[OperationLogger] = None


def setup_logging(
    output_dir: Optional[Path] = None,
    log_level: str = 'INFO',
    console_output: bool = True
) -> OperationLogger:
    """
    Setup global logging configuration.
    
    Args:
        output_dir: Directory for log files
        log_level: Minimum log level
        console_output: Whether to output to console
    
    Returns:
        Configured OperationLogger instance
    """
    global _global_logger
    _global_logger = OperationLogger(output_dir, log_level, console_output)
    return _global_logger


def get_logger(component_name: str) -> logging.Logger:
    """
    Get logger for component.
    
    Args:
        component_name: Component name
    
    Returns:
        Logger instance
    """
    if _global_logger is None:
        # Setup default logger if not configured
        setup_logging()
    return _global_logger.get_logger(component_name)


def close_logging() -> None:
    """Close global logging."""
    global _global_logger
    if _global_logger:
        _global_logger.close()
        _global_logger = None


# ============================================================================
# Default Logger Instance
# ============================================================================

# Create a default logger for CLI and general use
logger = get_logger("main")
