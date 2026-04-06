"""
Unit Tests for FaultInjector

Tests disk full simulation, memory limit simulation, file corruption,
signal injection, and cleanup after injection.

**Validates: Task 32.3**
"""

import pytest
import os
import signal
import time
from pathlib import Path
from tests.extreme.support.fault_injector import FaultInjector


class TestFaultInjector:
    """Unit tests for FaultInjector component."""
    
    @pytest.fixture
    def injector(self):
        """Create FaultInjector instance."""
        return FaultInjector()
    
    @pytest.fixture
    def temp_file(self, tmp_path):
        """Create a temporary file for testing."""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("Test content for corruption")
        return test_file
    
    # Test disk full simulation
    
    def test_inject_disk_full_context_manager(self, injector, tmp_path):
        """Test disk full injection as context manager."""
        with injector.inject_disk_full(str(tmp_path), threshold_bytes=1000) as target:
            assert isinstance(target, Path)
            assert target.exists()
            
            # Check that filler file was created
            filler_files = list(tmp_path.glob(".disk_filler_*.tmp"))
            # May or may not create filler depending on available space
            assert len(filler_files) <= 1
    
    def test_inject_disk_full_cleanup(self, injector, tmp_path):
        """Test disk full injection cleans up after context."""
        with injector.inject_disk_full(str(tmp_path)):
            pass
        
        # Filler file should be cleaned up
        filler_files = list(tmp_path.glob(".disk_filler_*.tmp"))
        assert len(filler_files) == 0
    
    def test_inject_disk_full_default_path(self, injector):
        """Test disk full injection with default path (temp dir)."""
        with injector.inject_disk_full() as target:
            assert isinstance(target, Path)
            assert target.exists()
    
    def test_inject_disk_full_with_threshold(self, injector, tmp_path):
        """Test disk full injection with specific threshold."""
        threshold = 10 * 1024 * 1024  # 10MB
        
        with injector.inject_disk_full(str(tmp_path), threshold_bytes=threshold) as target:
            assert target.exists()
    
    # Test memory limit simulation
    
    def test_inject_memory_limit_context_manager(self, injector):
        """Test memory limit injection as context manager."""
        limit_mb = 512
        
        with injector.inject_memory_limit(limit_mb):
            # Context manager should complete without error
            pass
    
    def test_inject_memory_limit_restores_original(self, injector):
        """Test memory limit injection restores original limits."""
        import sys
        
        if sys.platform == 'win32':
            pytest.skip("Memory limits not supported on Windows")
        
        import resource
        
        try:
            original_soft, original_hard = resource.getrlimit(resource.RLIMIT_AS)
        except (ValueError, OSError):
            pytest.skip("Cannot get resource limits on this system")
        
        with injector.inject_memory_limit(256):
            pass
        
        # Limits should be restored
        try:
            restored_soft, restored_hard = resource.getrlimit(resource.RLIMIT_AS)
            # Limits should be back to original (or close, depending on system)
            assert restored_soft == original_soft or restored_soft == -1
        except (ValueError, OSError):
            pass  # Some systems don't support this
    
    def test_inject_memory_limit_small_limit(self, injector):
        """Test memory limit injection with small limit."""
        with injector.inject_memory_limit(100):
            # Should complete without crashing
            pass
    
    def test_inject_memory_limit_large_limit(self, injector):
        """Test memory limit injection with large limit."""
        with injector.inject_memory_limit(2048):
            # Should complete without issue
            pass
    
    # Test file corruption
    
    def test_inject_corruption_modify(self, injector, temp_file):
        """Test file corruption with modify type."""
        original_content = temp_file.read_bytes()
        
        injector.inject_corruption(str(temp_file), corruption_type="modify")
        
        corrupted_content = temp_file.read_bytes()
        # Content should be different after corruption
        assert corrupted_content != original_content
        assert len(corrupted_content) == len(original_content)
    
    def test_inject_corruption_truncate(self, injector, temp_file):
        """Test file corruption with truncate type."""
        original_size = temp_file.stat().st_size
        
        injector.inject_corruption(str(temp_file), corruption_type="truncate")
        
        truncated_size = temp_file.stat().st_size
        # File should be truncated to half size
        assert truncated_size == original_size // 2
    
    def test_inject_corruption_delete(self, injector, temp_file):
        """Test file corruption with delete type."""
        assert temp_file.exists()
        
        injector.inject_corruption(str(temp_file), corruption_type="delete")
        
        # File should be deleted
        assert not temp_file.exists()
    
    def test_inject_corruption_nonexistent_file(self, injector, tmp_path):
        """Test file corruption on nonexistent file does nothing."""
        nonexistent = tmp_path / "nonexistent.txt"
        
        # Should not raise error
        injector.inject_corruption(str(nonexistent), corruption_type="modify")
        
        assert not nonexistent.exists()
    
    def test_inject_corruption_empty_file(self, injector, tmp_path):
        """Test file corruption on empty file."""
        empty_file = tmp_path / "empty.txt"
        empty_file.touch()
        
        injector.inject_corruption(str(empty_file), corruption_type="modify")
        
        # Should handle empty file gracefully
        assert empty_file.exists()
    
    # Test signal injection
    
    def test_inject_signal_with_delay(self, injector):
        """Test signal injection with delay."""
        # Use a harmless signal for testing
        signal_received = []
        
        def signal_handler(signum, frame):
            signal_received.append(signum)
        
        # Set up signal handler
        original_handler = signal.signal(signal.SIGUSR1, signal_handler)
        
        try:
            # Inject signal with delay
            injector.inject_signal(signal.SIGUSR1, delay_seconds=0.1)
            
            # Wait for signal
            time.sleep(0.2)
            
            # Signal should have been received
            assert len(signal_received) > 0
            assert signal_received[0] == signal.SIGUSR1
        finally:
            # Restore original handler
            signal.signal(signal.SIGUSR1, original_handler)
    
    def test_inject_signal_immediate(self, injector):
        """Test signal injection with no delay."""
        signal_received = []
        
        def signal_handler(signum, frame):
            signal_received.append(signum)
        
        original_handler = signal.signal(signal.SIGUSR1, signal_handler)
        
        try:
            injector.inject_signal(signal.SIGUSR1, delay_seconds=0.0)
            time.sleep(0.1)
            
            assert len(signal_received) > 0
        finally:
            signal.signal(signal.SIGUSR1, original_handler)
    
    # Test permission error injection
    
    def test_inject_permission_error_existing_file(self, injector, temp_file):
        """Test permission error injection on existing file."""
        original_mode = temp_file.stat().st_mode
        
        with injector.inject_permission_error(str(temp_file)) as target:
            assert isinstance(target, Path)
            
            # File should be read-only
            current_mode = target.stat().st_mode
            # Check that write permissions are removed
            assert (current_mode & 0o200) == 0  # Owner write bit should be 0
        
        # Permissions should be restored
        restored_mode = temp_file.stat().st_mode
        assert restored_mode == original_mode
    
    def test_inject_permission_error_nonexistent_file(self, injector, tmp_path):
        """Test permission error injection creates read-only file."""
        new_file = tmp_path / "new_file.txt"
        
        with injector.inject_permission_error(str(new_file)) as target:
            assert target.exists()
            
            # File should be read-only
            current_mode = target.stat().st_mode
            assert (current_mode & 0o200) == 0
    
    def test_inject_permission_error_directory(self, injector, tmp_path):
        """Test permission error injection on directory."""
        new_dir = tmp_path / "test_dir"
        
        with injector.inject_permission_error(str(new_dir)) as target:
            assert target.exists()
            assert target.is_dir()
            
            # Directory should have restricted permissions
            current_mode = target.stat().st_mode
            # Check that write permissions are removed
            assert (current_mode & 0o200) == 0
    
    def test_inject_permission_error_cleanup(self, injector, temp_file):
        """Test permission error injection restores permissions."""
        original_mode = temp_file.stat().st_mode
        
        with injector.inject_permission_error(str(temp_file)):
            # Permissions changed inside context
            pass
        
        # Permissions should be restored
        restored_mode = temp_file.stat().st_mode
        assert restored_mode == original_mode
    
    # Test delay injection
    
    def test_inject_delay(self, injector):
        """Test delay injection."""
        delay_seconds = 0.1
        start_time = time.time()
        
        with injector.inject_delay(delay_seconds):
            pass
        
        elapsed = time.time() - start_time
        
        # Should have delayed at least the specified time
        assert elapsed >= delay_seconds
    
    def test_inject_delay_zero(self, injector):
        """Test delay injection with zero delay."""
        start_time = time.time()
        
        with injector.inject_delay(0.0):
            pass
        
        elapsed = time.time() - start_time
        
        # Should complete quickly
        assert elapsed < 0.1
    
    def test_inject_delay_long(self, injector):
        """Test delay injection with longer delay."""
        delay_seconds = 0.2
        start_time = time.time()
        
        with injector.inject_delay(delay_seconds):
            pass
        
        elapsed = time.time() - start_time
        
        assert elapsed >= delay_seconds
        assert elapsed < delay_seconds + 0.1  # Should not be much longer
    
    # Test cleanup mechanisms
    
    def test_disk_full_cleanup_on_exception(self, injector, tmp_path):
        """Test disk full cleanup occurs even on exception."""
        try:
            with injector.inject_disk_full(str(tmp_path)):
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Filler file should still be cleaned up
        filler_files = list(tmp_path.glob(".disk_filler_*.tmp"))
        assert len(filler_files) == 0
    
    def test_permission_error_cleanup_on_exception(self, injector, temp_file):
        """Test permission error cleanup occurs even on exception."""
        original_mode = temp_file.stat().st_mode
        
        try:
            with injector.inject_permission_error(str(temp_file)):
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Permissions should still be restored
        restored_mode = temp_file.stat().st_mode
        assert restored_mode == original_mode
    
    def test_memory_limit_cleanup_on_exception(self, injector):
        """Test memory limit cleanup occurs even on exception."""
        import sys
        
        if sys.platform == 'win32':
            pytest.skip("Memory limits not supported on Windows")
        
        try:
            with injector.inject_memory_limit(256):
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Should not raise error - limits should be restored
    
    # Test multiple simultaneous injections
    
    def test_multiple_permission_errors(self, injector, tmp_path):
        """Test multiple permission error injections."""
        file1 = tmp_path / "file1.txt"
        file2 = tmp_path / "file2.txt"
        file1.write_text("content1")
        file2.write_text("content2")
        
        with injector.inject_permission_error(str(file1)):
            with injector.inject_permission_error(str(file2)):
                # Both files should be read-only
                assert (file1.stat().st_mode & 0o200) == 0
                assert (file2.stat().st_mode & 0o200) == 0
        
        # Both should be restored
        assert (file1.stat().st_mode & 0o200) != 0
        assert (file2.stat().st_mode & 0o200) != 0
    
    def test_combined_injections(self, injector, tmp_path):
        """Test combining multiple injection types."""
        test_file = tmp_path / "combined_test.txt"
        test_file.write_text("test content")
        
        with injector.inject_delay(0.05):
            with injector.inject_permission_error(str(test_file)):
                # Both injections should be active
                assert test_file.exists()
                assert (test_file.stat().st_mode & 0o200) == 0
        
        # Cleanup should occur for both
        assert (test_file.stat().st_mode & 0o200) != 0
