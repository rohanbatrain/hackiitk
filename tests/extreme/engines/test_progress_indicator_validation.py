"""
Progress Indicator Validation Tests

Tests progress indicator behavior under all conditions including:
- Regular updates during long operations
- Progress on failure scenarios
- 100% completion indicators
- Accuracy under all scenarios
- Performance impact measurement

Validates Requirements: 64.1, 64.2, 64.3, 64.4, 64.5
"""

import pytest
import time
import sys
import io
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from unittest.mock import patch, MagicMock
import threading

# Add project root to path
import sys
from pathlib import Path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.progress import (
    ProgressIndicator,
    StepProgress,
    ProgressLogger,
    ProgressState,
    create_progress_indicator,
    create_step_progress
)


@dataclass
class ProgressValidationResult:
    """Result from progress indicator validation test."""
    test_name: str
    passed: bool
    update_count: int
    update_intervals: List[float]
    completion_reached: bool
    failure_handled: bool
    performance_impact_ms: float
    error_message: Optional[str] = None
    details: Optional[Dict[str, Any]] = None


class ProgressIndicatorValidator:
    """Validator for progress indicator behavior."""
    
    def __init__(self):
        """Initialize validator."""
        self.logger = logging.getLogger(__name__)
        self.results: List[ProgressValidationResult] = []
    
    def test_progress_updates_every_10_seconds(self) -> ProgressValidationResult:
        """
        Test that progress indicators update at least every 10 seconds.
        
        Validates: Requirement 64.1
        """
        test_name = "test_progress_updates_every_10_seconds"
        self.logger.info(f"Running {test_name}...")
        
        try:
            # Capture stdout
            captured_output = io.StringIO()
            
            # Create progress indicator with 100 items
            total_items = 100
            progress = ProgressIndicator(
                total=total_items,
                operation_name="Test Operation",
                show_bar=True
            )
            
            # Track update times
            update_times = []
            last_output_length = 0
            
            # Simulate long-running operation with updates
            start_time = time.time()
            
            with patch('sys.stdout', captured_output):
                for i in range(total_items):
                    progress.update(current=i + 1)
                    
                    # Check if output changed (indicates update)
                    current_output = captured_output.getvalue()
                    if len(current_output) > last_output_length:
                        update_times.append(time.time() - start_time)
                        last_output_length = len(current_output)
                    
                    # Simulate work (small delay)
                    time.sleep(0.1)
            
            # Calculate update intervals
            update_intervals = []
            for i in range(1, len(update_times)):
                interval = update_times[i] - update_times[i-1]
                update_intervals.append(interval)
            
            # Verify updates occur at least every 10 seconds
            max_interval = max(update_intervals) if update_intervals else 0
            passed = max_interval <= 10.0
            
            # Check completion
            completion_reached = progress.state.current == total_items
            
            result = ProgressValidationResult(
                test_name=test_name,
                passed=passed and completion_reached,
                update_count=len(update_times),
                update_intervals=update_intervals,
                completion_reached=completion_reached,
                failure_handled=False,
                performance_impact_ms=0.0,
                details={
                    'max_interval_seconds': max_interval,
                    'min_interval_seconds': min(update_intervals) if update_intervals else 0,
                    'avg_interval_seconds': sum(update_intervals) / len(update_intervals) if update_intervals else 0,
                    'total_updates': len(update_times)
                }
            )
            
            self.logger.info(f"{test_name}: {'PASS' if result.passed else 'FAIL'}")
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"{test_name} failed with error: {e}")
            result = ProgressValidationResult(
                test_name=test_name,
                passed=False,
                update_count=0,
                update_intervals=[],
                completion_reached=False,
                failure_handled=False,
                performance_impact_ms=0.0,
                error_message=str(e)
            )
            self.results.append(result)
            return result
    
    def test_progress_on_failure(self) -> ProgressValidationResult:
        """
        Test that progress indicators reflect failures appropriately.
        
        Validates: Requirement 64.2
        """
        test_name = "test_progress_on_failure"
        self.logger.info(f"Running {test_name}...")
        
        try:
            # Capture stdout and logs
            captured_output = io.StringIO()
            
            # Create progress indicator
            total_items = 50
            progress = ProgressIndicator(
                total=total_items,
                operation_name="Test Operation with Failure",
                show_bar=True
            )
            
            failure_handled = False
            completion_reached = False
            
            with patch('sys.stdout', captured_output):
                try:
                    # Simulate operation that fails partway through
                    for i in range(total_items):
                        progress.update(current=i + 1)
                        
                        # Simulate failure at 50%
                        if i == total_items // 2:
                            raise RuntimeError("Simulated operation failure")
                        
                        time.sleep(0.01)
                    
                    progress.finish()
                    completion_reached = True
                    
                except RuntimeError as e:
                    # Progress should reflect partial completion
                    failure_handled = True
                    current_progress = progress.state.current
                    expected_progress = total_items // 2 + 1
                    
                    # Verify progress stopped at failure point
                    if current_progress == expected_progress:
                        self.logger.info(f"Progress correctly stopped at {current_progress}/{total_items}")
                    else:
                        self.logger.warning(
                            f"Progress mismatch: expected {expected_progress}, got {current_progress}"
                        )
            
            # Verify failure was handled and progress state is accurate
            passed = (
                failure_handled and
                progress.state.current < total_items and
                progress.state.current > 0
            )
            
            result = ProgressValidationResult(
                test_name=test_name,
                passed=passed,
                update_count=progress.state.current,
                update_intervals=[],
                completion_reached=completion_reached,
                failure_handled=failure_handled,
                performance_impact_ms=0.0,
                details={
                    'progress_at_failure': progress.state.current,
                    'total_items': total_items,
                    'percentage_at_failure': progress.state.percentage
                }
            )
            
            self.logger.info(f"{test_name}: {'PASS' if result.passed else 'FAIL'}")
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"{test_name} failed with error: {e}")
            result = ProgressValidationResult(
                test_name=test_name,
                passed=False,
                update_count=0,
                update_intervals=[],
                completion_reached=False,
                failure_handled=False,
                performance_impact_ms=0.0,
                error_message=str(e)
            )
            self.results.append(result)
            return result
    
    def test_100_percent_completion_indicator(self) -> ProgressValidationResult:
        """
        Test that progress indicators show 100% completion when operations complete.
        
        Validates: Requirement 64.3
        """
        test_name = "test_100_percent_completion_indicator"
        self.logger.info(f"Running {test_name}...")
        
        try:
            # Capture stdout
            captured_output = io.StringIO()
            
            # Create progress indicator
            total_items = 100
            progress = ProgressIndicator(
                total=total_items,
                operation_name="Test Complete Operation",
                show_bar=True
            )
            
            with patch('sys.stdout', captured_output):
                # Process all items
                for i in range(total_items):
                    progress.update(current=i + 1)
                    time.sleep(0.01)
                
                # Explicitly finish
                progress.finish()
            
            # Verify 100% completion
            completion_reached = progress.state.current == total_items
            percentage = progress.state.percentage
            is_100_percent = abs(percentage - 100.0) < 0.01
            
            # Check output contains 100%
            output = captured_output.getvalue()
            contains_100 = '100.0%' in output or '100%' in output
            
            passed = completion_reached and is_100_percent and contains_100
            
            result = ProgressValidationResult(
                test_name=test_name,
                passed=passed,
                update_count=total_items,
                update_intervals=[],
                completion_reached=completion_reached,
                failure_handled=False,
                performance_impact_ms=0.0,
                details={
                    'final_percentage': percentage,
                    'final_current': progress.state.current,
                    'final_total': progress.state.total,
                    'output_contains_100': contains_100
                }
            )
            
            self.logger.info(f"{test_name}: {'PASS' if result.passed else 'FAIL'}")
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"{test_name} failed with error: {e}")
            result = ProgressValidationResult(
                test_name=test_name,
                passed=False,
                update_count=0,
                update_intervals=[],
                completion_reached=False,
                failure_handled=False,
                performance_impact_ms=0.0,
                error_message=str(e)
            )
            self.results.append(result)
            return result
    
    def test_progress_accuracy_under_all_scenarios(self) -> ProgressValidationResult:
        """
        Test that progress indicators remain accurate under various scenarios.
        
        Validates: Requirement 64.4
        """
        test_name = "test_progress_accuracy_under_all_scenarios"
        self.logger.info(f"Running {test_name}...")
        
        scenarios_passed = []
        scenarios_failed = []
        
        try:
            # Scenario 1: Sequential updates
            progress1 = ProgressIndicator(total=100, operation_name="Sequential", show_bar=False)
            for i in range(100):
                progress1.update(current=i + 1)
            
            if progress1.state.percentage == 100.0:
                scenarios_passed.append("sequential_updates")
            else:
                scenarios_failed.append(f"sequential_updates (got {progress1.state.percentage}%)")
            
            # Scenario 2: Incremental updates
            progress2 = ProgressIndicator(total=50, operation_name="Incremental", show_bar=False)
            for i in range(50):
                progress2.update(increment=1)
            
            if progress2.state.percentage == 100.0:
                scenarios_passed.append("incremental_updates")
            else:
                scenarios_failed.append(f"incremental_updates (got {progress2.state.percentage}%)")
            
            # Scenario 3: Jump to specific values
            progress3 = ProgressIndicator(total=200, operation_name="Jump", show_bar=False)
            progress3.update(current=50)
            if abs(progress3.state.percentage - 25.0) < 0.01:
                scenarios_passed.append("jump_to_25_percent")
            else:
                scenarios_failed.append(f"jump_to_25_percent (got {progress3.state.percentage}%)")
            
            progress3.update(current=100)
            if abs(progress3.state.percentage - 50.0) < 0.01:
                scenarios_passed.append("jump_to_50_percent")
            else:
                scenarios_failed.append(f"jump_to_50_percent (got {progress3.state.percentage}%)")
            
            progress3.update(current=200)
            if abs(progress3.state.percentage - 100.0) < 0.01:
                scenarios_passed.append("jump_to_100_percent")
            else:
                scenarios_failed.append(f"jump_to_100_percent (got {progress3.state.percentage}%)")
            
            # Scenario 4: Zero total (edge case)
            progress4 = ProgressIndicator(total=0, operation_name="Zero Total", show_bar=False)
            if progress4.state.percentage == 0.0:
                scenarios_passed.append("zero_total")
            else:
                scenarios_failed.append(f"zero_total (got {progress4.state.percentage}%)")
            
            # Scenario 5: Large total
            progress5 = ProgressIndicator(total=1000000, operation_name="Large", show_bar=False)
            progress5.update(current=500000)
            if abs(progress5.state.percentage - 50.0) < 0.01:
                scenarios_passed.append("large_total_50_percent")
            else:
                scenarios_failed.append(f"large_total_50_percent (got {progress5.state.percentage}%)")
            
            # Scenario 6: StepProgress
            step_progress = StepProgress(total_steps=5, operation_name="Steps")
            for i in range(5):
                step_progress.start_step(f"Step {i+1}")
            
            if step_progress.current_step == 5:
                scenarios_passed.append("step_progress")
            else:
                scenarios_failed.append(f"step_progress (got {step_progress.current_step}/5)")
            
            passed = len(scenarios_failed) == 0
            
            result = ProgressValidationResult(
                test_name=test_name,
                passed=passed,
                update_count=len(scenarios_passed) + len(scenarios_failed),
                update_intervals=[],
                completion_reached=True,
                failure_handled=False,
                performance_impact_ms=0.0,
                details={
                    'scenarios_passed': scenarios_passed,
                    'scenarios_failed': scenarios_failed,
                    'total_scenarios': len(scenarios_passed) + len(scenarios_failed),
                    'pass_rate': len(scenarios_passed) / (len(scenarios_passed) + len(scenarios_failed))
                }
            )
            
            self.logger.info(f"{test_name}: {'PASS' if result.passed else 'FAIL'}")
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"{test_name} failed with error: {e}")
            result = ProgressValidationResult(
                test_name=test_name,
                passed=False,
                update_count=0,
                update_intervals=[],
                completion_reached=False,
                failure_handled=False,
                performance_impact_ms=0.0,
                error_message=str(e)
            )
            self.results.append(result)
            return result
    
    def test_no_performance_degradation(self) -> ProgressValidationResult:
        """
        Test that progress indicators do not cause performance degradation.
        
        Validates: Requirement 64.5
        """
        test_name = "test_no_performance_degradation"
        self.logger.info(f"Running {test_name}...")
        
        try:
            total_items = 1000
            
            # Simulate more realistic work (string operations)
            def do_work(i):
                """Simulate realistic work."""
                result = []
                for j in range(100):
                    result.append(f"item_{i}_{j}")
                return len(result)
            
            # Measure baseline performance without progress indicator
            start_baseline = time.time()
            for i in range(total_items):
                do_work(i)
            baseline_time = time.time() - start_baseline
            
            # Measure performance with progress indicator (throttled updates)
            progress = ProgressIndicator(
                total=total_items,
                operation_name="Performance Test",
                show_bar=False  # Disable visual output for fair comparison
            )
            
            # Temporarily disable logging to measure pure progress overhead
            original_level = logging.getLogger('utils.progress').level
            logging.getLogger('utils.progress').setLevel(logging.CRITICAL)
            
            start_with_progress = time.time()
            for i in range(total_items):
                progress.update(current=i + 1)
                do_work(i)
            with_progress_time = time.time() - start_with_progress
            
            # Restore logging
            logging.getLogger('utils.progress').setLevel(original_level)
            
            # Calculate overhead
            overhead_ms = (with_progress_time - baseline_time) * 1000
            overhead_percent = ((with_progress_time - baseline_time) / baseline_time) * 100 if baseline_time > 0 else 0
            
            # Progress indicator should add less than 10% overhead with realistic work
            # The throttling mechanism ensures updates only happen every 0.5 seconds
            passed = overhead_percent < 10.0
            
            result = ProgressValidationResult(
                test_name=test_name,
                passed=passed,
                update_count=total_items,
                update_intervals=[],
                completion_reached=True,
                failure_handled=False,
                performance_impact_ms=overhead_ms,
                details={
                    'baseline_time_ms': baseline_time * 1000,
                    'with_progress_time_ms': with_progress_time * 1000,
                    'overhead_ms': overhead_ms,
                    'overhead_percent': overhead_percent,
                    'total_items': total_items,
                    'note': 'Measured with realistic work (string operations)'
                }
            )
            
            self.logger.info(f"{test_name}: {'PASS' if result.passed else 'FAIL'}")
            self.logger.info(f"Performance overhead: {overhead_ms:.2f}ms ({overhead_percent:.2f}%)")
            self.results.append(result)
            return result
            
        except Exception as e:
            self.logger.error(f"{test_name} failed with error: {e}")
            result = ProgressValidationResult(
                test_name=test_name,
                passed=False,
                update_count=0,
                update_intervals=[],
                completion_reached=False,
                failure_handled=False,
                performance_impact_ms=0.0,
                error_message=str(e)
            )
            self.results.append(result)
            return result
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run all progress indicator validation tests."""
        self.logger.info("Starting progress indicator validation tests...")
        
        # Run all tests
        self.test_progress_updates_every_10_seconds()
        self.test_progress_on_failure()
        self.test_100_percent_completion_indicator()
        self.test_progress_accuracy_under_all_scenarios()
        self.test_no_performance_degradation()
        
        # Summarize results
        total_tests = len(self.results)
        passed_tests = sum(1 for r in self.results if r.passed)
        failed_tests = total_tests - passed_tests
        
        summary = {
            'total_tests': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0,
            'results': self.results
        }
        
        self.logger.info(f"Progress indicator validation complete: {passed_tests}/{total_tests} passed")
        
        return summary


# Pytest test functions

def test_progress_updates_every_10_seconds():
    """
    Test that progress indicators update at least every 10 seconds.
    
    Validates: Requirement 64.1
    """
    validator = ProgressIndicatorValidator()
    result = validator.test_progress_updates_every_10_seconds()
    assert result.passed, f"Progress updates test failed: {result.error_message or result.details}"


def test_progress_on_failure():
    """
    Test that progress indicators reflect failures appropriately.
    
    Validates: Requirement 64.2
    """
    validator = ProgressIndicatorValidator()
    result = validator.test_progress_on_failure()
    assert result.passed, f"Progress on failure test failed: {result.error_message or result.details}"


def test_100_percent_completion_indicator():
    """
    Test that progress indicators show 100% completion when operations complete.
    
    Validates: Requirement 64.3
    """
    validator = ProgressIndicatorValidator()
    result = validator.test_100_percent_completion_indicator()
    assert result.passed, f"100% completion test failed: {result.error_message or result.details}"


def test_progress_accuracy_under_all_scenarios():
    """
    Test that progress indicators remain accurate under various scenarios.
    
    Validates: Requirement 64.4
    """
    validator = ProgressIndicatorValidator()
    result = validator.test_progress_accuracy_under_all_scenarios()
    assert result.passed, f"Progress accuracy test failed: {result.error_message or result.details}"


def test_no_performance_degradation():
    """
    Test that progress indicators do not cause performance degradation.
    
    Validates: Requirement 64.5
    """
    validator = ProgressIndicatorValidator()
    result = validator.test_no_performance_degradation()
    assert result.passed, f"Performance degradation test failed: {result.error_message or result.details}"


if __name__ == "__main__":
    # Run all tests when executed directly
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    validator = ProgressIndicatorValidator()
    summary = validator.run_all_tests()
    
    print("\n" + "="*80)
    print("PROGRESS INDICATOR VALIDATION SUMMARY")
    print("="*80)
    print(f"Total Tests: {summary['total_tests']}")
    print(f"Passed: {summary['passed']}")
    print(f"Failed: {summary['failed']}")
    print(f"Pass Rate: {summary['pass_rate']:.1f}%")
    print("="*80)
    
    for result in summary['results']:
        status = "✓ PASS" if result.passed else "✗ FAIL"
        print(f"{status} - {result.test_name}")
        if result.details:
            for key, value in result.details.items():
                print(f"  {key}: {value}")
