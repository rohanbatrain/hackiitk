"""
Unit Tests for OracleValidator

Tests oracle loading, validation with matches and mismatches, accuracy
measurement, and oracle updates.

**Validates: Task 32.4**
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field
from typing import List
from tests.extreme.support.oracle_validator import OracleValidator, AccuracyMetrics
from tests.extreme.models import OracleTestCase, ValidationResult


# Mock GapAnalysisReport for testing
@dataclass
class MockGap:
    """Mock gap for testing."""
    subcategory_id: str


@dataclass
class MockGapAnalysisReport:
    """Mock gap analysis report for testing."""
    gaps: List[MockGap] = field(default_factory=list)
    covered_subcategories: List[str] = field(default_factory=list)


class TestOracleValidator:
    """Unit tests for OracleValidator component."""
    
    @pytest.fixture
    def oracle_dir(self, tmp_path):
        """Create temporary oracle directory."""
        oracle_path = tmp_path / "oracles"
        oracle_path.mkdir()
        return oracle_path
    
    @pytest.fixture
    def validator(self, oracle_dir):
        """Create OracleValidator instance."""
        return OracleValidator(str(oracle_dir))
    
    @pytest.fixture
    def sample_oracle(self, oracle_dir):
        """Create a sample oracle test case file."""
        oracle_data = {
            "test_id": "oracle_001",
            "policy_document": "Sample policy document content",
            "expected_gaps": ["ID.AM-1", "ID.AM-2", "PR.AC-1"],
            "expected_covered": ["ID.BE-1", "ID.GV-1", "PR.DS-1"],
            "expected_gap_count": 3,
            "tolerance": 0.05,
            "description": "Test oracle for basic gap detection"
        }
        
        oracle_file = oracle_dir / "oracle_001.json"
        with open(oracle_file, 'w') as f:
            json.dump(oracle_data, f)
        
        return oracle_data
    
    # Test oracle loading
    
    def test_load_oracles_empty_directory(self, validator):
        """Test loading oracles from empty directory."""
        oracles = validator.load_oracles()
        
        assert isinstance(oracles, list)
        assert len(oracles) == 0
    
    def test_load_oracles_single_oracle(self, validator, sample_oracle):
        """Test loading single oracle from directory."""
        oracles = validator.load_oracles()
        
        assert len(oracles) == 1
        oracle = oracles[0]
        assert oracle.test_id == "oracle_001"
        assert len(oracle.expected_gaps) == 3
        assert len(oracle.expected_covered) == 3
        assert oracle.tolerance == 0.05
    
    def test_load_oracles_multiple_oracles(self, validator, oracle_dir):
        """Test loading multiple oracles from directory."""
        # Create multiple oracle files
        for i in range(3):
            oracle_data = {
                "test_id": f"oracle_{i:03d}",
                "policy_document": f"Policy content {i}",
                "expected_gaps": [f"ID.AM-{i}"],
                "expected_covered": [f"PR.AC-{i}"],
                "expected_gap_count": 1,
                "tolerance": 0.05,
                "description": f"Test oracle {i}"
            }
            
            oracle_file = oracle_dir / f"oracle_{i:03d}.json"
            with open(oracle_file, 'w') as f:
                json.dump(oracle_data, f)
        
        oracles = validator.load_oracles()
        
        assert len(oracles) == 3
        test_ids = [o.test_id for o in oracles]
        assert "oracle_000" in test_ids
        assert "oracle_001" in test_ids
        assert "oracle_002" in test_ids
    
    def test_load_oracles_with_invalid_file(self, validator, oracle_dir, sample_oracle):
        """Test loading oracles with one invalid file."""
        # Create an invalid oracle file
        invalid_file = oracle_dir / "oracle_invalid.json"
        invalid_file.write_text("{ invalid json")
        
        oracles = validator.load_oracles()
        
        # Should load valid oracle, skip invalid
        assert len(oracles) == 1
        assert oracles[0].test_id == "oracle_001"
    
    def test_load_oracles_default_tolerance(self, validator, oracle_dir):
        """Test loading oracle without tolerance uses default."""
        oracle_data = {
            "test_id": "oracle_no_tolerance",
            "policy_document": "Policy content",
            "expected_gaps": ["ID.AM-1"],
            "expected_covered": ["PR.AC-1"],
            "expected_gap_count": 1
        }
        
        oracle_file = oracle_dir / "oracle_no_tolerance.json"
        with open(oracle_file, 'w') as f:
            json.dump(oracle_data, f)
        
        oracles = validator.load_oracles()
        
        assert len(oracles) == 1
        assert oracles[0].tolerance == 0.05  # Default tolerance
    
    # Test validation with matches
    
    def test_validate_against_oracle_perfect_match(self, validator):
        """Test validation with perfect match."""
        test_case = OracleTestCase(
            test_id="test_perfect",
            policy_document="content",
            expected_gaps=["ID.AM-1", "ID.AM-2"],
            expected_covered=["PR.AC-1", "PR.AC-2"],
            expected_gap_count=2,
            tolerance=0.05
        )
        
        # Create result that matches perfectly
        result = MockGapAnalysisReport(
            gaps=[MockGap("ID.AM-1"), MockGap("ID.AM-2")],
            covered_subcategories=["PR.AC-1", "PR.AC-2"]
        )
        
        validation = validator.validate_against_oracle(test_case, result)
        
        assert validation.passed is True
        assert validation.accuracy == 1.0
        assert len(validation.false_positives) == 0
        assert len(validation.false_negatives) == 0
    
    def test_validate_against_oracle_within_tolerance(self, validator):
        """Test validation within tolerance."""
        test_case = OracleTestCase(
            test_id="test_tolerance",
            policy_document="content",
            expected_gaps=["ID.AM-1", "ID.AM-2", "ID.AM-3", "ID.AM-4"],
            expected_covered=["PR.AC-1", "PR.AC-2", "PR.AC-3", "PR.AC-4"],
            expected_gap_count=4,
            tolerance=0.15  # 15% tolerance
        )
        
        # Result with 1 error out of 8 total = 87.5% accuracy (within 15% tolerance)
        result = MockGapAnalysisReport(
            gaps=[MockGap("ID.AM-1"), MockGap("ID.AM-2"), MockGap("ID.AM-3")],  # Missing ID.AM-4
            covered_subcategories=["PR.AC-1", "PR.AC-2", "PR.AC-3", "PR.AC-4"]
        )
        
        validation = validator.validate_against_oracle(test_case, result)
        
        assert validation.accuracy == 0.875  # 7/8 correct
        assert validation.passed is True  # Within tolerance
        assert len(validation.false_negatives) == 1  # Missed ID.AM-4
    
    # Test validation with mismatches
    
    def test_validate_against_oracle_false_positives(self, validator):
        """Test validation with false positives."""
        test_case = OracleTestCase(
            test_id="test_fp",
            policy_document="content",
            expected_gaps=["ID.AM-1"],
            expected_covered=["PR.AC-1", "PR.AC-2"],
            expected_gap_count=1,
            tolerance=0.05
        )
        
        # Result with extra gap (false positive)
        result = MockGapAnalysisReport(
            gaps=[MockGap("ID.AM-1"), MockGap("ID.AM-2")],  # ID.AM-2 is false positive
            covered_subcategories=["PR.AC-1", "PR.AC-2"]
        )
        
        validation = validator.validate_against_oracle(test_case, result)
        
        assert len(validation.false_positives) == 1
        assert "ID.AM-2" in validation.false_positives
        # Should fail due to high false positive rate (>5%)
        assert validation.passed is False
    
    def test_validate_against_oracle_false_negatives(self, validator):
        """Test validation with false negatives."""
        test_case = OracleTestCase(
            test_id="test_fn",
            policy_document="content",
            expected_gaps=["ID.AM-1", "ID.AM-2"],
            expected_covered=["PR.AC-1"],
            expected_gap_count=2,
            tolerance=0.05
        )
        
        # Result missing a gap (false negative)
        result = MockGapAnalysisReport(
            gaps=[MockGap("ID.AM-1")],  # Missing ID.AM-2
            covered_subcategories=["PR.AC-1"]
        )
        
        validation = validator.validate_against_oracle(test_case, result)
        
        assert len(validation.false_negatives) == 1
        assert "ID.AM-2" in validation.false_negatives
        assert validation.accuracy < 1.0
    
    def test_validate_against_oracle_exceeds_tolerance(self, validator):
        """Test validation that exceeds tolerance."""
        test_case = OracleTestCase(
            test_id="test_exceed",
            policy_document="content",
            expected_gaps=["ID.AM-1", "ID.AM-2"],
            expected_covered=["PR.AC-1", "PR.AC-2"],
            expected_gap_count=2,
            tolerance=0.05  # 5% tolerance
        )
        
        # Result with 50% accuracy (exceeds tolerance)
        result = MockGapAnalysisReport(
            gaps=[MockGap("ID.AM-1")],  # Missing ID.AM-2
            covered_subcategories=["PR.AC-1"]  # Missing PR.AC-2
        )
        
        validation = validator.validate_against_oracle(test_case, result)
        
        assert validation.passed is False
        assert validation.accuracy == 0.5  # 2/4 correct
        assert validation.error_message is not None
    
    def test_validate_against_oracle_high_false_positive_rate(self, validator):
        """Test validation fails with high false positive rate."""
        test_case = OracleTestCase(
            test_id="test_high_fp",
            policy_document="content",
            expected_gaps=["ID.AM-1"],
            expected_covered=["PR.AC-1", "PR.AC-2", "PR.AC-3"],
            expected_gap_count=1,
            tolerance=0.05
        )
        
        # Result with many false positives (>5% of total)
        result = MockGapAnalysisReport(
            gaps=[MockGap("ID.AM-1"), MockGap("ID.AM-2"), MockGap("ID.AM-3")],
            covered_subcategories=["PR.AC-1", "PR.AC-2", "PR.AC-3"]
        )
        
        validation = validator.validate_against_oracle(test_case, result)
        
        # Should fail due to high false positive rate
        assert validation.passed is False
    
    # Test accuracy measurement
    
    def test_measure_accuracy_all_passed(self, validator):
        """Test accuracy measurement with all tests passed."""
        results = [
            ValidationResult(
                test_case_id="test_1",
                passed=True,
                accuracy=1.0,
                false_positives=[],
                false_negatives=[]
            ),
            ValidationResult(
                test_case_id="test_2",
                passed=True,
                accuracy=0.98,
                false_positives=[],
                false_negatives=[]
            ),
            ValidationResult(
                test_case_id="test_3",
                passed=True,
                accuracy=0.96,
                false_positives=[],
                false_negatives=[]
            )
        ]
        
        metrics = validator.measure_accuracy(results)
        
        assert metrics.total_cases == 3
        assert metrics.passed_cases == 3
        assert metrics.failed_cases == 0
        assert metrics.overall_accuracy > 0.95
    
    def test_measure_accuracy_mixed_results(self, validator):
        """Test accuracy measurement with mixed results."""
        results = [
            ValidationResult(
                test_case_id="test_1",
                passed=True,
                accuracy=1.0,
                false_positives=[],
                false_negatives=[]
            ),
            ValidationResult(
                test_case_id="test_2",
                passed=False,
                accuracy=0.7,
                false_positives=["ID.AM-1"],
                false_negatives=["PR.AC-1"]
            )
        ]
        
        metrics = validator.measure_accuracy(results)
        
        assert metrics.total_cases == 2
        assert metrics.passed_cases == 1
        assert metrics.failed_cases == 1
        assert 0.8 < metrics.overall_accuracy < 0.9
    
    def test_measure_accuracy_empty_results(self, validator):
        """Test accuracy measurement with empty results."""
        metrics = validator.measure_accuracy([])
        
        assert metrics.total_cases == 0
        assert metrics.passed_cases == 0
        assert metrics.failed_cases == 0
        assert metrics.overall_accuracy == 0.0
    
    def test_measure_accuracy_calculates_precision_recall(self, validator):
        """Test accuracy measurement calculates precision and recall."""
        results = [
            ValidationResult(
                test_case_id="test_1",
                passed=True,
                accuracy=0.95,
                false_positives=["ID.AM-1"],
                false_negatives=["PR.AC-1"]
            )
        ]
        
        metrics = validator.measure_accuracy(results)
        
        assert 0 <= metrics.precision <= 1.0
        assert 0 <= metrics.recall <= 1.0
        assert 0 <= metrics.f1_score <= 1.0
        assert 0 <= metrics.false_positive_rate <= 1.0
        assert 0 <= metrics.false_negative_rate <= 1.0
    
    # Test oracle updates
    
    def test_update_oracle(self, validator, oracle_dir):
        """Test updating oracle test case."""
        # Create initial oracle
        test_case = OracleTestCase(
            test_id="oracle_update_test",
            policy_document="Original content",
            expected_gaps=["ID.AM-1"],
            expected_covered=["PR.AC-1"],
            expected_gap_count=1,
            tolerance=0.05
        )
        
        # Update oracle
        new_gaps = ["ID.AM-1", "ID.AM-2"]
        new_covered = ["PR.AC-1", "PR.AC-2"]
        reason = "System behavior changed after bug fix"
        
        validator.update_oracle(test_case, new_gaps, new_covered, reason)
        
        # Verify update
        assert test_case.expected_gaps == new_gaps
        assert test_case.expected_covered == new_covered
        assert test_case.expected_gap_count == 2
        
        # Verify file was written
        oracle_file = oracle_dir / "oracle_update_test.json"
        assert oracle_file.exists()
        
        with open(oracle_file, 'r') as f:
            data = json.load(f)
        
        assert data['expected_gaps'] == new_gaps
        assert data['expected_covered'] == new_covered
        assert data['update_reason'] == reason
        assert 'last_updated' in data
    
    def test_update_oracle_preserves_other_fields(self, validator, oracle_dir):
        """Test updating oracle preserves other fields."""
        test_case = OracleTestCase(
            test_id="oracle_preserve_test",
            policy_document="Content",
            expected_gaps=["ID.AM-1"],
            expected_covered=["PR.AC-1"],
            expected_gap_count=1,
            tolerance=0.10,
            description="Important test case"
        )
        
        validator.update_oracle(
            test_case,
            ["ID.AM-2"],
            ["PR.AC-2"],
            "Update reason"
        )
        
        # Verify other fields preserved
        assert test_case.tolerance == 0.10
        assert test_case.description == "Important test case"
    
    # Test accuracy trend tracking
    
    def test_track_accuracy_trend(self, validator):
        """Test tracking accuracy trends over time."""
        metrics = AccuracyMetrics(
            total_cases=10,
            passed_cases=9,
            failed_cases=1,
            overall_accuracy=0.95,
            precision=0.96,
            recall=0.94,
            f1_score=0.95,
            false_positive_rate=0.02,
            false_negative_rate=0.03
        )
        
        test_run_id = "run_001"
        
        validator.track_accuracy_trend(metrics, test_run_id)
        
        assert len(validator.accuracy_history) == 1
        trend = validator.accuracy_history[0]
        assert trend.test_run_id == test_run_id
        assert trend.metrics.overall_accuracy == 0.95
    
    def test_get_accuracy_trends(self, validator):
        """Test retrieving accuracy trends."""
        # Add multiple trends
        for i in range(5):
            metrics = AccuracyMetrics(
                total_cases=10,
                passed_cases=9 - i,
                failed_cases=1 + i,
                overall_accuracy=0.95 - (i * 0.05),
                precision=0.95,
                recall=0.95,
                f1_score=0.95,
                false_positive_rate=0.02,
                false_negative_rate=0.03
            )
            validator.track_accuracy_trend(metrics, f"run_{i:03d}")
        
        # Get recent trends
        trends = validator.get_accuracy_trends(limit=3)
        
        assert len(trends) == 3
        # Should return most recent
        assert trends[-1].test_run_id == "run_004"
    
    def test_accuracy_history_persistence(self, validator, oracle_dir):
        """Test accuracy history is persisted to file."""
        metrics = AccuracyMetrics(
            total_cases=10,
            passed_cases=9,
            failed_cases=1,
            overall_accuracy=0.95,
            precision=0.96,
            recall=0.94,
            f1_score=0.95,
            false_positive_rate=0.02,
            false_negative_rate=0.03
        )
        
        validator.track_accuracy_trend(metrics, "run_persist")
        
        # Check file was created
        history_file = oracle_dir / "accuracy_history.json"
        assert history_file.exists()
        
        with open(history_file, 'r') as f:
            data = json.load(f)
        
        assert len(data) == 1
        assert data[0]['test_run_id'] == "run_persist"
    
    def test_accuracy_metrics_to_dict(self):
        """Test AccuracyMetrics to_dict conversion."""
        metrics = AccuracyMetrics(
            total_cases=10,
            passed_cases=9,
            failed_cases=1,
            overall_accuracy=0.95,
            precision=0.96,
            recall=0.94,
            f1_score=0.95,
            false_positive_rate=0.02,
            false_negative_rate=0.03
        )
        
        metrics_dict = metrics.to_dict()
        
        assert metrics_dict['total_cases'] == 10
        assert metrics_dict['passed_cases'] == 9
        assert metrics_dict['overall_accuracy'] == 0.95
        assert metrics_dict['precision'] == 0.96
