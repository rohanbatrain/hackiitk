"""
Test Data Generator for Extreme Testing Framework

This module provides comprehensive test data generation capabilities including:
- Synthetic policy documents with configurable characteristics
- Malicious PDF files for security testing
- Documents with intentional gaps at specific CSF subcategories
- Documents with extreme structural properties
- Documents with diverse character sets and encodings
- CLI interface for custom test case generation
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from pathlib import Path
import random
import json
import hashlib
import logging


@dataclass
class DocumentSpec:
    """Specification for synthetic document generation."""
    size_pages: int = 10
    words_per_page: int = 500
    sections_per_page: int = 3
    coverage_percentage: float = 0.5  # 0.0 to 1.0
    include_csf_keywords: bool = True
    structure_type: str = "normal"  # normal, flat, deep, inconsistent
    language: str = "english"


class TestDataGenerator:
    """
    Generates diverse test data for comprehensive testing.
    
    This class provides methods to generate:
    - Synthetic policy documents with configurable characteristics
    - Malicious PDF files for security testing
    - Documents with intentional gaps at specific CSF subcategories
    - Documents with extreme structural properties
    - Documents with diverse character sets and encodings
    """
    
    # CSF subcategories for gap generation
    CSF_SUBCATEGORIES = [
        "ID.AM-1", "ID.AM-2", "ID.AM-3", "ID.AM-4", "ID.AM-5", "ID.AM-6",
        "ID.BE-1", "ID.BE-2", "ID.BE-3", "ID.BE-4", "ID.BE-5",
        "ID.GV-1", "ID.GV-2", "ID.GV-3", "ID.GV-4",
        "ID.RA-1", "ID.RA-2", "ID.RA-3", "ID.RA-4", "ID.RA-5", "ID.RA-6",
        "ID.RM-1", "ID.RM-2", "ID.RM-3",
        "PR.AC-1", "PR.AC-2", "PR.AC-3", "PR.AC-4", "PR.AC-5", "PR.AC-6", "PR.AC-7",
        "PR.AT-1", "PR.AT-2", "PR.AT-3", "PR.AT-4", "PR.AT-5",
        "PR.DS-1", "PR.DS-2", "PR.DS-3", "PR.DS-4", "PR.DS-5", "PR.DS-6", "PR.DS-7", "PR.DS-8",
        "PR.IP-1", "PR.IP-2", "PR.IP-3", "PR.IP-4", "PR.IP-5", "PR.IP-6",
        "PR.MA-1", "PR.MA-2", "PR.PT-1", "PR.PT-2", "PR.PT-3", "PR.PT-4"
    ]
    
    # CSF keywords for content generation
    CSF_KEYWORDS = {
        "ID.AM": ["asset management", "inventory", "hardware assets", "software assets", "data flows"],
        "ID.BE": ["business environment", "role", "mission", "dependencies", "critical functions"],
        "ID.GV": ["governance", "policy", "legal requirements", "risk management", "cybersecurity"],
        "ID.RA": ["risk assessment", "vulnerabilities", "threats", "likelihood", "impact"],
        "ID.RM": ["risk management", "risk tolerance", "risk response", "priorities"],
        "PR.AC": ["access control", "identity management", "authentication", "authorization", "credentials"],
        "PR.AT": ["awareness", "training", "privileged users", "third-party stakeholders"],
        "PR.DS": ["data security", "protection", "encryption", "integrity", "confidentiality"],
        "PR.IP": ["information protection", "baseline configuration", "change control", "backups"],
        "PR.MA": ["maintenance", "remote maintenance", "logging"],
        "PR.PT": ["protective technology", "audit logs", "least functionality", "communications"]
    }
    
    def __init__(self, cache_dir: Optional[Path] = None, logger: Optional[logging.Logger] = None):
        """
        Initialize test data generator.
        
        Args:
            cache_dir: Optional directory for caching generated test data
            logger: Optional logger instance
        """
        self.cache_dir = cache_dir or Path("test_outputs/test_data")
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.logger = logger or logging.getLogger(__name__)
        self._cache: Dict[str, Any] = {}
    
    def generate_policy_document(self, spec: DocumentSpec) -> str:
        """
        Generate synthetic policy document with specified characteristics.
        
        Args:
            spec: Document specification
            
        Returns:
            Generated policy document as markdown text
        """
        self.logger.info(f"Generating policy document: {spec.size_pages} pages, {spec.coverage_percentage*100}% coverage")
        
        # Calculate total sections
        total_sections = spec.size_pages * spec.sections_per_page
        
        # Determine which CSF subcategories to cover
        num_covered = int(len(self.CSF_SUBCATEGORIES) * spec.coverage_percentage)
        covered_subcategories = random.sample(self.CSF_SUBCATEGORIES, num_covered)
        
        # Generate document
        sections = []
        sections.append("# Cybersecurity Policy Document\n")
        sections.append("## Executive Summary\n")
        sections.append(self._generate_paragraph(100, spec.language))
        sections.append("\n")
        
        # Generate sections with CSF coverage
        for i in range(total_sections):
            section_num = i + 1
            section_title = f"## Section {section_num}: Policy Requirements\n"
            sections.append(section_title)
            
            # Determine if this section should cover a CSF subcategory
            if spec.include_csf_keywords and covered_subcategories and i % 3 == 0:
                # Pick a subcategory to cover
                subcategory = covered_subcategories[i % len(covered_subcategories)]
                function = subcategory.split(".")[0] + "." + subcategory.split(".")[1].split("-")[0]
                
                # Get keywords for this function
                keywords = self.CSF_KEYWORDS.get(function, ["security", "controls"])
                
                # Generate content with keywords
                content = self._generate_csf_content(subcategory, keywords, spec.words_per_page // spec.sections_per_page, spec.language)
                sections.append(content)
            else:
                # Generate generic content
                content = self._generate_paragraph(spec.words_per_page // spec.sections_per_page, spec.language)
                sections.append(content)
            
            sections.append("\n")
        
        document = "".join(sections)
        
        # Apply structure transformations
        if spec.structure_type != "normal":
            document = self._apply_structure_transformation(document, spec.structure_type)
        
        return document
    
    def generate_malicious_pdf(self, attack_type: str) -> bytes:
        """
        Generate malicious PDF for security testing.
        
        Args:
            attack_type: Type of attack (javascript, malformed, recursive, large_object)
            
        Returns:
            PDF file content as bytes
        """
        self.logger.info(f"Generating malicious PDF: {attack_type}")
        
        # Note: This is a simplified implementation that generates PDF-like content
        # In a real implementation, you would use a PDF library like PyPDF2 or reportlab
        
        if attack_type == "javascript":
            return self._generate_javascript_pdf()
        elif attack_type == "malformed":
            return self._generate_malformed_pdf()
        elif attack_type == "recursive":
            return self._generate_recursive_pdf()
        elif attack_type == "large_object":
            return self._generate_large_object_pdf()
        else:
            raise ValueError(f"Unknown attack type: {attack_type}")
    
    def generate_gap_policy(self, gap_subcategories: List[str]) -> str:
        """
        Generate policy with intentional gaps at specified subcategories.
        
        Args:
            gap_subcategories: List of CSF subcategory IDs that should be gaps
            
        Returns:
            Generated policy document with intentional gaps
        """
        self.logger.info(f"Generating gap policy with {len(gap_subcategories)} intentional gaps")
        
        # Determine which subcategories to cover (all except gaps)
        covered_subcategories = [sc for sc in self.CSF_SUBCATEGORIES if sc not in gap_subcategories]
        
        # Create spec with specific coverage
        spec = DocumentSpec(
            size_pages=10,
            words_per_page=500,
            sections_per_page=3,
            coverage_percentage=len(covered_subcategories) / len(self.CSF_SUBCATEGORIES),
            include_csf_keywords=True
        )
        
        # Generate document
        sections = []
        sections.append("# Cybersecurity Policy Document\n")
        sections.append("## Executive Summary\n")
        sections.append(self._generate_paragraph(100, "english"))
        sections.append("\n")
        
        # Generate sections covering only non-gap subcategories
        for i, subcategory in enumerate(covered_subcategories):
            section_num = i + 1
            section_title = f"## Section {section_num}: {subcategory} Requirements\n"
            sections.append(section_title)
            
            function = subcategory.split(".")[0] + "." + subcategory.split(".")[1].split("-")[0]
            keywords = self.CSF_KEYWORDS.get(function, ["security", "controls"])
            
            content = self._generate_csf_content(subcategory, keywords, 150, "english")
            sections.append(content)
            sections.append("\n")
        
        return "".join(sections)
    
    def generate_extreme_structure(self, structure_type: str) -> str:
        """
        Generate document with extreme structural properties.
        
        Args:
            structure_type: Type of structure (no_headings, deep_nesting, inconsistent_hierarchy,
                          only_tables, many_headings, many_sections)
            
        Returns:
            Generated document with extreme structure
        """
        self.logger.info(f"Generating extreme structure document: {structure_type}")
        
        if structure_type == "no_headings":
            return self._generate_no_headings_document()
        elif structure_type == "deep_nesting":
            return self._generate_deep_nesting_document()
        elif structure_type == "inconsistent_hierarchy":
            return self._generate_inconsistent_hierarchy_document()
        elif structure_type == "only_tables":
            return self._generate_only_tables_document()
        elif structure_type == "many_headings":
            return self._generate_many_headings_document()
        elif structure_type == "many_sections":
            return self._generate_many_sections_document()
        else:
            raise ValueError(f"Unknown structure type: {structure_type}")
    
    def generate_multilingual_document(self, languages: List[str]) -> str:
        """
        Generate document with diverse character sets.
        
        Args:
            languages: List of languages to include (chinese, arabic, cyrillic, emoji, greek)
            
        Returns:
            Generated multilingual document
        """
        self.logger.info(f"Generating multilingual document with {len(languages)} languages")
        
        sections = []
        sections.append("# Multilingual Cybersecurity Policy\n\n")
        
        for i, language in enumerate(languages):
            section_num = i + 1
            sections.append(f"## Section {section_num}: {language.title()} Content\n\n")
            sections.append(self._generate_paragraph(200, language))
            sections.append("\n\n")
        
        return "".join(sections)
    
    # Private helper methods
    
    def _generate_paragraph(self, word_count: int, language: str = "english") -> str:
        """Generate a paragraph with specified word count and language."""
        if language == "english":
            words = ["security", "policy", "system", "data", "access", "control", "management",
                    "protection", "risk", "compliance", "audit", "monitoring", "incident",
                    "response", "recovery", "backup", "encryption", "authentication"]
            return " ".join(random.choices(words, k=word_count)) + "."
        
        elif language == "chinese":
            # Chinese characters for cybersecurity terms
            chars = ["安全", "政策", "系统", "数据", "访问", "控制", "管理", "保护", "风险"]
            return "".join(random.choices(chars, k=word_count // 2)) + "。"
        
        elif language == "arabic":
            # Arabic characters for cybersecurity terms
            words = ["الأمن", "السياسة", "النظام", "البيانات", "الوصول", "التحكم", "الإدارة"]
            return " ".join(random.choices(words, k=word_count)) + "."
        
        elif language == "cyrillic":
            # Cyrillic characters for cybersecurity terms
            words = ["безопасность", "политика", "система", "данные", "доступ", "контроль"]
            return " ".join(random.choices(words, k=word_count)) + "."
        
        elif language == "emoji":
            # Emoji characters
            emojis = ["🔒", "🔐", "🛡️", "🔑", "⚠️", "✅", "❌", "📊", "📈", "💻"]
            return " ".join(random.choices(emojis, k=min(word_count, 50)))
        
        elif language == "greek":
            # Greek mathematical symbols
            symbols = ["α", "β", "γ", "δ", "ε", "θ", "λ", "μ", "π", "σ", "ω", "Σ", "Δ", "Ω"]
            return " ".join(random.choices(symbols, k=word_count)) + "."
        
        else:
            # Default to English
            return self._generate_paragraph(word_count, "english")
    
    def _generate_csf_content(self, subcategory: str, keywords: List[str], word_count: int, language: str) -> str:
        """Generate content that covers a specific CSF subcategory."""
        content_parts = []
        
        # Add subcategory reference
        content_parts.append(f"This section addresses {subcategory}. ")
        
        # Add keywords
        for keyword in keywords[:3]:
            content_parts.append(f"Our organization implements {keyword} controls. ")
        
        # Add filler content
        remaining_words = word_count - len(" ".join(content_parts).split())
        if remaining_words > 0:
            content_parts.append(self._generate_paragraph(remaining_words, language))
        
        return "".join(content_parts)
    
    def _apply_structure_transformation(self, document: str, structure_type: str) -> str:
        """Apply structural transformation to document."""
        if structure_type == "flat":
            # Remove all heading markers except H1
            lines = document.split("\n")
            transformed = []
            for line in lines:
                if line.startswith("##"):
                    transformed.append(line.replace("##", "").strip())
                else:
                    transformed.append(line)
            return "\n".join(transformed)
        
        elif structure_type == "deep":
            # Add deep nesting
            lines = document.split("\n")
            transformed = []
            nesting_level = 1
            for line in lines:
                if line.startswith("##"):
                    nesting_level = min(nesting_level + 1, 6)
                    transformed.append("#" * nesting_level + line[2:])
                else:
                    transformed.append(line)
            return "\n".join(transformed)
        
        elif structure_type == "inconsistent":
            # Create inconsistent hierarchy (H1 -> H5 -> H2)
            lines = document.split("\n")
            transformed = []
            levels = [1, 5, 2, 4, 3, 6, 2]
            level_idx = 0
            for line in lines:
                if line.startswith("##"):
                    level = levels[level_idx % len(levels)]
                    transformed.append("#" * level + line[2:])
                    level_idx += 1
                else:
                    transformed.append(line)
            return "\n".join(transformed)
        
        return document
    
    def _generate_no_headings_document(self) -> str:
        """Generate document with no headings."""
        content = []
        for _ in range(50):
            content.append(self._generate_paragraph(100, "english"))
            content.append("\n\n")
        return "".join(content)
    
    def _generate_deep_nesting_document(self) -> str:
        """Generate document with 100+ nesting levels."""
        sections = []
        for level in range(1, 101):
            heading_level = min(level, 6)  # Markdown only supports up to H6
            sections.append("#" * heading_level + f" Level {level} Heading\n\n")
            sections.append(self._generate_paragraph(50, "english"))
            sections.append("\n\n")
        return "".join(sections)
    
    def _generate_inconsistent_hierarchy_document(self) -> str:
        """Generate document with inconsistent heading hierarchy."""
        sections = []
        sections.append("# Main Title\n\n")
        sections.append(self._generate_paragraph(50, "english"))
        sections.append("\n\n")
        
        # Jump from H1 to H5
        sections.append("##### Subsection\n\n")
        sections.append(self._generate_paragraph(50, "english"))
        sections.append("\n\n")
        
        # Back to H2
        sections.append("## Another Section\n\n")
        sections.append(self._generate_paragraph(50, "english"))
        sections.append("\n\n")
        
        # Jump to H6
        sections.append("###### Deep Subsection\n\n")
        sections.append(self._generate_paragraph(50, "english"))
        sections.append("\n\n")
        
        return "".join(sections)
    
    def _generate_only_tables_document(self) -> str:
        """Generate document with only tables."""
        tables = []
        for i in range(20):
            tables.append(f"| Column 1 | Column 2 | Column 3 |\n")
            tables.append(f"|----------|----------|----------|\n")
            for j in range(10):
                tables.append(f"| Data {i}-{j}-1 | Data {i}-{j}-2 | Data {i}-{j}-3 |\n")
            tables.append("\n")
        return "".join(tables)
    
    def _generate_many_headings_document(self) -> str:
        """Generate document with 1000+ headings."""
        sections = []
        for i in range(1000):
            level = (i % 6) + 1
            sections.append("#" * level + f" Heading {i}\n\n")
            sections.append(self._generate_paragraph(20, "english"))
            sections.append("\n\n")
        return "".join(sections)
    
    def _generate_many_sections_document(self) -> str:
        """Generate document with 1000+ sections."""
        sections = []
        sections.append("# Policy Document\n\n")
        for i in range(1000):
            sections.append(f"## Section {i}\n\n")
            sections.append(self._generate_paragraph(50, "english"))
            sections.append("\n\n")
        return "".join(sections)
    
    def _generate_javascript_pdf(self) -> bytes:
        """Generate PDF with embedded JavaScript."""
        # Simplified PDF with JavaScript action
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/OpenAction << /S /JavaScript /JS (app.alert('XSS Test');) >>
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/Resources <<
/Font <<
/F1 <<
/Type /Font
/Subtype /Type1
/BaseFont /Helvetica
>>
>>
>>
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length 44
>>
stream
BT
/F1 12 Tf
100 700 Td
(Malicious PDF) Tj
ET
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000127 00000 n 
0000000184 00000 n 
0000000384 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
477
%%EOF
"""
        return pdf_content
    
    def _generate_malformed_pdf(self) -> bytes:
        """Generate malformed PDF."""
        # PDF with missing required elements
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
>>
endobj
xref
0 2
0000000000 65535 f 
0000000009 00000 n 
trailer
<<
/Size 2
/Root 1 0 R
>>
startxref
50
%%EOF
"""
        return pdf_content
    
    def _generate_recursive_pdf(self) -> bytes:
        """Generate PDF with recursive object references."""
        # PDF with circular reference
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
/Metadata 1 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
/Parent 2 0 R
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
>>
endobj
xref
0 4
0000000000 65535 f 
0000000009 00000 n 
0000000080 00000 n 
0000000160 00000 n 
trailer
<<
/Size 4
/Root 1 0 R
>>
startxref
240
%%EOF
"""
        return pdf_content
    
    def _generate_large_object_pdf(self) -> bytes:
        """Generate PDF with extremely large embedded object."""
        # PDF with large stream
        large_data = b"A" * 10000000  # 10MB of data
        pdf_content = b"""%PDF-1.4
1 0 obj
<<
/Type /Catalog
/Pages 2 0 R
>>
endobj
2 0 obj
<<
/Type /Pages
/Kids [3 0 R]
/Count 1
>>
endobj
3 0 obj
<<
/Type /Page
/Parent 2 0 R
/MediaBox [0 0 612 792]
/Contents 4 0 R
>>
endobj
4 0 obj
<<
/Length """ + str(len(large_data)).encode() + b"""
>>
stream
""" + large_data + b"""
endstream
endobj
xref
0 5
0000000000 65535 f 
0000000009 00000 n 
0000000058 00000 n 
0000000115 00000 n 
0000000215 00000 n 
trailer
<<
/Size 5
/Root 1 0 R
>>
startxref
""" + str(300 + len(large_data)).encode() + b"""
%%EOF
"""
        return pdf_content
    
    def save_to_cache(self, key: str, content: Any) -> Path:
        """
        Save generated content to cache.
        
        Args:
            key: Cache key
            content: Content to cache
            
        Returns:
            Path to cached file
        """
        # Generate filename from key
        filename = hashlib.md5(key.encode()).hexdigest()
        
        if isinstance(content, str):
            filepath = self.cache_dir / f"{filename}.md"
            filepath.write_text(content)
        elif isinstance(content, bytes):
            filepath = self.cache_dir / f"{filename}.pdf"
            filepath.write_bytes(content)
        else:
            filepath = self.cache_dir / f"{filename}.json"
            filepath.write_text(json.dumps(content))
        
        self.logger.info(f"Cached test data: {filepath}")
        return filepath
    
    def load_from_cache(self, key: str) -> Optional[Any]:
        """
        Load content from cache.
        
        Args:
            key: Cache key
            
        Returns:
            Cached content or None if not found
        """
        filename = hashlib.md5(key.encode()).hexdigest()
        
        # Try different extensions
        for ext in [".md", ".pdf", ".json"]:
            filepath = self.cache_dir / f"{filename}{ext}"
            if filepath.exists():
                if ext == ".md":
                    return filepath.read_text()
                elif ext == ".pdf":
                    return filepath.read_bytes()
                elif ext == ".json":
                    return json.loads(filepath.read_text())
        
        return None


