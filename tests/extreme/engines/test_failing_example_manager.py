"""
Unit Tests for Failing Example Manager

Tests the FailingExampleManager class and its methods.
"""

import pytest
import tempfile
import time
from pathlib import Path

from tests.extreme.engines.failing_example_manager import (
    FailingExampleManager,
    FailingExample,
    RegressionTestSuite
)


@pytest.fixture
def examples_dir():
    """Create temporary examples directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def manager(examples_dir):
    """Create FailingExampleManager instance."""
    return FailingExampleManager(examples_dir)


def test_manager_initialization(manager, examples_dir):
    """Test FailingExampleManager initialization."""
    assert manager.examples_dir == examples_dir
    assert manager.raw_examples_dir.exists()
    assert manager.regression_suites_dir.exists()
    assert manager.history_dir.exists()
    assert manager.hypothesis_db_dir.exists()


def test_save_failing_example(manager):
    """Test saving a failing example."""
    filepath = manager.save_failing_example(
        property_name="test_property",
        example_data={"input": 42, "expected": 84, "actual": 85},
        error_message="Assertion failed: 84 != 85",
        test_file="test_example.py",
        line_number=10
    )
    
    assert filepath.exists()
    assert filepath.parent == manager.raw_examples_dir
    assert "test_property" in filepath.name


def test_load_failing_examples(manager):
    """Test loading failing examples."""
    # Save some examples
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test1.py"
    )
    
    manager.save_failing_example(
        property_name="prop2",
        example_data={"x": 2},
        error_message="Error 2",
        test_file="test2.py"
    )
    
    # Load all examples
    examples = manager.load_failing_examples()
    assert len(examples) == 2
    
    # Load filtered examples
    prop1_examples = manager.load_failing_examples(property_name="prop1")
    assert len(prop1_examples) == 1
    assert prop1_examples[0].property_name == "prop1"


def test_create_regression_suite(manager):
    """Test creating a regression test suite."""
    # Save some examples
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test1.py"
    )
    
    manager.save_failing_example(
        property_name="prop2",
        example_data={"x": 2},
        error_message="Error 2",
        test_file="test2.py"
    )
    
    # Create suite
    suite = manager.create_regression_suite("test_suite")
    
    assert suite.suite_name == "test_suite"
    assert suite.total_examples == 2
    assert len(suite.examples) == 2


def test_load_regression_suite(manager):
    """Test loading a regression test suite."""
    # Create and save a suite
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test1.py"
    )
    
    created_suite = manager.create_regression_suite("test_suite")
    
    # Load the suite
    loaded_suite = manager.load_regression_suite("test_suite")
    
    assert loaded_suite is not None
    assert loaded_suite.suite_name == created_suite.suite_name
    assert loaded_suite.total_examples == created_suite.total_examples


def test_load_nonexistent_suite(manager):
    """Test loading a nonexistent regression suite."""
    suite = manager.load_regression_suite("nonexistent")
    assert suite is None


def test_list_regression_suites(manager):
    """Test listing regression test suites."""
    # Create some suites
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test1.py"
    )
    
    manager.create_regression_suite("suite1")
    manager.create_regression_suite("suite2")
    
    # List suites
    suites = manager.list_regression_suites()
    
    assert len(suites) == 2
    assert "suite1" in suites
    assert "suite2" in suites


def test_get_example_statistics(manager):
    """Test getting example statistics."""
    # Save some examples
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test1.py"
    )
    
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 2},
        error_message="Error 2",
        test_file="test1.py"
    )
    
    manager.save_failing_example(
        property_name="prop2",
        example_data={"x": 3},
        error_message="Error 3",
        test_file="test2.py"
    )
    
    # Get statistics
    stats = manager.get_example_statistics()
    
    assert stats["total_examples"] == 3
    assert stats["by_property"]["prop1"] == 2
    assert stats["by_property"]["prop2"] == 1
    assert stats["by_file"]["test1.py"] == 2
    assert stats["by_file"]["test2.py"] == 1


def test_clean_old_examples(manager):
    """Test cleaning old examples."""
    # Save an example with old timestamp
    old_example = FailingExample(
        property_name="old_prop",
        example_data={"x": 1},
        error_message="Old error",
        timestamp=time.time() - (40 * 24 * 60 * 60),  # 40 days ago
        test_file="test.py"
    )
    
    # Save manually with old timestamp
    import json
    from dataclasses import asdict
    
    filepath = manager.raw_examples_dir / "old_example.json"
    with open(filepath, 'w') as f:
        json.dump(asdict(old_example), f, default=str)
    
    # Save a recent example
    manager.save_failing_example(
        property_name="new_prop",
        example_data={"x": 2},
        error_message="New error",
        test_file="test.py"
    )
    
    # Clean examples older than 30 days
    deleted_count = manager.clean_old_examples(days=30)
    
    assert deleted_count == 1
    
    # Verify only recent example remains
    examples = manager.load_failing_examples()
    assert len(examples) == 1
    assert examples[0].property_name == "new_prop"


def test_verify_completion_time_within_limit(manager):
    """Test verifying completion time within limit."""
    result = manager.verify_completion_time(
        property_name="fast_property",
        duration_seconds=60,
        max_duration_seconds=300
    )
    
    assert result is True


def test_verify_completion_time_exceeds_limit(manager):
    """Test verifying completion time exceeds limit."""
    result = manager.verify_completion_time(
        property_name="slow_property",
        duration_seconds=400,
        max_duration_seconds=300
    )
    
    assert result is False
    
    # Verify violation was logged
    violations = manager.get_time_violations()
    assert len(violations) == 1
    assert violations[0]["property_name"] == "slow_property"
    assert violations[0]["duration_seconds"] == 400


def test_get_time_violations(manager):
    """Test getting time violations."""
    # Create some violations
    manager.verify_completion_time("prop1", 400, 300)
    manager.verify_completion_time("prop2", 500, 300)
    
    # Get violations
    violations = manager.get_time_violations()
    
    assert len(violations) == 2
    assert violations[0]["property_name"] == "prop1"
    assert violations[1]["property_name"] == "prop2"


def test_get_property_history(manager):
    """Test getting property failure history."""
    # Save multiple examples for same property
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test.py"
    )
    
    time.sleep(0.1)  # Ensure different timestamps
    
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 2},
        error_message="Error 2",
        test_file="test.py"
    )
    
    # Get history
    history = manager.get_property_history("prop1")
    
    assert len(history) == 2
    assert all(ex.property_name == "prop1" for ex in history)


def test_generate_regression_test_code(manager):
    """Test generating regression test code."""
    # Save some examples
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test.py"
    )
    
    manager.save_failing_example(
        property_name="prop2",
        example_data={"x": 2},
        error_message="Error 2",
        test_file="test.py"
    )
    
    # Create suite
    manager.create_regression_suite("test_suite")
    
    # Generate code
    output_file = manager.examples_dir / "test_regression.py"
    manager.generate_regression_test_code("test_suite", output_file)
    
    assert output_file.exists()
    
    # Verify code content
    with open(output_file) as f:
        code = f.read()
    
    assert "import pytest" in code
    assert "test_prop1_regression" in code
    assert "test_prop2_regression" in code


def test_create_regression_suite_with_filter(manager):
    """Test creating regression suite with property filter."""
    # Save examples for different properties
    manager.save_failing_example(
        property_name="prop1",
        example_data={"x": 1},
        error_message="Error 1",
        test_file="test.py"
    )
    
    manager.save_failing_example(
        property_name="prop2",
        example_data={"x": 2},
        error_message="Error 2",
        test_file="test.py"
    )
    
    manager.save_failing_example(
        property_name="prop3",
        example_data={"x": 3},
        error_message="Error 3",
        test_file="test.py"
    )
    
    # Create suite with filter
    suite = manager.create_regression_suite(
        "filtered_suite",
        property_names=["prop1", "prop2"]
    )
    
    assert suite.total_examples == 2
    assert all(ex.property_name in ["prop1", "prop2"] for ex in suite.examples)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
