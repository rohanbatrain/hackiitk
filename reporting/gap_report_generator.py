"""
Gap report generator for the Offline Policy Gap Analyzer.

This module generates gap analysis reports in both markdown and JSON formats,
including metadata for traceability and compliance.
"""

import json
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from models.domain import GapAnalysisReport, GapDetail
from models.schemas import validate_gap_analysis_report


class GapReportGenerator:
    """Generates gap analysis reports in markdown and JSON formats.
    
    The generator produces human-readable markdown reports with formatted
    sections for each gap, and machine-readable JSON reports conforming to
    the documented schema for integration and testing.
    """
    
    def __init__(self):
        """Initialize the gap report generator."""
        pass
    
    def generate_markdown(self, report: GapAnalysisReport, output_path: str) -> None:
        """
        Generate markdown gap analysis report.
        
        Args:
            report: GapAnalysisReport object containing analysis results
            output_path: Path where markdown file should be written
            
        The markdown report includes:
        - Analysis metadata (date, model, input file)
        - Summary statistics
        - Detailed gap sections with severity indicators
        - Evidence quotes from policy
        - Suggested fixes
        """
        md_content = self._build_markdown_content(report)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(md_content, encoding='utf-8')
    
    def generate_json(self, report: GapAnalysisReport, output_path: str) -> None:
        """
        Generate JSON gap analysis report.
        
        Args:
            report: GapAnalysisReport object containing analysis results
            output_path: Path where JSON file should be written
            
        The JSON report conforms to the documented schema and includes:
        - All gap details with required fields
        - Analysis metadata
        - Configuration parameters
        
        Raises:
            ValidationError: If generated JSON does not conform to schema
        """
        json_data = self._build_json_data(report)
        
        # Validate against schema before writing
        validate_gap_analysis_report(json_data)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(json_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
    
    def _build_markdown_content(self, report: GapAnalysisReport) -> str:
        """Build markdown content from gap analysis report."""
        lines = []
        
        # Header
        lines.append("# Gap Analysis Report")
        lines.append("")
        
        # Metadata section
        lines.append("## Analysis Metadata")
        lines.append("")
        lines.append(f"- **Analysis Date**: {self._format_datetime(report.analysis_date)}")
        lines.append(f"- **Input File**: `{report.input_file}`")
        lines.append(f"- **Input File Hash**: `{report.input_file_hash}`")
        lines.append(f"- **Model Name**: {report.model_name}")
        lines.append(f"- **Model Version**: {report.model_version}")
        lines.append(f"- **Embedding Model**: {report.embedding_model}")
        
        # Add metadata details
        if report.metadata:
            if 'prompt_version' in report.metadata:
                lines.append(f"- **Prompt Version**: {report.metadata['prompt_version']}")
            if 'config_hash' in report.metadata:
                lines.append(f"- **Config Hash**: `{report.metadata['config_hash']}`")
            if 'retrieval_params' in report.metadata:
                lines.append(f"- **Retrieval Parameters**: {json.dumps(report.metadata['retrieval_params'])}")
        
        lines.append("")
        
        # Summary section
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- **Total Gaps Identified**: {len(report.gaps)}")
        lines.append(f"- **Covered Subcategories**: {len(report.covered_subcategories)}")
        
        # Count by severity
        severity_counts = self._count_by_severity(report.gaps)
        lines.append(f"- **Critical Gaps**: {severity_counts.get('critical', 0)}")
        lines.append(f"- **High Severity Gaps**: {severity_counts.get('high', 0)}")
        lines.append(f"- **Medium Severity Gaps**: {severity_counts.get('medium', 0)}")
        lines.append(f"- **Low Severity Gaps**: {severity_counts.get('low', 0)}")
        lines.append("")
        
        # Gaps section
        if report.gaps:
            lines.append("## Identified Gaps")
            lines.append("")
            
            for i, gap in enumerate(report.gaps, 1):
                lines.extend(self._format_gap_section(gap, i))
        else:
            lines.append("## Identified Gaps")
            lines.append("")
            lines.append("No gaps identified. The policy appears to adequately cover all analyzed NIST CSF 2.0 subcategories.")
            lines.append("")
        
        # Covered subcategories section
        if report.covered_subcategories:
            lines.append("## Covered Subcategories")
            lines.append("")
            lines.append("The following NIST CSF 2.0 subcategories are adequately covered by the policy:")
            lines.append("")
            for subcategory_id in sorted(report.covered_subcategories):
                lines.append(f"- {subcategory_id}")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_gap_section(self, gap: GapDetail, index: int) -> list:
        """Format a single gap as markdown section."""
        lines = []
        
        # Gap header with severity indicator
        severity_emoji = self._get_severity_emoji(gap.severity)
        lines.append(f"### Gap {index}: {gap.subcategory_id} {severity_emoji}")
        lines.append("")
        
        # Severity badge
        lines.append(f"**Severity**: {gap.severity.upper()}")
        lines.append("")
        
        # Status
        lines.append(f"**Status**: {gap.status.replace('_', ' ').title()}")
        lines.append("")
        
        # Description
        lines.append("**NIST CSF Requirement**:")
        lines.append("")
        lines.append(f"> {gap.subcategory_description}")
        lines.append("")
        
        # Evidence quote
        lines.append("**Evidence from Policy**:")
        lines.append("")
        if gap.evidence_quote:
            lines.append(f"> {gap.evidence_quote}")
        else:
            lines.append("> *(No relevant text found in policy)*")
        lines.append("")
        
        # Gap explanation
        lines.append("**Gap Explanation**:")
        lines.append("")
        lines.append(gap.gap_explanation)
        lines.append("")
        
        # Suggested fix
        lines.append("**Suggested Fix**:")
        lines.append("")
        lines.append(gap.suggested_fix)
        lines.append("")
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _build_json_data(self, report: GapAnalysisReport) -> Dict[str, Any]:
        """Build JSON data structure from gap analysis report."""
        return {
            "analysis_date": self._format_datetime_iso(report.analysis_date),
            "input_file": report.input_file,
            "input_file_hash": report.input_file_hash,
            "model_name": report.model_name,
            "model_version": report.model_version,
            "embedding_model": report.embedding_model,
            "gaps": [
                {
                    "subcategory_id": gap.subcategory_id,
                    "description": gap.subcategory_description,
                    "status": gap.status,
                    "evidence_quote": gap.evidence_quote,
                    "gap_explanation": gap.gap_explanation,
                    "severity": gap.severity,
                    "suggested_fix": gap.suggested_fix
                }
                for gap in report.gaps
            ],
            "covered_subcategories": report.covered_subcategories,
            "metadata": report.metadata
        }
    
    def _count_by_severity(self, gaps: list) -> Dict[str, int]:
        """Count gaps by severity level."""
        counts = {}
        for gap in gaps:
            severity = gap.severity
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _extract_function_from_id(self, subcategory_id: str) -> str:
        """Extract CSF function from subcategory ID.
        
        Args:
            subcategory_id: CSF subcategory ID (e.g., "GV.OC-01", "PR.DS-01")
            
        Returns:
            Function name or "UNKNOWN" if cannot be determined
        """
        if not subcategory_id:
            return "UNKNOWN"
        
        # Extract prefix before first dot
        prefix = subcategory_id.split('.')[0] if '.' in subcategory_id else subcategory_id[:2]
        
        # Map prefix to function name
        function_map = {
            'GV': 'Govern',
            'ID': 'Identify',
            'PR': 'Protect',
            'DE': 'Detect',
            'RS': 'Respond',
            'RC': 'Recover'
        }
        
        return function_map.get(prefix, "UNKNOWN")
    
    def _count_by_severity(self, gaps: list) -> Dict[str, int]:
        """Count gaps by severity level."""
        counts = {}
        for gap in gaps:
            severity = gap.severity
            counts[severity] = counts.get(severity, 0) + 1
        return counts
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji indicator for severity level."""
        emoji_map = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        return emoji_map.get(severity.lower(), '⚪')
    
    def _format_datetime(self, dt: datetime) -> str:
        """Format datetime for human-readable display."""
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    
    def _format_datetime_iso(self, dt: datetime) -> str:
        """Format datetime in ISO 8601 format for JSON."""
        return dt.isoformat()
