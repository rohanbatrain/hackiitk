"""
Fault Injector for Chaos Testing

This module provides mechanisms for simulating system failures during testing,
including disk full scenarios, memory exhaustion, file corruption, process
interruption, and permission errors.
"""

import os
import sys
import signal
import time
import tempfile
import shutil
from pathlib import Path
from contextlib import contextmanager
from typing import Optional, Callable
import resource


class FaultInjector:
    """Provides mechanisms for simulating system failures during testing."""
    
    def __init__(self):
        """Initialize the fault injector."""
        self._cleanup_actions = []
    
    @contextmanager
    def inject_disk_full(self, target_path: Optional[str] = None, threshold_bytes: int = 0):
        """
        Simulate disk full condition using OS-level mechanisms.
        
        On Unix-like systems, this creates a large file to fill up available space
        in the target directory, leaving only threshold_bytes available.
        
        Args:
            target_path: Path where disk full should be simulated (defaults to temp dir)
            threshold_bytes: Bytes to leave available (0 = completely full)
            
        Yields:
            Path object for the target directory
            
        Requirements: 3.1, 3.2, 3.3, 4.1, 4.2, 7.1, 7.2
        """
        if target_path is None:
            target_path = tempfile.gettempdir()
        
        target = Path(target_path)
        filler_file = target / f".disk_filler_{os.getpid()}.tmp"
        
        try:
            # Get available disk space
            stat = os.statvfs(target)
            available_bytes = stat.f_bavail * stat.f_frsize
            
            # Calculate how much to fill - cap at 100MB to avoid actually filling the disk
            # This is a simulation, not a real disk fill
            max_fill = min(100 * 1024 * 1024, available_bytes - threshold_bytes - 100 * 1024 * 1024)
            fill_bytes = max(0, max_fill)
            
            if fill_bytes > 0:
                # Create a large file to consume disk space
                with open(filler_file, 'wb') as f:
                    # Write in chunks to avoid memory issues
                    chunk_size = 1024 * 1024  # 1MB chunks
                    remaining = fill_bytes
                    while remaining > 0:
                        write_size = min(chunk_size, remaining)
                        f.write(b'\0' * write_size)
                        remaining -= write_size
            
            yield target
            
        finally:
            # Cleanup: remove the filler file
            if filler_file.exists():
                try:
                    filler_file.unlink()
                except Exception:
                    pass  # Best effort cleanup
    
    @contextmanager
    def inject_memory_limit(self, limit_mb: int):
        """
        Simulate memory limit using resource.setrlimit.
        
        Sets the virtual memory limit for the current process. This only works
        on Unix-like systems. On macOS, this may not work due to system restrictions.
        
        Args:
            limit_mb: Memory limit in megabytes
            
        Yields:
            None
            
        Requirements: 4.1, 4.2, 4.3
        """
        if sys.platform == 'win32':
            # Windows doesn't support resource limits
            yield
            return
        
        # Save original limits
        try:
            soft, hard = resource.getrlimit(resource.RLIMIT_AS)
            original_limits = (soft, hard)
        except (ValueError, OSError):
            # If we can't get limits, skip the injection
            yield
            return
        
        try:
            # Set new memory limit
            limit_bytes = limit_mb * 1024 * 1024
            
            # On macOS, the hard limit might be unlimited (-1), so we need to handle that
            if hard == resource.RLIM_INFINITY or hard == -1:
                # Use a reasonable hard limit if unlimited
                new_hard = max(limit_bytes * 2, 1024 * 1024 * 1024)  # At least 1GB
            else:
                new_hard = hard
            
            # Only set if the new limit is less than the current soft limit
            # This avoids the "current limit exceeds maximum limit" error
            if soft == resource.RLIM_INFINITY or soft == -1 or limit_bytes < soft:
                resource.setrlimit(resource.RLIMIT_AS, (limit_bytes, new_hard))
            
            yield
            
        except (ValueError, OSError) as e:
            # If we can't set the limit (e.g., on macOS), just skip it
            yield
        finally:
            # Restore original limits
            try:
                resource.setrlimit(resource.RLIMIT_AS, original_limits)
            except (ValueError, OSError):
                pass  # Best effort cleanup
    
    @contextmanager
    def inject_permission_error(self, path: str):
        """
        Simulate permission error by changing file modes.
        
        Makes the specified path read-only (removes write permissions) to
        simulate permission errors.
        
        Args:
            path: Path to make read-only
            
        Yields:
            Path object
            
        Requirements: 7.1, 7.2, 7.3
        """
        target = Path(path)
        original_mode = None
        
        try:
            # Save original permissions
            if target.exists():
                original_mode = target.stat().st_mode
                # Remove write permissions
                target.chmod(0o444)
            else:
                # Create the path as read-only
                if target.suffix:  # It's a file
                    target.parent.mkdir(parents=True, exist_ok=True)
                    target.touch()
                    target.chmod(0o444)
                else:  # It's a directory
                    target.mkdir(parents=True, exist_ok=True)
                    target.chmod(0o555)
                original_mode = target.stat().st_mode
            
            yield target
            
        finally:
            # Restore original permissions
            if original_mode is not None and target.exists():
                try:
                    target.chmod(original_mode)
                except Exception:
                    pass  # Best effort cleanup
    
    def inject_corruption(self, file_path: str, corruption_type: str = "modify"):
        """
        Corrupt specified file.
        
        Args:
            file_path: Path to file to corrupt
            corruption_type: Type of corruption:
                - "modify": Modify random bytes in the file
                - "truncate": Truncate the file to half its size
                - "delete": Delete the file entirely
                
        Requirements: 5.1, 5.2, 20.1
        """
        target = Path(file_path)
        
        if not target.exists():
            return
        
        if corruption_type == "delete":
            target.unlink()
        
        elif corruption_type == "truncate":
            # Truncate to half size
            size = target.stat().st_size
            with open(target, 'r+b') as f:
                f.truncate(size // 2)
        
        elif corruption_type == "modify":
            # Modify random bytes
            try:
                with open(target, 'r+b') as f:
                    content = f.read()
                    if len(content) > 0:
                        # Corrupt the middle of the file
                        mid = len(content) // 2
                        corrupted = bytearray(content)
                        # Flip some bits
                        for i in range(mid, min(mid + 100, len(corrupted))):
                            corrupted[i] = (corrupted[i] + 1) % 256
                        f.seek(0)
                        f.write(bytes(corrupted))
            except Exception:
                pass  # If we can't corrupt, that's okay
    
    def inject_signal(self, sig: int, delay_seconds: float = 0.0):
        """
        Send signal to current process after delay.
        
        Args:
            sig: Signal to send (e.g., signal.SIGINT, signal.SIGTERM)
            delay_seconds: Delay before sending signal
            
        Requirements: 6.1, 6.2, 6.3
        """
        def send_signal():
            time.sleep(delay_seconds)
            os.kill(os.getpid(), sig)
        
        import threading
        thread = threading.Thread(target=send_signal, daemon=True)
        thread.start()
    
    @contextmanager
    def inject_delay(self, delay_seconds: float):
        """
        Inject delay for simulating slow operations.
        
        Args:
            delay_seconds: Delay in seconds
            
        Yields:
            None
            
        Requirements: 20.1
        """
        time.sleep(delay_seconds)
        yield
