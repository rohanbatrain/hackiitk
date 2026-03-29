"""
Error handling framework for the Offline Policy Gap Analyzer.

This module provides custom exceptions, retry logic, graceful degradation,
and memory monitoring to ensure robust operation on consumer hardware.
"""

import time
import logging
import psutil
from typing import Callable, Any, Optional, Type
from functools import wraps

logger = logging.getLogger(__name__)


# ============================================================================
# Custom Exceptions
# ============================================================================

class PolicyAnalyzerError(Exception):
    """Base exception for all Policy Analyzer errors."""
    
    def __init__(self, message: str, troubleshooting: Optional[str] = None):
        self.message = message
        self.troubleshooting = troubleshooting
        super().__init__(self.message)
    
    def __str__(self):
        if self.troubleshooting:
            return f"{self.message}\n\nTroubleshooting: {self.troubleshooting}"
        return self.message


class UnsupportedFormatError(PolicyAnalyzerError):
    """Raised when document format is not supported."""
    
    def __init__(self, file_path: str, file_format: str):
        message = f"Unsupported file format: {file_format} for file {file_path}"
        troubleshooting = (
            "Supported formats are: PDF (text-based), DOCX, and TXT. "
            "If you have a scanned PDF, please convert it to a text-based PDF first."
        )
        super().__init__(message, troubleshooting)
        self.file_path = file_path
        self.file_format = file_format


class OCRRequiredError(PolicyAnalyzerError):
    """Raised when PDF contains only scanned images without text layer."""
    
    def __init__(self, file_path: str):
        message = f"OCR is not supported; please provide a text-based PDF: {file_path}"
        troubleshooting = (
            "The PDF appears to contain only scanned images. "
            "Please use an external OCR tool to convert it to a text-based PDF, "
            "or provide the document in DOCX or TXT format."
        )
        super().__init__(message, troubleshooting)
        self.file_path = file_path


class ParsingError(PolicyAnalyzerError):
    """Raised when document parsing fails."""
    
    def __init__(self, file_path: str, reason: str):
        message = f"Failed to parse document {file_path}: {reason}"
        troubleshooting = (
            "Ensure the file is not corrupted and is in a supported format. "
            "Try opening the file in its native application to verify it's valid."
        )
        super().__init__(message, troubleshooting)
        self.file_path = file_path
        self.reason = reason


class ModelNotFoundError(PolicyAnalyzerError):
    """Raised when required model files are not found."""
    
    def __init__(self, model_name: str, expected_path: str):
        message = f"Model not found: {model_name} at {expected_path}"
        troubleshooting = (
            f"Please download the required model using:\n"
            f"  python scripts/setup_models.py\n\n"
            f"Or manually download {model_name} and place it in {expected_path}"
        )
        super().__init__(message, troubleshooting)
        self.model_name = model_name
        self.expected_path = expected_path


class MemoryError(PolicyAnalyzerError):
    """Raised when memory usage exceeds safe thresholds."""
    
    def __init__(self, current_usage: float, threshold: float):
        message = f"Memory usage ({current_usage:.1f}%) exceeds threshold ({threshold:.1f}%)"
        troubleshooting = (
            "Try one of the following:\n"
            "  1. Close other applications to free up memory\n"
            "  2. Use a smaller model (e.g., Qwen2.5-3B instead of Mistral-7B)\n"
            "  3. Reduce chunk_size in configuration\n"
            "  4. Process a shorter policy document"
        )
        super().__init__(message, troubleshooting)
        self.current_usage = current_usage
        self.threshold = threshold


class RetryableError(PolicyAnalyzerError):
    """Raised for transient errors that can be retried."""
    
    def __init__(self, operation: str, reason: str):
        message = f"Retryable error in {operation}: {reason}"
        troubleshooting = "This error is transient and will be retried automatically."
        super().__init__(message, troubleshooting)
        self.operation = operation
        self.reason = reason


# ============================================================================
# Memory Monitoring
# ============================================================================

