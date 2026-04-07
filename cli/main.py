#!/usr/bin/env python3
"""
Command-line interface for Offline Policy Gap Analyzer.

Provides a user-friendly CLI for analyzing policy documents against NIST CSF 2.0.
"""

import argparse
import sys
import signal
from pathlib import Path
from typing import Optional

from utils.logger import setup_logging, logger
from utils.config_loader import ConfigLoader
from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig


class ProgressIndicator:
    """Simple progress indicator for CLI."""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        self.current_step = 0
        self.total_steps = 9
    
    def update(self, step: int, message: str):
        """Update progress display."""
        if not self.enabled:
            return
        
        self.current_step = step
        percentage = int((step / self.total_steps) * 100)
        bar_length = 30
        filled = int((step / self.total_steps) * bar_length)
        bar = "█" * filled + "░" * (bar_length - filled)
        
        print(f"\r[{bar}] {percentage}% - {message}", end="", flush=True)
        
        if step == self.total_steps:
            print()  # New line when complete
    
    def finish(self):
        """Mark progress as complete."""
        if self.enabled:
            self.update(self.total_steps, "Complete")


def signal_handler(signum, frame):
    """Handle keyboard interrupts gracefully."""
    print("\n\n⚠️  Analysis interrupted by user. Cleaning up...")
    sys.exit(130)  # Standard exit code for SIGINT


def validate_policy_path(policy_path: str) -> Path:
    """Validate that policy file exists and has supported extension.
    
    Args:
        policy_path: Path to policy document
        
    Returns:
        Path object for the policy file
        
    Raises:
        SystemExit: If file doesn't exist or has unsupported format
    """
    path = Path(policy_path)
    
    if not path.exists():
        print(f"❌ Error: Policy file not found: {policy_path}")
        sys.exit(1)
    
    if not path.is_file():
        print(f"❌ Error: Path is not a file: {policy_path}")
        sys.exit(1)
    
    supported_extensions = {".pdf", ".docx", ".txt", ".md"}
    if path.suffix.lower() not in supported_extensions:
        print(f"❌ Error: Unsupported file format: {path.suffix}")
        print(f"   Supported formats: {', '.join(supported_extensions)}")
        sys.exit(1)
    
    return path


def validate_config_path(config_path: Optional[str]) -> Optional[Path]:
    """Validate configuration file if provided.
    
    Args:
        config_path: Path to config file or None
        
    Returns:
        Path object or None
        
    Raises:
        SystemExit: If config file specified but doesn't exist
    """
    if config_path is None:
        return None
    
    path = Path(config_path)
    
    if not path.exists():
        print(f"❌ Error: Configuration file not found: {config_path}")
        sys.exit(1)
    
    return path


def load_configuration(config_path: Optional[Path]) -> PipelineConfig:
    """Load configuration from file or use defaults.
    
    Args:
        config_path: Path to config file or None for defaults
        
    Returns:
        PipelineConfig object
    """
    try:
        if config_path:
            print(f"📋 Loading configuration from: {config_path}")
            config_loader = ConfigLoader(str(config_path))
            config_dict = config_loader.load()
            return PipelineConfig(config_dict)
        else:
            print("📋 Using default configuration")
            return PipelineConfig()
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        sys.exit(1)


