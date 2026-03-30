"""
Unit Tests for Oracle Validator

Tests oracle loading, validation logic, accuracy metrics, and oracle updates.

**Validates: Requirements 71.1, 71.2, 71.3, 71.4, 71.5**
"""

import pytest
import json
import tempfile
from pathlib import Path
from datetime import datetime

from tests.extreme.support.oracle_validator import OracleValidator, AccuracyMetrics, AccuracyTrend
from tests.extreme.models import OracleTestCase, ValidationResult
from models.domain import GapAnalysisReport, GapDetail


@pytest.fixture
def temp_oracle_dir():
    """Create temporary oracle directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield Path(tmpdir)


@pytest.fixture
def sample_oracle(temp_oracle_dir):
    """Create a sample oracle test case."""
    oracle_data = {
        "test_id": "test_oracle_001",
        "description": "Test oracle with 10 gaps",
        "policy_document": "test_policy.md",
        "expected_gaps": [f"ID.AM-{i}" for i in range(1, 11)],
        "expected_covered": [f"PR.AC-{i}" for i in range(1, 8)],
        "expected_gap_count": 10,
        "tolerance": 0.05
    }
    
    oracle_file = temp_oracle_dir / "oracle_test_oracle_001.json"
    with open(oracle_file, 'w') as f:
        json.dump(oracle_data, f)
    
    return oracle_data


@pytest.fixture
def oracle_validator(temp_oracle_dir):
    """Create OracleValidator instance."""
    return OracleValidator(str(temp_oracle_dir))


def create_gap_analysis_report(gaps, covered):
    """Helper to create a GapAnalysisReport."""
    gap_details = [
        GapDetail(
            subcategory_id=gap_id,
            subcategory_description=f"Test description for {gap_id}",
            status="missing",
            evidence_quote="",
            gap_explanation="Test gap explanation",
            severity="High",
            suggested_fix="Test suggested fix"
        )
        for gap_id in gaps
    ]
    
    return GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file="test.pdf",
        input_file_hash="abc123",
        model_name="test-model",
        model_version="1.0",
        embedding_model="test-embed",
        gaps=gap_details,
        covered_subcategories=covered,
        metadata={}
    )


class TestOracleLoading:
    """Test oracle test case loading."""
    
    def test_load_oracles_success(self, oracle_validator, sample_oracle):
        """Test successful oracle loading."""
        oracles = oracle_validator.load_oracles()
        
        assert len(oracles) == 1
        assert oracles[0].test_id == "test_oracle_001"
        assert len(oracles[0].expected_gaps) == 10
        assert len(oracles[0].expected_covered) == 7
    
    def test_load_oracles_empty_directory(self, temp_oracle_dir):
        """Test loading from empty directory."""
        validator = OracleValidator(str(temp_oracle_dir))
        oracles = validator.load_oracles()
        
        assert len(oracles) == 0
    
    def test_load_multiple_oracles(self, temp_oracle_dir):
        """Test loading multiple oracle files."""
        # Create multiple oracle files
        for i in range(1, 4):
            oracle_data = {
                "test_id": f"oracle_{i:03d}",
                "description": f"Test oracle {i}",
                "policy_document": f"test_{i}.md",
                "expected_gaps": [f"ID.AM-{j}" for j in range(1, i+1)],
                "expected_covered": [],
                "expected_gap_count": i,
                "tolerance": 0.05
            }
            
            oracle_file = temp_oracle_dir / f"oracle_oracle_{i:03d}.json"
            with open(oracle_file, 'w') as f:
                json.dump(oracle_data, f)
        
        validator = OracleValidator(str(temp_oracle_dir))
        oracles = validator.load_oracles()
        
        assert len(oracles) == 3
    
    def test_load_oracles_with_invalid_file(self, temp_oracle_dir):
        """Test loading with invalid JSON file."""
        # Create valid oracle
        oracle_data = {
            "test_id": "valid_oracle",
            "description": "Valid oracle",
            "policy_document": "test.md",
            "expected_gaps": [],
            "expected_covered": ["ID.AM-1"],
            "expected_gap_count": 0,
            "tolerance": 0.05
        }
        
        valid_file = temp_oracle_dir / "oracle_valid_oracle.json"
        with open(valid_file, 'w') as f:
            json.dump(oracle_data, f)
        
        # Create invalid oracle
        invalid_file = temp_oracle_dir / "oracle_invalid.json"
        with open(invalid_file, 'w') as f:
            f.write("{ invalid json }")
        
        validator = OracleValidator(str(temp_oracle_dir))
        oracles = validator.load_oracles()
        
        # Should load only the valid oracle
        assert len(oracles) == 1
        assert oracles[0].test_id == "valid_oracle"


class TestValidationLogic:
    """Test oracle validation logic."""
    
    def test_perfect_match(self, oracle_validator, sample_oracle):
        """Test validation with perfect match."""
        oracle_validator.load_oracles()
        test_case = oracle_validator.oracles[0]
        
        # Create result that matches oracle exactly
        result = create_gap_analysis_report(
            gaps=test_case.expected_gaps,
            covered=test_case.expected_covered
        )
        
        validation = oracle_validator.validate_against_oracle(test_case, result)
        
        assert validation.passed
        assert validation.accuracy == 1.0
        assert len(validation.false_positives) == 0
        assert len(validation.false_negatives) == 0
    
    def test_false_positives(self, oracle_validator, sample_oracle):
        """Test detection of false positives."""
        oracle_validator.load_oracles()
        test_case = oracle_validator.oracles[0]
        
        # Add extra gaps not in oracle (false positives)
        extra_gaps = ["PR.DS-1", "PR.DS-2"]
        result = create_gap_analysis_report(
            gaps=test_case.expected_gaps + extra_gaps,
            covered=test_case.expected_covered
        )
        
        validation = oracle_validator.validate_against_oracle(test_case, result)
        
        assert not validation.passed  # Should fail due to false positives
        assert len(validation.false_positives) == 2
        assert "PR.DS-1" in validation.false_positives
        assert "PR.DS-2" in validation.false_positives
    
    def test_false_negatives(self, oracle_validator, sample_oracle):
        """Test detection of false negatives."""
        oracle_validator.load_oracles()
        test_case = oracle_validator.oracles[0]
        
        # Miss some expected gaps (false negatives)
        missed_gaps = test_case.expected_gaps[:5]  # Only detect half
        result = create_gap_analysis_report(
            gaps=missed_gaps,
            covered=test_case.expected_covered + test_case.expected_gaps[5:]
        )
        
        validation = oracle_validator.validate_against_oracle(test_case, result)
        
        assert not validation.passed  # Should fail due to false negatives
        assert len(validation.false_negatives) == 5
    
    def test_within_tolerance(self, oracle_validator, sample_oracle):
        """Test validation within tolerance."""
        oracle_validator.load_oracles()
        test_case = oracle_validator.oracles[0]
        
        # Miss 1 gap out of 17 total subcategories (94% accuracy, within 5% tolerance)
        result = create_gap_analysis_report(
            gaps=test_case.expected_gaps[:-1],  # Miss one gap
            covered=test_case.expected_covered + [test_case.expected_gaps[-1]]
        )
        
        validation = oracle_validator.validate_against_oracle(test_case, result)
        
        # Should pass if accuracy >= 95%
        total = len(test_case.expected_gaps) + len(test_case.expected_covered)
        correct = total - 1
        accuracy = correct / total
        
        assert validation.accuracy == pytest.approx(accuracy, 0.01)
    
    def test_false_positive_rate_threshold(self, oracle_validator, sample_oracle):
        """Test false positive rate threshold (< 5%)."""
        oracle_validator.load_oracles()
        test_case = oracle_validator.oracles[0]
        
        # Add 2 false positives out of 17 total (11.7% FP rate, exceeds 5%)
        extra_gaps = ["PR.DS-1", "PR.DS-2"]
        result = create_gap_analysis_report(
            gaps=test_case.expected_gaps + extra_gaps,
            covered=test_case.expected_covered
        )
        
        validation = oracle_validator.validate_against_oracle(test_case, result)
        
        assert not validation.passed  # Should fail due to high FP rate
        assert len(validation.false_positives) == 2


class TestAccuracyMetrics:
    """Test accuracy metrics calculation."""
    
    def test_measure_accuracy_all_passed(self, oracle_validator):
        """Test accuracy metrics when all validations pass."""
        results = [
            ValidationResult(
                test_case_id=f"test_{i}",
                passed=True,
                accuracy=0.98,
                false_positives=[],
                false_negatives=[]
            )
            for i in range(5)
        ]
        
        metrics = oracle_validator.measure_accuracy(results)
        
        assert metrics.total_cases == 5
        assert metrics.passed_cases == 5
        assert metrics.failed_cases == 0
        assert metrics.overall_accuracy == pytest.approx(0.98, 0.01)
    
    def test_measure_accuracy_mixed_results(self, oracle_validator):
        """Test accuracy metrics with mixed pass/fail."""
        results = [
            ValidationResult(
                test_case_id="test_1",
                passed=True,
                accuracy=0.98,
                false_positives=[],
                false_negatives=[]
            ),
            ValidationResult(
                test_case_id="test_2",
                passed=False,
                accuracy=0.85,
                false_positives=["ID.AM-1"],
                false_negatives=["PR.AC-1"]
            ),
            ValidationResult(
                test_case_id="test_3",
                passed=True,
                accuracy=0.96,
                false_positives=[],
                false_negatives=[]
            )
        ]
        
        metrics = oracle_validator.measure_accuracy(results)
        
        assert metrics.total_cases == 3
        assert metrics.passed_cases == 2
        assert metrics.failed_cases == 1
        assert metrics.overall_accuracy == pytest.approx((0.98 + 0.85 + 0.96) / 3, 0.01)
    
    def test_measure_accuracy_empty_results(self, oracle_validator):
        """Test accuracy metrics with no results."""
        metrics = oracle_validator.measure_accuracy([])
        
        assert metrics.total_cases == 0
        assert metrics.passed_cases == 0
        assert metrics.overall_accuracy == 0.0
    
    def test_precision_recall_f1(self, oracle_validator):
        """Test precision, recall, and F1 score calculation."""
        results = [
            ValidationResult(
                test_case_id="test_1",
                passed=False,
                accuracy=0.90,
                false_positives=["ID.AM-1", "ID.AM-2"],
                false_negatives=["PR.AC-1"]
            )
        ]
        
        metrics = oracle_validator.measure_accuracy(results)
        
        # Verify metrics are calculated
        assert 0.0 <= metrics.precision <= 1.0
        assert 0.0 <= metrics.recall <= 1.0
        assert 0.0 <= metrics.f1_score <= 1.0
        assert 0.0 <= metrics.false_positive_rate <= 1.0
        assert 0.0 <= metrics.false_negative_rate <= 1.0


class TestOracleUpdate:
    """Test oracle update mechanism."""
    
    def test_update_oracle(self, oracle_validator, sample_oracle):
        """Test updating an oracle test case."""
        oracle_validator.load_oracles()
        test_case = oracle_validator.oracles[0]
        
        new_gaps = ["ID.AM-1", "ID.AM-2"]
        new_covered = ["PR.AC-1", "PR.AC-2", "PR.AC-3"]
        reason = "Updated reference catalog"
        
        oracle_validator.update_oracle(
            test_case,
            new_gaps,
            new_covered,
            reason
        )
        
        # Verify test case was updated
        assert test_case.expected_gaps == new_gaps
        assert test_case.expected_covered == new_covered
        assert test_case.expected_gap_count == 2
        
        # Verify file was updated
        oracle_file = Path(oracle_validator.oracle_dir) / f"{test_case.test_id}.json"
        assert oracle_file.exists()
        
        with open(oracle_file, 'r') as f:
            data = json.load(f)
        
        assert data['expected_gaps'] == new_gaps
        assert data['expected_covered'] == new_covered
        assert data['update_reason'] == reason
        assert 'last_updated' in data
    
    def test_update_oracle_preserves_metadata(self, oracle_validator, sample_oracle):
        """Test that oracle update preserves other metadata."""
        oracle_validator.load_oracles()
        test_case = oracle_validator.oracles[0]
        
        original_description = test_case.description
        original_tolerance = test_case.tolerance
        
        oracle_validator.update_oracle(
            test_case,
            ["ID.AM-1"],
            ["PR.AC-1"],
            "Test update"
        )
        
        # Reload and verify metadata preserved
        oracle_validator.load_oracles()
        updated_case = oracle_validator.oracles[0]
        
        assert updated_case.description == original_description
        assert updated_case.tolerance == original_tolerance


class TestAccuracyTrends:
    """Test accuracy trend tracking."""
    
    def test_track_accuracy_trend(self, oracle_validator):
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
        
        oracle_validator.track_accuracy_trend(metrics, "test_run_001")
        
        assert len(oracle_validator.accuracy_history) == 1
        assert oracle_validator.accuracy_history[0].test_run_id == "test_run_001"
        assert oracle_validator.accuracy_history[0].metrics.overall_accuracy == 0.95
    
    def test_get_accuracy_trends(self, oracle_validator):
        """Test retrieving accuracy trends."""
        # Track multiple trends
        for i in range(15):
            metrics = AccuracyMetrics(
                total_cases=10,
                passed_cases=9,
                failed_cases=1,
                overall_accuracy=0.90 + (i * 0.01),
                precision=0.95,
                recall=0.93,
                f1_score=0.94,
                false_positive_rate=0.02,
                false_negative_rate=0.03
            )
            oracle_validator.track_accuracy_trend(metrics, f"run_{i:03d}")
        
        # Get last 10 trends
        recent_trends = oracle_validator.get_accuracy_trends(limit=10)
        
        assert len(recent_trends) == 10
        assert recent_trends[-1].test_run_id == "run_014"
    
    def test_accuracy_history_persistence(self, temp_oracle_dir):
        """Test that accuracy history is persisted to file."""
        validator = OracleValidator(str(temp_oracle_dir))
        
        metrics = AccuracyMetrics(
            total_cases=5,
            passed_cases=5,
            failed_cases=0,
            overall_accuracy=1.0,
            precision=1.0,
            recall=1.0,
            f1_score=1.0,
            false_positive_rate=0.0,
            false_negative_rate=0.0
        )
        
        validator.track_accuracy_trend(metrics, "test_run")
        
        # Verify history file exists
        history_file = temp_oracle_dir / "accuracy_history.json"
        assert history_file.exists()
        
        # Create new validator and verify history is loaded
        validator2 = OracleValidator(str(temp_oracle_dir))
        assert len(validator2.accuracy_history) == 1
        assert validator2.accuracy_history[0].test_run_id == "test_run"


class TestIntegration:
    """Integration tests for complete oracle validation workflow."""
    
    def test_complete_validation_workflow(self, oracle_validator, sample_oracle):
        """Test complete workflow: load, validate, measure, track."""
        # Load oracles
        oracles = oracle_validator.load_oracles()
        assert len(oracles) == 1
        
        # Validate against oracle
        test_case = oracles[0]
        result = create_gap_analysis_report(
            gaps=test_case.expected_gaps,
            covered=test_case.expected_covered
        )
        
        validation = oracle_validator.validate_against_oracle(test_case, result)
        assert validation.passed
        
        # Measure accuracy
        metrics = oracle_validator.measure_accuracy([validation])
        assert metrics.passed_cases == 1
        
        # Track trend
        oracle_validator.track_accuracy_trend(metrics, "integration_test")
        assert len(oracle_validator.accuracy_history) == 1
    
    def test_multiple_oracle_validation(self, temp_oracle_dir):
        """Test validating multiple oracles."""
        # Create multiple oracles
        for i in range(3):
            oracle_data = {
                "test_id": f"oracle_{i:03d}",
                "description": f"Test oracle {i}",
                "policy_document": f"test_{i}.md",
                "expected_gaps": [f"ID.AM-{j}" for j in range(1, i+2)],
                "expected_covered": [f"PR.AC-{j}" for j in range(1, 4)],
                "expected_gap_count": i+1,
                "tolerance": 0.05
            }
            
            oracle_file = temp_oracle_dir / f"oracle_oracle_{i:03d}.json"
            with open(oracle_file, 'w') as f:
                json.dump(oracle_data, f)
        
        validator = OracleValidator(str(temp_oracle_dir))
        oracles = validator.load_oracles()
        
        # Validate all oracles
        validations = []
        for oracle in oracles:
            result = create_gap_analysis_report(
                gaps=oracle.expected_gaps,
                covered=oracle.expected_covered
            )
            validation = validator.validate_against_oracle(oracle, result)
            validations.append(validation)
        
        # Measure aggregate accuracy
        metrics = validator.measure_accuracy(validations)
        
        assert metrics.total_cases == 3
        assert metrics.passed_cases == 3
        assert metrics.overall_accuracy == 1.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