class MemoryMonitor:
    """Monitor system memory usage and enforce thresholds."""
    
    def __init__(self, threshold_percent: float = 90.0):
        """
        Initialize memory monitor.
        
        Args:
            threshold_percent: Memory usage percentage threshold (default 90%)
        """
        self.threshold_percent = threshold_percent
    
    def get_memory_usage(self) -> float:
        """
        Get current memory usage percentage.
        
        Returns:
            Memory usage as percentage (0-100)
        """
        memory = psutil.virtual_memory()
        return memory.percent
    
    def check_memory(self) -> None:
        """
        Check if memory usage is within safe limits.
        
        Raises:
            MemoryError: If memory usage exceeds threshold
        """
        current_usage = self.get_memory_usage()
        if current_usage >= self.threshold_percent:
            logger.error(f"Memory usage critical: {current_usage:.1f}%")
            raise MemoryError(current_usage, self.threshold_percent)
        
        if current_usage >= self.threshold_percent * 0.8:
            logger.warning(
                f"Memory usage high: {current_usage:.1f}% "
                f"(threshold: {self.threshold_percent:.1f}%)"
            )
    
    def get_available_memory_mb(self) -> float:
        """
        Get available memory in megabytes.
        
        Returns:
            Available memory in MB
        """
        memory = psutil.virtual_memory()
        return memory.available / (1024 * 1024)


