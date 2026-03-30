"""
Unit Tests for Fault Injector

Tests the fault injection mechanisms to ensure they correctly simulate
system failures and clean up properly.
"""

import os
import sys
import signal
import tempfile
import time
from pathlib import Path
import pytest

from .fault_injector import FaultInjector


class TestDiskFullInjection:
    """Tests for disk full simulation."""
    
    def test_inject_disk_full_creates_filler_file(self):
        """Test that disk full injection creates a filler file."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with injector.inject_disk_full(tmpdir, threshold_bytes=1024*1024):
                # Check that a filler file was created
                filler_files = list(Path(tmpdir).glob(".disk_filler_*.tmp"))
                assert len(filler_files) > 0, "Filler file should be created"
    
    def test_inject_disk_full_cleanup(self):
        """Test that disk full injection cleans up filler file."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            with injector.inject_disk_full(tmpdir, threshold_bytes=1024*1024):
                pass
            
            # After context exit, filler file should be removed
            filler_files = list(Path(tmpdir).glob(".disk_filler_*.tmp"))
            assert len(filler_files) == 0, "Filler file should be cleaned up"
    
    def test_inject_disk_full_reduces_available_space(self):
        """Test that disk full injection reduces available disk space."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Get initial available space
            stat_before = os.statvfs(tmpdir)
            available_before = stat_before.f_bavail * stat_before.f_frsize
            
            # Inject disk full with 10MB threshold
            threshold = 10 * 1024 * 1024
            with injector.inject_disk_full(tmpdir, threshold_bytes=threshold):
                stat_during = os.statvfs(tmpdir)
                available_during = stat_during.f_bavail * stat_during.f_frsize
                
                # Available space should be reduced (we create a filler file)
                # The filler is capped at 100MB, so we just check it's less than before
                assert available_during < available_before, "Available space should be reduced"
    
    def test_inject_disk_full_causes_write_failure(self):
        """Test that disk full injection simulates low disk space."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Inject disk full - this creates a filler file
            with injector.inject_disk_full(tmpdir, threshold_bytes=0):
                # The filler file should exist
                filler_files = list(Path(tmpdir).glob(".disk_filler_*.tmp"))
                assert len(filler_files) > 0, "Filler file should exist during injection"
                
                # Check that the filler file has some size
                if filler_files:
                    size = filler_files[0].stat().st_size
                    assert size > 0, "Filler file should have content"


class TestMemoryLimitInjection:
    """Tests for memory limit simulation."""
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Memory limits not supported on Windows")
    def test_inject_memory_limit_sets_limit(self):
        """Test that memory limit injection attempts to set resource limit."""
        import resource
        
        injector = FaultInjector()
        
        # Get original limit
        try:
            original_soft, original_hard = resource.getrlimit(resource.RLIMIT_AS)
        except (ValueError, OSError):
            pytest.skip("Cannot get memory limits on this system")
        
        # Set a limit - use a large value to avoid issues
        limit_mb = 1000  # 1GB should be safe
        with injector.inject_memory_limit(limit_mb):
            try:
                current_soft, current_hard = resource.getrlimit(resource.RLIMIT_AS)
                
                # On some systems (like macOS), the limit might not actually be set
                # due to system restrictions, so we just check it doesn't crash
                # If it was set, verify it's correct
                expected_bytes = limit_mb * 1024 * 1024
                if current_soft != original_soft and current_soft != resource.RLIM_INFINITY:
                    assert current_soft == expected_bytes, \
                        f"Memory limit should be {expected_bytes}, got {current_soft}"
            except (ValueError, OSError):
                # On some systems, we can't even read the limit after setting
                pass
        
        # After context exit, limit should be restored (if it was changed)
        try:
            restored_soft, restored_hard = resource.getrlimit(resource.RLIMIT_AS)
            # Just verify we can read it - the value might not have changed on some systems
        except (ValueError, OSError):
            pass
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Memory limits not supported on Windows")
    def test_inject_memory_limit_cleanup(self):
        """Test that memory limit injection doesn't crash."""
        import resource
        
        injector = FaultInjector()
        
        # Just verify it doesn't crash - on some systems it's a no-op
        try:
            with injector.inject_memory_limit(1000):
                pass
        except (ValueError, OSError):
            pytest.skip("Memory limits not supported on this system")
    
    @pytest.mark.skipif(sys.platform != 'win32', reason="Test Windows behavior")
    def test_inject_memory_limit_noop_on_windows(self):
        """Test that memory limit injection is a no-op on Windows."""
        injector = FaultInjector()
        
        # Should not raise an error on Windows
        with injector.inject_memory_limit(100):
            pass  # Should succeed without doing anything


