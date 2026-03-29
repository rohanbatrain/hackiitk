"""
Output Manager for the Offline Policy Gap Analyzer.

This module handles all file outputs for the analysis system, including:
- Timestamped output directory creation
- File conflict handling (overwrite confirmation or unique naming)
- Generation of gap analysis reports (MD + JSON)
- Generation of revised policy documents (MD)
- Generation of implementation roadmaps (MD + JSON)
- Metadata inclusion in all outputs

**Validates: Requirements 14.1, 14.2, 14.3, 14.4, 14.5, 14.6, 14.7, 14.8**
"""

import json
import logging
import hashlib
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional

from models.domain import (
    GapAnalysisReport,
    RevisedPolicy,
    ImplementationRoadmap
)
from reporting.gap_report_generator import GapReportGenerator
from reporting.roadmap_generator import RoadmapGenerator


logger = logging.getLogger(__name__)


class OutputManager:
    """Manages all file outputs for the analysis system.
    
    The OutputManager is responsible for:
    - Creating timestamped output directories
    - Handling file conflicts (prompt for overwrite or generate unique names)
    - Writing gap analysis reports (markdown and JSON)
    - Writing revised policy documents (markdown)
    - Writing implementation roadmaps (markdown and JSON)
    - Including metadata in all outputs for traceability
    
    All outputs include metadata:
    - analysis_date: Timestamp of analysis execution
    - model_version: LLM model version used
    - model_name: LLM model name used
    - input_file_name: Name of analyzed policy file
    - prompt_template_version: Version of prompt templates
    - configuration_hash: Hash of configuration parameters
    - retrieval_parameters: Retrieval configuration used
    
    Attributes:
        base_output_dir: Base directory for all outputs
        gap_report_generator: Generator for gap analysis reports
        roadmap_generator: Generator for implementation roadmaps
        prompt_for_overwrite: Whether to prompt user for overwrite confirmation
    """
    
    def __init__(
        self,
        base_output_dir: str = "outputs",
        prompt_for_overwrite: bool = True
    ):
        """Initialize output manager.
        
        Args:
            base_output_dir: Base directory for all outputs (default: "outputs")
            prompt_for_overwrite: Whether to prompt for overwrite confirmation
        """
        self.base_output_dir = Path(base_output_dir)
        self.gap_report_generator = GapReportGenerator()
        self.roadmap_generator = RoadmapGenerator(catalog=None)  # Catalog set later
        self.prompt_for_overwrite = prompt_for_overwrite
        
        logger.info(f"Initialized OutputManager with base_output_dir={base_output_dir}")
    
    def set_roadmap_catalog(self, catalog):
        """Set the reference catalog for roadmap generator.
        
        Args:
            catalog: ReferenceCatalog instance
        """
        self.roadmap_generator.catalog = catalog
    
    def create_output_directory(
        self,
        timestamp: Optional[datetime] = None
    ) -> Path:
        """Create timestamped output directory.
        
        Creates a directory with format: outputs/analysis_YYYYMMDD_HHMMSS/
        
        Args:
            timestamp: Optional timestamp to use (defaults to current time)
            
        Returns:
            Path to created output directory
            
        Raises:
            OSError: If directory creation fails
        """
        if timestamp is None:
            timestamp = datetime.now()
        
        # Format: analysis_YYYYMMDD_HHMMSS
        dir_name = f"analysis_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        output_dir = self.base_output_dir / dir_name
        
        # Create directory
        output_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Created output directory: {output_dir}")
        
        return output_dir
    
    def handle_file_conflict(
        self,
        file_path: Path,
        prompt_user: bool = None
    ) -> Path:
        """Handle file conflict by prompting for overwrite or generating unique name.
        
        Args:
            file_path: Path to file that may exist
            prompt_user: Whether to prompt user (defaults to self.prompt_for_overwrite)
            
        Returns:
            Path to use (original or unique)
            
        Raises:
            FileExistsError: If user declines overwrite
        """
        if not file_path.exists():
            return file_path
        
        if prompt_user is None:
            prompt_user = self.prompt_for_overwrite
        
        if prompt_user:
            # Prompt user for overwrite confirmation
            logger.warning(f"File already exists: {file_path}")
            response = input(f"File {file_path.name} already exists. Overwrite? (y/n): ")
            
            if response.lower() in ['y', 'yes']:
                logger.info(f"User confirmed overwrite: {file_path}")
                return file_path
            else:
                logger.info("User declined overwrite, generating unique filename")
                return self._generate_unique_filename(file_path)
        else:
            # Automatically generate unique filename
            logger.info(f"File exists, generating unique filename: {file_path}")
            return self._generate_unique_filename(file_path)
    
    def _generate_unique_filename(self, file_path: Path) -> Path:
        """Generate unique filename by appending counter.
        
        Args:
            file_path: Original file path
            
        Returns:
            Unique file path with counter suffix
        """
        counter = 1
        stem = file_path.stem
        suffix = file_path.suffix
        parent = file_path.parent
        
        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                logger.info(f"Generated unique filename: {new_path}")
                return new_path
            counter += 1
    
    def write_gap_analysis_report(
        self,
        report: GapAnalysisReport,
        output_dir: Path,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Path]:
        """Write gap analysis report in markdown and JSON formats.
        
        Args:
            report: GapAnalysisReport object
            output_dir: Directory to write outputs
            metadata: Optional additional metadata to include
            
        Returns:
            Dictionary with 'markdown' and 'json' keys mapping to file paths
            
        Raises:
            IOError: If file writing fails
        """
        logger.info("Writing gap analysis report")
        
        # Merge additional metadata
        if metadata:
            report.metadata.update(metadata)
        
        # Define output paths
        md_path = output_dir / "gap_analysis_report.md"
        json_path = output_dir / "gap_analysis_report.json"
        
        # Handle file conflicts
        md_path = self.handle_file_conflict(md_path)
        json_path = self.handle_file_conflict(json_path)
        
        # Generate markdown report
        self.gap_report_generator.generate_markdown(report, str(md_path))
        logger.info(f"Wrote gap analysis markdown: {md_path}")
        
        # Generate JSON report
        self.gap_report_generator.generate_json(report, str(json_path))
        logger.info(f"Wrote gap analysis JSON: {json_path}")
        
        return {
            'markdown': md_path,
            'json': json_path
        }
    
    def write_revised_policy(
        self,
        revised_policy: RevisedPolicy,
        output_dir: Path,
        input_file_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Path:
        """Write revised policy document in markdown format.
        
        Args:
            revised_policy: RevisedPolicy object
            output_dir: Directory to write output
            input_file_name: Name of original policy file
            metadata: Optional additional metadata to include
            
        Returns:
            Path to written file
            
        Raises:
            IOError: If file writing fails
        """
        logger.info("Writing revised policy")
        
        # Define output path
        md_path = output_dir / "revised_policy.md"
        
        # Handle file conflict
        md_path = self.handle_file_conflict(md_path)
        
        # Build markdown content
        md_content = self._build_revised_policy_markdown(
            revised_policy,
            input_file_name,
            metadata
        )
        
        # Write file
        md_path.write_text(md_content, encoding='utf-8')
        logger.info(f"Wrote revised policy: {md_path}")
        
        return md_path
    
    def write_implementation_roadmap(
        self,
        roadmap: ImplementationRoadmap,
        output_dir: Path,
        input_file_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Path]:
        """Write implementation roadmap in markdown and JSON formats.
        
        Args:
            roadmap: ImplementationRoadmap object
            output_dir: Directory to write outputs
            input_file_name: Name of analyzed policy file
            metadata: Optional additional metadata to include
            
        Returns:
            Dictionary with 'markdown' and 'json' keys mapping to file paths
            
        Raises:
            IOError: If file writing fails
        """
        logger.info("Writing implementation roadmap")
        
        # Merge additional metadata
        if metadata:
            roadmap.metadata.update(metadata)
        
        # Define output paths
        md_path = output_dir / "implementation_roadmap.md"
        json_path = output_dir / "implementation_roadmap.json"
        
        # Handle file conflicts
        md_path = self.handle_file_conflict(md_path)
        json_path = self.handle_file_conflict(json_path)
        
        # Generate markdown roadmap
        self.roadmap_generator.generate_markdown(roadmap, str(md_path), input_file_name)
        logger.info(f"Wrote roadmap markdown: {md_path}")
        
        # Generate JSON roadmap
        self.roadmap_generator.generate_json(roadmap, str(json_path), input_file_name)
        logger.info(f"Wrote roadmap JSON: {json_path}")
        
        return {
            'markdown': md_path,
            'json': json_path
        }
    
    def write_all_outputs(
        self,
        gap_report: GapAnalysisReport,
        revised_policy: RevisedPolicy,
        roadmap: ImplementationRoadmap,
        input_file_name: str,
        metadata: Optional[Dict[str, Any]] = None,
        output_dir: Optional[Path] = None
    ) -> Dict[str, Any]:
        """Write all analysis outputs to disk.
        
        This is a convenience method that writes all outputs in one call:
        - gap_analysis_report.md
        - gap_analysis_report.json
        - revised_policy.md
        - implementation_roadmap.md
        - implementation_roadmap.json
        
        Args:
            gap_report: GapAnalysisReport object
            revised_policy: RevisedPolicy object
            roadmap: ImplementationRoadmap object
            input_file_name: Name of analyzed policy file
            metadata: Optional metadata to include in all outputs
            output_dir: Optional output directory (creates timestamped if None)
            
        Returns:
            Dictionary with output paths:
            {
                'output_dir': Path,
                'gap_report': {'markdown': Path, 'json': Path},
                'revised_policy': Path,
                'roadmap': {'markdown': Path, 'json': Path}
            }
            
        Raises:
            IOError: If file writing fails
        """
        logger.info(f"Writing all outputs for {input_file_name}")
        
        # Create output directory if not provided
        if output_dir is None:
            output_dir = self.create_output_directory()
        
        # Ensure metadata includes required fields
        if metadata is None:
            metadata = {}
        
        # Write gap analysis report
        gap_paths = self.write_gap_analysis_report(
            gap_report,
            output_dir,
            metadata
        )
        
        # Write revised policy
        policy_path = self.write_revised_policy(
            revised_policy,
            output_dir,
            input_file_name,
            metadata
        )
        
        # Write implementation roadmap
        roadmap_paths = self.write_implementation_roadmap(
            roadmap,
            output_dir,
            input_file_name,
            metadata
        )
        
        logger.info(f"All outputs written to: {output_dir}")
        
        return {
            'output_dir': output_dir,
            'gap_report': gap_paths,
            'revised_policy': policy_path,
            'roadmap': roadmap_paths
        }
    
    def _build_revised_policy_markdown(
        self,
        revised_policy: RevisedPolicy,
        input_file_name: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build markdown content for revised policy.
        
        Args:
            revised_policy: RevisedPolicy object
            input_file_name: Name of original policy file
            metadata: Optional metadata to include
            
        Returns:
            Markdown content string
        """
        lines = []
        
        # Header
        lines.append("# Revised Policy Document")
        lines.append("")
        
        # Metadata section
        lines.append("## Document Metadata")
        lines.append("")
        lines.append(f"- **Original Policy**: `{input_file_name}`")
        lines.append(f"- **Revision Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append(f"- **Revisions Applied**: {len(revised_policy.revisions)}")
        
        if metadata:
            if 'model_name' in metadata:
                lines.append(f"- **Model Used**: {metadata['model_name']}")
            if 'model_version' in metadata:
                lines.append(f"- **Model Version**: {metadata['model_version']}")
            if 'prompt_template_version' in metadata:
                lines.append(f"- **Prompt Version**: {metadata['prompt_template_version']}")
            if 'configuration_hash' in metadata:
                lines.append(f"- **Config Hash**: `{metadata['configuration_hash']}`")
        
        lines.append("")
        
        # Warning section
        lines.append("## ⚠️ Important Notice")
        lines.append("")
        lines.append(revised_policy.warning)
        lines.append("")
        
        # Revised policy content
        lines.append("## Revised Policy Text")
        lines.append("")
        lines.append(revised_policy.revised_text)
        lines.append("")
        
        return "\n".join(lines)
    
    def compute_configuration_hash(self, config: Dict[str, Any]) -> str:
        """Compute SHA-256 hash of configuration parameters.
        
        Args:
            config: Configuration dictionary
            
        Returns:
            Hexadecimal hash string
        """
        # Sort keys for consistent hashing
        config_str = json.dumps(config, sort_keys=True)
        hash_obj = hashlib.sha256(config_str.encode('utf-8'))
        return hash_obj.hexdigest()
    
    def __repr__(self) -> str:
        """String representation of output manager."""
        return f"OutputManager(base_output_dir={self.base_output_dir})"

