# Fault Injector Implementation

## Overview

The Fault Injector provides mechanisms for simulating system failures during chaos testing. It enables testing of error handling, graceful degradation, and recovery mechanisms under adverse conditions.

## Features

### 1. Disk Full Simulation (`inject_disk_full`)
- Creates a large filler file to consume disk space
- Configurable threshold for remaining space
- Automatic cleanup after testing
- **Requirements**: 3.1, 3.2, 3.3, 4.1, 4.2, 7.1, 7.2

### 2. Memory Limit Simulation (`inject_memory_limit`)
- Uses `resource.setrlimit` to set memory limits
- Works on Unix-like systems (macOS, Linux)
- Gracefully handles systems where limits cannot be set
- Automatic restoration of original limits
- **Requirements**: 4.1, 4.2, 4.3

### 3. Permission Error Simulation (`inject_permission_error`)
- Makes files/directories read-only
- Simulates permission denied errors
- Automatic restoration of original permissions
- **Requirements**: 7.1, 7.2, 7.3

### 4. File Corruption (`inject_corruption`)
- Three corruption types:
  - `modify`: Corrupts random bytes in the file
  - `truncate`: Truncates file to half its size
  - `delete`: Deletes the file entirely
- **Requirements**: 5.1, 5.2, 20.1

### 5. Signal Injection (`inject_signal`)
- Sends signals to the current process
- Configurable delay before signal delivery
- Useful for testing interruption handling (SIGINT, SIGTERM, SIGKILL)
- **Requirements**: 6.1, 6.2, 6.3

### 6. Delay Injection (`inject_delay`)
- Introduces artificial delays
- Simulates slow operations
- **Requirements**: 20.1

## Usage Examples

```python
from tests.extreme.support import FaultInjector

injector = FaultInjector()

# Simulate disk full
with injector.inject_disk_full("/tmp/test", threshold_bytes=1024*1024):
    # Code that writes to disk
    pass

# Simulate memory limit
with injector.inject_memory_limit(100):  # 100MB limit
    # Code that allocates memory
    pass

# Simulate permission error
with injector.inject_permission_error("/path/to/file"):
    # Code that tries to write to file
    pass

# Corrupt a file
injector.inject_corruption("/path/to/file", corruption_type="modify")

# Send signal after delay
injector.inject_signal(signal.SIGINT, delay_seconds=1.0)

# Inject delay
with injector.inject_delay(0.5):
    # Code that should be delayed
    pass
```

## Cleanup Mechanisms

All context managers ensure proper cleanup:
- Disk full: Removes filler files
- Memory limit: Restores original limits
- Permission error: Restores original permissions

Cleanup happens even if exceptions are raised during testing.

## Platform Support

- **Disk Full**: All platforms (Unix, macOS, Windows)
- **Memory Limit**: Unix-like systems only (macOS, Linux)
- **Permission Error**: All platforms
- **File Corruption**: All platforms
- **Signal Injection**: All platforms
- **Delay Injection**: All platforms

## Testing

Comprehensive unit tests cover:
- All injection mechanisms
- Cleanup after normal execution
- Cleanup after exceptions
- Nested injections
- Platform-specific behavior

Run tests with:
```bash
python -m pytest tests/extreme/support/test_fault_injector.py -v
```

## Implementation Notes

### Disk Full Simulation
- Caps filler file at 100MB to avoid actually filling the disk
- This is a simulation for testing purposes, not a real disk fill
- Provides enough space reduction to trigger error handling

### Memory Limit Simulation
- On macOS, memory limits may not work due to system restrictions
- The implementation gracefully handles systems where limits cannot be set
- Uses large default limits to avoid issues with system processes

### Safety Considerations
- All operations are designed to be safe for testing environments
- Cleanup is guaranteed through context managers
- Best-effort cleanup even on errors
- No permanent system modifications
