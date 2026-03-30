"""
Example Usage of Fault Injector in Chaos Testing

This module demonstrates how the FaultInjector would be used in the
Chaos Engine to test system behavior under failure conditions.
"""

import signal
import tempfile
from pathlib import Path
from .fault_injector import FaultInjector


def example_disk_full_test():
    """Example: Test system behavior when disk is full."""
    injector = FaultInjector()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "output.txt"
        
        # Simulate disk full condition
        with injector.inject_disk_full(tmpdir, threshold_bytes=1024*1024):
            try:
                # Try to write output - should fail or handle gracefully
                with open(output_file, 'w') as f:
                    f.write("x" * (10 * 1024 * 1024))  # Try to write 10MB
                
                print("Write succeeded (unexpected)")
            except OSError as e:
                print(f"Write failed as expected: {e}")
                # Verify error message is descriptive
                assert "space" in str(e).lower() or "quota" in str(e).lower()


def example_memory_limit_test():
    """Example: Test system behavior with memory constraints."""
    injector = FaultInjector()
    
    # Set a 500MB memory limit
    with injector.inject_memory_limit(500):
        try:
            # Try to allocate large amount of memory
            large_list = [0] * (100 * 1024 * 1024)  # Try to allocate 100M integers
            print("Memory allocation succeeded")
        except MemoryError:
            print("Memory allocation failed as expected")


def example_permission_error_test():
    """Example: Test system behavior with permission errors."""
    injector = FaultInjector()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_dir = Path(tmpdir) / "output"
        output_dir.mkdir()
        
        # Make output directory read-only
        with injector.inject_permission_error(str(output_dir)):
            try:
                # Try to create a file in read-only directory
                test_file = output_dir / "test.txt"
                test_file.write_text("content")
                print("Write succeeded (unexpected)")
            except PermissionError as e:
                print(f"Write failed as expected: {e}")
                # Verify error message mentions permissions
                assert "permission" in str(e).lower()


def example_corruption_test():
    """Example: Test system behavior with corrupted files."""
    injector = FaultInjector()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        model_file = Path(tmpdir) / "model.bin"
        model_file.write_bytes(b"MODEL_DATA" * 1000)
        
        # Corrupt the model file
        injector.inject_corruption(str(model_file), corruption_type="modify")
        
        # Try to load the corrupted model
        try:
            content = model_file.read_bytes()
            # Verify content is corrupted
            assert content != b"MODEL_DATA" * 1000
            print("Model file is corrupted as expected")
        except Exception as e:
            print(f"Failed to read corrupted file: {e}")


def example_signal_interruption_test():
    """Example: Test system behavior when interrupted by signal."""
    injector = FaultInjector()
    
    # Set up signal handler
    interrupted = []
    
    def handler(signum, frame):
        interrupted.append(True)
        print("Received interrupt signal")
    
    original_handler = signal.signal(signal.SIGUSR1, handler)
    
    try:
        # Schedule signal to be sent after 0.5 seconds
        injector.inject_signal(signal.SIGUSR1, delay_seconds=0.5)
        
        # Simulate long-running operation
        import time
        time.sleep(1.0)
        
        # Verify signal was received
        assert len(interrupted) > 0, "Signal should have been received"
        print("Signal interruption test passed")
    
    finally:
        signal.signal(signal.SIGUSR1, original_handler)


def example_delay_injection_test():
    """Example: Test system behavior with slow operations."""
    injector = FaultInjector()
    
    import time
    
    start = time.time()
    
    # Inject 1 second delay
    with injector.inject_delay(1.0):
        # This block will be delayed by 1 second
        pass
    
    elapsed = time.time() - start
    assert elapsed >= 1.0, "Delay should be at least 1 second"
    print(f"Delay injection test passed (elapsed: {elapsed:.2f}s)")


def example_nested_fault_injection():
    """Example: Test with multiple simultaneous faults."""
    injector = FaultInjector()
    
    with tempfile.TemporaryDirectory() as tmpdir:
        output_file = Path(tmpdir) / "output.txt"
        output_file.write_text("initial content")
        
        # Combine multiple fault injections
        with injector.inject_disk_full(tmpdir, threshold_bytes=1024*1024):
            with injector.inject_permission_error(str(output_file)):
                try:
                    # Try to write to read-only file on full disk
                    output_file.write_text("new content")
                    print("Write succeeded (unexpected)")
                except (PermissionError, OSError) as e:
                    print(f"Write failed as expected: {e}")


if __name__ == "__main__":
    print("Running Fault Injector Examples\n")
    
    print("1. Disk Full Test")
    example_disk_full_test()
    print()
    
    print("2. Memory Limit Test")
    example_memory_limit_test()
    print()
    
    print("3. Permission Error Test")
    example_permission_error_test()
    print()
    
    print("4. Corruption Test")
    example_corruption_test()
    print()
    
    print("5. Signal Interruption Test")
    example_signal_interruption_test()
    print()
    
    print("6. Delay Injection Test")
    example_delay_injection_test()
    print()
    
    print("7. Nested Fault Injection Test")
    example_nested_fault_injection()
    print()
    
    print("All examples completed successfully!")
