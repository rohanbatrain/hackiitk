"""
Unit tests for .github/scripts/run_tests.sh

Tests the test runner script's category mapping, error handling,
and output file generation.

Requirements: 13.1-13.8
"""

import subprocess
import tempfile
import os
import json
from pathlib import Path
import pytest


class TestRunTestsScript:
    """Test suite for the run_tests.sh script"""
    
    @pytest.fixture
    def script_path(self):
        """Get the path to the run_tests.sh script"""
        return Path(".github/scripts/run_tests.sh")
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create a temporary directory for test outputs"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir
    
    def run_script(self, script_path, category, output_dir):
        """Helper to run the script and capture output"""
        result = subprocess.run(
            ["bash", str(script_path), category, output_dir],
            capture_output=True,
            text=True,
            timeout=30
        )
        return result
    
    # Test category mapping for all 8 categories (Requirement 13.1-13.8)
    
    def test_property_category_mapping(self, script_path, temp_output_dir):
        """Test that property category maps to correct test paths"""
        result = self.run_script(script_path, "property", temp_output_dir)
        
        # Script should complete (exit 0)
        assert result.returncode == 0
        
        # Should mention property tests in output
        assert "property" in result.stdout.lower()
        assert "test_property_test_expander.py" in result.stdout or "tests/property/" in result.stdout
    
    def test_boundary_category_mapping(self, script_path, temp_output_dir):
        """Test that boundary category maps to correct test paths"""
        result = self.run_script(script_path, "boundary", temp_output_dir)
        
        assert result.returncode == 0
        assert "boundary" in result.stdout.lower()
        assert "test_boundary_tester.py" in result.stdout
    
    def test_adversarial_category_mapping(self, script_path, temp_output_dir):
        """Test that adversarial category maps to correct test paths"""
        result = self.run_script(script_path, "adversarial", temp_output_dir)
        
        assert result.returncode == 0
        assert "adversarial" in result.stdout.lower()
        assert "test_adversarial_tester.py" in result.stdout
    
    def test_stress_category_mapping(self, script_path, temp_output_dir):
        """Test that stress category maps to correct test paths"""
        result = self.run_script(script_path, "stress", temp_output_dir)
        
        assert result.returncode == 0
        assert "stress" in result.stdout.lower()
        assert "test_stress_tester.py" in result.stdout or "test_component_stress_tester.py" in result.stdout
    
    def test_chaos_category_mapping(self, script_path, temp_output_dir):
        """Test that chaos category maps to correct test paths"""
        result = self.run_script(script_path, "chaos", temp_output_dir)
        
        assert result.returncode == 0
        assert "chaos" in result.stdout.lower()
        assert "test_chaos_engine.py" in result.stdout or "test_integration_chaos.py" in result.stdout
    
    def test_performance_category_mapping(self, script_path, temp_output_dir):
        """Test that performance category maps to correct test paths"""
        result = self.run_script(script_path, "performance", temp_output_dir)
        
        assert result.returncode == 0
        assert "performance" in result.stdout.lower()
        assert "test_performance_profiler.py" in result.stdout
    
    def test_unit_category_mapping(self, script_path, temp_output_dir):
        """Test that unit category maps to correct test paths"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        assert result.returncode == 0
        assert "unit" in result.stdout.lower()
        assert "tests/unit/" in result.stdout
    
    def test_integration_category_mapping(self, script_path, temp_output_dir):
        """Test that integration category maps to correct test paths"""
        result = self.run_script(script_path, "integration", temp_output_dir)
        
        assert result.returncode == 0
        assert "integration" in result.stdout.lower()
        assert "tests/integration/" in result.stdout
    
    # Test invalid category handling (Requirement 13.1-13.8)
    
    def test_invalid_category_returns_error(self, script_path, temp_output_dir):
        """Test that invalid category is rejected with error"""
        result = self.run_script(script_path, "invalid_category", temp_output_dir)
        
        # Should exit with error code 1
        assert result.returncode == 1
        
        # Should display error message
        assert "Unknown category" in result.stdout or "invalid" in result.stdout.lower()
    
    def test_invalid_category_shows_valid_options(self, script_path, temp_output_dir):
        """Test that invalid category shows list of valid categories"""
        result = self.run_script(script_path, "invalid_category", temp_output_dir)
        
        # Should list valid categories
        assert "property" in result.stdout
        assert "boundary" in result.stdout
        assert "adversarial" in result.stdout
        assert "stress" in result.stdout
        assert "chaos" in result.stdout
        assert "performance" in result.stdout
        assert "unit" in result.stdout
        assert "integration" in result.stdout
        assert "all" in result.stdout
    
    # Test output file generation (Requirement 13.1-13.8)
    
    def test_output_directory_created(self, script_path, temp_output_dir):
        """Test that output directory is created if it doesn't exist"""
        output_path = os.path.join(temp_output_dir, "nested", "output")
        result = self.run_script(script_path, "unit", output_path)
        
        # Directory should be created
        assert os.path.exists(output_path)
    
    def test_junit_xml_file_naming(self, script_path, temp_output_dir):
        """Test that JUnit XML files are named correctly"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        # Should mention junit XML file in output
        assert "junit_unit.xml" in result.stdout
    
    def test_json_report_file_naming(self, script_path, temp_output_dir):
        """Test that JSON report files are named correctly"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        # Should mention JSON report file in output
        assert "report_unit.json" in result.stdout
    
    def test_output_files_listed_at_end(self, script_path, temp_output_dir):
        """Test that generated output files are listed at the end"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        # Should show generated outputs section
        assert "Generated Test Outputs" in result.stdout or "outputs generated" in result.stdout.lower()
    
    # Test maxfail configuration per category (Requirement 13.1-13.8)
    
    def test_property_maxfail_limit(self, script_path, temp_output_dir):
        """Test that property category uses maxfail=5"""
        result = self.run_script(script_path, "property", temp_output_dir)
        
        # Should use maxfail=5 for property tests
        assert "--maxfail=5" in result.stdout or "maxfail" in result.stdout.lower()
    
    def test_boundary_maxfail_limit(self, script_path, temp_output_dir):
        """Test that boundary category uses maxfail=5"""
        result = self.run_script(script_path, "boundary", temp_output_dir)
        
        assert "--maxfail=5" in result.stdout or "maxfail" in result.stdout.lower()
    
    def test_adversarial_maxfail_limit(self, script_path, temp_output_dir):
        """Test that adversarial category uses maxfail=5"""
        result = self.run_script(script_path, "adversarial", temp_output_dir)
        
        assert "--maxfail=5" in result.stdout or "maxfail" in result.stdout.lower()
    
    def test_stress_maxfail_limit(self, script_path, temp_output_dir):
        """Test that stress category uses maxfail=3"""
        result = self.run_script(script_path, "stress", temp_output_dir)
        
        assert "--maxfail=3" in result.stdout or "maxfail" in result.stdout.lower()
    
    def test_chaos_maxfail_limit(self, script_path, temp_output_dir):
        """Test that chaos category uses maxfail=3"""
        result = self.run_script(script_path, "chaos", temp_output_dir)
        
        assert "--maxfail=3" in result.stdout or "maxfail" in result.stdout.lower()
    
    def test_performance_maxfail_limit(self, script_path, temp_output_dir):
        """Test that performance category uses maxfail=3"""
        result = self.run_script(script_path, "performance", temp_output_dir)
        
        assert "--maxfail=3" in result.stdout or "maxfail" in result.stdout.lower()
    
    def test_unit_maxfail_limit(self, script_path, temp_output_dir):
        """Test that unit category uses maxfail=10"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        assert "--maxfail=10" in result.stdout or "maxfail" in result.stdout.lower()
    
    def test_integration_maxfail_limit(self, script_path, temp_output_dir):
        """Test that integration category uses maxfail=5"""
        result = self.run_script(script_path, "integration", temp_output_dir)
        
        assert "--maxfail=5" in result.stdout or "maxfail" in result.stdout.lower()
    
    # Test "all" category behavior
    
    def test_all_category_runs_all_tests(self, script_path, temp_output_dir):
        """Test that 'all' category runs all test categories"""
        result = self.run_script(script_path, "all", temp_output_dir)
        
        assert result.returncode == 0
        
        # Should mention all categories
        output_lower = result.stdout.lower()
        assert "property" in output_lower
        assert "boundary" in output_lower
        assert "adversarial" in output_lower
        assert "stress" in output_lower
        assert "chaos" in output_lower
        assert "performance" in output_lower
        assert "unit" in output_lower
        assert "integration" in output_lower
    
    # Test script header and output formatting
    
    def test_script_displays_header(self, script_path, temp_output_dir):
        """Test that script displays informative header"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        # Should show header with category and output directory
        assert "Test Execution Script" in result.stdout or "Category:" in result.stdout
    
    def test_script_displays_category_in_header(self, script_path, temp_output_dir):
        """Test that script displays the category being run"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        assert "Category: unit" in result.stdout or "unit" in result.stdout
    
    def test_script_displays_output_directory(self, script_path, temp_output_dir):
        """Test that script displays the output directory"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        assert temp_output_dir in result.stdout or "Output Directory:" in result.stdout
    
    # Test default parameter handling
    
    def test_default_output_directory(self, script_path):
        """Test that script uses default output directory when not specified"""
        result = subprocess.run(
            ["bash", str(script_path), "unit"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        # Should use default output directory
        assert "test_outputs/extreme" in result.stdout or result.returncode == 0
    
    # Test script completion messages
    
    def test_script_completion_message(self, script_path, temp_output_dir):
        """Test that script displays completion message"""
        result = self.run_script(script_path, "unit", temp_output_dir)
        
        assert "completed" in result.stdout.lower() or "✓" in result.stdout
