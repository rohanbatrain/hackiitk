"""
Unit Tests: Roadmap Generator

Tests the RoadmapGenerator component for creating prioritized implementation
roadmaps from identified gaps.
"""

import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock
from datetime import datetime

from models.domain import (
    GapDetail,
    ActionItem,
    ImplementationRoadmap,
    CSFSubcategory
)
from reporting.roadmap_generator import RoadmapGenerator
from reference_builder.reference_catalog import ReferenceCatalog


@pytest.fixture
def mock_catalog():
    """Create mock reference catalog."""
    catalog = Mock(spec=ReferenceCatalog)
    
    def get_subcategory(subcategory_id):
        return CSFSubcategory(
            subcategory_id=subcategory_id,
            function="Govern",
            category="Risk Management Strategy",
            description="Risk management processes are established and managed",
            keywords=["risk", "management", "strategy"],
            domain_tags=["isms", "risk_management"],
            mapped_templates=["Risk Management Policy"],
            priority="high"
        )
    
    catalog.get_subcategory.side_effect = get_subcategory
    return catalog


@pytest.fixture
def sample_gaps():
    """Create sample gaps for testing."""
    return [
        GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Risk management processes are established",
            status="missing",
            evidence_quote="",
            gap_explanation="No risk management process documented",
            severity="critical",
            suggested_fix="Establish formal risk management program"
        ),
        GapDetail(
            subcategory_id="GV.RM-02",
            subcategory_description="Risk appetite and tolerance are established",
            status="partially_covered",
            evidence_quote="Risk assessment is performed annually",
            gap_explanation="Risk tolerance levels not defined",
            severity="high",
            suggested_fix="Define and document risk tolerance levels"
        ),
        GapDetail(
            subcategory_id="ID.AM-01",
            subcategory_description="Assets are inventoried and managed",
            status="missing",
            evidence_quote="",
            gap_explanation="No asset inventory exists",
            severity="medium",
            suggested_fix="Create comprehensive asset inventory"
        ),
        GapDetail(
            subcategory_id="PR.DS-01",
            subcategory_description="Data at rest is protected",
            status="partially_covered",
            evidence_quote="Encryption is used for some systems",
            gap_explanation="Not all data at rest is encrypted",
            severity="low",
            suggested_fix="Implement encryption for all data at rest"
        )
    ]


