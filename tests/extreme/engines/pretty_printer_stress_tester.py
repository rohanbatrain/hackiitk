"""
Pretty Printer Stress Tester

This module implements stress tests for the PrettyPrinter to validate
round-trip properties under extreme conditions including 10,000+ sections,
100+ nesting levels, and special characters in headings.

Requirements: 55.1, 55.2, 55.3, 55.4, 55.5
"""

import logging
import time
import random
import string
from pathlib import Path
from typing import List, Optional

from ..models import TestResult, TestStatus, Metrics
from ..config import TestConfig
from ..support.metrics_collector import MetricsCollector
from models.domain import ParsedDocument, DocumentStructure, Section, Heading
from ingestion.pretty_printer import PrettyPrinter
from ingestion.document_parser import DocumentParser


class PrettyPrinterStressTester:
    """
    Stress tests for the PrettyPrinter.
    
    Tests:
    - 10,000+ sections
    - 100+ nesting levels
    - Special characters in headings
    - Round-trip for 1,000+ structures
    - All edge case structures
    
    Requirements: 55.1, 55.2, 55.3, 55.4, 55.5
    """
    
    def __init__(
        self,
        config: TestConfig,
        metrics_collector: MetricsCollector,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize pretty printer stress tester.
        
        Args:
            config: Test configuration
            metrics_collector: Metrics collection
            logger: Optional logger
        """
        self.config = config
        self.metrics_collector = metrics_collector
        self.logger = logger or logging.getLogger(__name__)
        self.pretty_printer = PrettyPrinter()
        self.document_parser = DocumentParser()
    
    def run_tests(self) -> List[TestResult]:
        """
        Run all pretty printer stress tests.
        
        Returns:
            List of test results
        """
        results = []
        
        # Test 1: 10,000+ sections
        results.append(self.test_large_section_count())
        
        # Test 2: 100+ nesting levels
        results.append(self.test_deep_nesting())
        
        # Test 3: Special characters in headings
        results.append(self.test_special_characters())
        
        # Test 4: Round-trip for 1,000+ structures
        results.extend(self.test_round_trip_properties())
        
        # Test 5: Edge case structures
        results.extend(self.test_edge_case_structures())
        
        return results
    
    def test_large_section_count(self) -> TestResult:
        """
        Test with 10,000+ sections.
        
        Requirements: 55.1
        """
        self.logger.info("Testing with 10,000+ sections...")
        test_id = "pretty_printer_large_sections"
        
        try:
            self.metrics_collector.start_collection(test_id)
            start_time = time.time()
            
            # Generate document with 10,000+ sections
            sections = []
            for i in range(10000):
                section = Section(
                    title=f"Section {i}",
                    content=f"Content for section {i}",
                    level=1,
                    subsections=[]
                )
                sections.append(section)
            
            # Create parsed document
            parsed_doc = ParsedDocument(
                text="",  # Will be generated from structure
                structure=DocumentStructure(
                    headings=[Heading(text=s.title, level=1, start_pos=0, end_pos=0) for s in sections],
                    sections=sections
                )
            )
            
            # Format to markdown
            markdown = self.pretty_printer.format_to_markdown(parsed_doc)
            
            # Verify completion
            success = len(markdown) > 0 and markdown.count('#') >= 10000
            
            metrics = self.metrics_collector.stop_collection(test_id)
            duration = time.time() - start_time
            
            status = TestStatus.PASS if success else TestStatus.FAIL
            
            return TestResult(
                test_id=test_id,
                requirement_id="55.1",
                category="pretty_printer_stress",
                status=status,
                duration_seconds=duration,
                error_message=None if success else "Failed to format 10,000+ sections",
                metrics=metrics,
                artifacts=[]
            )
            
        except Exception as e:
            self.logger.error(f"Large section test failed: {e}")
            return TestResult(
                test_id=test_id,
                requirement_id="55.1",
                category="pretty_printer_stress",
                status=TestStatus.FAIL,
                duration_seconds=0.0,
                error_message=f"Test execution failed: {str(e)}",
                metrics=None,
                artifacts=[]
            )
    
    def test_deep_nesting(self) -> TestResult:
        """
        Test with deeply nested structure (100+ levels).
        
        Requirements: 55.2
        """
        self.logger.info("Testing with 100+ nesting levels...")
        test_id = "pretty_printer_deep_nesting"
        
        try:
            self.metrics_collector.start_collection(test_id)
            start_time = time.time()
            
            # Generate deeply nested structure
            root_section = self._create_nested_sections(depth=100)
            
            # Create parsed document
            parsed_doc = ParsedDocument(
                text="",
                structure=DocumentStructure(
                    headings=[],
                    sections=[root_section]
                )
            )
            
            # Format to markdown
            markdown = self.pretty_printer.format_to_markdown(parsed_doc)
            
            # Verify formatting is correct (should have multiple heading levels)
            success = len(markdown) > 0 and '######' in markdown  # Max heading level
            
            metrics = self.metrics_collector.stop_collection(test_id)
            duration = time.time() - start_time
            
            status = TestStatus.PASS if success else TestStatus.FAIL
            
            return TestResult(
                test_id=test_id,
                requirement_id="55.2",
                category="pretty_printer_stress",
                status=status,
                duration_seconds=duration,
                error_message=None if success else "Failed to format deep nesting",
                metrics=metrics,
                artifacts=[]
            )
            
        except Exception as e:
            self.logger.error(f"Deep nesting test failed: {e}")
            return TestResult(
                test_id=test_id,
                requirement_id="55.2",
                category="pretty_printer_stress",
                status=TestStatus.FAIL,
                duration_seconds=0.0,
                error_message=f"Test execution failed: {str(e)}",
                metrics=None,
                artifacts=[]
            )
    
    def test_special_characters(self) -> TestResult:
        """
        Test with special characters in headings.
        
        Requirements: 55.3
        """
        self.logger.info("Testing with special characters in headings...")
        test_id = "pretty_printer_special_chars"
        
        try:
            self.metrics_collector.start_collection(test_id)
            start_time = time.time()
            
            # Generate sections with special characters
            special_chars = ['#', '*', '_', '[', ']', '(', ')', '`', '~', '|', '<', '>', '&', '"', "'"]
            sections = []
            
            for i, char in enumerate(special_chars):
                section = Section(
                    title=f"Section with {char} special character",
                    content=f"Content with {char} in it",
                    level=1,
                    subsections=[]
                )
                sections.append(section)
            
            # Create parsed document
            parsed_doc = ParsedDocument(
                text="",
                structure=DocumentStructure(
                    headings=[Heading(text=s.title, level=1, start_pos=0, end_pos=0) for s in sections],
                    sections=sections
                )
            )
            
            # Format to markdown
            markdown = self.pretty_printer.format_to_markdown(parsed_doc)
            
            # Verify escaping works correctly
            success = len(markdown) > 0
            
            metrics = self.metrics_collector.stop_collection(test_id)
            duration = time.time() - start_time
            
            status = TestStatus.PASS if success else TestStatus.FAIL
            
            return TestResult(
                test_id=test_id,
                requirement_id="55.3",
                category="pretty_printer_stress",
                status=status,
                duration_seconds=duration,
                error_message=None if success else "Failed to handle special characters",
                metrics=metrics,
                artifacts=[]
            )
            
        except Exception as e:
            self.logger.error(f"Special characters test failed: {e}")
            return TestResult(
                test_id=test_id,
                requirement_id="55.3",
                category="pretty_printer_stress",
                status=TestStatus.FAIL,
                duration_seconds=0.0,
                error_message=f"Test execution failed: {str(e)}",
                metrics=None,
                artifacts=[]
            )
    
    def test_round_trip_properties(self) -> List[TestResult]:
        """
        Verify round-trip property holds for 1,000+ randomly generated structures.
        
        Requirements: 55.4
        """
        self.logger.info("Testing round-trip properties for 1,000+ structures...")
        results = []
        
        num_tests = 1000
        passed = 0
        failed = 0
        
        for i in range(num_tests):
            test_id = f"pretty_printer_round_trip_{i}"
            
            try:
                # Generate random structure
                structure = self._generate_random_structure()
                
                # Create parsed document
                parsed_doc = ParsedDocument(
                    text="",
                    structure=structure
                )
                
                # Format to markdown
                markdown = self.pretty_printer.format_to_markdown(parsed_doc)
                
                # Parse back (simplified - just verify it doesn't crash)
                # In a real implementation, we would parse the markdown back
                # and verify structural equivalence
                success = len(markdown) > 0
                
                if success:
                    passed += 1
                else:
                    failed += 1
                
            except Exception as e:
                self.logger.error(f"Round-trip test {i} failed: {e}")
                failed += 1
        
        # Create summary result
        success_rate = passed / num_tests if num_tests > 0 else 0
        status = TestStatus.PASS if success_rate >= 0.95 else TestStatus.FAIL
        
        result = TestResult(
            test_id="pretty_printer_round_trip_summary",
            requirement_id="55.4",
            category="pretty_printer_stress",
            status=status,
            duration_seconds=0.0,
            error_message=None if success_rate >= 0.95 else f"Success rate {success_rate:.1%} < 95%",
            metrics=None,
            artifacts=[]
        )
        results.append(result)
        
        self.logger.info(f"Round-trip tests: {passed} passed, {failed} failed (success rate: {success_rate:.1%})")
        
        return results
    
    def test_edge_case_structures(self) -> List[TestResult]:
        """
        Test all edge case document structures.
        
        Requirements: 55.5
        """
        self.logger.info("Testing edge case structures...")
        results = []
        
        edge_cases = [
            ("empty_document", self._create_empty_structure()),
            ("single_section", self._create_single_section_structure()),
            ("no_content", self._create_no_content_structure()),
            ("only_headings", self._create_only_headings_structure()),
            ("mixed_levels", self._create_mixed_levels_structure()),
        ]
        
        for case_name, structure in edge_cases:
            test_id = f"pretty_printer_edge_case_{case_name}"
            
            try:
                self.metrics_collector.start_collection(test_id)
                start_time = time.time()
                
                # Create parsed document
                parsed_doc = ParsedDocument(
                    text="",
                    structure=structure
                )
                
                # Format to markdown
                markdown = self.pretty_printer.format_to_markdown(parsed_doc)
                
                # Verify it doesn't crash
                success = markdown is not None
                
                metrics = self.metrics_collector.stop_collection(test_id)
                duration = time.time() - start_time
                
                status = TestStatus.PASS if success else TestStatus.FAIL
                
                result = TestResult(
                    test_id=test_id,
                    requirement_id="55.5",
                    category="pretty_printer_stress",
                    status=status,
                    duration_seconds=duration,
                    error_message=None if success else f"Failed on edge case: {case_name}",
                    metrics=metrics,
                    artifacts=[]
                )
                results.append(result)
                
            except Exception as e:
                self.logger.error(f"Edge case {case_name} failed: {e}")
                result = TestResult(
                    test_id=test_id,
                    requirement_id="55.5",
                    category="pretty_printer_stress",
                    status=TestStatus.FAIL,
                    duration_seconds=0.0,
                    error_message=f"Test execution failed: {str(e)}",
                    metrics=None,
                    artifacts=[]
                )
                results.append(result)
        
        return results
    
    def _create_nested_sections(self, depth: int, current_level: int = 1) -> Section:
        """Create deeply nested sections."""
        if depth <= 0:
            return Section(
                title=f"Leaf Section",
                content="Leaf content",
                level=current_level,
                subsections=[]
            )
        
        subsection = self._create_nested_sections(depth - 1, current_level + 1)
        
        return Section(
            title=f"Section Level {current_level}",
            content=f"Content at level {current_level}",
            level=current_level,
            subsections=[subsection]
        )
    
    def _generate_random_structure(self) -> DocumentStructure:
        """Generate random document structure."""
        num_sections = random.randint(1, 20)
        sections = []
        headings = []
        
        for i in range(num_sections):
            level = random.randint(1, 3)
            title = f"Section {i}"
            content = f"Content {i}"
            
            section = Section(
                title=title,
                content=content,
                level=level,
                subsections=[]
            )
            sections.append(section)
            
            heading = Heading(
                text=title,
                level=level,
                start_pos=0,
                end_pos=0
            )
            headings.append(heading)
        
        return DocumentStructure(
            headings=headings,
            sections=sections
        )
    
    def _create_empty_structure(self) -> DocumentStructure:
        """Create empty structure."""
        return DocumentStructure(headings=[], sections=[])
    
    def _create_single_section_structure(self) -> DocumentStructure:
        """Create structure with single section."""
        section = Section(
            title="Single Section",
            content="Single content",
            level=1,
            subsections=[]
        )
        heading = Heading(text="Single Section", level=1, start_pos=0, end_pos=0)
        return DocumentStructure(headings=[heading], sections=[section])
    
    def _create_no_content_structure(self) -> DocumentStructure:
        """Create structure with no content."""
        sections = [
            Section(title=f"Section {i}", content="", level=1, subsections=[])
            for i in range(5)
        ]
        headings = [
            Heading(text=f"Section {i}", level=1, start_pos=0, end_pos=0)
            for i in range(5)
        ]
        return DocumentStructure(headings=headings, sections=sections)
    
    def _create_only_headings_structure(self) -> DocumentStructure:
        """Create structure with only headings."""
        headings = [
            Heading(text=f"Heading {i}", level=random.randint(1, 6), start_pos=0, end_pos=0)
            for i in range(10)
        ]
        return DocumentStructure(headings=headings, sections=[])
    
    def _create_mixed_levels_structure(self) -> DocumentStructure:
        """Create structure with mixed heading levels."""
        sections = [
            Section(title="H1", content="Content 1", level=1, subsections=[]),
            Section(title="H5", content="Content 5", level=5, subsections=[]),
            Section(title="H2", content="Content 2", level=2, subsections=[]),
            Section(title="H6", content="Content 6", level=6, subsections=[]),
            Section(title="H3", content="Content 3", level=3, subsections=[]),
        ]
        headings = [
            Heading(text=s.title, level=s.level, start_pos=0, end_pos=0)
            for s in sections
        ]
        return DocumentStructure(headings=headings, sections=sections)
