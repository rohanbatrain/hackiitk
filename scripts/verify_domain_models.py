#!/usr/bin/env python3
"""
Verification script for domain models.

This script verifies that all domain models can be instantiated
and have the correct fields as specified in the design document.
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from datetime import datetime
from models.domain import (
    ParsedDocument,
    DocumentStructure,
    Heading,
    Section,
    Paragraph,
    TextChunk,
    CSFSubcategory,
    RetrievalResult,
    CoverageAssessment,
    GapDetail,
    GapAnalysisReport,
    Revision,
    RevisedPolicy,
    ActionItem,
    ImplementationRoadmap,
    AuditLogEntry,
)


def verify_models():
    """Verify all domain models can be instantiated."""
    
    print("Verifying domain models...")
    print()
    
    # 1. ParsedDocument
    structure = DocumentStructure(headings=[], sections=[])
    doc = ParsedDocument(
        text="Sample text",
        file_path="/path/to/file.pdf",
        file_type="pdf",
        page_count=10,
        structure=structure,
        metadata={}
    )
    print("✓ ParsedDocument")
    
    # 2. DocumentStructure
    print("✓ DocumentStructure")
    
    # 3. Heading
    heading = Heading(level=1, text="Title", start_pos=0, end_pos=5)
    print("✓ Heading")
    
    # 4. Section
    section = Section(
        title="Section 1",
        content="Content",
        start_pos=0,
        end_pos=10,
        subsections=[]
    )
    print("✓ Section")
    
    # 5. Paragraph
    para = Paragraph(text="Paragraph text", start_pos=0, end_pos=14)
    print("✓ Paragraph")
    
    # 6. TextChunk
    chunk = TextChunk(
        text="Chunk text",
        chunk_id="chunk_001",
        source_file="/path/to/file.pdf",
        start_pos=0,
        end_pos=10
    )
    print("✓ TextChunk")
    
    # 7. CSFSubcategory
    subcategory = CSFSubcategory(
        subcategory_id="GV.RM-01",
        function="Govern",
        category="Risk Management",
        description="Risk management objectives...",
        keywords=["risk", "management"],
        domain_tags=["isms"],
        mapped_templates=["Risk Policy"],
        priority="high"
    )
    print("✓ CSFSubcategory")
    
    # 8. RetrievalResult
    result = RetrievalResult(
        subcategory_id="GV.RM-01",
        subcategory_text="Risk management...",
        relevance_score=0.85,
        evidence_spans=["Evidence text"],
        retrieval_method="hybrid"
    )
    print("✓ RetrievalResult")
    
    # 9. CoverageAssessment
    assessment = CoverageAssessment(
        subcategory_id="GV.RM-01",
        status="covered",
        lexical_score=0.8,
        semantic_score=0.9,
        evidence_spans=["Evidence"],
        confidence=0.85
    )
    print("✓ CoverageAssessment")
    
    # 10. GapDetail
    gap = GapDetail(
        subcategory_id="GV.RM-01",
        subcategory_description="Description",
        status="missing",
        evidence_quote="",
        gap_explanation="Explanation",
        severity="high",
        suggested_fix="Fix text"
    )
    print("✓ GapDetail")
    
    # 11. GapAnalysisReport
    report = GapAnalysisReport(
        analysis_date=datetime.now(),
        input_file="/path/to/file.pdf",
        input_file_hash="abc123",
        model_name="qwen2.5-3b",
        model_version="q4_k_m",
        embedding_model="all-MiniLM-L6-v2",
        gaps=[gap],
        covered_subcategories=["GV.OC-01"],
        metadata={}
    )
    print("✓ GapAnalysisReport")
    
    # 12. Revision
    revision = Revision(
        section="Section 1",
        gap_addressed="GV.RM-01",
        original_clause="Original",
        revised_clause="Revised",
        revision_type="strengthening"
    )
    print("✓ Revision")
    
    # 13. RevisedPolicy
    policy = RevisedPolicy(
        original_text="Original",
        revised_text="Revised",
        revisions=[revision],
        warning="Warning text",
        metadata={}
    )
    print("✓ RevisedPolicy")
    
    # 14. ActionItem
    action = ActionItem(
        action_id="ACT-001",
        timeframe="immediate",
        severity="high",
        effort="medium",
        csf_subcategory="GV.RM-01",
        policy_section="Section 1",
        description="Action description",
        technical_steps=["Step 1"],
        administrative_steps=["Step 2"],
        physical_steps=[]
    )
    print("✓ ActionItem")
    
    # 15. ImplementationRoadmap
    roadmap = ImplementationRoadmap(
        immediate_actions=[action],
        near_term_actions=[],
        medium_term_actions=[],
        metadata={}
    )
    print("✓ ImplementationRoadmap")
    
    # 16. AuditLogEntry
    audit = AuditLogEntry(
        timestamp=datetime.now(),
        input_file_path="/path/to/file.pdf",
        input_file_hash="abc123",
        model_name="qwen2.5-3b",
        model_version="q4_k_m",
        embedding_model_version="all-MiniLM-L6-v2",
        configuration_parameters={},
        retrieval_parameters={},
        prompt_template_version="1.0.0",
        output_directory="/path/to/output",
        analysis_duration_seconds=120.0
    )
    print("✓ AuditLogEntry")
    
    print()
    print("=" * 50)
    print("All 16 domain models verified successfully!")
    print("=" * 50)


if __name__ == "__main__":
    verify_models()
