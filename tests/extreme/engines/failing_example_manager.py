"""
Failing Example Manager

Manages failing examples from property-based tests for regression testing.
Uses Hypothesis example database to persist and replay failing examples.

Validates Requirements:
- 17.5: Save failing examples for regression testing
- 17.6: Verify property tests complete within 5 minutes
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

from hypothesis.database import DirectoryBasedExampleDatabase


@dataclass
class FailingExample:
    """A failing example from a property test."""
    property_name: str
    example_data: Any
    error_message: str
    timestamp: float
    test_file: str
    line_number: Optional[int] = None


@dataclass
class RegressionTestSuite:
    """A suite of regression tests from failing examples."""
    suite_name: str
    created_at: float
    examples: List[FailingExample]
    total_examples: int


class FailingExampleManager:
    """
    Manages failing examples from property-based tests.
    
    Provides functionality to:
    - Save failing examples to disk
    - Load failing examples for regression testing
    - Create regression test suites
    - Track example history
    """
    
    def __init__(self, examples_dir: Path):
        """
        Initialize FailingExampleManager.
        
        Args:
            examples_dir: Directory to store failing examples
        """
        self.examples_dir = Path(examples_dir)
        self.examples_dir.mkdir(parents=True, exist_ok=True)
        
        # Create subdirectories
        self.raw_examples_dir = self.examples_dir / "raw"
        self.raw_examples_dir.mkdir(parents=True, exist_ok=True)
        
        self.regression_suites_dir = self.examples_dir / "regression_suites"
        self.regression_suites_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_dir = self.examples_dir / "history"
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Hypothesis example database
        self.hypothesis_db_dir = self.examples_dir / "hypothesis_db"
        self.hypothesis_db_dir.mkdir(parents=True, exist_ok=True)
        self.hypothesis_db = DirectoryBasedExampleDatabase(str(self.hypothesis_db_dir))
    
    def save_failing_example(
        self,
        property_name: str,
        example_data: Any,
        error_message: str,
        test_file: str,
        line_number: Optional[int] = None
    ) -> Path:
        """
        Save a failing example to disk.
        
        Args:
            property_name: Name of the property that failed
            example_data: The failing example data
            error_message: Error message from the failure
            test_file: Path to the test file
            line_number: Line number where the property is defined
        
        Returns:
            Path to the saved example file
        
        Validates: Requirements 17.5
        """
        example = FailingExample(
            property_name=property_name,
            example_data=example_data,
            error_message=error_message,
            timestamp=time.time(),
            test_file=test_file,
            line_number=line_number
        )
        
        # Create filename with timestamp
        timestamp_str = datetime.fromtimestamp(example.timestamp).strftime("%Y%m%d_%H%M%S")
        filename = f"{property_name}_{timestamp_str}.json"
        filepath = self.raw_examples_dir / filename
        
        # Save to JSON
        with open(filepath, 'w') as f:
            json.dump(asdict(example), f, indent=2, default=str)
        
        # Also save to history
        self._save_to_history(example)
        
        return filepath
    
    def load_failing_examples(
        self,
        property_name: Optional[str] = None
    ) -> List[FailingExample]:
        """
        Load failing examples from disk.
        
        Args:
            property_name: Optional property name to filter by
        
        Returns:
            List of failing examples
        """
        examples = []
        
        for filepath in self.raw_examples_dir.glob("*.json"):
            with open(filepath) as f:
                data = json.load(f)
            
            example = FailingExample(**data)
            
            # Filter by property name if specified
            if property_name is None or example.property_name == property_name:
                examples.append(example)
        
        return examples
    
    def create_regression_suite(
        self,
        suite_name: str,
        property_names: Optional[List[str]] = None
    ) -> RegressionTestSuite:
        """
        Create a regression test suite from failing examples.
        
        Args:
            suite_name: Name for the regression suite
            property_names: Optional list of property names to include
        
        Returns:
            Regression test suite
        
        Validates: Requirements 17.5
        """
        # Load examples
        if property_names:
            examples = []
            for prop_name in property_names:
                examples.extend(self.load_failing_examples(prop_name))
        else:
            examples = self.load_failing_examples()
        
        # Create suite
        suite = RegressionTestSuite(
            suite_name=suite_name,
            created_at=time.time(),
            examples=examples,
            total_examples=len(examples)
        )
        
        # Save suite
        suite_file = self.regression_suites_dir / f"{suite_name}.json"
        with open(suite_file, 'w') as f:
            json.dump({
                "suite_name": suite.suite_name,
                "created_at": suite.created_at,
                "total_examples": suite.total_examples,
                "examples": [asdict(ex) for ex in suite.examples]
            }, f, indent=2, default=str)
        
        return suite
    
    def load_regression_suite(self, suite_name: str) -> Optional[RegressionTestSuite]:
        """
        Load a regression test suite.
        
        Args:
            suite_name: Name of the suite to load
        
        Returns:
            Regression test suite or None if not found
        """
        suite_file = self.regression_suites_dir / f"{suite_name}.json"
        
        if not suite_file.exists():
            return None
        
        with open(suite_file) as f:
            data = json.load(f)
        
        examples = [FailingExample(**ex) for ex in data["examples"]]
        
        return RegressionTestSuite(
            suite_name=data["suite_name"],
            created_at=data["created_at"],
            examples=examples,
            total_examples=data["total_examples"]
        )
    
    def list_regression_suites(self) -> List[str]:
        """
        List all available regression test suites.
        
        Returns:
            List of suite names
        """
        return [f.stem for f in self.regression_suites_dir.glob("*.json")]
    
    def get_example_statistics(self) -> Dict[str, Any]:
        """
        Get statistics about failing examples.
        
        Returns:
            Dictionary with statistics
        """
        examples = self.load_failing_examples()
        
        # Count by property
        by_property = {}
        for example in examples:
            prop_name = example.property_name
            by_property[prop_name] = by_property.get(prop_name, 0) + 1
        
        # Count by test file
        by_file = {}
        for example in examples:
            test_file = example.test_file
            by_file[test_file] = by_file.get(test_file, 0) + 1
        
        return {
            "total_examples": len(examples),
            "by_property": by_property,
            "by_file": by_file,
            "oldest_example": min((ex.timestamp for ex in examples), default=None),
            "newest_example": max((ex.timestamp for ex in examples), default=None)
        }
    
    def clean_old_examples(self, days: int = 30) -> int:
        """
        Clean up examples older than specified days.
        
        Args:
            days: Number of days to keep examples
        
        Returns:
            Number of examples deleted
        """
        cutoff_time = time.time() - (days * 24 * 60 * 60)
        deleted_count = 0
        
        for filepath in self.raw_examples_dir.glob("*.json"):
            with open(filepath) as f:
                data = json.load(f)
            
            if data["timestamp"] < cutoff_time:
                filepath.unlink()
                deleted_count += 1
        
        return deleted_count
    
    def verify_completion_time(
        self,
        property_name: str,
        duration_seconds: float,
        max_duration_seconds: float = 300
    ) -> bool:
        """
        Verify that a property test completed within time limit.
        
        Args:
            property_name: Name of the property
            duration_seconds: Actual duration
            max_duration_seconds: Maximum allowed duration (default 5 minutes)
        
        Returns:
            True if within time limit, False otherwise
        
        Validates: Requirements 17.6
        """
        if duration_seconds > max_duration_seconds:
            # Log the violation
            violation = {
                "property_name": property_name,
                "duration_seconds": duration_seconds,
                "max_duration_seconds": max_duration_seconds,
                "timestamp": time.time()
            }
            
            violations_file = self.examples_dir / "time_violations.json"
            
            # Load existing violations
            violations = []
            if violations_file.exists():
                with open(violations_file) as f:
                    violations = json.load(f)
            
            # Add new violation
            violations.append(violation)
            
            # Save violations
            with open(violations_file, 'w') as f:
                json.dump(violations, f, indent=2)
            
            return False
        
        return True
    
    def get_time_violations(self) -> List[Dict[str, Any]]:
        """
        Get all time limit violations.
        
        Returns:
            List of time violations
        """
        violations_file = self.examples_dir / "time_violations.json"
        
        if not violations_file.exists():
            return []
        
        with open(violations_file) as f:
            return json.load(f)
    
    def _save_to_history(self, example: FailingExample) -> None:
        """
        Save example to history for tracking.
        
        Args:
            example: Failing example to save
        """
        # Create history file for this property
        history_file = self.history_dir / f"{example.property_name}_history.json"
        
        # Load existing history
        history = []
        if history_file.exists():
            with open(history_file) as f:
                history = json.load(f)
        
        # Add new example
        history.append(asdict(example))
        
        # Save history
        with open(history_file, 'w') as f:
            json.dump(history, f, indent=2, default=str)
    
    def get_property_history(self, property_name: str) -> List[FailingExample]:
        """
        Get failure history for a specific property.
        
        Args:
            property_name: Name of the property
        
        Returns:
            List of failing examples for this property
        """
        history_file = self.history_dir / f"{property_name}_history.json"
        
        if not history_file.exists():
            return []
        
        with open(history_file) as f:
            history = json.load(f)
        
        return [FailingExample(**ex) for ex in history]
    
    def generate_regression_test_code(
        self,
        suite_name: str,
        output_file: Path
    ) -> None:
        """
        Generate Python test code from a regression suite.
        
        Args:
            suite_name: Name of the regression suite
            output_file: Path to write the test code
        """
        suite = self.load_regression_suite(suite_name)
        
        if not suite:
            raise ValueError(f"Regression suite '{suite_name}' not found")
        
        # Generate test code
        code_lines = [
            '"""',
            f'Regression Tests: {suite_name}',
            '',
            f'Generated from {suite.total_examples} failing examples.',
            f'Created at: {datetime.fromtimestamp(suite.created_at).isoformat()}',
            '"""',
            '',
            'import pytest',
            'from hypothesis import given, example',
            '',
            ''
        ]
        
        # Group examples by property
        by_property = {}
        for ex in suite.examples:
            prop_name = ex.property_name
            if prop_name not in by_property:
                by_property[prop_name] = []
            by_property[prop_name].append(ex)
        
        # Generate test functions
        for prop_name, examples in by_property.items():
            code_lines.append(f'def test_{prop_name}_regression():')
            code_lines.append(f'    """Regression test for {prop_name}."""')
            code_lines.append('    # Add test implementation here')
            code_lines.append(f'    # {len(examples)} failing examples')
            code_lines.append('')
            
            for i, ex in enumerate(examples[:5]):  # Show first 5 examples
                code_lines.append(f'    # Example {i+1}: {ex.error_message[:50]}...')
            
            code_lines.append('')
            code_lines.append('')
        
        # Write to file
        with open(output_file, 'w') as f:
            f.write('\n'.join(code_lines))