def main():
    """CLI interface for test data generation."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Generate test data for extreme testing")
    parser.add_argument("--type", choices=["policy", "malicious", "gap", "structure", "multilingual"],
                       required=True, help="Type of test data to generate")
    parser.add_argument("--output", type=str, required=True, help="Output file path")
    parser.add_argument("--pages", type=int, default=10, help="Number of pages (for policy)")
    parser.add_argument("--coverage", type=float, default=0.5, help="Coverage percentage (for policy)")
    parser.add_argument("--attack", type=str, help="Attack type (for malicious)")
    parser.add_argument("--gaps", type=str, help="Comma-separated gap subcategories (for gap)")
    parser.add_argument("--structure", type=str, help="Structure type (for structure)")
    parser.add_argument("--languages", type=str, help="Comma-separated languages (for multilingual)")
    
    args = parser.parse_args()
    
    generator = TestDataGenerator()
    
    if args.type == "policy":
        spec = DocumentSpec(size_pages=args.pages, coverage_percentage=args.coverage)
        content = generator.generate_policy_document(spec)
        Path(args.output).write_text(content)
        print(f"Generated policy document: {args.output}")
    
    elif args.type == "malicious":
        if not args.attack:
            print("Error: --attack required for malicious type")
            return
        content = generator.generate_malicious_pdf(args.attack)
        Path(args.output).write_bytes(content)
        print(f"Generated malicious PDF: {args.output}")
    
    elif args.type == "gap":
        if not args.gaps:
            print("Error: --gaps required for gap type")
            return
        gap_list = args.gaps.split(",")
        content = generator.generate_gap_policy(gap_list)
        Path(args.output).write_text(content)
        print(f"Generated gap policy: {args.output}")
    
    elif args.type == "structure":
        if not args.structure:
            print("Error: --structure required for structure type")
            return
        content = generator.generate_extreme_structure(args.structure)
        Path(args.output).write_text(content)
        print(f"Generated extreme structure document: {args.output}")
    
    elif args.type == "multilingual":
        if not args.languages:
            print("Error: --languages required for multilingual type")
            return
        lang_list = args.languages.split(",")
        content = generator.generate_multilingual_document(lang_list)
        Path(args.output).write_text(content)
        print(f"Generated multilingual document: {args.output}")


if __name__ == "__main__":
    main()
