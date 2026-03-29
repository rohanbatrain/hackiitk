"""
Domain Mapper for CSF Subcategory Prioritization.

This module maps policy domains to prioritized CSF subcategories,
enabling domain-specific gap analysis with appropriate warnings.

**Validates: Requirements 12.1, 12.2, 12.3, 12.4, 12.5, 12.6, 12.7**
"""

import logging
from typing import List, Optional, Tuple

from models.domain import CSFSubcategory
from reference_builder.reference_catalog import ReferenceCatalog


logger = logging.getLogger(__name__)


class DomainMapper:
    """
    Maps policy domains to prioritized CSF subcategories.
    
    Provides domain-specific prioritization for targeted gap analysis
    and includes appropriate warnings for framework limitations.
    """
    
    # Domain-specific prioritization rules
    DOMAIN_MAPPINGS = {
        'isms': {
            'description': 'Information Security Management System',
            'prioritize_functions': ['Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover'],
            'prioritize_subcategories': [],  # All CSF subcategories for comprehensive ISMS analysis
            'warning': None
        },
        'risk_management': {
            'description': 'Risk Management',
            'prioritize_functions': [],
            'prioritize_subcategories': ['GV.RM-01', 'GV.RM-02', 'GV.RM-03', 'GV.OV-01', 'ID.RA-01', 'ID.RA-02', 'ID.RA-03', 'ID.RA-04', 'ID.RA-05'],
            'warning': None
        },
        'patch_management': {
            'description': 'Patch Management',
            'prioritize_functions': [],
            'prioritize_subcategories': ['ID.RA-01', 'PR.DS-01', 'PR.DS-02', 'PR.PS-01', 'PR.PS-02'],
            'warning': None
        },
        'data_privacy': {
            'description': 'Data Privacy',
            'prioritize_functions': [],
            'prioritize_subcategories': ['PR.AA-01', 'PR.AA-02', 'PR.AA-03', 'PR.AA-05', 'PR.DS-01', 'PR.DS-02', 'PR.AT-01'],
            'warning': (
                "The NIST CSF 2.0 addresses cybersecurity aspects of data protection "
                "but is not a complete privacy framework. Privacy-specific compliance "
                "requirements may extend beyond CSF scope."
            )
        }
    }
    
    def __init__(self, catalog: ReferenceCatalog):
        """
        Initialize domain mapper with reference catalog.
        
        Args:
            catalog: Reference catalog containing all CSF subcategories
        """
        self.catalog = catalog
    
    def get_prioritized_subcategories(
        self,
        domain: Optional[str] = None
    ) -> Tuple[List[CSFSubcategory], Optional[str]]:
        """
        Get prioritized CSF subcategories for a policy domain.
        
        Args:
            domain: Policy domain identifier (e.g., 'isms', 'risk_management',
                   'patch_management', 'data_privacy'). If None or unknown,
                   returns all CSF subcategories.
        
        Returns:
            Tuple of (prioritized_subcategories, warning_message)
            - prioritized_subcategories: List of CSF subcategories to analyze
            - warning_message: Optional warning about framework limitations
        
        Examples:
            >>> mapper = DomainMapper(catalog)
            >>> subcats, warning = mapper.get_prioritized_subcategories('isms')
            >>> # Returns all GV function subcategories, no warning
            
            >>> subcats, warning = mapper.get_prioritized_subcategories('data_privacy')
            >>> # Returns PR.AA, PR.DS, PR.AT subcategories with privacy warning
            
            >>> subcats, warning = mapper.get_prioritized_subcategories('unknown')
            >>> # Returns all CSF subcategories, no warning
        """
        # Handle None or unknown domain - fallback to all subcategories
        if not domain or domain not in self.DOMAIN_MAPPINGS:
            if domain:
                logger.warning(
                    f"Unknown domain '{domain}', evaluating against all CSF functions"
                )
            else:
                logger.info("No domain specified, evaluating against all CSF functions")
            
            return self.catalog.get_all_subcategories(), None
        
        # Get domain mapping configuration
        mapping = self.DOMAIN_MAPPINGS[domain]
        logger.info(
            f"Applying domain-specific prioritization for: {mapping['description']}"
        )
        
        # Collect prioritized subcategories
        prioritized = []
        
        # Add subcategories from prioritized functions
        if mapping['prioritize_functions']:
            for function in mapping['prioritize_functions']:
                function_subcats = self.catalog.get_by_function(function)
                prioritized.extend(function_subcats)
                logger.debug(
                    f"Added {len(function_subcats)} subcategories from {function} function"
                )
        
        # Add specific prioritized subcategories
        if mapping['prioritize_subcategories']:
            for subcategory_id in mapping['prioritize_subcategories']:
                subcat = self.catalog.get_subcategory(subcategory_id)
                if subcat and subcat not in prioritized:
                    prioritized.append(subcat)
            logger.debug(
                f"Added {len(mapping['prioritize_subcategories'])} specific subcategories"
            )
        
        # Log warning if present
        warning = mapping['warning']
        if warning:
            logger.warning(f"Domain limitation: {warning}")
        
        logger.info(
            f"Domain '{domain}' prioritization: {len(prioritized)} subcategories selected"
        )
        
        return prioritized, warning
    
    def get_supported_domains(self) -> List[str]:
        """
        Get list of supported policy domains.
        
        Returns:
            List of supported domain identifiers
        """
        return list(self.DOMAIN_MAPPINGS.keys())
    
    def get_domain_description(self, domain: str) -> Optional[str]:
        """
        Get human-readable description for a domain.
        
        Args:
            domain: Policy domain identifier
        
        Returns:
            Domain description if domain is supported, None otherwise
        """
        mapping = self.DOMAIN_MAPPINGS.get(domain)
        return mapping['description'] if mapping else None
