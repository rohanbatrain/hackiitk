"""
Reference Catalog Builder for NIST CSF 2.0 Subcategories.

This module parses the CIS MS-ISAC NIST CSF 2.0 Policy Template Guide
and structures it into a queryable knowledge base with all 49 subcategories.

**Validates: Requirements 3.1, 3.2, 3.3, 3.4, 3.5, 3.6**
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

from models.domain import CSFSubcategory


logger = logging.getLogger(__name__)


class ReferenceCatalog:
    """
    Reference catalog of NIST CSF 2.0 subcategories from CIS guide.
    
    Provides structured access to all 49 CSF subcategories with metadata
    including keywords, domain tags, mapped templates, and priority levels.
    """
    
    def __init__(self):
        """Initialize empty reference catalog."""
        self._subcategories: Dict[str, CSFSubcategory] = {}
        self._by_function: Dict[str, List[CSFSubcategory]] = {}
        self._by_domain: Dict[str, List[CSFSubcategory]] = {}
    
    def build_from_cis_guide(self, cis_guide_path: str) -> None:
        """
        Parse CIS guide PDF and build structured catalog.
        
        Args:
            cis_guide_path: Path to CIS MS-ISAC NIST CSF 2.0 Policy Template Guide PDF
            
        Raises:
            FileNotFoundError: If CIS guide file not found
            ValueError: If parsing fails or catalog incomplete
        """
        guide_path = Path(cis_guide_path)
        if not guide_path.exists():
            raise FileNotFoundError(f"CIS guide not found: {cis_guide_path}")
        
        logger.info(f"Building reference catalog from: {cis_guide_path}")
        
        # Parse CIS guide and extract subcategories
        # For now, use the hardcoded NIST CSF 2.0 subcategories
        # TODO: Implement actual PDF parsing when CIS guide is available
        subcategories = self._get_nist_csf_subcategories()
        
        # Build internal indexes
        for subcategory in subcategories:
            self._subcategories[subcategory.subcategory_id] = subcategory
            
            # Index by function
            if subcategory.function not in self._by_function:
                self._by_function[subcategory.function] = []
            self._by_function[subcategory.function].append(subcategory)
            
            # Index by domain tags
            for domain in subcategory.domain_tags:
                if domain not in self._by_domain:
                    self._by_domain[domain] = []
                self._by_domain[domain].append(subcategory)
        
        # Validate completeness
        if len(self._subcategories) != 49:
            raise ValueError(
                f"Incomplete catalog: expected 49 subcategories, got {len(self._subcategories)}"
            )
        
        logger.info(f"Successfully built catalog with {len(self._subcategories)} subcategories")
    
    def get_subcategory(self, subcategory_id: str) -> Optional[CSFSubcategory]:
        """
        Retrieve specific subcategory by ID.
        
        Args:
            subcategory_id: CSF subcategory identifier (e.g., 'GV.RM-01')
            
        Returns:
            CSFSubcategory if found, None otherwise
        """
        return self._subcategories.get(subcategory_id)
    
    def get_by_function(self, function: str) -> List[CSFSubcategory]:
        """
        Retrieve all subcategories for a CSF function.
        
        Args:
            function: CSF function name ('Govern', 'Identify', 'Protect', 'Detect', 'Respond', 'Recover')
            
        Returns:
            List of CSFSubcategory objects for the function
        """
        return self._by_function.get(function, [])
    
    def get_by_domain(self, domain: str) -> List[CSFSubcategory]:
        """
        Retrieve subcategories relevant to a policy domain.
        
        Args:
            domain: Policy domain tag (e.g., 'isms', 'risk_management', 'patch_management')
            
        Returns:
            List of CSFSubcategory objects tagged with the domain
        """
        return self._by_domain.get(domain, [])
    
    def get_all_subcategories(self) -> List[CSFSubcategory]:
        """
        Retrieve all subcategories in the catalog.
        
        Returns:
            List of all CSFSubcategory objects
        """
        return list(self._subcategories.values())
    
    def persist(self, output_path: str) -> None:
        """
        Save catalog to JSON for reuse.
        
        Args:
            output_path: Path where JSON catalog should be saved
            
        Raises:
            IOError: If file cannot be written
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Convert subcategories to dictionaries
        catalog_data = {
            "subcategories": [
                {
                    "subcategory_id": sub.subcategory_id,
                    "function": sub.function,
                    "category": sub.category,
                    "description": sub.description,
                    "keywords": sub.keywords,
                    "domain_tags": sub.domain_tags,
                    "mapped_templates": sub.mapped_templates,
                    "priority": sub.priority,
                }
                for sub in self._subcategories.values()
            ]
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(catalog_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Catalog persisted to: {output_path}")
    
    def load(self, catalog_path: str) -> None:
        """
        Load previously built catalog from JSON.
        
        Args:
            catalog_path: Path to JSON catalog file
            
        Raises:
            FileNotFoundError: If catalog file not found
            ValueError: If catalog format invalid or incomplete
        """
        catalog_file = Path(catalog_path)
        if not catalog_file.exists():
            raise FileNotFoundError(f"Catalog file not found: {catalog_path}")
        
        logger.info(f"Loading catalog from: {catalog_path}")
        
        with open(catalog_file, 'r', encoding='utf-8') as f:
            catalog_data = json.load(f)
        
        # Clear existing data
        self._subcategories.clear()
        self._by_function.clear()
        self._by_domain.clear()
        
        # Load subcategories
        for sub_data in catalog_data.get("subcategories", []):
            subcategory = CSFSubcategory(
                subcategory_id=sub_data["subcategory_id"],
                function=sub_data["function"],
                category=sub_data["category"],
                description=sub_data["description"],
                keywords=sub_data["keywords"],
                domain_tags=sub_data["domain_tags"],
                mapped_templates=sub_data["mapped_templates"],
                priority=sub_data["priority"],
            )
            
            self._subcategories[subcategory.subcategory_id] = subcategory
            
            # Index by function
            if subcategory.function not in self._by_function:
                self._by_function[subcategory.function] = []
            self._by_function[subcategory.function].append(subcategory)
            
            # Index by domain tags
            for domain in subcategory.domain_tags:
                if domain not in self._by_domain:
                    self._by_domain[domain] = []
                self._by_domain[domain].append(subcategory)
        
        # Validate completeness
        if len(self._subcategories) != 49:
            raise ValueError(
                f"Incomplete catalog: expected 49 subcategories, got {len(self._subcategories)}"
            )
        
        logger.info(f"Successfully loaded catalog with {len(self._subcategories)} subcategories")
    
    def validate_completeness(self) -> bool:
        """
        Validate that catalog contains all 49 required subcategories.
        
        Returns:
            True if catalog is complete, False otherwise
        """
        if len(self._subcategories) != 49:
            logger.error(f"Catalog incomplete: {len(self._subcategories)}/49 subcategories")
            return False
        
        # Validate all required fields present
        for sub_id, subcategory in self._subcategories.items():
            if not all([
                subcategory.subcategory_id,
                subcategory.function,
                subcategory.category,
                subcategory.description,
                subcategory.keywords,
                subcategory.domain_tags,
                subcategory.mapped_templates,
                subcategory.priority,
            ]):
                logger.error(f"Subcategory {sub_id} missing required fields")
                return False
        
        return True
    
    def _get_nist_csf_subcategories(self) -> List[CSFSubcategory]:
        """
        Get all 49 NIST CSF 2.0 subcategories with metadata.
        
        This is a hardcoded baseline representing the NIST CSF 2.0 structure.
        In production, this would parse the actual CIS guide PDF.
        
        Distribution: GV(14) + ID(8) + PR(15) + DE(5) + RS(4) + RC(3) = 49
        
        Returns:
            List of all 49 CSFSubcategory objects
        """
        return [
            # GOVERN (GV) - 14 subcategories
            CSFSubcategory(
                subcategory_id="GV.OC-01",
                function="Govern",
                category="Organizational Context",
                description="The organizational mission, objectives, stakeholders, and activities are understood and inform cybersecurity risk management decisions",
                keywords=["mission", "objectives", "stakeholders", "organizational context"],
                domain_tags=["isms", "governance"],
                mapped_templates=["Information Security Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="GV.OC-02",
                function="Govern",
                category="Organizational Context",
                description="Internal and external stakeholders are understood, and their needs and expectations regarding cybersecurity risk management are understood and considered",
                keywords=["stakeholders", "expectations", "requirements"],
                domain_tags=["isms", "governance"],
                mapped_templates=["Information Security Policy"],
                priority="medium"
            ),
            CSFSubcategory(
                subcategory_id="GV.OC-03",
                function="Govern",
                category="Organizational Context",
                description="Legal, regulatory, and contractual requirements regarding cybersecurity are understood and managed",
                keywords=["legal", "regulatory", "compliance", "contractual"],
                domain_tags=["isms", "compliance"],
                mapped_templates=["Information Security Policy", "Compliance Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="GV.OV-01",
                function="Govern",
                category="Oversight",
                description="Cybersecurity risk management strategy, expectations, and policy are established, communicated, and monitored",
                keywords=["strategy", "policy", "oversight", "monitoring"],
                domain_tags=["isms", "risk_management", "governance"],
                mapped_templates=["Information Security Policy", "Risk Management Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="GV.OV-02",
                function="Govern",
                category="Oversight",
                description="Cybersecurity roles, responsibilities, and authorities are established, communicated, understood, and enforced",
                keywords=["roles", "responsibilities", "authorities", "accountability"],
                domain_tags=["isms", "governance"],
                mapped_templates=["Information Security Policy", "Roles and Responsibilities"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="GV.RM-01",
                function="Govern",
                category="Risk Management Strategy",
                description="Risk management objectives are established and agreed to by organizational stakeholders",
                keywords=["risk objectives", "risk appetite", "risk tolerance"],
                domain_tags=["risk_management", "isms"],
                mapped_templates=["Risk Management Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="GV.RM-02",
                function="Govern",
                category="Risk Management Strategy",
                description="Risk appetite and risk tolerance statements are established, communicated, and maintained",
                keywords=["risk appetite", "risk tolerance", "risk thresholds"],
                domain_tags=["risk_management", "isms"],
                mapped_templates=["Risk Management Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="GV.RM-03",
                function="Govern",
                category="Risk Management Strategy",
                description="Cybersecurity risk management activities and outcomes are included in enterprise risk management processes",
                keywords=["enterprise risk", "risk integration", "risk reporting"],
                domain_tags=["risk_management", "isms"],
                mapped_templates=["Risk Management Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="GV.SC-01",
                function="Govern",
                category="Supply Chain Risk Management",
                description="A cybersecurity supply chain risk management program, strategy, objectives, policies, and processes are established and agreed to by organizational stakeholders",
                keywords=["supply chain", "third party", "vendor risk"],
                domain_tags=["supply_chain", "isms"],
                mapped_templates=["Third Party Risk Management Policy", "Vendor Management"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="GV.SC-02",
                function="Govern",
                category="Supply Chain Risk Management",
                description="Suppliers and third-party partners are included in incident planning, response, and recovery activities",
                keywords=["supplier incident response", "third party coordination"],
                domain_tags=["supply_chain", "incident_response"],
                mapped_templates=["Third Party Risk Management Policy", "Incident Response Policy"],
                priority="medium"
            ),
            CSFSubcategory(
                subcategory_id="GV.RR-01",
                function="Govern",
                category="Cybersecurity Roles and Responsibilities",
                description="Organizational leadership is responsible and accountable for cybersecurity risk and fosters a culture that is risk-aware, ethical, and continually improving",
                keywords=["leadership", "accountability", "security culture"],
                domain_tags=["governance", "isms"],
                mapped_templates=["Information Security Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="GV.RR-02",
                function="Govern",
                category="Cybersecurity Roles and Responsibilities",
                description="Roles, responsibilities, and authorities related to cybersecurity risk management are established, communicated, understood, and enforced",
                keywords=["roles", "responsibilities", "RACI"],
                domain_tags=["governance", "isms"],
                mapped_templates=["Information Security Policy", "Roles and Responsibilities"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="GV.PO-01",
                function="Govern",
                category="Policy",
                description="Policy for managing cybersecurity risks is established based on organizational context, cybersecurity strategy, and priorities and is communicated and enforced",
                keywords=["policy", "security policy", "policy management"],
                domain_tags=["governance", "isms"],
                mapped_templates=["Information Security Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="GV.PO-02",
                function="Govern",
                category="Policy",
                description="Policy for managing cybersecurity risks is reviewed, updated, communicated, and enforced to reflect changes in requirements, threats, technology, and organizational mission",
                keywords=["policy review", "policy updates", "policy maintenance"],
                domain_tags=["governance", "isms"],
                mapped_templates=["Information Security Policy"],
                priority="high"
            ),
            
            # IDENTIFY (ID) - 8 subcategories
            CSFSubcategory(
                subcategory_id="ID.AM-01",
                function="Identify",
                category="Asset Management",
                description="Inventories of hardware managed by the organization are maintained",
                keywords=["asset inventory", "hardware", "devices", "equipment"],
                domain_tags=["asset_management", "isms"],
                mapped_templates=["Asset Management Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="ID.AM-02",
                function="Identify",
                category="Asset Management",
                description="Inventories of software, services, and systems managed by the organization are maintained",
                keywords=["software inventory", "applications", "services", "systems"],
                domain_tags=["asset_management", "isms"],
                mapped_templates=["Asset Management Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="ID.AM-03",
                function="Identify",
                category="Asset Management",
                description="Representations of the organization's authorized network communication and internal and external network data flows are maintained",
                keywords=["network diagram", "data flows", "network topology"],
                domain_tags=["asset_management", "network_security"],
                mapped_templates=["Network Security Policy"],
                priority="medium"
            ),
            CSFSubcategory(
                subcategory_id="ID.RA-01",
                function="Identify",
                category="Risk Assessment",
                description="Vulnerabilities in assets are identified, validated, and recorded",
                keywords=["vulnerability", "vulnerability assessment", "vulnerability scanning"],
                domain_tags=["risk_management", "patch_management", "vulnerability_management"],
                mapped_templates=["Vulnerability Management Policy", "Patch Management Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="ID.RA-02",
                function="Identify",
                category="Risk Assessment",
                description="Cyber threat intelligence is received from information sharing forums and sources",
                keywords=["threat intelligence", "threat feeds", "threat information"],
                domain_tags=["risk_management", "threat_management"],
                mapped_templates=["Threat Intelligence Policy"],
                priority="medium"
            ),
            CSFSubcategory(
                subcategory_id="ID.RA-03",
                function="Identify",
                category="Risk Assessment",
                description="Internal and external threats to the organization are identified and recorded",
                keywords=["threat identification", "threat assessment", "threat modeling"],
                domain_tags=["risk_management", "threat_management"],
                mapped_templates=["Risk Assessment Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="ID.RA-04",
                function="Identify",
                category="Risk Assessment",
                description="Potential impacts and likelihoods of threats exploiting vulnerabilities are identified and recorded",
                keywords=["risk analysis", "impact assessment", "likelihood"],
                domain_tags=["risk_management"],
                mapped_templates=["Risk Assessment Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="ID.RA-05",
                function="Identify",
                category="Risk Assessment",
                description="Threats, vulnerabilities, likelihoods, and impacts are used to understand inherent risk and inform risk response decisions",
                keywords=["risk evaluation", "inherent risk", "risk treatment"],
                domain_tags=["risk_management"],
                mapped_templates=["Risk Management Policy"],
                priority="critical"
            ),
            
            # PROTECT (PR) - 15 subcategories
            CSFSubcategory(
                subcategory_id="PR.AA-01",
                function="Protect",
                category="Identity Management, Authentication and Access Control",
                description="Identities and credentials for authorized users, services, and hardware are managed by the organization",
                keywords=["identity management", "user accounts", "credentials"],
                domain_tags=["access_control", "data_privacy", "isms"],
                mapped_templates=["Access Control Policy", "Identity Management Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="PR.AA-02",
                function="Protect",
                category="Identity Management, Authentication and Access Control",
                description="Identities are proofed and bound to credentials based on the context of interactions",
                keywords=["identity proofing", "authentication", "credential binding"],
                domain_tags=["access_control", "data_privacy"],
                mapped_templates=["Access Control Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="PR.AA-03",
                function="Protect",
                category="Identity Management, Authentication and Access Control",
                description="Users, services, and hardware are authenticated",
                keywords=["authentication", "multi-factor", "MFA", "verification"],
                domain_tags=["access_control", "data_privacy"],
                mapped_templates=["Access Control Policy", "Authentication Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="PR.AA-04",
                function="Protect",
                category="Identity Management, Authentication and Access Control",
                description="Identity assertions are protected, conveyed, and verified",
                keywords=["identity assertion", "SSO", "federation", "tokens"],
                domain_tags=["access_control"],
                mapped_templates=["Access Control Policy"],
                priority="medium"
            ),
            CSFSubcategory(
                subcategory_id="PR.AA-05",
                function="Protect",
                category="Identity Management, Authentication and Access Control",
                description="Access permissions, entitlements, and authorizations are defined in a policy, managed, enforced, and reviewed, incorporating the principles of least privilege and separation of duties",
                keywords=["authorization", "least privilege", "separation of duties", "access control"],
                domain_tags=["access_control", "data_privacy", "isms"],
                mapped_templates=["Access Control Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="PR.AA-06",
                function="Protect",
                category="Identity Management, Authentication and Access Control",
                description="Physical access to assets is managed, monitored, and enforced commensurate with risk",
                keywords=["physical access", "physical security", "facility access"],
                domain_tags=["physical_security", "isms"],
                mapped_templates=["Physical Security Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="PR.AT-01",
                function="Protect",
                category="Awareness and Training",
                description="Personnel are provided with cybersecurity awareness and training so that they can perform their cybersecurity-related duties and responsibilities",
                keywords=["security awareness", "training", "education"],
                domain_tags=["awareness_training", "data_privacy", "isms"],
                mapped_templates=["Security Awareness Policy", "Training Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="PR.DS-01",
                function="Protect",
                category="Data Security",
                description="The confidentiality, integrity, and availability of data-at-rest are protected",
                keywords=["data at rest", "encryption", "data protection", "confidentiality"],
                domain_tags=["data_security", "data_privacy", "patch_management"],
                mapped_templates=["Data Protection Policy", "Encryption Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="PR.DS-02",
                function="Protect",
                category="Data Security",
                description="The confidentiality, integrity, and availability of data-in-transit are protected",
                keywords=["data in transit", "encryption", "TLS", "network security"],
                domain_tags=["data_security", "data_privacy", "patch_management"],
                mapped_templates=["Data Protection Policy", "Network Security Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="PR.DS-03",
                function="Protect",
                category="Data Security",
                description="Assets are formally managed throughout removal, transfers, and disposition",
                keywords=["asset disposal", "data sanitization", "decommissioning"],
                domain_tags=["data_security", "asset_management"],
                mapped_templates=["Asset Management Policy", "Data Disposal Policy"],
                priority="medium"
            ),
            CSFSubcategory(
                subcategory_id="PR.DS-11",
                function="Protect",
                category="Data Security",
                description="Backups of data are created, protected, maintained, and tested",
                keywords=["backup testing", "backup verification", "restore testing"],
                domain_tags=["data_security", "business_continuity"],
                mapped_templates=["Backup Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="PR.PS-01",
                function="Protect",
                category="Platform Security",
                description="Configuration management practices are established and applied",
                keywords=["configuration management", "baseline", "hardening"],
                domain_tags=["platform_security", "patch_management", "isms"],
                mapped_templates=["Configuration Management Policy", "Hardening Standards"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="PR.PS-02",
                function="Protect",
                category="Platform Security",
                description="Software is maintained, replaced, and removed commensurate with risk",
                keywords=["software maintenance", "patching", "updates", "EOL"],
                domain_tags=["platform_security", "patch_management"],
                mapped_templates=["Patch Management Policy", "Software Lifecycle Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="PR.PS-04",
                function="Protect",
                category="Platform Security",
                description="Log records are generated and made available for continuous monitoring",
                keywords=["logging", "audit logs", "log generation"],
                domain_tags=["platform_security", "incident_detection"],
                mapped_templates=["Log Management Policy", "Security Monitoring Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="PR.IR-01",
                function="Protect",
                category="Technology Infrastructure Resilience",
                description="Networks and environments are protected from unauthorized logical access and usage",
                keywords=["network access control", "network segmentation", "firewall"],
                domain_tags=["network_security", "isms"],
                mapped_templates=["Network Security Policy", "Firewall Policy"],
                priority="critical"
            ),
            
            # DETECT (DE) - 5 subcategories
            CSFSubcategory(
                subcategory_id="DE.AE-01",
                function="Detect",
                category="Adverse Event Analysis",
                description="Potentially adverse events are analyzed to better understand associated activities",
                keywords=["event analysis", "log analysis", "security events"],
                domain_tags=["incident_detection", "isms"],
                mapped_templates=["Security Monitoring Policy", "Log Management Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="DE.AE-02",
                function="Detect",
                category="Adverse Event Analysis",
                description="Potentially adverse events are analyzed to understand attack targets and methods",
                keywords=["threat analysis", "attack analysis", "TTPs"],
                domain_tags=["incident_detection", "threat_management"],
                mapped_templates=["Incident Response Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="DE.CM-01",
                function="Detect",
                category="Continuous Monitoring",
                description="Networks and network services are monitored to find potentially adverse events",
                keywords=["network monitoring", "IDS", "IPS", "network security"],
                domain_tags=["incident_detection", "network_security"],
                mapped_templates=["Security Monitoring Policy", "Network Security Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="DE.CM-04",
                function="Detect",
                category="Continuous Monitoring",
                description="Malicious code is detected",
                keywords=["malware detection", "antivirus", "endpoint protection"],
                domain_tags=["incident_detection", "platform_security"],
                mapped_templates=["Malware Protection Policy", "Endpoint Security Policy"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="DE.CM-08",
                function="Detect",
                category="Continuous Monitoring",
                description="Vulnerability scans are performed",
                keywords=["vulnerability scanning", "security scanning", "assessment"],
                domain_tags=["vulnerability_management", "patch_management"],
                mapped_templates=["Vulnerability Management Policy"],
                priority="high"
            ),
            
            # RESPOND (RS) - 4 subcategories
            CSFSubcategory(
                subcategory_id="RS.MA-01",
                function="Respond",
                category="Incident Management",
                description="The incident response plan is executed in coordination with relevant third parties once an incident is declared",
                keywords=["incident response", "incident handling", "incident management"],
                domain_tags=["incident_response", "isms"],
                mapped_templates=["Incident Response Policy", "Incident Response Plan"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="RS.MA-02",
                function="Respond",
                category="Incident Management",
                description="Incident reports are triaged and validated",
                keywords=["incident triage", "incident validation", "incident classification"],
                domain_tags=["incident_response"],
                mapped_templates=["Incident Response Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="RS.AN-01",
                function="Respond",
                category="Incident Analysis",
                description="Investigations are conducted to ensure effective response and support forensics and recovery activities",
                keywords=["incident investigation", "forensics", "root cause analysis"],
                domain_tags=["incident_response"],
                mapped_templates=["Incident Response Policy", "Forensics Policy"],
                priority="high"
            ),
            CSFSubcategory(
                subcategory_id="RS.MI-01",
                function="Respond",
                category="Incident Mitigation",
                description="Incidents are contained",
                keywords=["containment", "incident containment", "isolation"],
                domain_tags=["incident_response"],
                mapped_templates=["Incident Response Policy"],
                priority="critical"
            ),
            
            # RECOVER (RC) - 3 subcategories
            CSFSubcategory(
                subcategory_id="RC.RP-01",
                function="Recover",
                category="Recovery Planning",
                description="The recovery portion of the incident response plan is executed once initiated from the incident response process",
                keywords=["recovery", "restoration", "business continuity"],
                domain_tags=["recovery", "business_continuity"],
                mapped_templates=["Business Continuity Policy", "Disaster Recovery Plan"],
                priority="critical"
            ),
            CSFSubcategory(
                subcategory_id="RC.CO-01",
                function="Recover",
                category="Recovery Communications",
                description="Public relations are managed during and after an incident",
                keywords=["public relations", "communications", "reputation management"],
                domain_tags=["recovery", "incident_response"],
                mapped_templates=["Incident Response Policy", "Communications Policy"],
                priority="medium"
            ),
            CSFSubcategory(
                subcategory_id="RC.IM-01",
                function="Recover",
                category="Improvements",
                description="Recovery activities are improved based on lessons learned",
                keywords=["lessons learned", "continuous improvement", "post-incident review"],
                domain_tags=["recovery", "incident_response"],
                mapped_templates=["Incident Response Policy", "Continuous Improvement"],
                priority="medium"
            ),
        ]