# ============================================================================
# Retry Logic with Exponential Backoff
# ============================================================================

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (RetryableError, ConnectionError, TimeoutError)
):
    """
    Decorator for retrying functions with exponential backoff.
    
    Args:
        max_retries: Maximum number of retry attempts
        initial_delay: Initial delay in seconds before first retry
        backoff_factor: Multiplier for delay after each retry
        exceptions: Tuple of exception types to catch and retry
    
    Returns:
        Decorated function with retry logic
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            delay = initial_delay
            last_exception = None
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_retries:
                        logger.warning(
                            f"Attempt {attempt + 1}/{max_retries + 1} failed for {func.__name__}: {e}. "
                            f"Retrying in {delay:.1f}s..."
                        )
                        time.sleep(delay)
                        delay *= backoff_factor
                    else:
                        logger.error(
                            f"All {max_retries + 1} attempts failed for {func.__name__}"
                        )
            
            # All retries exhausted
            raise last_exception
        
        return wrapper
    return decorator


# ============================================================================
# Graceful Degradation
# ============================================================================

class GracefulDegradation:
    """Handle errors gracefully and continue with available data."""
    
    @staticmethod
    def handle_parsing_error(
        file_path: str,
        error: Exception,
        continue_on_error: bool = True
    ) -> Optional[str]:
        """
        Handle parsing errors gracefully.
        
        Args:
            file_path: Path to file that failed to parse
            error: Exception that occurred
            continue_on_error: Whether to continue or raise
        
        Returns:
            None if continuing, raises if not
        
        Raises:
            ParsingError: If continue_on_error is False
        """
        logger.error(f"Failed to parse {file_path}: {error}")
        
        if continue_on_error:
            logger.info(f"Continuing analysis with available data (skipping {file_path})")
            return None
        else:
            if isinstance(error, ParsingError):
                raise error
            raise ParsingError(file_path, str(error))
    
    @staticmethod
    def handle_embedding_error(
        text: str,
        error: Exception,
        fallback_value: Optional[Any] = None
    ) -> Optional[Any]:
        """
        Handle embedding generation errors gracefully.
        
        Args:
            text: Text that failed to embed
            error: Exception that occurred
            fallback_value: Value to return on error
        
        Returns:
            Fallback value
        """
        logger.error(f"Failed to generate embedding: {error}")
        logger.info(f"Using fallback value for text: {text[:100]}...")
        return fallback_value
    
    @staticmethod
    def handle_retrieval_error(
        query: str,
        error: Exception,
        fallback_results: Optional[list] = None
    ) -> list:
        """
        Handle retrieval errors gracefully.
        
        Args:
            query: Query that failed
            error: Exception that occurred
            fallback_results: Results to return on error
        
        Returns:
            Fallback results or empty list
        """
        logger.error(f"Failed to retrieve results for query: {error}")
        logger.info("Continuing with empty retrieval results")
        return fallback_results if fallback_results is not None else []


# ============================================================================
# Context Truncation
# ============================================================================

class ContextTruncator:
    """Truncate context when memory limits are approached."""
    
    def __init__(self, memory_monitor: MemoryMonitor):
        """
        Initialize context truncator.
        
        Args:
            memory_monitor: MemoryMonitor instance for checking usage
        """
        self.memory_monitor = memory_monitor
    
    def truncate_if_needed(
        self,
        text: str,
        max_tokens: int,
        tokenizer: Optional[Callable] = None
    ) -> tuple[str, bool]:
        """
        Truncate text if memory usage is high.
        
        Args:
            text: Text to potentially truncate
            max_tokens: Maximum tokens to keep
            tokenizer: Optional tokenizer function (defaults to word split)
        
        Returns:
            Tuple of (truncated_text, was_truncated)
        """
        memory_usage = self.memory_monitor.get_memory_usage()
        
        # If memory usage is below 80% of threshold, no truncation needed
        if memory_usage < self.memory_monitor.threshold_percent * 0.8:
            return text, False
        
        logger.warning(
            f"Memory usage at {memory_usage:.1f}%, truncating context to {max_tokens} tokens"
        )
        
        # Simple word-based tokenization if no tokenizer provided
        if tokenizer is None:
            tokens = text.split()
        else:
            tokens = tokenizer(text)
        
        if len(tokens) <= max_tokens:
            return text, False
        
        # Truncate to max_tokens
        if tokenizer is None:
            truncated = ' '.join(tokens[:max_tokens])
        else:
            truncated = tokenizer.decode(tokens[:max_tokens])
        
        logger.info(f"Context truncated from {len(tokens)} to {max_tokens} tokens")
        return truncated, True


# ============================================================================
# Error Handler Facade
# ============================================================================

class ErrorHandler:
    """
    Unified error handling facade for the Policy Analyzer.
    
    Provides centralized error handling, retry logic, memory monitoring,
    and graceful degradation.
    """
    
    def __init__(self, memory_threshold: float = 90.0):
        """
        Initialize error handler.
        
        Args:
            memory_threshold: Memory usage threshold percentage
        """
        self.memory_monitor = MemoryMonitor(memory_threshold)
        self.context_truncator = ContextTruncator(self.memory_monitor)
        self.degradation = GracefulDegradation()
    
    def check_memory(self) -> None:
        """Check memory usage and raise if threshold exceeded."""
        self.memory_monitor.check_memory()
    
    def get_memory_usage(self) -> float:
        """Get current memory usage percentage."""
        return self.memory_monitor.get_memory_usage()
    
    def truncate_context(
        self,
        text: str,
        max_tokens: int,
        tokenizer: Optional[Callable] = None
    ) -> tuple[str, bool]:
        """Truncate context if memory usage is high."""
        return self.context_truncator.truncate_if_needed(text, max_tokens, tokenizer)
    
    def handle_parsing_error(
        self,
        file_path: str,
        error: Exception,
        continue_on_error: bool = True
    ) -> Optional[str]:
        """Handle parsing errors gracefully."""
        return self.degradation.handle_parsing_error(file_path, error, continue_on_error)
    
    def handle_embedding_error(
        self,
        text: str,
        error: Exception,
        fallback_value: Optional[Any] = None
    ) -> Optional[Any]:
        """Handle embedding errors gracefully."""
        return self.degradation.handle_embedding_error(text, error, fallback_value)
    
    def handle_retrieval_error(
        self,
        query: str,
        error: Exception,
        fallback_results: Optional[list] = None
    ) -> list:
        """Handle retrieval errors gracefully."""
        return self.degradation.handle_retrieval_error(query, error, fallback_results)