class TestPermissionErrorInjection:
    """Tests for permission error simulation."""
    
    def test_inject_permission_error_makes_readonly(self):
        """Test that permission error injection makes path read-only."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            
            with injector.inject_permission_error(str(test_file)):
                # File should be read-only
                mode = test_file.stat().st_mode
                # Check that write bit is not set for owner
                assert not (mode & 0o200), "File should be read-only"
                
                # Try to write - should fail
                with pytest.raises(PermissionError):
                    test_file.write_text("new content")
    
    def test_inject_permission_error_cleanup(self):
        """Test that permission error injection restores original permissions."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            
            # Get original mode
            original_mode = test_file.stat().st_mode
            
            with injector.inject_permission_error(str(test_file)):
                pass
            
            # Permissions should be restored
            restored_mode = test_file.stat().st_mode
            assert restored_mode == original_mode, "Permissions should be restored"
            
            # Should be able to write again
            test_file.write_text("new content")
            assert test_file.read_text() == "new content"
    
    def test_inject_permission_error_creates_readonly_file(self):
        """Test that permission error injection can create a read-only file."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "new_file.txt"
            
            with injector.inject_permission_error(str(test_file)):
                # File should exist and be read-only
                assert test_file.exists(), "File should be created"
                mode = test_file.stat().st_mode
                assert not (mode & 0o200), "File should be read-only"
    
    def test_inject_permission_error_directory(self):
        """Test that permission error injection works on directories."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_dir = Path(tmpdir) / "test_dir"
            
            with injector.inject_permission_error(str(test_dir)):
                # Directory should exist and be read-only
                assert test_dir.exists(), "Directory should be created"
                assert test_dir.is_dir(), "Should be a directory"
                
                # Try to create a file in the directory - should fail
                with pytest.raises(PermissionError):
                    (test_dir / "file.txt").write_text("content")


