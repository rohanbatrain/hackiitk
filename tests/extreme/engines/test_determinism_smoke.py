"""
Smoke test for determinism validation - quick verification that tests can run.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))

from tests.extreme.engines.test_determinism_reproducibility import DeterminismValidator


def test_validator_initialization():
    """Test that the validator can be initialized."""
    validator = DeterminismValidator()
    assert validator is not None
    assert validator.data_generator is not None
    assert validator.temp_dir.exists()
    validator.cleanup()


def test_data_generator_works():
    """Test that the data generator can create test policies."""
    from tests.extreme.data_generator import TestDataGenerator, DocumentSpec
    
    generator = TestDataGenerator()
    spec = DocumentSpec(size_pages=2, words_per_page=100, coverage_percentage=0.5)
    policy_content = generator.generate_policy_document(spec)
    
    assert policy_content is not None
    assert len(policy_content) > 0
    assert "# Cybersecurity Policy Document" in policy_content


if __name__ == "__main__":
    print("Running determinism smoke tests...")
    test_validator_initialization()
    print("✓ Validator initialization test passed")
    
    test_data_generator_works()
    print("✓ Data generator test passed")
    
    print("\nAll smoke tests passed!")
