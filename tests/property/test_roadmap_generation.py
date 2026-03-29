"""
Property Tests: Roadmap Generation

**Property 32: Roadmap Generation from Gaps**
**Validates: Requirements 11.1, 11.2**

**Property 33: Severity-Based Prioritization**
**Validates: Requirements 11.3**

**Property 34: Action Item Completeness**
**Validates: Requirements 11.4, 11.5, 11.6**

**Property 35: Roadmap Output Format**
**Validates: Requirements 11.7, 14.4, 14.5**

These property tests verify that the RoadmapGenerator:
- Creates prioritized roadmaps with Immediate/Near-term/Medium-term categories
- Prioritizes Critical/High gaps as Immediate, Medium as Near-term, Low as Medium-term
- Includes all required fields and steps in action items
- Outputs roadmaps in both markdown and JSON formats
"""

import pytest
from hypothesis import given, strategies as st, settings, assume
from unittest.mock import Mock
import json
import tempfile
from pathlib import Path

from models.domain import (
    GapDetail,
    ActionItem,
    ImplementationRoadmap,
    CSFSubcategory
)
from reporting.roadmap_generator import RoadmapGenerator
from reference_builder.reference_catalog import ReferenceCatalog


# Strategy for generating gap details
@st.composite
def gap_detail_strategy(draw):
    """Generate random gap detail."""
    functions = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
    statuses = ['missing', 'partially_covered']
    severities = ['critical', 'high', 'medium', 'low']
    
    function = draw(st.sampled_from(functions))
    subcategory_id = f"{function[:2].upper()}.{draw(st.text(min_size=2, max_size=2, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))}-{draw(st.integers(min_value=1, max_value=99)):02d}"
    status = draw(st.sampled_from(statuses))
    
    return GapDetail(
        subcategory_id=subcategory_id,
        subcategory_description=draw(st.text(min_size=20, max_size=200)),
        status=status,
        evidence_quote="" if status == 'missing' else draw(st.text(min_size=10, max_size=100)),
        gap_explanation=draw(st.text(min_size=20, max_size=200)),
        severity=draw(st.sampled_from(severities)),
        suggested_fix=draw(st.text(min_size=20, max_size=200))
    )


# Strategy for generating CSF subcategories
@st.composite
def csf_subcategory_strategy(draw):
    """Generate random CSF subcategory."""
    functions = ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover']
    priorities = ['critical', 'high', 'medium', 'low']
    
    function = draw(st.sampled_from(functions))
    subcategory_id = f"{function[:2].upper()}.{draw(st.text(min_size=2, max_size=2, alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ'))}-{draw(st.integers(min_value=1, max_value=99)):02d}"
    
    return CSFSubcategory(
        subcategory_id=subcategory_id,
        function=function,
        category=draw(st.text(min_size=5, max_size=50)),
        description=draw(st.text(min_size=20, max_size=200)),
        keywords=draw(st.lists(st.text(min_size=3, max_size=15), min_size=1, max_size=10)),
        domain_tags=draw(st.lists(st.text(min_size=3, max_size=20), min_size=0, max_size=5)),
        mapped_templates=draw(st.lists(st.text(min_size=5, max_size=30), min_size=0, max_size=3)),
        priority=draw(st.sampled_from(priorities))
    )


