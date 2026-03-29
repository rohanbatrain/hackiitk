"""
Property Test 45: LLM Generation Retry

Validates Requirement 15.7:
- Failed LLM generations retry up to 3 times
- Exponential backoff is applied between retries
- All retries exhausted before final failure
"""

import pytest
from hypothesis import given, strategies as st, settings
import time
from unittest.mock import Mock, patch
from typing import Callable

from utils.error_handler import retry_with_backoff, RetryableError


# ============================================================================
# Test Strategies
# ============================================================================

@st.composite
def retry_scenario_strategy(draw):
    """Generate retry scenarios."""
    failure_count = draw(st.integers(min_value=0, max_value=5))
    exception_type = draw(st.sampled_from([
        RetryableError,
        ConnectionError,
        TimeoutError
    ]))
    
    return {
        'failure_count': failure_count,
        'exception_type': exception_type
    }


# ============================================================================
# Property Tests
# ============================================================================

@given(scenario=retry_scenario_strategy())
@settings(max_examples=50, deadline=10000)
def test_llm_generation_retries_up_to_3_times(scenario):
    """
    Property 45: LLM Generation Retry
    
    Test that failed LLM generations:
    1. Retry up to 3 times (4 total attempts)
    2. Apply exponential backoff between retries
    3. Raise exception after all retries exhausted
    4. Succeed if any attempt succeeds
    """
    failure_count = scenario['failure_count']
    exception_type = scenario['exception_type']
    
    # Track attempts
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,  # Short delay for testing
        backoff_factor=2.0,
        exceptions=(RetryableError, ConnectionError, TimeoutError)
    )
    def mock_llm_generate(prompt: str) -> str:
        """Mock LLM generation that fails a specified number of times."""
        attempt_num = len(attempts)
        attempts.append(time.time())
        
        if attempt_num < failure_count:
            # Fail this attempt
            if exception_type == RetryableError:
                raise RetryableError('llm_generate', 'Simulated failure')
            elif exception_type == ConnectionError:
                raise ConnectionError('Simulated connection error')
            else:
                raise TimeoutError('Simulated timeout')
        else:
            # Succeed
            return f"Generated response for: {prompt}"
    
    # Test the retry behavior
    if failure_count <= 3:
        # Should eventually succeed
        result = mock_llm_generate("test prompt")
        assert result == "Generated response for: test prompt"
        assert len(attempts) == failure_count + 1, \
            f"Should have {failure_count + 1} attempts (including success)"
    else:
        # Should fail after 4 attempts (initial + 3 retries)
        with pytest.raises((RetryableError, ConnectionError, TimeoutError)):
            mock_llm_generate("test prompt")
        assert len(attempts) == 4, \
            "Should have exactly 4 attempts (initial + 3 retries)"
    
    # Verify exponential backoff (if there were retries)
    if len(attempts) > 1:
        for i in range(1, len(attempts)):
            delay = attempts[i] - attempts[i-1]
            # Expected delay: initial_delay * (backoff_factor ** (i-1))
            expected_delay = 0.01 * (2.0 ** (i-1))
            # Allow some tolerance for timing
            assert delay >= expected_delay * 0.8, \
                f"Delay between attempts should follow exponential backoff"


def test_retry_with_immediate_success():
    """
    Test that no retries occur when operation succeeds immediately.
    
    Verifies that retry logic doesn't add overhead to successful operations.
    """
    attempts = []
    
    @retry_with_backoff(max_retries=3, initial_delay=0.1)
    def successful_operation():
        attempts.append(1)
        return "success"
    
    result = successful_operation()
    
    assert result == "success"
    assert len(attempts) == 1, "Should only attempt once for immediate success"