class TestRoadmapGenerator:
    """Unit tests for RoadmapGenerator."""
    
    def test_initialization(self, mock_catalog):
        """Test roadmap generator initialization."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        assert generator.catalog == mock_catalog
    
    def test_generate_empty_gaps(self, mock_catalog):
        """Test roadmap generation with no gaps."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        roadmap = generator.generate([])
        
        assert isinstance(roadmap, ImplementationRoadmap)
        assert len(roadmap.immediate_actions) == 0
        assert len(roadmap.near_term_actions) == 0
        assert len(roadmap.medium_term_actions) == 0
        assert roadmap.metadata['total_gaps'] == 0
        assert roadmap.metadata['total_actions'] == 0
    
    def test_generate_with_gaps(self, mock_catalog, sample_gaps):
        """Test roadmap generation with sample gaps."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        roadmap = generator.generate(sample_gaps)
        
        assert isinstance(roadmap, ImplementationRoadmap)
        assert len(roadmap.immediate_actions) == 2  # critical + high
        assert len(roadmap.near_term_actions) == 1  # medium
        assert len(roadmap.medium_term_actions) == 1  # low
        assert roadmap.metadata['total_gaps'] == 4
        assert roadmap.metadata['total_actions'] == 4
    
    def test_prioritize_by_severity(self, mock_catalog, sample_gaps):
        """Test gap prioritization by severity."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        prioritized = generator.prioritize(sample_gaps)
        
        assert 'immediate' in prioritized
        assert 'near_term' in prioritized
        assert 'medium_term' in prioritized
        
        # Critical and high go to immediate
        assert len(prioritized['immediate']) == 2
        assert all(g.severity.lower() in ['critical', 'high'] for g in prioritized['immediate'])
        
        # Medium goes to near-term
        assert len(prioritized['near_term']) == 1
        assert all(g.severity.lower() == 'medium' for g in prioritized['near_term'])
        
        # Low goes to medium-term
        assert len(prioritized['medium_term']) == 1
        assert all(g.severity.lower() == 'low' for g in prioritized['medium_term'])
    
    def test_create_action_from_gap(self, mock_catalog, sample_gaps):
        """Test action item creation from gap."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        gap = sample_gaps[0]  # Critical gap
        action = generator.create_action(gap)
        
        assert isinstance(action, ActionItem)
        assert action.action_id == f"ACT-{gap.subcategory_id}"
        assert action.timeframe == 'immediate'
        assert action.severity == gap.severity
        assert action.csf_subcategory == gap.subcategory_id
        assert len(action.description) > 0
        assert len(action.technical_steps) > 0
        assert len(action.administrative_steps) > 0
        assert isinstance(action.physical_steps, list)
    
    def test_estimate_effort_missing_gap(self, mock_catalog):
        """Test effort estimation for missing gap."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Missing critical gap should have high effort
        gap_critical = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="missing",
            evidence_quote="",
            gap_explanation="Test",
            severity="critical",
            suggested_fix="Test"
        )
        
        effort = generator.estimate_effort(gap_critical)
        assert effort == 'high'
        
        # Missing medium gap should have medium effort
        gap_medium = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="missing",
            evidence_quote="",
            gap_explanation="Test",
            severity="medium",
            suggested_fix="Test"
        )
        
        effort = generator.estimate_effort(gap_medium)
        assert effort == 'medium'
    
    def test_estimate_effort_partial_gap(self, mock_catalog):
        """Test effort estimation for partially covered gap."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Partial high gap should have medium effort
        gap_high = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="partially_covered",
            evidence_quote="Some coverage",
            gap_explanation="Test",
            severity="high",
            suggested_fix="Test"
        )
        
        effort = generator.estimate_effort(gap_high)
        assert effort == 'medium'
        
        # Partial low gap should have low effort
        gap_low = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="partially_covered",
            evidence_quote="Some coverage",
            gap_explanation="Test",
            severity="low",
            suggested_fix="Test"
        )
        
        effort = generator.estimate_effort(gap_low)
        assert effort == 'low'
    
    def test_generate_markdown_output(self, mock_catalog, sample_gaps):
        """Test markdown output generation."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        roadmap = generator.generate(sample_gaps)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "roadmap.md"
            
            generator.generate_markdown(roadmap, str(output_path), "test_policy.pdf")
            
            assert output_path.exists()
            
            content = output_path.read_text()
            
            # Check for required sections
            assert "# Implementation Roadmap" in content
            assert "## Immediate Actions" in content
            assert "## Near-term Actions" in content
            assert "## Medium-term Actions" in content
            assert "test_policy.pdf" in content
            
            # Check for action IDs
            assert "ACT-GV.RM-01" in content
            assert "ACT-GV.RM-02" in content
    
    def test_generate_json_output(self, mock_catalog, sample_gaps):
        """Test JSON output generation."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        roadmap = generator.generate(sample_gaps)
        
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "roadmap.json"
            
            generator.generate_json(roadmap, str(output_path), "test_policy.pdf")
            
            assert output_path.exists()
            
            content = output_path.read_text()
            data = json.loads(content)
            
            # Check required fields
            assert "roadmap_date" in data
            assert "policy_analyzed" in data
            assert data["policy_analyzed"] == "test_policy.pdf"
            assert "immediate_actions" in data
            assert "near_term_actions" in data
            assert "medium_term_actions" in data
            assert "metadata" in data
            
            # Check action counts
            assert len(data["immediate_actions"]) == 2
            assert len(data["near_term_actions"]) == 1
            assert len(data["medium_term_actions"]) == 1
            
            # Check action structure
            for action in data["immediate_actions"]:
                assert "action_id" in action
                assert "timeframe" in action
                assert "severity" in action
                assert "effort" in action
                assert "csf_subcategory" in action
                assert "policy_section" in action
                assert "description" in action
                assert "technical_steps" in action
                assert "administrative_steps" in action
                assert "physical_steps" in action
    
    def test_action_id_generation(self, mock_catalog):
        """Test action ID generation."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        gap = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="missing",
            evidence_quote="",
            gap_explanation="Test",
            severity="critical",
            suggested_fix="Test"
        )
        
        action_id = generator._generate_action_id(gap)
        assert action_id == "ACT-GV.RM-01"
    
    def test_severity_to_timeframe_mapping(self, mock_catalog):
        """Test severity to timeframe conversion."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        assert generator._severity_to_timeframe('critical') == 'immediate'
        assert generator._severity_to_timeframe('high') == 'immediate'
        assert generator._severity_to_timeframe('medium') == 'near_term'
        assert generator._severity_to_timeframe('low') == 'medium_term'
        assert generator._severity_to_timeframe('unknown') == 'near_term'  # default
    
    def test_technical_steps_generation(self, mock_catalog):
        """Test technical steps generation."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        subcategory = CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Risk Management Strategy",
            description="Test",
            keywords=["risk"],
            domain_tags=["isms"],
            mapped_templates=[],
            priority="high"
        )
        
        gap = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="missing",
            evidence_quote="",
            gap_explanation="Test",
            severity="critical",
            suggested_fix="Test"
        )
        
        steps = generator._generate_technical_steps(gap, subcategory)
        
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert all(isinstance(step, str) for step in steps)
        # Risk-related category should have risk-specific steps
        assert any('risk' in step.lower() for step in steps)
    
    def test_administrative_steps_generation(self, mock_catalog):
        """Test administrative steps generation."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        subcategory = CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Risk Management Strategy",
            description="Test",
            keywords=["risk"],
            domain_tags=["isms"],
            mapped_templates=[],
            priority="high"
        )
        
        gap = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="missing",
            evidence_quote="",
            gap_explanation="Test",
            severity="critical",
            suggested_fix="Test"
        )
        
        steps = generator._generate_administrative_steps(gap, subcategory)
        
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert all(isinstance(step, str) for step in steps)
        # Should include policy documentation
        assert any('policy' in step.lower() for step in steps)
        # Should include training
        assert any('training' in step.lower() for step in steps)
    
    def test_physical_steps_generation(self, mock_catalog):
        """Test physical steps generation."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        # Non-physical category should have empty physical steps
        subcategory_non_physical = CSFSubcategory(
            subcategory_id="GV.RM-01",
            function="Govern",
            category="Risk Management Strategy",
            description="Test",
            keywords=["risk"],
            domain_tags=["isms"],
            mapped_templates=[],
            priority="high"
        )
        
        gap = GapDetail(
            subcategory_id="GV.RM-01",
            subcategory_description="Test",
            status="missing",
            evidence_quote="",
            gap_explanation="Test",
            severity="critical",
            suggested_fix="Test"
        )
        
        steps = generator._generate_physical_steps(gap, subcategory_non_physical)
        assert isinstance(steps, list)
        assert len(steps) == 0  # No physical steps for risk management
        
        # Physical category should have physical steps
        subcategory_physical = CSFSubcategory(
            subcategory_id="PR.AC-01",
            function="Protect",
            category="Physical Access Control",
            description="Test",
            keywords=["physical"],
            domain_tags=["physical_security"],
            mapped_templates=[],
            priority="high"
        )
        
        steps = generator._generate_physical_steps(gap, subcategory_physical)
        assert isinstance(steps, list)
        assert len(steps) > 0
        assert any('physical' in step.lower() for step in steps)
    
    def test_metadata_completeness(self, mock_catalog, sample_gaps):
        """Test that roadmap metadata is complete."""
        generator = RoadmapGenerator(catalog=mock_catalog)
        
        roadmap = generator.generate(sample_gaps)
        
        assert 'generation_date' in roadmap.metadata
        assert 'total_gaps' in roadmap.metadata
        assert 'total_actions' in roadmap.metadata
        assert 'immediate_count' in roadmap.metadata
        assert 'near_term_count' in roadmap.metadata
        assert 'medium_term_count' in roadmap.metadata
        
        assert roadmap.metadata['total_gaps'] == len(sample_gaps)
        assert roadmap.metadata['total_actions'] == len(sample_gaps)
        assert roadmap.metadata['immediate_count'] == 2
        assert roadmap.metadata['near_term_count'] == 1
        assert roadmap.metadata['medium_term_count'] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
