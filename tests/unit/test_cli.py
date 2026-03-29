"""
Unit tests for CLI functionality.
"""

import pytest
import sys
from pathlib import Path
from unittest.mock import patch, MagicMock
from io import StringIO

from cli.main import (
    validate_policy_path,
    validate_config_path,
    create_parser,
    ProgressIndicator
)


class TestValidatePolicyPath:
    """Test policy path validation."""
    
    def test_valid_pdf_path(self, tmp_path):
        """Test validation of valid PDF path."""
        policy_file = tmp_path / "policy.pdf"
        policy_file.write_text("test")
        
        result = validate_policy_path(str(policy_file))
        assert result == policy_file
    
    def test_valid_docx_path(self, tmp_path):
        """Test validation of valid DOCX path."""
        policy_file = tmp_path / "policy.docx"
        policy_file.write_text("test")
        
        result = validate_policy_path(str(policy_file))
        assert result == policy_file
    
    def test_valid_txt_path(self, tmp_path):
        """Test validation of valid TXT path."""
        policy_file = tmp_path / "policy.txt"
        policy_file.write_text("test")
        
        result = validate_policy_path(str(policy_file))
        assert result == policy_file
    
    def test_valid_md_path(self, tmp_path):
        """Test validation of valid MD path."""
        policy_file = tmp_path / "policy.md"
        policy_file.write_text("test")
        
        result = validate_policy_path(str(policy_file))
        assert result == policy_file
    
    def test_nonexistent_file(self):
        """Test validation fails for nonexistent file."""
        with pytest.raises(SystemExit) as exc_info:
            validate_policy_path("nonexistent.pdf")
        assert exc_info.value.code == 1
    
    def test_unsupported_format(self, tmp_path):
        """Test validation fails for unsupported format."""
        policy_file = tmp_path / "policy.xyz"
        policy_file.write_text("test")
        
        with pytest.raises(SystemExit) as exc_info:
            validate_policy_path(str(policy_file))
        assert exc_info.value.code == 1
    
    def test_directory_not_file(self, tmp_path):
        """Test validation fails for directory."""
        with pytest.raises(SystemExit) as exc_info:
            validate_policy_path(str(tmp_path))
        assert exc_info.value.code == 1


class TestValidateConfigPath:
    """Test config path validation."""
    
    def test_valid_config_path(self, tmp_path):
        """Test validation of valid config path."""
        config_file = tmp_path / "config.yaml"
        config_file.write_text("test: value")
        
        result = validate_config_path(str(config_file))
        assert result == config_file
    
    def test_none_config_path(self):
        """Test validation with None returns None."""
        result = validate_config_path(None)
        assert result is None
    
    def test_nonexistent_config(self):
        """Test validation fails for nonexistent config."""
        with pytest.raises(SystemExit) as exc_info:
            validate_config_path("nonexistent.yaml")
        assert exc_info.value.code == 1


class TestProgressIndicator:
    """Test progress indicator."""
    
    def test_progress_update(self, capsys):
        """Test progress indicator updates."""
        progress = ProgressIndicator(enabled=True)
        progress.update(5, "Testing")
        
        captured = capsys.readouterr()
        assert "Testing" in captured.out
        assert "%" in captured.out
    
    def test_progress_disabled(self, capsys):
        """Test progress indicator when disabled."""
        progress = ProgressIndicator(enabled=False)
        progress.update(5, "Testing")
        
        captured = capsys.readouterr()
        assert captured.out == ""
    
    def test_progress_finish(self, capsys):
        """Test progress indicator finish."""
        progress = ProgressIndicator(enabled=True)
        progress.finish()
        
        captured = capsys.readouterr()
        assert "100%" in captured.out
        assert "Complete" in captured.out


class TestArgumentParser:
    """Test argument parser."""
    
    def test_parser_creation(self):
        """Test parser can be created."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "policy-analyzer"
    
    def test_required_policy_path(self):
        """Test policy-path is required."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args([])
    
    def test_parse_minimal_args(self):
        """Test parsing minimal arguments."""
        parser = create_parser()
        args = parser.parse_args(["--policy-path", "test.pdf"])
        
        assert args.policy_path == "test.pdf"
        assert args.config is None
        assert args.domain is None
        assert args.output_dir is None
        assert args.model is None
        assert args.verbose is False
    
    def test_parse_all_args(self):
        """Test parsing all arguments."""
        parser = create_parser()
        args = parser.parse_args([
            "--policy-path", "test.pdf",
            "--config", "config.yaml",
            "--domain", "isms",
            "--output-dir", "./output",
            "--model", "qwen2.5-3b",
            "--verbose"
        ])
        
        assert args.policy_path == "test.pdf"
        assert args.config == "config.yaml"
        assert args.domain == "isms"
        assert args.output_dir == "./output"
        assert args.model == "qwen2.5-3b"
        assert args.verbose is True
    
    def test_domain_choices(self):
        """Test domain argument accepts valid choices."""
        parser = create_parser()
        
        valid_domains = ["isms", "risk_management", "patch_management", "data_privacy"]
        for domain in valid_domains:
            args = parser.parse_args(["--policy-path", "test.pdf", "--domain", domain])
            assert args.domain == domain
    
    def test_invalid_domain(self):
        """Test invalid domain is rejected."""
        parser = create_parser()
        
        with pytest.raises(SystemExit):
            parser.parse_args(["--policy-path", "test.pdf", "--domain", "invalid"])


class TestCLIIntegration:
    """Integration tests for CLI."""
    
    @patch('cli.main.AnalysisPipeline')
    def test_successful_analysis(self, mock_pipeline, tmp_path):
        """Test successful analysis execution."""
        # Create test policy file
        policy_file = tmp_path / "test.pdf"
        policy_file.write_text("test policy")
        
        # Mock pipeline
        mock_instance = MagicMock()
        mock_pipeline.return_value = mock_instance
        
        # Mock result
        mock_result = MagicMock()
        mock_result.gap_report.gaps = []
        mock_result.metadata = {
            'gap_report_path': 'report.md',
            'revised_policy_path': 'policy.md',
            'roadmap_path': 'roadmap.md',
            'audit_log_path': 'audit.json',
            'duration_seconds': 10.5
        }
        mock_instance.execute.return_value = mock_result
        
        # Import and run
        from cli.main import run_analysis
        from orchestration.analysis_pipeline import PipelineConfig
        
        config = PipelineConfig()
        exit_code = run_analysis(
            policy_path=policy_file,
            config=config,
            domain="isms"
        )
        
        assert exit_code == 0
        mock_instance.execute.assert_called_once()
        mock_instance.cleanup.assert_called_once()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
