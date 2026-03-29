"""
Progress indicator utilities for the Offline Policy Gap Analyzer.

This module provides progress tracking and display functionality for
long-running operations in the analysis pipeline.
"""

import sys
import time
import logging
from typing import Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ProgressState:
    """State for tracking progress of an operation."""
    total: int
    current: int = 0
    start_time: float = 0.0
    operation_name: str = ""
    
    def __post_init__(self):
        if self.start_time == 0.0:
            self.start_time = time.time()
    
    @property
    def percentage(self) -> float:
        """Get completion percentage."""
        if self.total == 0:
            return 0.0
        return (self.current / self.total) * 100.0
    
    @property
    def elapsed_time(self) -> float:
        """Get elapsed time in seconds."""
        return time.time() - self.start_time
    
    @property
    def estimated_remaining(self) -> float:
        """Get estimated remaining time in seconds."""
        if self.current == 0:
            return 0.0
        
        rate = self.current / self.elapsed_time
        remaining_items = self.total - self.current
        
        if rate > 0:
            return remaining_items / rate
        return 0.0


class ProgressIndicator:
    """Display progress for long-running operations.
    
    Provides console-based progress indicators with percentage completion
    and estimated time remaining.
    """
    
    def __init__(self, total: int, operation_name: str = "Processing", show_bar: bool = True):
        """Initialize progress indicator.
        
        Args:
            total: Total number of items to process
            operation_name: Name of the operation
            show_bar: Whether to show progress bar (default: True)
        """
        self.state = ProgressState(total=total, operation_name=operation_name)
        self.show_bar = show_bar
        self.last_update = 0.0
        self.update_interval = 0.5  # Update every 0.5 seconds
    
    def update(self, current: Optional[int] = None, increment: int = 1) -> None:
        """Update progress.
        
        Args:
            current: Set current progress (if None, increments by increment)
            increment: Amount to increment if current is None
        """
        if current is not None:
            self.state.current = current
        else:
            self.state.current += increment
        
        # Throttle updates to avoid excessive output
        now = time.time()
        if now - self.last_update >= self.update_interval or self.state.current >= self.state.total:
            self._display()
            self.last_update = now
    
    def _display(self) -> None:
        """Display current progress."""
        percentage = self.state.percentage
        elapsed = self.state.elapsed_time
        remaining = self.state.estimated_remaining
        
        if self.show_bar:
            # Progress bar
            bar_length = 40
            filled = int(bar_length * percentage / 100)
            bar = '█' * filled + '░' * (bar_length - filled)
            
            # Format time
            elapsed_str = self._format_time(elapsed)
            remaining_str = self._format_time(remaining) if remaining > 0 else "calculating..."
            
            # Display
            message = (
                f"\r{self.state.operation_name}: [{bar}] "
                f"{percentage:.1f}% "
                f"({self.state.current}/{self.state.total}) "
                f"| Elapsed: {elapsed_str} | Remaining: {remaining_str}"
            )
            
            sys.stdout.write(message)
            sys.stdout.flush()
            
            # New line when complete
            if self.state.current >= self.state.total:
                sys.stdout.write("\n")
                sys.stdout.flush()
        else:
            # Simple percentage display
            logger.info(
                f"{self.state.operation_name}: {percentage:.1f}% "
                f"({self.state.current}/{self.state.total})"
            )
    
    def finish(self) -> None:
        """Mark progress as complete."""
        self.state.current = self.state.total
        self._display()
        
        logger.info(
            f"{self.state.operation_name} complete in {self._format_time(self.state.elapsed_time)}"
        )
    
    @staticmethod
    def _format_time(seconds: float) -> str:
        """Format time in human-readable format.
        
        Args:
            seconds: Time in seconds
            
        Returns:
            Formatted time string
        """
        if seconds < 60:
            return f"{seconds:.0f}s"
        elif seconds < 3600:
            minutes = seconds / 60
            return f"{minutes:.1f}m"
        else:
            hours = seconds / 3600
            return f"{hours:.1f}h"


class StepProgress:
    """Track progress through multi-step operations."""
    
    def __init__(self, total_steps: int, operation_name: str = "Analysis"):
        """Initialize step progress tracker.
        
        Args:
            total_steps: Total number of steps
            operation_name: Name of the overall operation
        """
        self.total_steps = total_steps
        self.current_step = 0
        self.operation_name = operation_name
        self.start_time = time.time()
    
    def start_step(self, step_name: str) -> None:
        """Start a new step.
        
        Args:
            step_name: Name of the step
        """
        self.current_step += 1
        percentage = (self.current_step / self.total_steps) * 100
        
        logger.info(
            f"Step {self.current_step}/{self.total_steps} ({percentage:.0f}%): {step_name}..."
        )
    
    def finish(self) -> None:
        """Mark all steps as complete."""
        elapsed = time.time() - self.start_time
        logger.info(
            f"{self.operation_name} complete: {self.total_steps} steps in "
            f"{ProgressIndicator._format_time(elapsed)}"
        )


class ProgressLogger:
    """Log progress for operations without visual progress bars."""
    
    def __init__(self, operation_name: str, log_interval: int = 10):
        """Initialize progress logger.
        
        Args:
            operation_name: Name of the operation
            log_interval: Log every N items (default: 10)
        """
        self.operation_name = operation_name
        self.log_interval = log_interval
        self.count = 0
        self.start_time = time.time()
    
    def increment(self, amount: int = 1) -> None:
        """Increment progress counter.
        
        Args:
            amount: Amount to increment
        """
        self.count += amount
        
        if self.count % self.log_interval == 0:
            elapsed = time.time() - self.start_time
            rate = self.count / elapsed if elapsed > 0 else 0
            
            logger.debug(
                f"{self.operation_name}: {self.count} items processed "
                f"({rate:.1f} items/sec)"
            )
    
    def finish(self, total: Optional[int] = None) -> None:
        """Mark operation as complete.
        
        Args:
            total: Optional total count (if different from current count)
        """
        final_count = total if total is not None else self.count
        elapsed = time.time() - self.start_time
        rate = final_count / elapsed if elapsed > 0 else 0
        
        logger.info(
            f"{self.operation_name} complete: {final_count} items in "
            f"{ProgressIndicator._format_time(elapsed)} "
            f"({rate:.1f} items/sec)"
        )


def create_progress_indicator(
    total: int,
    operation_name: str,
    show_bar: bool = True
) -> ProgressIndicator:
    """Factory function to create progress indicator.
    
    Args:
        total: Total number of items
        operation_name: Name of the operation
        show_bar: Whether to show progress bar
        
    Returns:
        ProgressIndicator instance
    """
    return ProgressIndicator(total=total, operation_name=operation_name, show_bar=show_bar)


def create_step_progress(total_steps: int, operation_name: str = "Analysis") -> StepProgress:
    """Factory function to create step progress tracker.
    
    Args:
        total_steps: Total number of steps
        operation_name: Name of the operation
        
    Returns:
        StepProgress instance
    """
    return StepProgress(total_steps=total_steps, operation_name=operation_name)