def test_retry_with_all_failures():
    """
    Test that all retries are exhausted before final failure.
    
    Verifies Requirement 15.7 for retry exhaustion.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(RetryableError,)
    )
    def always_fails():
        attempts.append(1)
        raise RetryableError('test_op', 'Always fails')
    
    with pytest.raises(RetryableError):
        always_fails()
    
    assert len(attempts) == 4, \
        "Should attempt 4 times total (initial + 3 retries)"


def test_retry_with_success_on_second_attempt():
    """
    Test that operation succeeds on retry after initial failure.
    
    Verifies that retry logic enables recovery from transient errors.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(RetryableError,)
    )
    def fails_once():
        attempts.append(1)
        if len(attempts) == 1:
            raise RetryableError('test_op', 'First attempt fails')
        return "success on retry"
    
    result = fails_once()
    
    assert result == "success on retry"
    assert len(attempts) == 2, "Should succeed on second attempt"


def test_retry_with_success_on_third_attempt():
    """
    Test that operation succeeds on third attempt (second retry).
    
    Verifies that multiple retries work correctly.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(RetryableError,)
    )
    def fails_twice():
        attempts.append(1)
        if len(attempts) <= 2:
            raise RetryableError('test_op', f'Attempt {len(attempts)} fails')
        return "success on third attempt"
    
    result = fails_twice()
    
    assert result == "success on third attempt"
    assert len(attempts) == 3, "Should succeed on third attempt"


def test_retry_with_success_on_fourth_attempt():
    """
    Test that operation succeeds on fourth attempt (third retry).
    
    Verifies that all 3 retries are available.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(RetryableError,)
    )
    def fails_three_times():
        attempts.append(1)
        if len(attempts) <= 3:
            raise RetryableError('test_op', f'Attempt {len(attempts)} fails')
        return "success on fourth attempt"
    
    result = fails_three_times()
    
    assert result == "success on fourth attempt"
    assert len(attempts) == 4, "Should succeed on fourth attempt (last retry)"


def test_exponential_backoff_timing():
    """
    Test that exponential backoff delays increase correctly.
    
    Verifies that delays follow the pattern: initial, initial*2, initial*4, etc.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.05,
        backoff_factor=2.0,
        exceptions=(RetryableError,)
    )
    def always_fails():
        attempts.append(time.time())
        raise RetryableError('test_op', 'Always fails')
    
    with pytest.raises(RetryableError):
        always_fails()
    
    # Verify delays between attempts
    assert len(attempts) == 4
    
    # First retry: ~0.05s delay
    delay1 = attempts[1] - attempts[0]
    assert 0.04 <= delay1 <= 0.15, f"First retry delay should be ~0.05s, got {delay1:.3f}s"
    
    # Second retry: ~0.10s delay (0.05 * 2)
    delay2 = attempts[2] - attempts[1]
    assert 0.08 <= delay2 <= 0.25, f"Second retry delay should be ~0.10s, got {delay2:.3f}s"
    
    # Third retry: ~0.20s delay (0.05 * 4)
    delay3 = attempts[3] - attempts[2]
    assert 0.15 <= delay3 <= 0.40, f"Third retry delay should be ~0.20s, got {delay3:.3f}s"


def test_retry_only_catches_specified_exceptions():
    """
    Test that retry logic only catches specified exception types.
    
    Verifies that unexpected exceptions are not retried.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(RetryableError,)
    )
    def raises_unexpected_error():
        attempts.append(1)
        raise ValueError("Unexpected error type")
    
    # Should raise immediately without retries
    with pytest.raises(ValueError):
        raises_unexpected_error()
    
    assert len(attempts) == 1, \
        "Should not retry for exception types not in exceptions tuple"


def test_retry_with_multiple_exception_types():
    """
    Test that retry logic handles multiple exception types.
    
    Verifies that all specified exception types trigger retries.
    """
    attempts = []
    exception_sequence = [
        ConnectionError("Connection failed"),
        TimeoutError("Request timed out"),
        RetryableError("test_op", "Retryable error"),
        None  # Success on 4th attempt
    ]
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(RetryableError, ConnectionError, TimeoutError)
    )
    def raises_different_errors():
        attempt_num = len(attempts)
        attempts.append(1)
        
        if attempt_num < len(exception_sequence) - 1:
            raise exception_sequence[attempt_num]
        return "success"
    
    result = raises_different_errors()
    
    assert result == "success"
    assert len(attempts) == 4, "Should retry for all specified exception types"


