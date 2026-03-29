"""
Basic setup tests to verify project structure.
"""

import pytest
from pathlib import Path


def test_project_structure():
    """Verify all required directories exist."""
    required_dirs = [
        "ingestion",
        "reference_builder",
        "retrieval",
        "analysis",
        "revision",
        "reporting",
        "models",
        "tests",
        "docs"
    ]
    
    for dir_name in required_dirs:
        assert Path(dir_name).exists(), f"Directory {dir_name} should exist"
        assert Path(dir_name).is_dir(), f"{dir_name} should be a directory"


def test_config_files_exist():
    """Verify configuration files exist."""
    required_files = [
        "config.yaml",
        "requirements.txt",
        "pyproject.toml",
        ".gitignore",
        "README.md"
    ]
    
    for file_name in required_files:
        assert Path(file_name).exists(), f"File {file_name} should exist"
        assert Path(file_name).is_file(), f"{file_name} should be a file"


def test_module_imports():
    """Verify all modules can be imported."""
    modules = [
        "ingestion",
        "reference_builder",
        "retrieval",
        "analysis",
        "revision",
        "reporting",
        "models"
    ]
    
    for module_name in modules:
        try:
            __import__(module_name)
        except ImportError as e:
            pytest.fail(f"Failed to import {module_name}: {e}")


def test_config_file_valid(sample_config):
    """Verify sample configuration is valid."""
    assert "chunking" in sample_config
    assert "retrieval" in sample_config
    assert "llm" in sample_config
    assert "analysis" in sample_config
    
    assert sample_config["chunking"]["chunk_size"] == 512
    assert sample_config["chunking"]["overlap"] == 50
    assert sample_config["retrieval"]["top_k"] == 5