def run_analysis(
    policy_path: Path,
    config: PipelineConfig,
    domain: Optional[str] = None,
    output_dir: Optional[str] = None,
    model: Optional[str] = None
) -> int:
    """Execute the analysis pipeline.
    
    Args:
        policy_path: Path to policy document
        config: Pipeline configuration
        domain: Optional policy domain
        output_dir: Optional output directory
        model: Optional model name override
        
    Returns:
        Exit code (0 for success, non-zero for error)
    """
    progress = ProgressIndicator()
    
    try:
        # Override config with CLI arguments if provided
        if model:
            config.model_name = model
        
        # Initialize pipeline
        print(f"\n🔍 Analyzing policy: {policy_path.name}")
        if domain:
            print(f"📂 Domain: {domain}")
        print()
        
        pipeline = AnalysisPipeline(config)
        
        # Execute analysis
        progress.update(0, "Initializing...")
        result = pipeline.execute(
            policy_path=str(policy_path),
            domain=domain,
            output_dir=output_dir
        )
        
        progress.finish()
        
        # Print summary
        print("\n" + "=" * 60)
        print("✅ Analysis Complete!")
        print("=" * 60)
        print(f"\n📊 Summary:")
        print(f"   • Gaps identified: {len(result.gap_report.gaps)}")
        print(f"   • Critical gaps: {sum(1 for g in result.gap_report.gaps if g.severity == 'Critical')}")
        print(f"   • High severity gaps: {sum(1 for g in result.gap_report.gaps if g.severity == 'High')}")
        print(f"   • Medium severity gaps: {sum(1 for g in result.gap_report.gaps if g.severity == 'Medium')}")
        print(f"   • Low severity gaps: {sum(1 for g in result.gap_report.gaps if g.severity == 'Low')}")
        
        print(f"\n📁 Outputs generated:")
        print(f"   • Output directory: {result.output_directory}")
        print(f"   • Gap analysis report: {result.output_directory}/gap_analysis_report.json")
        print(f"   • Gap analysis report (MD): {result.output_directory}/gap_analysis_report.md")
        print(f"   • Revised policy: {result.output_directory}/revised_policy.md")
        print(f"   • Implementation roadmap: {result.output_directory}/implementation_roadmap.md")
        print(f"   • Implementation roadmap (JSON): {result.output_directory}/implementation_roadmap.json")
        
        print(f"\n⏱️  Analysis duration: {result.duration_seconds:.1f} seconds")
        print()
        
        return 0
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Analysis interrupted by user")
        return 130
    except FileNotFoundError as e:
        print(f"\n❌ Error: {e}")
        return 1
    except Exception as e:
        print(f"\n❌ Analysis failed: {e}")
        logger.exception("Analysis pipeline failed")
        return 1
    finally:
        # Cleanup
        try:
            if 'pipeline' in locals():
                pipeline.cleanup()
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")


def create_parser() -> argparse.ArgumentParser:
    """Create and configure argument parser.
    
    Returns:
        Configured ArgumentParser
    """
    parser = argparse.ArgumentParser(
        prog="policy-analyzer",
        description="Offline Policy Gap Analyzer - NIST CSF 2.0 Compliance Analysis",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze an ISMS policy
  policy-analyzer --policy-path isms_policy.pdf --domain isms
  
  # Analyze with custom configuration
  policy-analyzer --policy-path policy.docx --config custom.yaml
  
  # Specify output directory and model
  policy-analyzer --policy-path policy.txt --output-dir ./results --model qwen2.5-3b
  
  # Auto-detect domain
  policy-analyzer --policy-path policy.pdf

Supported domains:
  • isms              - Information Security Management System
  • risk_management   - Risk Management
  • patch_management  - Patch Management
  • data_privacy      - Data Privacy

Supported file formats:
  • PDF (.pdf)        - Text-based PDFs only (no OCR)
  • Word (.docx)      - Microsoft Word documents
  • Text (.txt, .md)  - Plain text and Markdown
        """
    )
    
    parser.add_argument(
        "--policy-path",
        type=str,
        required=True,
        metavar="PATH",
        help="Path to policy document (PDF/DOCX/TXT/MD)"
    )
    
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        metavar="PATH",
        help="Path to configuration file (default: use built-in defaults)"
    )
    
    parser.add_argument(
        "--domain",
        type=str,
        choices=["isms", "risk_management", "patch_management", "data_privacy"],
        default=None,
        metavar="DOMAIN",
        help="Policy domain for CSF prioritization (default: auto-detect)"
    )
    
    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        metavar="PATH",
        help="Output directory for results (default: ./outputs/TIMESTAMP)"
    )
    
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        metavar="NAME",
        help="LLM model name (default: from config or qwen2.5-3b)"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Offline Policy Gap Analyzer v0.1.0"
    )
    
    return parser


def main():
    """Main CLI entry point."""
    # Set up signal handler for graceful interrupts
    signal.signal(signal.SIGINT, signal_handler)
    
    # Parse arguments
    parser = create_parser()
    args = parser.parse_args()
    
    # Set up logging with verbose mode
    log_level = "DEBUG" if args.verbose else "INFO"
    setup_logging(log_level=log_level, verbose=args.verbose)
    
    if args.verbose:
        logger.info("=" * 60)
        logger.info("VERBOSE MODE ENABLED")
        logger.info("=" * 60)
        logger.info("Detailed debugging information will be displayed")
        logger.info("This includes:")
        logger.info("  • Function entry/exit traces")
        logger.info("  • Performance metrics")
        logger.info("  • Memory usage tracking")
        logger.info("  • Detailed error stack traces")
        logger.info("  • Component-level debugging")
        logger.info("=" * 60)
        logger.info("")
    
    # Validate inputs
    policy_path = validate_policy_path(args.policy_path)
    config_path = validate_config_path(args.config)
    
    # Load configuration
    config = load_configuration(config_path)
    
    # Run analysis
    exit_code = run_analysis(
        policy_path=policy_path,
        config=config,
        domain=args.domain,
        output_dir=args.output_dir,
        model=args.model
    )
    
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