@given(
    max_retries=st.integers(min_value=0, max_value=5),
    initial_delay=st.floats(min_value=0.01, max_value=0.1),
    backoff_factor=st.floats(min_value=1.5, max_value=3.0)
)
@settings(max_examples=20, deadline=10000)
def test_retry_configuration_parameters(max_retries, initial_delay, backoff_factor):
    """
    Property: Retry configuration parameters are respected.
    
    Verifies that max_retries, initial_delay, and backoff_factor work correctly.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=max_retries,
        initial_delay=initial_delay,
        backoff_factor=backoff_factor,
        exceptions=(RetryableError,)
    )
    def always_fails():
        attempts.append(time.time())
        raise RetryableError('test_op', 'Always fails')
    
    with pytest.raises(RetryableError):
        always_fails()
    
    # Verify correct number of attempts
    expected_attempts = max_retries + 1
    assert len(attempts) == expected_attempts, \
        f"Should have {expected_attempts} attempts with max_retries={max_retries}"


def test_retry_preserves_function_metadata():
    """
    Test that retry decorator preserves function metadata.
    
    Verifies that functools.wraps is used correctly.
    """
    @retry_with_backoff(max_retries=3)
    def documented_function():
        """This function has documentation."""
        return "result"
    
    assert documented_function.__name__ == "documented_function"
    assert "documentation" in documented_function.__doc__


def test_retry_with_function_arguments():
    """
    Test that retry decorator works with functions that take arguments.
    
    Verifies that arguments are passed correctly through retries.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=2,
        initial_delay=0.01,
        exceptions=(RetryableError,)
    )
    def function_with_args(x: int, y: str, z: bool = False):
        attempts.append((x, y, z))
        if len(attempts) == 1:
            raise RetryableError('test_op', 'First attempt fails')
        return f"x={x}, y={y}, z={z}"
    
    result = function_with_args(42, "test", z=True)
    
    assert result == "x=42, y=test, z=True"
    assert len(attempts) == 2
    # Verify arguments preserved across retries
    assert attempts[0] == (42, "test", True)
    assert attempts[1] == (42, "test", True)


def test_retry_with_return_values():
    """
    Test that retry decorator preserves return values.
    
    Verifies that successful operations return correct values.
    """
    @retry_with_backoff(max_retries=3, initial_delay=0.01)
    def returns_complex_value():
        return {
            'status': 'success',
            'data': [1, 2, 3],
            'nested': {'key': 'value'}
        }
    
    result = returns_complex_value()
    
    assert result['status'] == 'success'
    assert result['data'] == [1, 2, 3]
    assert result['nested']['key'] == 'value'


def test_llm_generation_retry_integration():
    """
    Integration test simulating real LLM generation with retries.
    
    Verifies that retry logic works in realistic LLM generation scenario.
    """
    attempts = []
    
    @retry_with_backoff(
        max_retries=3,
        initial_delay=0.01,
        exceptions=(RetryableError, ConnectionError)
    )
    def mock_llm_generate(prompt: str, temperature: float = 0.1, max_tokens: int = 512):
        """Mock LLM generation that may fail transiently."""
        attempts.append({
            'prompt': prompt,
            'temperature': temperature,
            'max_tokens': max_tokens,
            'timestamp': time.time()
        })
        
        # Simulate transient failure on first attempt
        if len(attempts) == 1:
            raise ConnectionError("LLM backend temporarily unavailable")
        
        # Succeed on retry
        return f"Generated response for prompt: {prompt[:50]}..."
    
    # Call with realistic parameters
    result = mock_llm_generate(
        prompt="Analyze the following policy section for gaps...",
        temperature=0.1,
        max_tokens=512
    )
    
    assert "Generated response" in result
    assert len(attempts) == 2, "Should succeed on second attempt"
    
    # Verify parameters preserved across retry
    assert attempts[0]['temperature'] == 0.1
    assert attempts[1]['temperature'] == 0.1
    assert attempts[0]['max_tokens'] == 512
    assert attempts[1]['max_tokens'] == 512


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
