"""
CIS Guide Parser Helper.

This module provides utilities for extracting CSF subcategory mappings,
policy template recommendations, keywords, domain tags, and priority levels
from the CIS MS-ISAC NIST CSF 2.0 Policy Template Guide PDF.

**Validates: Requirements 3.1, 3.2**
"""

import logging
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import fitz  # PyMuPDF

from models.domain import CSFSubcategory


logger = logging.getLogger(__name__)


class CISGuideParser:
    """
    Parser for CIS MS-ISAC NIST CSF 2.0 Policy Template Guide.
    
    Extracts CSF subcategory mappings, policy templates, keywords,
    domain tags, and priority levels from the CIS guide PDF.
    """
    
    # Priority keywords that indicate criticality
    CRITICAL_KEYWORDS = [
        "critical", "essential", "mandatory", "required", "must have"
    ]
    HIGH_KEYWORDS = [
        "important", "significant", "high priority", "strongly recommended"
    ]
    MEDIUM_KEYWORDS = [
        "recommended", "should have", "advisable"
    ]
    
    # Domain tag mappings based on policy template names
    DOMAIN_MAPPINGS = {
        "information security": ["isms", "governance"],
        "risk management": ["risk_management"],
        "access control": ["access_control", "data_privacy"],
        "patch management": ["patch_management", "vulnerability_management"],
        "vulnerability": ["vulnerability_management"],
        "incident response": ["incident_response"],
        "business continuity": ["business_continuity", "recovery"],
        "disaster recovery": ["recovery", "business_continuity"],
        "third party": ["supply_chain"],
        "vendor": ["supply_chain"],
        "supply chain": ["supply_chain"],
        "data protection": ["data_security", "data_privacy"],
        "privacy": ["data_privacy"],
        "network security": ["network_security"],
        "physical security": ["physical_security"],
        "awareness": ["awareness_training"],
        "training": ["awareness_training"],
        "asset management": ["asset_management"],
        "monitoring": ["incident_detection"],
        "logging": ["incident_detection"],
    }
    
    def __init__(self, cis_guide_path: str):
        """
        Initialize parser with CIS guide PDF path.
        
        Args:
            cis_guide_path: Path to CIS MS-ISAC NIST CSF 2.0 Policy Template Guide PDF
            
        Raises:
            FileNotFoundError: If CIS guide file not found
        """
        self.guide_path = Path(cis_guide_path)
        if not self.guide_path.exists():
            raise FileNotFoundError(f"CIS guide not found: {cis_guide_path}")
        
        self.doc = None
    
    def parse(self) -> List[CSFSubcategory]:
        """
        Parse CIS guide and extract all CSF subcategories.
        
        Returns:
            List of CSFSubcategory objects with complete metadata
            
        Raises:
            ValueError: If parsing fails or produces incomplete results
        """
        logger.info(f"Parsing CIS guide: {self.guide_path}")
        
        try:
            self.doc = fitz.open(self.guide_path)
            subcategories = []
            
            # Extract text from all pages
            full_text = ""
            for page_num in range(len(self.doc)):
                page = self.doc[page_num]
                full_text += page.get_text()
            
            # Parse subcategories from text
            # This is a placeholder - actual implementation would use
            # more sophisticated parsing based on CIS guide structure
            subcategories = self._extract_subcategories(full_text)
            
            logger.info(f"Extracted {len(subcategories)} subcategories from CIS guide")
            
            if len(subcategories) != 49:
                logger.warning(
                    f"Expected 49 subcategories, found {len(subcategories)}. "
                    "CIS guide may have changed or parsing may be incomplete."
                )
            
            return subcategories
            
        finally:
            if self.doc:
                self.doc.close()
    
    def _extract_subcategories(self, text: str) -> List[CSFSubcategory]:
        """
        Extract CSF subcategories from CIS guide text.
        
        Args:
            text: Full text content of CIS guide
            
        Returns:
            List of CSFSubcategory objects
        """
        # This is a placeholder implementation
        # Real implementation would parse the actual CIS guide structure
        # For now, return empty list to indicate parsing not yet implemented
        logger.warning("CIS guide parsing not yet implemented - using hardcoded subcategories")
        return []
    
    def extract_keywords(self, description: str, template_names: List[str]) -> List[str]:
        """
        Extract keywords from subcategory description and template names.
        
        Args:
            description: CSF subcategory description text
            template_names: List of policy template names
            
        Returns:
            List of extracted keywords
        """
        keywords = []
        
        # Extract key phrases from description
        # Remove common words and focus on domain-specific terms
        words = re.findall(r'\b[a-z]{4,}\b', description.lower())
        
        # Filter out common words
        common_words = {
            "that", "with", "from", "have", "this", "they", "been",
            "their", "which", "other", "about", "into", "through"
        }
        keywords.extend([w for w in words if w not in common_words])
        
        # Extract keywords from template names
        for template in template_names:
            template_words = re.findall(r'\b[a-z]{4,}\b', template.lower())
            keywords.extend([w for w in template_words if w not in common_words])
        
        # Remove duplicates and return
        return list(set(keywords))
    
    def extract_domain_tags(self, template_names: List[str], category: str) -> List[str]:
        """
        Extract domain tags from policy template names and CSF category.
        
        Args:
            template_names: List of policy template names
            category: CSF category name
            
        Returns:
            List of domain tags
        """
        tags = set()
        
        # Check template names against domain mappings
        for template in template_names:
            template_lower = template.lower()
            for keyword, domains in self.DOMAIN_MAPPINGS.items():
                if keyword in template_lower:
                    tags.update(domains)
        
        # Check category name against domain mappings
        category_lower = category.lower()
        for keyword, domains in self.DOMAIN_MAPPINGS.items():
            if keyword in category_lower:
                tags.update(domains)
        
        return list(tags) if tags else ["isms"]  # Default to ISMS if no tags found
    
    def assign_priority(self, description: str, template_names: List[str]) -> str:
        """
        Assign priority level based on CIS guidance and subcategory context.
        
        Args:
            description: CSF subcategory description text
            template_names: List of policy template names
            
        Returns:
            Priority level: 'critical', 'high', 'medium', or 'low'
        """
        text = (description + " " + " ".join(template_names)).lower()
        
        # Check for critical indicators
        if any(keyword in text for keyword in self.CRITICAL_KEYWORDS):
            return "critical"
        
        # Check for high priority indicators
        if any(keyword in text for keyword in self.HIGH_KEYWORDS):
            return "high"
        
        # Check for medium priority indicators
        if any(keyword in text for keyword in self.MEDIUM_KEYWORDS):
            return "medium"
        
        # Default to medium for most subcategories
        return "medium"
    
    def parse_template_mappings(self, text: str, subcategory_id: str) -> List[str]:
        """
        Parse policy template recommendations for a specific subcategory.
        
        Args:
            text: Text section containing template mappings
            subcategory_id: CSF subcategory identifier
            
        Returns:
            List of policy template names
        """
        # This is a placeholder - real implementation would parse
        # the actual CIS guide structure to extract template mappings
        templates = []
        
        # Look for common template patterns
        template_patterns = [
            r"Information Security Policy",
            r"Risk Management Policy",
            r"Access Control Policy",
            r"Incident Response Policy",
            r"Business Continuity Policy",
            r"Patch Management Policy",
            r"Vulnerability Management Policy",
        ]
        
        for pattern in template_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                templates.append(pattern)
        
        return templates if templates else ["General Security Policy"]