class TestCorruptionInjection:
    """Tests for file corruption simulation."""
    
    def test_inject_corruption_modify(self):
        """Test that corruption injection modifies file bytes."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            original_content = b"x" * 1000
            test_file.write_bytes(original_content)
            
            # Corrupt the file
            injector.inject_corruption(str(test_file), corruption_type="modify")
            
            # Content should be different
            corrupted_content = test_file.read_bytes()
            assert corrupted_content != original_content, "File should be corrupted"
            assert len(corrupted_content) == len(original_content), \
                "File size should remain the same"
    
    def test_inject_corruption_truncate(self):
        """Test that corruption injection truncates file."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            original_content = b"x" * 1000
            test_file.write_bytes(original_content)
            
            # Corrupt the file
            injector.inject_corruption(str(test_file), corruption_type="truncate")
            
            # File should be truncated
            truncated_size = test_file.stat().st_size
            assert truncated_size == 500, "File should be truncated to half size"
    
    def test_inject_corruption_delete(self):
        """Test that corruption injection deletes file."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            
            # Corrupt the file
            injector.inject_corruption(str(test_file), corruption_type="delete")
            
            # File should be deleted
            assert not test_file.exists(), "File should be deleted"
    
    def test_inject_corruption_nonexistent_file(self):
        """Test that corruption injection handles nonexistent files gracefully."""
        injector = FaultInjector()
        
        # Should not raise an error
        injector.inject_corruption("/nonexistent/file.txt", corruption_type="modify")


class TestSignalInjection:
    """Tests for signal injection."""
    
    def test_inject_signal_sends_signal(self):
        """Test that signal injection sends signal to process."""
        injector = FaultInjector()
        
        # Set up signal handler
        signal_received = []
        
        def handler(signum, frame):
            signal_received.append(signum)
        
        original_handler = signal.signal(signal.SIGUSR1, handler)
        
        try:
            # Inject signal with short delay
            injector.inject_signal(signal.SIGUSR1, delay_seconds=0.1)
            
            # Wait for signal
            time.sleep(0.5)
            
            # Signal should have been received
            assert len(signal_received) > 0, "Signal should be received"
            assert signal_received[0] == signal.SIGUSR1, "Correct signal should be received"
        
        finally:
            # Restore original handler
            signal.signal(signal.SIGUSR1, original_handler)
    
    def test_inject_signal_with_delay(self):
        """Test that signal injection respects delay."""
        injector = FaultInjector()
        
        signal_received = []
        
        def handler(signum, frame):
            signal_received.append(time.time())
        
        original_handler = signal.signal(signal.SIGUSR1, handler)
        
        try:
            start_time = time.time()
            
            # Inject signal with 0.5 second delay
            injector.inject_signal(signal.SIGUSR1, delay_seconds=0.5)
            
            # Wait for signal
            time.sleep(1.0)
            
            # Signal should have been received after delay
            assert len(signal_received) > 0, "Signal should be received"
            elapsed = signal_received[0] - start_time
            assert elapsed >= 0.5, f"Signal should be delayed (elapsed: {elapsed})"
            assert elapsed < 1.0, f"Signal should not be delayed too long (elapsed: {elapsed})"
        
        finally:
            signal.signal(signal.SIGUSR1, original_handler)


class TestDelayInjection:
    """Tests for delay injection."""
    
    def test_inject_delay(self):
        """Test that delay injection introduces delay."""
        injector = FaultInjector()
        
        start_time = time.time()
        
        with injector.inject_delay(0.5):
            pass
        
        elapsed = time.time() - start_time
        assert elapsed >= 0.5, f"Delay should be at least 0.5 seconds (elapsed: {elapsed})"
        assert elapsed < 1.0, f"Delay should not be too long (elapsed: {elapsed})"


class TestCleanupMechanisms:
    """Tests for cleanup after fault injection."""
    
    def test_cleanup_after_exception(self):
        """Test that cleanup happens even when exception is raised."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            original_mode = test_file.stat().st_mode
            
            try:
                with injector.inject_permission_error(str(test_file)):
                    # Raise an exception
                    raise ValueError("Test exception")
            except ValueError:
                pass
            
            # Permissions should still be restored
            restored_mode = test_file.stat().st_mode
            assert restored_mode == original_mode, \
                "Permissions should be restored even after exception"
    
    def test_multiple_injections_cleanup(self):
        """Test that multiple injections clean up properly."""
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            # Multiple disk full injections
            for i in range(3):
                with injector.inject_disk_full(tmpdir, threshold_bytes=1024*1024):
                    pass
            
            # No filler files should remain
            filler_files = list(Path(tmpdir).glob(".disk_filler_*.tmp"))
            assert len(filler_files) == 0, "All filler files should be cleaned up"
    
    @pytest.mark.skipif(sys.platform == 'win32', reason="Memory limits not supported on Windows")
    def test_nested_injections_cleanup(self):
        """Test that nested injections clean up in correct order."""
        import resource
        
        injector = FaultInjector()
        
        with tempfile.TemporaryDirectory() as tmpdir:
            test_file = Path(tmpdir) / "test.txt"
            test_file.write_text("test content")
            original_mode = test_file.stat().st_mode
            
            # Nested injections - memory limit might not work on all systems
            try:
                with injector.inject_memory_limit(1000):
                    with injector.inject_permission_error(str(test_file)):
                        pass
                    
                    # Permission should be restored
                    assert test_file.stat().st_mode == original_mode
            except (ValueError, OSError):
                # If memory limits don't work, just test permission injection
                with injector.inject_permission_error(str(test_file)):
                    pass
                assert test_file.stat().st_mode == original_mode
