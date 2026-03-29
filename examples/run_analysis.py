#!/usr/bin/env python3
"""
Example script demonstrating the Analysis Pipeline usage.

This script shows how to use the AnalysisPipeline to analyze a policy document
and generate gap reports, revised policies, and implementation roadmaps.
"""

import sys
import argparse
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from orchestration.analysis_pipeline import AnalysisPipeline, PipelineConfig
from utils.logger import setup_logging


def main():
    """Main entry point for analysis pipeline example."""
    parser = argparse.ArgumentParser(
        description='Analyze policy document against NIST CSF 2.0 standards'
    )
    parser.add_argument(
        'policy_path',
        help='Path to policy document (PDF, DOCX, or TXT)'
    )
    parser.add_argument(
        '--domain',
        choices=['isms', 'risk_management', 'patch_management', 'data_privacy'],
        help='Policy domain for prioritization (optional)'
    )
    parser.add_argument(
        '--output-dir',
        default='outputs',
        help='Output directory for results (default: outputs)'
    )
    parser.add_argument(
        '--config',
        help='Path to configuration file (YAML or JSON)'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        default='INFO',
        help='Logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Setup logging
    setup_logging(log_level=args.log_level, console_output=True)
    
    # Load configuration
    if args.config:
        from utils.config_loader import ConfigLoader
        loader = ConfigLoader()
        config = loader.load(args.config)
        
        # Convert to PipelineConfig
        pipeline_config = PipelineConfig({
            'chunk_size': config.chunk_size,
            'overlap': config.overlap,
            'top_k': config.top_k,
            'temperature': config.temperature,
            'max_tokens': config.max_tokens,
            'output_dir': args.output_dir
        })
    else:
        # Use default configuration
        pipeline_config = PipelineConfig({'output_dir': args.output_dir})
    
    # Create and execute pipeline
    print(f"\n{'='*80}")
    print(f"Offline Policy Gap Analyzer")
    print(f"{'='*80}\n")
    print(f"Policy: {args.policy_path}")
    print(f"Domain: {args.domain or 'auto-detect'}")
    print(f"Output: {args.output_dir}")
    print(f"\nStarting analysis...\n")
    
    try:
        pipeline = AnalysisPipeline(config=pipeline_config)
        
        result = pipeline.execute(
            policy_path=args.policy_path,
            domain=args.domain,
            output_dir=args.output_dir
        )
        
        # Print summary
        print(f"\n{'='*80}")
        print(f"Analysis Complete!")
        print(f"{'='*80}\n")
        print(f"Duration: {result.duration_seconds:.2f} seconds")
        print(f"\nResults:")
        print(f"  - Gaps identified: {len(result.gap_report.gaps)}")
        print(f"  - Subcategories covered: {len(result.gap_report.covered_subcategories)}")
        print(f"  - Policy revisions: {len(result.revised_policy.revisions)}")
        print(f"  - Immediate actions: {len(result.roadmap.immediate_actions)}")
        print(f"  - Near-term actions: {len(result.roadmap.near_term_actions)}")
        print(f"  - Medium-term actions: {len(result.roadmap.medium_term_actions)}")
        print(f"\nOutputs written to: {result.output_directory}")
        print(f"\nFiles generated:")
        print(f"  - gap_analysis_report.md")
        print(f"  - gap_analysis_report.json")
        print(f"  - revised_policy.md")
        print(f"  - implementation_roadmap.md")
        print(f"  - implementation_roadmap.json")
        print(f"\nAudit log created in: {pipeline_config.audit_dir}")
        print()
        
        # Cleanup
        pipeline.cleanup()
        
        return 0
        
    except FileNotFoundError as e:
        print(f"\nError: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"\nError: Analysis failed: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
