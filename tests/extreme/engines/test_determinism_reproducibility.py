"""
Determinism and Reproducibility Tests

This module implements Task 22.1 from the comprehensive hardest testing spec:
- Test same policy twice with identical config
- Test same policy on different machines (simulated)
- Test with temperature=0.0
- Test 20+ different policies
- Verify audit log hash matching
- Identify sources of non-determinism

Validates Requirements 32.1, 32.2, 32.3, 32.4, 32.5, 32.6
"""

import pytest
import sys
import os
import tempfile
import hashlib
import json
import time
from pathlib import Path
from typing import Dict, Any, List, Tuple
from dataclasses import dataclass
from unittest.mock import Mock, patch

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig
from tests.extreme.data_generator import TestDataGenerator, DocumentSpec
from reporting.audit_logger import AuditLogger


@dataclass
class DeterminismTestResult:
    """Result from a determinism test."""
    test_name: str
    passed: bool
    error_message: str = ""
    details: Dict[str, Any] = None
    non_determinism_sources: List[str] = None


class DeterminismValidator:
    """
    Validates determinism and reproducibility of analysis pipeline.
    
    Tests that identical inputs with identical configurations produce
    identical outputs, which is critical for compliance and auditing.
    """
    
    def __init__(self):
        self.data_generator = TestDataGenerator()
        self.temp_dir = Path(tempfile.mkdtemp())
        self.results = []
    
    def cleanup(self):
        """Clean up temporary files."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_same_policy_twice_identical_config(self) -> DeterminismTestResult:
        """
        Test that analyzing the same policy twice with identical config produces identical results.
        Requirement 32.1
        """
        try:
            # Generate test policy
            spec = DocumentSpec(size_pages=5, words_per_page=300, coverage_percentage=0.6)
            policy_content = self.data_generator.generate_policy_document(spec)
            policy_path = self.temp_dir / "test_policy.md"
            policy_path.write_text(policy_content)
            
            # Create deterministic configuration (temperature=0.0)
            config = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'top_k': 5,
                'temperature': 0.0,  # Deterministic
                'max_tokens': 512,
                'model_name': 'qwen2.5:3b-instruct',
                'output_dir': str(self.temp_dir / "outputs1"),
                'audit_dir': str(self.temp_dir / "audit1")
            })
            
            # Run analysis twice
            pipeline1 = AnalysisPipeline(config)
            pipeline1.initialize_resources()
            result1 = pipeline1.execute(str(policy_path))
            
            # Second run with same config
            config2 = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'top_k': 5,
                'temperature': 0.0,
                'max_tokens': 512,
                'model_name': 'qwen2.5:3b-instruct',
                'output_dir': str(self.temp_dir / "outputs2"),
                'audit_dir': str(self.temp_dir / "audit2")
            })
            
            pipeline2 = AnalysisPipeline(config2)
            pipeline2.initialize_resources()
            result2 = pipeline2.execute(str(policy_path))
            
            # Compare results
            comparison = self._compare_analysis_results(result1, result2)
            
            return DeterminismTestResult(
                test_name="same_policy_twice_identical_config",
                passed=comparison['identical'],
                error_message="" if comparison['identical'] else f"Results differ: {comparison['differences']}",
                details=comparison,
                non_determinism_sources=comparison.get('non_determinism_sources', [])
            )
            
        except Exception as e:
            return DeterminismTestResult(
                test_name="same_policy_twice_identical_config",
                passed=False,
                error_message=f"Test failed with error: {e}",
                non_determinism_sources=["test_execution_error"]
            )
    
    def test_same_policy_different_machines(self) -> DeterminismTestResult:
        """
        Test that analyzing the same policy on different machines produces identical results.
        Requirement 32.2
        
        Note: This simulates different machines by using different working directories
        and environment variables, as we cannot actually test on different physical machines.
        """
        try:
            # Generate test policy
            spec = DocumentSpec(size_pages=3, words_per_page=200, coverage_percentage=0.5)
            policy_content = self.data_generator.generate_policy_document(spec)
            
            # Simulate "machine 1"
            machine1_dir = self.temp_dir / "machine1"
            machine1_dir.mkdir()
            policy_path1 = machine1_dir / "policy.md"
            policy_path1.write_text(policy_content)
            
            config1 = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'temperature': 0.0,
                'output_dir': str(machine1_dir / "outputs"),
                'audit_dir': str(machine1_dir / "audit")
            })
            
            # Simulate "machine 2"
            machine2_dir = self.temp_dir / "machine2"
            machine2_dir.mkdir()
            policy_path2 = machine2_dir / "policy.md"
            policy_path2.write_text(policy_content)
            
            config2 = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'temperature': 0.0,
                'output_dir': str(machine2_dir / "outputs"),
                'audit_dir': str(machine2_dir / "audit")
            })
            
            # Run on "machine 1"
            pipeline1 = AnalysisPipeline(config1)
            pipeline1.initialize_resources()
            result1 = pipeline1.execute(str(policy_path1))
            
            # Run on "machine 2"
            pipeline2 = AnalysisPipeline(config2)
            pipeline2.initialize_resources()
            result2 = pipeline2.execute(str(policy_path2))
            
            # Compare results
            comparison = self._compare_analysis_results(result1, result2)
            
            return DeterminismTestResult(
                test_name="same_policy_different_machines",
                passed=comparison['identical'],
                error_message="" if comparison['identical'] else f"Results differ across machines: {comparison['differences']}",
                details=comparison,
                non_determinism_sources=comparison.get('non_determinism_sources', [])
            )
            
        except Exception as e:
            return DeterminismTestResult(
                test_name="same_policy_different_machines",
                passed=False,
                error_message=f"Test failed with error: {e}",
                non_determinism_sources=["test_execution_error"]
            )
    
    def test_temperature_zero_determinism(self) -> DeterminismTestResult:
        """
        Test that temperature=0.0 produces deterministic LLM outputs.
        Requirement 32.3
        """
        try:
            # Generate test policy
            spec = DocumentSpec(size_pages=2, words_per_page=150, coverage_percentage=0.4)
            policy_content = self.data_generator.generate_policy_document(spec)
            policy_path = self.temp_dir / "temp_zero_policy.md"
            policy_path.write_text(policy_content)
            
            # Run 5 times with temperature=0.0
            results = []
            for i in range(5):
                config = PipelineConfig({
                    'chunk_size': 512,
                    'overlap': 50,
                    'temperature': 0.0,
                    'output_dir': str(self.temp_dir / f"temp_zero_outputs_{i}"),
                    'audit_dir': str(self.temp_dir / f"temp_zero_audit_{i}")
                })
                
                pipeline = AnalysisPipeline(config)
                pipeline.initialize_resources()
                result = pipeline.execute(str(policy_path))
                results.append(result)
            
            # Compare all results to first result
            all_identical = True
            differences = []
            
            for i in range(1, len(results)):
                comparison = self._compare_analysis_results(results[0], results[i])
                if not comparison['identical']:
                    all_identical = False
                    differences.append(f"Run {i+1} differs from run 1: {comparison['differences']}")
            
            return DeterminismTestResult(
                test_name="temperature_zero_determinism",
                passed=all_identical,
                error_message="" if all_identical else f"Temperature=0.0 not deterministic: {differences}",
                details={"runs": len(results), "differences": differences},
                non_determinism_sources=["llm_sampling"] if not all_identical else []
            )
            
        except Exception as e:
            return DeterminismTestResult(
                test_name="temperature_zero_determinism",
                passed=False,
                error_message=f"Test failed with error: {e}",
                non_determinism_sources=["test_execution_error"]
            )
    
    def test_multiple_policies_reproducibility(self, num_policies: int = 20) -> DeterminismTestResult:
        """
        Test reproducibility across 20+ different policies.
        Requirement 32.4
        """
        try:
            reproducible_count = 0
            non_reproducible_policies = []
            
            for i in range(num_policies):
                # Generate unique policy
                spec = DocumentSpec(
                    size_pages=2 + (i % 5),
                    words_per_page=100 + (i * 10),
                    coverage_percentage=0.3 + (i * 0.02)
                )
                policy_content = self.data_generator.generate_policy_document(spec)
                policy_path = self.temp_dir / f"policy_{i}.md"
                policy_path.write_text(policy_content)
                
                # Run twice
                config1 = PipelineConfig({
                    'chunk_size': 512,
                    'overlap': 50,
                    'temperature': 0.0,
                    'output_dir': str(self.temp_dir / f"policy_{i}_run1"),
                    'audit_dir': str(self.temp_dir / f"policy_{i}_audit1")
                })
                
                pipeline1 = AnalysisPipeline(config1)
                pipeline1.initialize_resources()
                result1 = pipeline1.execute(str(policy_path))
                
                config2 = PipelineConfig({
                    'chunk_size': 512,
                    'overlap': 50,
                    'temperature': 0.0,
                    'output_dir': str(self.temp_dir / f"policy_{i}_run2"),
                    'audit_dir': str(self.temp_dir / f"policy_{i}_audit2")
                })
                
                pipeline2 = AnalysisPipeline(config2)
                pipeline2.initialize_resources()
                result2 = pipeline2.execute(str(policy_path))
                
                # Compare
                comparison = self._compare_analysis_results(result1, result2)
                if comparison['identical']:
                    reproducible_count += 1
                else:
                    non_reproducible_policies.append({
                        'policy_id': i,
                        'differences': comparison['differences']
                    })
            
            reproducibility_rate = reproducible_count / num_policies
            passed = reproducibility_rate >= 0.95  # 95% reproducibility threshold
            
            return DeterminismTestResult(
                test_name="multiple_policies_reproducibility",
                passed=passed,
                error_message="" if passed else f"Only {reproducible_count}/{num_policies} policies reproducible",
                details={
                    'total_policies': num_policies,
                    'reproducible': reproducible_count,
                    'reproducibility_rate': reproducibility_rate,
                    'non_reproducible': non_reproducible_policies
                },
                non_determinism_sources=self._identify_common_non_determinism_sources(non_reproducible_policies)
            )
            
        except Exception as e:
            return DeterminismTestResult(
                test_name="multiple_policies_reproducibility",
                passed=False,
                error_message=f"Test failed with error: {e}",
                non_determinism_sources=["test_execution_error"]
            )
    
    def test_audit_log_hash_matching(self) -> DeterminismTestResult:
        """
        Verify audit log hashes match for identical analyses.
        Requirement 32.5
        """
        try:
            # Generate test policy
            spec = DocumentSpec(size_pages=3, words_per_page=200, coverage_percentage=0.5)
            policy_content = self.data_generator.generate_policy_document(spec)
            policy_path = self.temp_dir / "audit_test_policy.md"
            policy_path.write_text(policy_content)
            
            # Run analysis twice
            config1 = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'temperature': 0.0,
                'output_dir': str(self.temp_dir / "audit_outputs1"),
                'audit_dir': str(self.temp_dir / "audit_logs1")
            })
            
            pipeline1 = AnalysisPipeline(config1)
            pipeline1.initialize_resources()
            result1 = pipeline1.execute(str(policy_path))
            
            config2 = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'temperature': 0.0,
                'output_dir': str(self.temp_dir / "audit_outputs2"),
                'audit_dir': str(self.temp_dir / "audit_logs2")
            })
            
            pipeline2 = AnalysisPipeline(config2)
            pipeline2.initialize_resources()
            result2 = pipeline2.execute(str(policy_path))
            
            # Load audit logs
            audit_logger1 = AuditLogger(audit_dir=str(self.temp_dir / "audit_logs1"))
            audit_logger2 = AuditLogger(audit_dir=str(self.temp_dir / "audit_logs2"))
            
            entries1 = audit_logger1.get_all_entries()
            entries2 = audit_logger2.get_all_entries()
            
            if not entries1 or not entries2:
                return DeterminismTestResult(
                    test_name="audit_log_hash_matching",
                    passed=False,
                    error_message="No audit log entries found",
                    non_determinism_sources=["audit_logging_failure"]
                )
            
            # Compare audit log hashes (excluding timestamp and output_directory)
            entry1 = entries1[-1]  # Most recent
            entry2 = entries2[-1]
            
            # Calculate hash of relevant fields
            hash1 = self._calculate_audit_hash(entry1)
            hash2 = self._calculate_audit_hash(entry2)
            
            hashes_match = hash1 == hash2
            
            return DeterminismTestResult(
                test_name="audit_log_hash_matching",
                passed=hashes_match,
                error_message="" if hashes_match else f"Audit log hashes don't match: {hash1} != {hash2}",
                details={
                    'hash1': hash1,
                    'hash2': hash2,
                    'entry1': self._audit_entry_to_dict(entry1),
                    'entry2': self._audit_entry_to_dict(entry2)
                },
                non_determinism_sources=["audit_log_content"] if not hashes_match else []
            )
            
        except Exception as e:
            return DeterminismTestResult(
                test_name="audit_log_hash_matching",
                passed=False,
                error_message=f"Test failed with error: {e}",
                non_determinism_sources=["test_execution_error"]
            )
    
    def identify_non_determinism_sources(self) -> DeterminismTestResult:
        """
        Systematically identify sources of non-determinism in the pipeline.
        Requirement 32.6
        """
        try:
            sources = []
            
            # Test 1: Check if timestamps cause non-determinism
            spec = DocumentSpec(size_pages=2, words_per_page=100)
            policy_content = self.data_generator.generate_policy_document(spec)
            policy_path = self.temp_dir / "nondeterminism_test.md"
            policy_path.write_text(policy_content)
            
            config = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'temperature': 0.0,
                'output_dir': str(self.temp_dir / "nondeterminism_outputs"),
                'audit_dir': str(self.temp_dir / "nondeterminism_audit")
            })
            
            pipeline = AnalysisPipeline(config)
            pipeline.initialize_resources()
            
            # Run twice with small delay
            result1 = pipeline.execute(str(policy_path))
            time.sleep(0.1)
            result2 = pipeline.execute(str(policy_path))
            
            comparison = self._compare_analysis_results(result1, result2)
            
            # Analyze differences to identify sources
            if not comparison['identical']:
                if 'timestamp' in str(comparison['differences']):
                    sources.append("timestamps_in_outputs")
                if 'random' in str(comparison['differences']).lower():
                    sources.append("random_number_generation")
                if 'llm' in str(comparison['differences']).lower():
                    sources.append("llm_non_determinism")
                if 'embedding' in str(comparison['differences']).lower():
                    sources.append("embedding_non_determinism")
                if 'retrieval' in str(comparison['differences']).lower():
                    sources.append("retrieval_ordering")
            
            # Test 2: Check LLM with different temperatures
            config_temp_high = PipelineConfig({
                'chunk_size': 512,
                'overlap': 50,
                'temperature': 0.7,  # Non-deterministic
                'output_dir': str(self.temp_dir / "temp_high_outputs"),
                'audit_dir': str(self.temp_dir / "temp_high_audit")
            })
            
            pipeline_temp = AnalysisPipeline(config_temp_high)
            pipeline_temp.initialize_resources()
            
            result_temp1 = pipeline_temp.execute(str(policy_path))
            result_temp2 = pipeline_temp.execute(str(policy_path))
            
            comparison_temp = self._compare_analysis_results(result_temp1, result_temp2)
            if not comparison_temp['identical']:
                sources.append("llm_temperature_sampling")
            
            # Compile report
            return DeterminismTestResult(
                test_name="identify_non_determinism_sources",
                passed=True,  # This test always passes, it's informational
                details={
                    'identified_sources': sources,
                    'temperature_0_comparison': comparison,
                    'temperature_0.7_comparison': comparison_temp
                },
                non_determinism_sources=sources
            )
            
        except Exception as e:
            return DeterminismTestResult(
                test_name="identify_non_determinism_sources",
                passed=False,
                error_message=f"Test failed with error: {e}",
                non_determinism_sources=["test_execution_error"]
            )
    
    # Helper methods
    
    def _compare_analysis_results(self, result1, result2) -> Dict[str, Any]:
        """Compare two analysis results for determinism."""
        differences = []
        non_determinism_sources = []
        
        # Compare gap counts
        gap_count1 = len(result1.gap_report.gaps)
        gap_count2 = len(result2.gap_report.gaps)
        if gap_count1 != gap_count2:
            differences.append(f"Gap count differs: {gap_count1} vs {gap_count2}")
            non_determinism_sources.append("gap_detection")
        
        # Compare gap IDs
        gap_ids1 = sorted([gap.subcategory_id for gap in result1.gap_report.gaps])
        gap_ids2 = sorted([gap.subcategory_id for gap in result2.gap_report.gaps])
        if gap_ids1 != gap_ids2:
            differences.append(f"Gap IDs differ: {set(gap_ids1) ^ set(gap_ids2)}")
            non_determinism_sources.append("gap_identification")
        
        # Compare gap explanations (check if they're similar, not necessarily identical)
        for gap1, gap2 in zip(result1.gap_report.gaps, result2.gap_report.gaps):
            if gap1.subcategory_id == gap2.subcategory_id:
                if gap1.gap_explanation != gap2.gap_explanation:
                    differences.append(f"Explanation differs for {gap1.subcategory_id}")
                    non_determinism_sources.append("llm_explanation_generation")
                    break
        
        # Compare coverage scores
        if hasattr(result1.gap_report, 'coverage_summary') and hasattr(result2.gap_report, 'coverage_summary'):
            if result1.gap_report.coverage_summary != result2.gap_report.coverage_summary:
                differences.append("Coverage summary differs")
                non_determinism_sources.append("coverage_calculation")
        
        identical = len(differences) == 0
        
        return {
            'identical': identical,
            'differences': differences,
            'non_determinism_sources': list(set(non_determinism_sources))
        }
    
    def _calculate_audit_hash(self, entry) -> str:
        """Calculate hash of audit log entry excluding non-deterministic fields."""
        # Extract deterministic fields
        deterministic_data = {
            'input_file_hash': entry.input_file_hash,
            'model_name': entry.model_name,
            'model_version': entry.model_version,
            'embedding_model_version': entry.embedding_model_version,
            'configuration_parameters': entry.configuration_parameters,
            'retrieval_parameters': entry.retrieval_parameters,
            'prompt_template_version': entry.prompt_template_version
        }
        
        # Calculate hash
        data_str = json.dumps(deterministic_data, sort_keys=True)
        return hashlib.sha256(data_str.encode()).hexdigest()
    
    def _audit_entry_to_dict(self, entry) -> Dict[str, Any]:
        """Convert audit entry to dictionary for comparison."""
        return {
            'input_file_hash': entry.input_file_hash,
            'model_name': entry.model_name,
            'model_version': entry.model_version,
            'embedding_model_version': entry.embedding_model_version,
            'configuration_parameters': entry.configuration_parameters,
            'retrieval_parameters': entry.retrieval_parameters,
            'prompt_template_version': entry.prompt_template_version
        }
    
    def _identify_common_non_determinism_sources(self, non_reproducible_policies: List[Dict]) -> List[str]:
        """Identify common sources of non-determinism across multiple policies."""
        if not non_reproducible_policies:
            return []
        
        # Count occurrences of different types of differences
        source_counts = {}
        for policy in non_reproducible_policies:
            diffs = str(policy.get('differences', ''))
            if 'gap count' in diffs.lower():
                source_counts['gap_detection'] = source_counts.get('gap_detection', 0) + 1
            if 'explanation' in diffs.lower():
                source_counts['llm_generation'] = source_counts.get('llm_generation', 0) + 1
            if 'coverage' in diffs.lower():
                source_counts['coverage_calculation'] = source_counts.get('coverage_calculation', 0) + 1
        
        # Return sources that appear in >50% of non-reproducible cases
        threshold = len(non_reproducible_policies) * 0.5
        common_sources = [source for source, count in source_counts.items() if count >= threshold]
        
        return common_sources if common_sources else ['unknown']


# Pytest test functions

def test_same_policy_twice_identical_config():
    """Test that analyzing the same policy twice produces identical results."""
    validator = DeterminismValidator()
    try:
        result = validator.test_same_policy_twice_identical_config()
        print(f"\nSame policy twice: {'PASSED' if result.passed else 'FAILED'}")
        if not result.passed:
            print(f"Error: {result.error_message}")
            print(f"Non-determinism sources: {result.non_determinism_sources}")
        assert result.passed, result.error_message
    finally:
        validator.cleanup()


def test_same_policy_different_machines():
    """Test that analyzing the same policy on different machines produces identical results."""
    validator = DeterminismValidator()
    try:
        result = validator.test_same_policy_different_machines()
        print(f"\nSame policy different machines: {'PASSED' if result.passed else 'FAILED'}")
        if not result.passed:
            print(f"Error: {result.error_message}")
            print(f"Non-determinism sources: {result.non_determinism_sources}")
        assert result.passed, result.error_message
    finally:
        validator.cleanup()


def test_temperature_zero_determinism():
    """Test that temperature=0.0 produces deterministic outputs."""
    validator = DeterminismValidator()
    try:
        result = validator.test_temperature_zero_determinism()
        print(f"\nTemperature=0.0 determinism: {'PASSED' if result.passed else 'FAILED'}")
        if not result.passed:
            print(f"Error: {result.error_message}")
            print(f"Non-determinism sources: {result.non_determinism_sources}")
        assert result.passed, result.error_message
    finally:
        validator.cleanup()


def test_multiple_policies_reproducibility():
    """Test reproducibility across 20+ different policies."""
    validator = DeterminismValidator()
    try:
        result = validator.test_multiple_policies_reproducibility(num_policies=20)
        print(f"\nMultiple policies reproducibility: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Reproducibility rate: {result.details.get('reproducibility_rate', 0):.2%}")
        if not result.passed:
            print(f"Error: {result.error_message}")
            print(f"Non-determinism sources: {result.non_determinism_sources}")
        assert result.passed, result.error_message
    finally:
        validator.cleanup()


def test_audit_log_hash_matching():
    """Test that audit log hashes match for identical analyses."""
    validator = DeterminismValidator()
    try:
        result = validator.test_audit_log_hash_matching()
        print(f"\nAudit log hash matching: {'PASSED' if result.passed else 'FAILED'}")
        if not result.passed:
            print(f"Error: {result.error_message}")
            print(f"Non-determinism sources: {result.non_determinism_sources}")
        assert result.passed, result.error_message
    finally:
        validator.cleanup()


def test_identify_non_determinism_sources():
    """Identify sources of non-determinism in the pipeline."""
    validator = DeterminismValidator()
    try:
        result = validator.identify_non_determinism_sources()
        print(f"\nIdentify non-determinism sources: {'PASSED' if result.passed else 'FAILED'}")
        print(f"Identified sources: {result.non_determinism_sources}")
        if result.details:
            print(f"Details: {json.dumps(result.details, indent=2)}")
        # This test is informational, so we don't assert
    finally:
        validator.cleanup()


if __name__ == "__main__":
    print("Running Determinism and Reproducibility Tests...")
    print("=" * 80)
    
    print("\n### Test 1: Same Policy Twice with Identical Config ###")
    test_same_policy_twice_identical_config()
    
    print("\n### Test 2: Same Policy on Different Machines ###")
    test_same_policy_different_machines()
    
    print("\n### Test 3: Temperature=0.0 Determinism ###")
    test_temperature_zero_determinism()
    
    print("\n### Test 4: Multiple Policies Reproducibility ###")
    test_multiple_policies_reproducibility()
    
    print("\n### Test 5: Audit Log Hash Matching ###")
    test_audit_log_hash_matching()
    
    print("\n### Test 6: Identify Non-Determinism Sources ###")
    test_identify_non_determinism_sources()
    
    print("\n" + "=" * 80)
    print("All determinism tests completed!")
