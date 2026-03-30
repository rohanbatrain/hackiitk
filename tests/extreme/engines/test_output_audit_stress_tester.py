"""
Tests for the Output and Audit Stress Tester.
"""

import pytest
import tempfile
from pathlib import Path

from tests.extreme.engines.output_audit_stress_tester import OutputAuditStressTester
from tests.extreme.support.metrics_collector import MetricsCollector
from tests.extreme.models import TestStatus


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def metrics_collector():
    """Create a metrics collector."""
    return MetricsCollector()


@pytest.fixture
def tester(metrics_collector, temp_dir):
    """Create an output audit stress tester."""
    return OutputAuditStressTester(metrics_collector, temp_dir)


class TestOutputManagerStress:
    """Tests for output manager stress testing."""
    
    def test_high_volume_output_generation(self, tester):
        """Test generating many output files."""
        result = tester.test_output_manager_high_volume()
        assert result.status == TestStatus.PASS
        assert "46.1" in result.requirement_id
    
    def test_special_character_filenames(self, tester):
        """Test filenames with special characters."""
        result = tester.test_special_character_filenames()
        assert result.status == TestStatus.PASS
        assert "46.2" in result.requirement_id
    
    def test_long_path_names(self, tester):
        """Test paths exceeding 255 characters."""
        result = tester.test_long_path_names()
        assert result.status == TestStatus.PASS
        assert "46.3" in result.requirement_id
    
    def test_large_output_files(self, tester):
        """Test files exceeding 100MB."""
        result = tester.test_large_output_files()
        assert result.status == TestStatus.PASS
        assert "46.4" in result.requirement_id
    
    def test_file_handle_leak_detection(self, tester):
        """Test file handle leak detection."""
        result = tester.test_file_handle_leak_detection()
        assert result.status == TestStatus.PASS
        assert "46.5" in result.requirement_id


class TestOutputFileConflicts:
    """Tests for output file conflict handling."""
    
    def test_concurrent_writes_same_directory(self, tester):
        """Test concurrent writes to same directory."""
        result = tester.test_concurrent_writes_same_directory()
        assert result.status == TestStatus.PASS
        assert "23.1" in result.requirement_id or "23.2" in result.requirement_id

    def test_existing_file_handling(self, tester):
        """Test existing file handling."""
        result = tester.test_existing_file_handling()
        assert result.status == TestStatus.PASS
        assert "23.2" in result.requirement_id
    
    def test_directory_creation_failures(self, tester):
        """Test directory creation failures."""
        result = tester.test_directory_creation_failures()
        assert result.status == TestStatus.PASS
        assert "23.3" in result.requirement_id
    
    def test_timestamp_based_naming(self, tester):
        """Test timestamp-based naming prevents conflicts."""
        result = tester.test_timestamp_based_naming()
        assert result.status == TestStatus.PASS
        assert "23.4" in result.requirement_id or "23.5" in result.requirement_id


class TestAuditLoggerStress:
    """Tests for audit logger stress testing."""
    
    def test_high_volume_sequential(self, tester):
        """Test 10,000 sequential audit log entries."""
        result = tester.test_audit_logger_high_volume_sequential()
        assert result.status == TestStatus.PASS
        assert "47.1" in result.requirement_id
    
    def test_concurrent_writes(self, tester):
        """Test 100 concurrent audit log entries."""
        result = tester.test_audit_logger_concurrent_writes()
        assert result.status == TestStatus.PASS
        assert "22.2" in result.requirement_id or "47.2" in result.requirement_id
    
    def test_large_files(self, tester):
        """Test audit logs exceeding 1GB."""
        result = tester.test_audit_log_large_files()
        assert result.status == TestStatus.PASS
        assert "47.3" in result.requirement_id
    
    def test_immutability(self, tester):
        """Test audit log immutability."""
        result = tester.test_audit_log_immutability()
        assert result.status == TestStatus.PASS
        assert "22.4" in result.requirement_id or "47.4" in result.requirement_id
    
    def test_integrity_under_failures(self, tester):
        """Test audit log integrity under failures."""
        result = tester.test_audit_log_integrity_under_failures()
        assert result.status == TestStatus.PASS
        assert "22.1" in result.requirement_id or "22.3" in result.requirement_id
    
    def test_metadata_completeness(self, tester):
        """Test audit log metadata completeness."""
        result = tester.test_audit_log_metadata_completeness()
        assert result.status == TestStatus.PASS
        assert "22.7" in result.requirement_id


class TestJSONMarkdownValidation:
    """Tests for JSON and Markdown validation."""
    
    def test_json_schema_validation_malformed(self, tester):
        """Test JSON schema validation with malformed samples."""
        result = tester.test_json_schema_validation_malformed()
        assert result.status == TestStatus.PASS
        assert "24.1" in result.requirement_id or "24.2" in result.requirement_id
    
    def test_json_parseability(self, tester):
        """Test JSON parseability."""
        result = tester.test_json_parseability()
        assert result.status == TestStatus.PASS
        assert "24.4" in result.requirement_id or "24.5" in result.requirement_id
    
    def test_markdown_formatting_edge_cases(self, tester):
        """Test markdown formatting edge cases."""
        result = tester.test_markdown_formatting_edge_cases()
        assert result.status == TestStatus.PASS
        assert "25.1" in result.requirement_id


class TestCitationMetadata:
    """Tests for citation and metadata handling."""
    
    def test_citation_traceability_high_volume(self, tester):
        """Test citation traceability with 1,000+ chunks."""
        result = tester.test_citation_traceability_high_volume()
        assert result.status == TestStatus.PASS
        assert "26.1" in result.requirement_id or "58.1" in result.requirement_id
    
    def test_chunk_boundary_citation_accuracy(self, tester):
        """Test chunk boundary citation accuracy."""
        result = tester.test_chunk_boundary_citation_accuracy()
        assert result.status == TestStatus.PASS
        assert "26.2" in result.requirement_id
    
    def test_metadata_consistency_through_pipeline(self, tester):
        """Test metadata consistency through pipeline."""
        result = tester.test_metadata_consistency_through_pipeline()
        assert result.status == TestStatus.PASS
        assert "26.3" in result.requirement_id or "58.3" in result.requirement_id
    
    def test_duplicate_chunk_id_detection(self, tester):
        """Test duplicate chunk ID detection."""
        result = tester.test_duplicate_chunk_id_detection()
        assert result.status == TestStatus.PASS
        assert "26.5" in result.requirement_id or "58.2" in result.requirement_id
    
    def test_metadata_preservation_in_all_formats(self, tester):
        """Test metadata preservation in all formats."""
        result = tester.test_metadata_preservation_in_all_formats()
        assert result.status == TestStatus.PASS
        assert "58.5" in result.requirement_id


class TestIntegration:
    """Integration tests for the output audit stress tester."""
    
    def test_run_all_tests(self, tester):
        """Test running all tests."""
        results = tester.run_all_tests()
        
        # Should have all test results
        assert len(results) >= 20
        
        # Most tests should pass
        passed = sum(1 for r in results if r.status == "pass")
        assert passed >= len(results) * 0.8  # At least 80% pass rate