class TestRoadmapGenerationProperties:
    """Property tests for roadmap generation."""
    
    @given(gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50, deadline=None)
    def test_property_32_roadmap_generation_from_gaps(self, gaps):
        """Property 32: Roadmap is created with Immediate/Near-term/Medium-term categories.
        
        Verifies that:
        - Roadmap is generated from gaps
        - Contains Immediate, Near-term, and Medium-term action lists
        - All gaps result in actions (allowing for some tolerance)
        """
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        # Configure catalog to return matching subcategories
        def get_subcategory(subcategory_id):
            for gap in gaps:
                if gap.subcategory_id == subcategory_id:
                    return CSFSubcategory(
                        subcategory_id=subcategory_id,
                        function="Govern",
                        category="Test Category",
                        description=gap.subcategory_description,
                        keywords=["test"],
                        domain_tags=["test"],
                        mapped_templates=[],
                        priority=gap.severity
                    )
            return None
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        # Create generator
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Generate roadmap
        roadmap = generator.generate(gaps)
        
        # Property: Roadmap must have all three timeframe categories
        assert hasattr(roadmap, 'immediate_actions'), \
            "Roadmap must have immediate_actions"
        assert hasattr(roadmap, 'near_term_actions'), \
            "Roadmap must have near_term_actions"
        assert hasattr(roadmap, 'medium_term_actions'), \
            "Roadmap must have medium_term_actions"
        
        # Property: All action lists must be lists
        assert isinstance(roadmap.immediate_actions, list), \
            "immediate_actions must be a list"
        assert isinstance(roadmap.near_term_actions, list), \
            "near_term_actions must be a list"
        assert isinstance(roadmap.medium_term_actions, list), \
            "medium_term_actions must be a list"
        
        # Property: Total actions should match number of gaps
        total_actions = (
            len(roadmap.immediate_actions) +
            len(roadmap.near_term_actions) +
            len(roadmap.medium_term_actions)
        )
        assert total_actions == len(gaps), \
            f"Expected {len(gaps)} actions, got {total_actions}"
        
        # Property: Metadata must be present
        assert hasattr(roadmap, 'metadata'), \
            "Roadmap must have metadata"
        assert isinstance(roadmap.metadata, dict), \
            "Metadata must be a dictionary"
    
    @given(gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50, deadline=None)
    def test_property_33_severity_based_prioritization(self, gaps):
        """Property 33: Critical/High gaps are Immediate, Medium are Near-term, Low are Medium-term.
        
        Verifies that:
        - Critical and High severity gaps → Immediate timeframe
        - Medium severity gaps → Near-term timeframe
        - Low severity gaps → Medium-term timeframe
        """
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        def get_subcategory(subcategory_id):
            for gap in gaps:
                if gap.subcategory_id == subcategory_id:
                    return CSFSubcategory(
                        subcategory_id=subcategory_id,
                        function="Govern",
                        category="Test Category",
                        description=gap.subcategory_description,
                        keywords=["test"],
                        domain_tags=["test"],
                        mapped_templates=[],
                        priority=gap.severity
                    )
            return None
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        # Create generator
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Generate roadmap
        roadmap = generator.generate(gaps)
        
        # Property: All immediate actions must be Critical or High severity
        for action in roadmap.immediate_actions:
            assert action.severity.lower() in ['critical', 'high'], \
                f"Immediate action {action.action_id} has severity {action.severity}, expected Critical or High"
            assert action.timeframe == 'immediate', \
                f"Action {action.action_id} should have timeframe 'immediate', got '{action.timeframe}'"
        
        # Property: All near-term actions must be Medium severity
        for action in roadmap.near_term_actions:
            assert action.severity.lower() == 'medium', \
                f"Near-term action {action.action_id} has severity {action.severity}, expected Medium"
            assert action.timeframe == 'near_term', \
                f"Action {action.action_id} should have timeframe 'near_term', got '{action.timeframe}'"
        
        # Property: All medium-term actions must be Low severity
        for action in roadmap.medium_term_actions:
            assert action.severity.lower() == 'low', \
                f"Medium-term action {action.action_id} has severity {action.severity}, expected Low"
            assert action.timeframe == 'medium_term', \
                f"Action {action.action_id} should have timeframe 'medium_term', got '{action.timeframe}'"
        
        # Property: Count gaps by severity and verify distribution
        critical_high_count = sum(1 for g in gaps if g.severity.lower() in ['critical', 'high'])
        medium_count = sum(1 for g in gaps if g.severity.lower() == 'medium')
        low_count = sum(1 for g in gaps if g.severity.lower() == 'low')
        
        assert len(roadmap.immediate_actions) == critical_high_count, \
            f"Expected {critical_high_count} immediate actions, got {len(roadmap.immediate_actions)}"
        assert len(roadmap.near_term_actions) == medium_count, \
            f"Expected {medium_count} near-term actions, got {len(roadmap.near_term_actions)}"
        assert len(roadmap.medium_term_actions) == low_count, \
            f"Expected {low_count} medium-term actions, got {len(roadmap.medium_term_actions)}"
    
    @given(gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=20))
    @settings(max_examples=50, deadline=None)
    def test_property_34_action_item_completeness(self, gaps):
        """Property 34: All action items include required fields and steps.
        
        Verifies that each action item includes:
        - action_id
        - timeframe
        - severity
        - effort estimate
        - csf_subcategory reference
        - policy_section reference
        - description
        - technical_steps (list)
        - administrative_steps (list)
        - physical_steps (list)
        """
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        def get_subcategory(subcategory_id):
            for gap in gaps:
                if gap.subcategory_id == subcategory_id:
                    return CSFSubcategory(
                        subcategory_id=subcategory_id,
                        function="Govern",
                        category="Test Category",
                        description=gap.subcategory_description,
                        keywords=["test"],
                        domain_tags=["test"],
                        mapped_templates=[],
                        priority=gap.severity
                    )
            return None
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        # Create generator
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Generate roadmap
        roadmap = generator.generate(gaps)
        
        # Collect all actions
        all_actions = (
            roadmap.immediate_actions +
            roadmap.near_term_actions +
            roadmap.medium_term_actions
        )
        
        # Property: Each action must have all required fields
        for action in all_actions:
            # Required string fields
            assert hasattr(action, 'action_id') and action.action_id, \
                "Action must have non-empty action_id"
            assert hasattr(action, 'timeframe') and action.timeframe, \
                "Action must have non-empty timeframe"
            assert hasattr(action, 'severity') and action.severity, \
                "Action must have non-empty severity"
            assert hasattr(action, 'effort') and action.effort, \
                "Action must have non-empty effort"
            assert hasattr(action, 'csf_subcategory') and action.csf_subcategory, \
                "Action must have non-empty csf_subcategory"
            assert hasattr(action, 'policy_section') and action.policy_section, \
                "Action must have non-empty policy_section"
            assert hasattr(action, 'description') and action.description, \
                "Action must have non-empty description"
            
            # Timeframe must be valid
            assert action.timeframe in ['immediate', 'near_term', 'medium_term'], \
                f"Invalid timeframe: {action.timeframe}"
            
            # Severity must be valid
            assert action.severity.lower() in ['critical', 'high', 'medium', 'low'], \
                f"Invalid severity: {action.severity}"
            
            # Effort must be valid
            assert action.effort.lower() in ['low', 'medium', 'high'], \
                f"Invalid effort: {action.effort}"
            
            # CSF subcategory must match one of the gaps
            gap_ids = {g.subcategory_id for g in gaps}
            assert action.csf_subcategory in gap_ids, \
                f"Action references unknown subcategory: {action.csf_subcategory}"
            
            # Required list fields
            assert hasattr(action, 'technical_steps'), \
                "Action must have technical_steps"
            assert isinstance(action.technical_steps, list), \
                "technical_steps must be a list"
            
            assert hasattr(action, 'administrative_steps'), \
                "Action must have administrative_steps"
            assert isinstance(action.administrative_steps, list), \
                "administrative_steps must be a list"
            
            assert hasattr(action, 'physical_steps'), \
                "Action must have physical_steps"
            assert isinstance(action.physical_steps, list), \
                "physical_steps must be a list"
            
            # At least one of technical or administrative steps must be non-empty
            assert len(action.technical_steps) > 0 or len(action.administrative_steps) > 0, \
                f"Action {action.action_id} must have at least technical or administrative steps"
    
    @given(gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=10))
    @settings(max_examples=30, deadline=None)
    def test_property_35_roadmap_output_format(self, gaps):
        """Property 35: Roadmap is output in both markdown and JSON formats.
        
        Verifies that:
        - Markdown output is generated
        - JSON output is generated
        - Both outputs contain required content
        - JSON conforms to schema
        """
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        def get_subcategory(subcategory_id):
            for gap in gaps:
                if gap.subcategory_id == subcategory_id:
                    return CSFSubcategory(
                        subcategory_id=subcategory_id,
                        function="Govern",
                        category="Test Category",
                        description=gap.subcategory_description,
                        keywords=["test"],
                        domain_tags=["test"],
                        mapped_templates=[],
                        priority=gap.severity
                    )
            return None
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        # Create generator
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Generate roadmap
        roadmap = generator.generate(gaps)
        
        # Create temporary directory for outputs
        with tempfile.TemporaryDirectory() as tmpdir:
            md_path = Path(tmpdir) / "roadmap.md"
            json_path = Path(tmpdir) / "roadmap.json"
            
            # Generate markdown output
            generator.generate_markdown(roadmap, str(md_path), "test_policy.pdf")
            
            # Property: Markdown file must be created
            assert md_path.exists(), \
                "Markdown file must be created"
            
            # Property: Markdown file must contain content
            md_content = md_path.read_text()
            assert len(md_content) > 0, \
                "Markdown file must not be empty"
            
            # Property: Markdown must contain required sections
            assert "# Implementation Roadmap" in md_content, \
                "Markdown must have main header"
            assert "## Immediate Actions" in md_content, \
                "Markdown must have Immediate Actions section"
            assert "## Near-term Actions" in md_content, \
                "Markdown must have Near-term Actions section"
            assert "## Medium-term Actions" in md_content, \
                "Markdown must have Medium-term Actions section"
            
            # Generate JSON output
            generator.generate_json(roadmap, str(json_path), "test_policy.pdf")
            
            # Property: JSON file must be created
            assert json_path.exists(), \
                "JSON file must be created"
            
            # Property: JSON file must contain valid JSON
            json_content = json_path.read_text()
            json_data = json.loads(json_content)
            
            # Property: JSON must have required top-level keys
            assert "roadmap_date" in json_data, \
                "JSON must have roadmap_date"
            assert "policy_analyzed" in json_data, \
                "JSON must have policy_analyzed"
            assert "immediate_actions" in json_data, \
                "JSON must have immediate_actions"
            assert "near_term_actions" in json_data, \
                "JSON must have near_term_actions"
            assert "medium_term_actions" in json_data, \
                "JSON must have medium_term_actions"
            assert "metadata" in json_data, \
                "JSON must have metadata"
            
            # Property: JSON action arrays must match roadmap
            assert len(json_data["immediate_actions"]) == len(roadmap.immediate_actions), \
                "JSON immediate_actions count must match roadmap"
            assert len(json_data["near_term_actions"]) == len(roadmap.near_term_actions), \
                "JSON near_term_actions count must match roadmap"
            assert len(json_data["medium_term_actions"]) == len(roadmap.medium_term_actions), \
                "JSON medium_term_actions count must match roadmap"
            
            # Property: Each JSON action must have required fields
            for action_list_key in ["immediate_actions", "near_term_actions", "medium_term_actions"]:
                for action in json_data[action_list_key]:
                    assert "action_id" in action, \
                        f"JSON action must have action_id"
                    assert "timeframe" in action, \
                        f"JSON action must have timeframe"
                    assert "severity" in action, \
                        f"JSON action must have severity"
                    assert "effort" in action, \
                        f"JSON action must have effort"
                    assert "csf_subcategory" in action, \
                        f"JSON action must have csf_subcategory"
                    assert "policy_section" in action, \
                        f"JSON action must have policy_section"
                    assert "description" in action, \
                        f"JSON action must have description"
                    assert "technical_steps" in action, \
                        f"JSON action must have technical_steps"
                    assert "administrative_steps" in action, \
                        f"JSON action must have administrative_steps"
                    assert "physical_steps" in action, \
                        f"JSON action must have physical_steps"
    
    @given(gaps=st.lists(gap_detail_strategy(), min_size=1, max_size=10))
    @settings(max_examples=20, deadline=None)
    def test_effort_estimation_consistency(self, gaps):
        """Verify that effort estimation is consistent and reasonable.
        
        Checks that:
        - Effort is always one of: low, medium, high
        - Effort estimation considers both status and severity
        - Critical/High severity gaps have higher effort than Low severity
        """
        # Create mock catalog
        mock_catalog = Mock(spec=ReferenceCatalog)
        
        def get_subcategory(subcategory_id):
            for gap in gaps:
                if gap.subcategory_id == subcategory_id:
                    return CSFSubcategory(
                        subcategory_id=subcategory_id,
                        function="Govern",
                        category="Test Category",
                        description=gap.subcategory_description,
                        keywords=["test"],
                        domain_tags=["test"],
                        mapped_templates=[],
                        priority=gap.severity
                    )
            return None
        
        mock_catalog.get_subcategory.side_effect = get_subcategory
        
        # Create generator
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Generate roadmap
        roadmap = generator.generate(gaps)
        
        # Collect all actions
        all_actions = (
            roadmap.immediate_actions +
            roadmap.near_term_actions +
            roadmap.medium_term_actions
        )
        
        # Property: All efforts must be valid
        for action in all_actions:
            assert action.effort.lower() in ['low', 'medium', 'high'], \
                f"Invalid effort level: {action.effort}"
        
        # Property: Effort should correlate with severity
        # Critical/High severity gaps should generally have higher effort than Low severity
        effort_values = {'low': 1, 'medium': 2, 'high': 3}
        
        critical_high_efforts = []
        low_efforts = []
        
        for action in all_actions:
            # Find corresponding gap
            gap = next((g for g in gaps if g.subcategory_id == action.csf_subcategory), None)
            if gap:
                effort_val = effort_values[action.effort.lower()]
                if gap.severity.lower() in ['critical', 'high']:
                    critical_high_efforts.append(effort_val)
                elif gap.severity.lower() == 'low':
                    low_efforts.append(effort_val)
        
        # If we have both types, critical/high should generally have higher effort
        if critical_high_efforts and low_efforts:
            avg_critical_high = sum(critical_high_efforts) / len(critical_high_efforts)
            avg_low = sum(low_efforts) / len(low_efforts)
            
            # Critical/High should have higher or equal average effort
            assert avg_critical_high >= avg_low, \
                f"Critical/High severity gaps should have higher effort (avg {avg_critical_high:.2f}) than Low severity (avg {avg_low:.2f})"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
