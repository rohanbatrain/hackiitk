"""
Roadmap Generator for the Offline Policy Gap Analyzer.

This module generates prioritized implementation roadmaps from identified gaps,
categorizing actions into Immediate, Near-term, and Medium-term timeframes based
on severity, and providing specific technical, administrative, and physical steps.

**Validates: Requirements 11.1, 11.2, 11.3, 11.4, 11.5, 11.6, 11.7**
"""

import json
import logging
from datetime import datetime
from typing import List, Dict, Any
from pathlib import Path

from models.domain import (
    GapDetail,
    ActionItem,
    ImplementationRoadmap,
    CSFSubcategory
)
from reference_builder.reference_catalog import ReferenceCatalog
from models.schemas import validate_implementation_roadmap


logger = logging.getLogger(__name__)


class RoadmapGenerator:
    """Generates prioritized implementation roadmaps from identified gaps.
    
    The generator creates actionable implementation plans by:
    - Prioritizing gaps based on severity (Critical/High → Immediate, etc.)
    - Generating specific action items with technical/administrative/physical steps
    - Estimating implementation effort (Low/Medium/High)
    - Maintaining traceability to CSF subcategories and policy sections
    - Outputting both markdown and JSON formats
    
    Attributes:
        catalog: Reference catalog for CSF subcategory context
    """
    
    def __init__(self, catalog: ReferenceCatalog):
        """Initialize roadmap generator.
        
        Args:
            catalog: Reference catalog for CSF subcategory context
        """
        self.catalog = catalog
        logger.info("Initialized RoadmapGenerator")
    
    def generate(self, gaps: List[GapDetail]) -> ImplementationRoadmap:
        """Create prioritized roadmap from identified gaps.
        
        Workflow:
        1. Prioritize gaps into Immediate/Near-term/Medium-term categories
        2. Create action items for each gap
        3. Estimate effort for each action
        4. Generate metadata
        
        Args:
            gaps: List of identified gaps from gap analysis
            
        Returns:
            ImplementationRoadmap with categorized actions
            
        Raises:
            ValueError: If gaps list is empty
        """
        if not gaps:
            logger.warning("No gaps provided, generating empty roadmap")
            return ImplementationRoadmap(
                immediate_actions=[],
                near_term_actions=[],
                medium_term_actions=[],
                metadata={
                    'generation_date': datetime.now().isoformat(),
                    'total_gaps': 0,
                    'total_actions': 0
                }
            )
        
        logger.info(f"Generating roadmap for {len(gaps)} gaps")
        
        # Prioritize gaps into timeframe categories
        prioritized = self.prioritize(gaps)
        
        # Create action items for each category
        immediate_actions = []
        for gap in prioritized['immediate']:
            action = self.create_action(gap)
            immediate_actions.append(action)
        
        near_term_actions = []
        for gap in prioritized['near_term']:
            action = self.create_action(gap)
            near_term_actions.append(action)
        
        medium_term_actions = []
        for gap in prioritized['medium_term']:
            action = self.create_action(gap)
            medium_term_actions.append(action)
        
        # Build metadata
        metadata = {
            'generation_date': datetime.now().isoformat(),
            'total_gaps': len(gaps),
            'total_actions': len(immediate_actions) + len(near_term_actions) + len(medium_term_actions),
            'immediate_count': len(immediate_actions),
            'near_term_count': len(near_term_actions),
            'medium_term_count': len(medium_term_actions)
        }
        
        roadmap = ImplementationRoadmap(
            immediate_actions=immediate_actions,
            near_term_actions=near_term_actions,
            medium_term_actions=medium_term_actions,
            metadata=metadata
        )
        
        logger.info(
            f"Roadmap generated: {len(immediate_actions)} immediate, "
            f"{len(near_term_actions)} near-term, {len(medium_term_actions)} medium-term actions"
        )
        
        return roadmap
    
    def prioritize(self, gaps: List[GapDetail]) -> Dict[str, List[GapDetail]]:
        """Categorize gaps into Immediate/Near-term/Medium-term timeframes.
        
        Prioritization mapping:
        - Critical/High severity → Immediate (0-3 months)
        - Medium severity → Near-term (3-6 months)
        - Low severity → Medium-term (6-12 months)
        
        Args:
            gaps: List of identified gaps
            
        Returns:
            Dictionary with 'immediate', 'near_term', 'medium_term' keys
        """
        immediate = []
        near_term = []
        medium_term = []
        
        for gap in gaps:
            severity = gap.severity.lower()
            
            if severity in ['critical', 'high']:
                immediate.append(gap)
            elif severity == 'medium':
                near_term.append(gap)
            elif severity == 'low':
                medium_term.append(gap)
            else:
                # Default to near-term for unknown severity
                logger.warning(f"Unknown severity '{gap.severity}' for {gap.subcategory_id}, defaulting to near-term")
                near_term.append(gap)
        
        logger.debug(
            f"Prioritized: {len(immediate)} immediate, "
            f"{len(near_term)} near-term, {len(medium_term)} medium-term"
        )
        
        return {
            'immediate': immediate,
            'near_term': near_term,
            'medium_term': medium_term
        }
    
    def create_action(self, gap: GapDetail) -> ActionItem:
        """Generate specific action item for gap.
        
        Creates an action item with:
        - Unique action ID
        - Timeframe based on severity
        - Effort estimate
        - CSF subcategory and policy section references
        - Specific technical, administrative, and physical steps
        
        Args:
            gap: Gap detail to create action for
            
        Returns:
            ActionItem with complete implementation details
        """
        # Generate action ID
        action_id = self._generate_action_id(gap)
        
        # Determine timeframe from severity
        timeframe = self._severity_to_timeframe(gap.severity)
        
        # Estimate effort
        effort = self.estimate_effort(gap)
        
        # Get subcategory details for context
        subcategory = self.catalog.get_subcategory(gap.subcategory_id)
        
        # Determine policy section (use first few words of evidence or "General")
        policy_section = self._extract_policy_section(gap)
        
        # Generate implementation steps
        technical_steps = self._generate_technical_steps(gap, subcategory)
        administrative_steps = self._generate_administrative_steps(gap, subcategory)
        physical_steps = self._generate_physical_steps(gap, subcategory)
        
        # Create description
        description = self._generate_description(gap, subcategory)
        
        action = ActionItem(
            action_id=action_id,
            timeframe=timeframe,
            severity=gap.severity,
            effort=effort,
            csf_subcategory=gap.subcategory_id,
            policy_section=policy_section,
            description=description,
            technical_steps=technical_steps,
            administrative_steps=administrative_steps,
            physical_steps=physical_steps
        )
        
        logger.debug(f"Created action {action_id} for {gap.subcategory_id}")
        
        return action
    
    def estimate_effort(self, gap: GapDetail) -> str:
        """Estimate implementation effort (Low/Medium/High).
        
        Effort estimation considers:
        - Gap status (missing requires more effort than partial)
        - Severity (critical gaps often require more resources)
        - CSF subcategory complexity
        
        Args:
            gap: Gap detail to estimate effort for
            
        Returns:
            Effort level: 'low', 'medium', or 'high'
        """
        # Base effort on gap status
        if gap.status == 'missing':
            # Missing provisions require more effort
            base_effort = 'medium'
        else:
            # Partial coverage requires less effort
            base_effort = 'low'
        
        # Adjust based on severity
        severity = gap.severity.lower()
        
        if severity == 'critical':
            # Critical gaps often require significant resources
            if base_effort == 'medium':
                return 'high'
            else:
                return 'medium'
        elif severity == 'high':
            # High severity may increase effort
            if base_effort == 'low':
                return 'medium'
            else:
                return 'high'
        elif severity == 'low':
            # Low severity typically requires less effort
            return 'low'
        else:
            # Medium severity or unknown
            return base_effort
    
    def _generate_action_id(self, gap: GapDetail) -> str:
        """Generate unique action ID from gap details.
        
        Format: ACT-{subcategory_id}
        Example: ACT-GV.RM-01
        """
        return f"ACT-{gap.subcategory_id}"
    
    def _severity_to_timeframe(self, severity: str) -> str:
        """Convert severity to timeframe.
        
        Mapping:
        - Critical/High → immediate
        - Medium → near_term
        - Low → medium_term
        """
        severity_lower = severity.lower()
        
        if severity_lower in ['critical', 'high']:
            return 'immediate'
        elif severity_lower == 'medium':
            return 'near_term'
        elif severity_lower == 'low':
            return 'medium_term'
        else:
            return 'near_term'  # Default
    
    def _extract_policy_section(self, gap: GapDetail) -> str:
        """Extract policy section name from gap evidence.
        
        Uses evidence quote to infer section, or defaults to "General".
        """
        if gap.evidence_quote and len(gap.evidence_quote) > 0:
            # Try to extract section from first line
            first_line = gap.evidence_quote.split('\n')[0].strip()
            if len(first_line) < 100:  # Likely a heading
                return first_line
        
        # Default to general section
        return "General Policy"
    
    def _generate_description(self, gap: GapDetail, subcategory: CSFSubcategory = None) -> str:
        """Generate action description from gap details."""
        if gap.status == 'missing':
            return f"Establish {subcategory.category if subcategory else 'controls'} to address {gap.subcategory_id}"
        else:
            return f"Strengthen {subcategory.category if subcategory else 'controls'} for {gap.subcategory_id}"
    
    def _generate_technical_steps(self, gap: GapDetail, subcategory: CSFSubcategory = None) -> List[str]:
        """Generate technical implementation steps.
        
        Technical steps focus on systems, tools, and technical controls.
        """
        steps = []
        
        # Extract keywords from subcategory for context
        if subcategory:
            category_lower = subcategory.category.lower()
            
            # Generate steps based on category patterns
            if 'risk' in category_lower:
                steps.extend([
                    "Implement risk assessment tools and frameworks",
                    "Configure risk scoring and tracking systems",
                    "Integrate risk data with security monitoring"
                ])
            elif 'supply chain' in category_lower or 'vendor' in category_lower:
                steps.extend([
                    "Deploy vendor security assessment platform",
                    "Implement third-party risk monitoring tools",
                    "Configure vendor access controls and logging"
                ])
            elif 'access' in category_lower or 'authentication' in category_lower:
                steps.extend([
                    "Implement multi-factor authentication systems",
                    "Configure identity and access management (IAM) platform",
                    "Deploy privileged access management (PAM) solution"
                ])
            elif 'data' in category_lower or 'protection' in category_lower:
                steps.extend([
                    "Implement data classification and labeling tools",
                    "Deploy data loss prevention (DLP) solutions",
                    "Configure encryption for data at rest and in transit"
                ])
            elif 'incident' in category_lower or 'response' in category_lower:
                steps.extend([
                    "Deploy security incident and event management (SIEM) system",
                    "Configure incident response automation tools",
                    "Implement forensics and investigation capabilities"
                ])
            elif 'vulnerability' in category_lower or 'patch' in category_lower:
                steps.extend([
                    "Deploy vulnerability scanning and management platform",
                    "Implement automated patch management system",
                    "Configure vulnerability prioritization and tracking"
                ])
            else:
                # Generic technical steps
                steps.extend([
                    "Implement technical controls and monitoring systems",
                    "Configure security tools and platforms",
                    "Deploy automation for compliance tracking"
                ])
        else:
            # Fallback generic steps
            steps.extend([
                "Implement required technical controls",
                "Configure monitoring and logging systems",
                "Deploy security tools as needed"
            ])
        
        return steps
    
    def _generate_administrative_steps(self, gap: GapDetail, subcategory: CSFSubcategory = None) -> List[str]:
        """Generate administrative implementation steps.
        
        Administrative steps focus on policies, procedures, and governance.
        """
        steps = []
        
        # Always include policy documentation
        if gap.status == 'missing':
            steps.append(f"Draft policy section addressing {gap.subcategory_id} requirements")
        else:
            steps.append(f"Revise existing policy to strengthen {gap.subcategory_id} coverage")
        
        # Add role and responsibility steps
        steps.append("Define roles and responsibilities for implementation")
        
        # Add training and awareness
        steps.append("Develop training materials and conduct staff awareness sessions")
        
        # Add approval workflow
        steps.append("Obtain management approval and stakeholder sign-off")
        
        # Add documentation
        steps.append("Document procedures and maintain compliance records")
        
        return steps
    
    def _generate_physical_steps(self, gap: GapDetail, subcategory: CSFSubcategory = None) -> List[str]:
        """Generate physical implementation steps.
        
        Physical steps focus on physical security controls.
        Most CSF subcategories don't require physical steps.
        """
        steps = []
        
        # Only add physical steps for relevant categories
        if subcategory:
            category_lower = subcategory.category.lower()
            
            if 'physical' in category_lower or 'facility' in category_lower:
                steps.extend([
                    "Implement physical access controls and monitoring",
                    "Deploy surveillance and intrusion detection systems",
                    "Establish secure areas for sensitive operations"
                ])
            elif 'data center' in category_lower or 'infrastructure' in category_lower:
                steps.extend([
                    "Secure physical infrastructure and equipment",
                    "Implement environmental controls and monitoring",
                    "Establish physical security perimeter"
                ])
        
        # Most gaps don't require physical steps
        return steps
    
    def generate_markdown(self, roadmap: ImplementationRoadmap, output_path: str, policy_file: str = None) -> None:
        """Generate markdown implementation roadmap.
        
        Args:
            roadmap: ImplementationRoadmap object
            output_path: Path where markdown file should be written
            policy_file: Optional name of analyzed policy file
        """
        md_content = self._build_markdown_content(roadmap, policy_file)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(md_content, encoding='utf-8')
        
        logger.info(f"Generated markdown roadmap: {output_path}")
    
    def generate_json(self, roadmap: ImplementationRoadmap, output_path: str, policy_file: str = None) -> None:
        """Generate JSON implementation roadmap.
        
        Args:
            roadmap: ImplementationRoadmap object
            output_path: Path where JSON file should be written
            policy_file: Optional name of analyzed policy file
            
        Raises:
            ValidationError: If generated JSON does not conform to schema
        """
        json_data = self._build_json_data(roadmap, policy_file)
        
        # Validate against schema
        validate_implementation_roadmap(json_data)
        
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        output_file.write_text(
            json.dumps(json_data, indent=2, ensure_ascii=False),
            encoding='utf-8'
        )
        
        logger.info(f"Generated JSON roadmap: {output_path}")
    
    def _build_markdown_content(self, roadmap: ImplementationRoadmap, policy_file: str = None) -> str:
        """Build markdown content from roadmap."""
        lines = []
        
        # Header
        lines.append("# Implementation Roadmap")
        lines.append("")
        
        # Metadata
        lines.append("## Roadmap Metadata")
        lines.append("")
        if policy_file:
            lines.append(f"- **Policy Analyzed**: `{policy_file}`")
        lines.append(f"- **Generation Date**: {roadmap.metadata.get('generation_date', 'Unknown')}")
        lines.append(f"- **Total Actions**: {roadmap.metadata.get('total_actions', 0)}")
        lines.append(f"  - Immediate: {roadmap.metadata.get('immediate_count', 0)}")
        lines.append(f"  - Near-term: {roadmap.metadata.get('near_term_count', 0)}")
        lines.append(f"  - Medium-term: {roadmap.metadata.get('medium_term_count', 0)}")
        lines.append("")
        
        # Timeframe definitions
        lines.append("## Timeframe Definitions")
        lines.append("")
        lines.append("- **Immediate** (0-3 months): Critical and high-severity gaps requiring urgent attention")
        lines.append("- **Near-term** (3-6 months): Medium-severity gaps for planned implementation")
        lines.append("- **Medium-term** (6-12 months): Low-severity gaps for longer-term planning")
        lines.append("")
        
        # Immediate actions
        lines.append("## Immediate Actions (0-3 months)")
        lines.append("")
        if roadmap.immediate_actions:
            for action in roadmap.immediate_actions:
                lines.extend(self._format_action_markdown(action))
        else:
            lines.append("*No immediate actions required.*")
            lines.append("")
        
        # Near-term actions
        lines.append("## Near-term Actions (3-6 months)")
        lines.append("")
        if roadmap.near_term_actions:
            for action in roadmap.near_term_actions:
                lines.extend(self._format_action_markdown(action))
        else:
            lines.append("*No near-term actions required.*")
            lines.append("")
        
        # Medium-term actions
        lines.append("## Medium-term Actions (6-12 months)")
        lines.append("")
        if roadmap.medium_term_actions:
            for action in roadmap.medium_term_actions:
                lines.extend(self._format_action_markdown(action))
        else:
            lines.append("*No medium-term actions required.*")
            lines.append("")
        
        return "\n".join(lines)
    
    def _format_action_markdown(self, action: ActionItem) -> List[str]:
        """Format a single action item as markdown."""
        lines = []
        
        # Action header
        severity_emoji = self._get_severity_emoji(action.severity)
        lines.append(f"### {action.action_id}: {action.description} {severity_emoji}")
        lines.append("")
        
        # Metadata
        lines.append(f"- **CSF Subcategory**: {action.csf_subcategory}")
        lines.append(f"- **Policy Section**: {action.policy_section}")
        lines.append(f"- **Severity**: {action.severity.upper()}")
        lines.append(f"- **Effort**: {action.effort.upper()}")
        lines.append("")
        
        # Technical steps
        if action.technical_steps:
            lines.append("**Technical Steps:**")
            lines.append("")
            for step in action.technical_steps:
                lines.append(f"- {step}")
            lines.append("")
        
        # Administrative steps
        if action.administrative_steps:
            lines.append("**Administrative Steps:**")
            lines.append("")
            for step in action.administrative_steps:
                lines.append(f"- {step}")
            lines.append("")
        
        # Physical steps
        if action.physical_steps:
            lines.append("**Physical Steps:**")
            lines.append("")
            for step in action.physical_steps:
                lines.append(f"- {step}")
            lines.append("")
        
        lines.append("---")
        lines.append("")
        
        return lines
    
    def _build_json_data(self, roadmap: ImplementationRoadmap, policy_file: str = None) -> Dict[str, Any]:
        """Build JSON data structure from roadmap."""
        return {
            "roadmap_date": roadmap.metadata.get('generation_date', datetime.now().isoformat()),
            "policy_analyzed": policy_file or "unknown",
            "immediate_actions": [self._action_to_dict(a) for a in roadmap.immediate_actions],
            "near_term_actions": [self._action_to_dict(a) for a in roadmap.near_term_actions],
            "medium_term_actions": [self._action_to_dict(a) for a in roadmap.medium_term_actions],
            "metadata": roadmap.metadata
        }
    
    def _action_to_dict(self, action: ActionItem) -> Dict[str, Any]:
        """Convert ActionItem to dictionary."""
        return {
            "action_id": action.action_id,
            "timeframe": action.timeframe,
            "severity": action.severity,
            "effort": action.effort,
            "csf_subcategory": action.csf_subcategory,
            "policy_section": action.policy_section,
            "description": action.description,
            "technical_steps": action.technical_steps,
            "administrative_steps": action.administrative_steps,
            "physical_steps": action.physical_steps
        }
    
    def _get_severity_emoji(self, severity: str) -> str:
        """Get emoji indicator for severity level."""
        emoji_map = {
            'critical': '🔴',
            'high': '🟠',
            'medium': '🟡',
            'low': '🟢'
        }
        return emoji_map.get(severity.lower(), '⚪')
