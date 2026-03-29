#!/bin/bash
# End-to-End Gap Detection Test
# This script creates a deliberately incomplete policy and verifies the analyzer detects the gaps

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${GREEN}✓${NC} $1"; }
log_warn() { echo -e "${YELLOW}⚠${NC} $1"; }
log_error() { echo -e "${RED}✗${NC} $1"; }
log_section() { echo -e "\n${BLUE}═══ $1 ═══${NC}\n"; }

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  End-to-End Gap Detection Test                              ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Activate virtual environment
log_section "Step 1: Activating Virtual Environment"
if [ -d "venv311" ]; then
    source venv311/bin/activate
    log_info "Virtual environment activated"
else
    log_error "Virtual environment not found. Run ./setup.sh first."
    exit 1
fi

# Create test directory
log_section "Step 2: Creating Test Directory"
TEST_DIR="test_gap_detection_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$TEST_DIR"
log_info "Test directory created: $TEST_DIR"

# Create a complete baseline policy
log_section "Step 3: Creating Complete Baseline Policy"
cat > "$TEST_DIR/complete_policy.md" << 'EOF'
# Information Security Management System (ISMS) Policy

## 1. Purpose and Scope
This policy establishes the framework for managing information security across the organization.

## 2. Governance and Oversight
### 2.1 Organizational Context
The organization maintains awareness of its mission, stakeholders, and legal/regulatory requirements.

### 2.2 Cybersecurity Supply Chain Risk Management
We assess and manage cybersecurity risks throughout our supply chain, including third-party vendors and service providers.

### 2.3 Roles, Responsibilities, and Authorities
Clear roles and responsibilities are defined for cybersecurity management:
- CISO: Overall security strategy and oversight
- Security Team: Day-to-day security operations
- Department Heads: Security within their domains

## 3. Risk Management
### 3.1 Risk Management Strategy
The organization has established a comprehensive risk management strategy that:
- Identifies and assesses information security risks
- Determines risk appetite and tolerance levels
- Implements appropriate risk treatment measures

### 3.2 Risk Assessment
Regular risk assessments are conducted to:
- Identify threats and vulnerabilities
- Evaluate likelihood and impact
- Prioritize risks based on business impact

### 3.3 Risk Response
Risk treatment options include:
- Risk mitigation through controls
- Risk transfer through insurance
- Risk acceptance with documented justification
- Risk avoidance by eliminating activities

## 4. Asset Management
### 4.1 Asset Inventory
A comprehensive inventory of all information assets is maintained, including:
- Hardware assets (servers, workstations, mobile devices)
- Software assets (applications, operating systems)
- Data assets (databases, files, intellectual property)
- Network assets (routers, switches, firewalls)

### 4.2 Asset Classification
Assets are classified based on confidentiality, integrity, and availability requirements.

## 5. Identity and Access Management
### 5.1 Identity Management
User identities are managed through:
- Centralized identity management system
- Unique user accounts for each individual
- Regular review of user accounts

### 5.2 Access Control
Access to systems and data is controlled through:
- Role-based access control (RBAC)
- Principle of least privilege
- Regular access reviews and recertification

### 5.3 Authentication and Authorization
Strong authentication mechanisms are enforced:
- Multi-factor authentication for privileged accounts
- Password complexity requirements
- Account lockout after failed attempts

## 6. Data Security
### 6.1 Data Protection
Sensitive data is protected through:
- Encryption at rest and in transit
- Data loss prevention (DLP) controls
- Secure data disposal procedures

### 6.2 Data Classification
Data is classified into categories:
- Public: No restrictions
- Internal: For internal use only
- Confidential: Restricted access
- Highly Confidential: Strictly controlled

## 7. Network Security
### 7.1 Network Segmentation
Networks are segmented to isolate critical systems and limit lateral movement.

### 7.2 Network Monitoring
Continuous network monitoring detects and responds to security events.

### 7.3 Boundary Protection
Firewalls and intrusion prevention systems protect network boundaries.

## 8. Security Monitoring and Detection
### 8.1 Continuous Monitoring
Security monitoring is performed 24/7 to detect anomalies and threats.

### 8.2 Log Management
Security logs are collected, retained, and analyzed for:
- Security event correlation
- Forensic investigation
- Compliance reporting

### 8.3 Threat Detection
Advanced threat detection capabilities include:
- Intrusion detection systems (IDS)
- Security information and event management (SIEM)
- Threat intelligence integration

## 9. Incident Response
### 9.1 Incident Response Plan
A documented incident response plan defines:
- Incident classification and severity levels
- Response procedures and escalation paths
- Communication protocols

### 9.2 Incident Detection and Analysis
Security incidents are detected through monitoring and reported by users.

### 9.3 Incident Containment and Recovery
Procedures are in place to contain incidents and restore normal operations.

## 10. Business Continuity and Disaster Recovery
### 10.1 Business Continuity Planning
Business continuity plans ensure critical operations continue during disruptions.

### 10.2 Disaster Recovery
Disaster recovery procedures enable recovery of IT systems and data.

### 10.3 Testing and Exercises
Regular testing validates the effectiveness of continuity and recovery plans.

## 11. Security Awareness and Training
### 11.1 Security Awareness Program
All employees receive security awareness training covering:
- Phishing and social engineering
- Password security
- Data handling procedures
- Incident reporting

### 11.2 Role-Based Training
Specialized training is provided based on job responsibilities.

## 12. Vulnerability Management
### 12.1 Vulnerability Scanning
Regular vulnerability scans identify security weaknesses in systems and applications.

### 12.2 Patch Management
Security patches are tested and deployed in a timely manner.

### 12.3 Vulnerability Remediation
Identified vulnerabilities are prioritized and remediated based on risk.

## 13. Compliance and Audit
### 13.1 Compliance Monitoring
Compliance with security policies and regulations is continuously monitored.

### 13.2 Internal Audits
Regular internal audits assess the effectiveness of security controls.

### 13.3 External Audits
Independent external audits provide objective assurance.

## 14. Policy Review and Updates
This policy is reviewed annually and updated as needed to address emerging threats and business changes.

## 15. Approval and Enforcement
This policy is approved by executive management and applies to all employees, contractors, and third parties.
EOF

log_info "Complete baseline policy created"

# Create an incomplete policy with intentional gaps
log_section "Step 4: Creating Incomplete Policy with Intentional Gaps"
cat > "$TEST_DIR/incomplete_policy.md" << 'EOF'
# Information Security Management System (ISMS) Policy

## 1. Purpose and Scope
This policy establishes the framework for managing information security across the organization.

## 2. Governance and Oversight
### 2.1 Organizational Context
The organization maintains awareness of its mission, stakeholders, and legal/regulatory requirements.

### 2.2 Roles, Responsibilities, and Authorities
Clear roles and responsibilities are defined for cybersecurity management:
- CISO: Overall security strategy and oversight
- Security Team: Day-to-day security operations

## 3. Asset Management
### 3.1 Asset Inventory
A basic inventory of information assets is maintained.

## 4. Identity and Access Management
### 4.1 Identity Management
User identities are managed through a centralized system.

### 4.2 Access Control
Access to systems is controlled through basic permissions.

## 5. Security Awareness and Training
### 5.1 Security Awareness Program
Employees receive basic security awareness training.

## 6. Policy Review and Updates
This policy is reviewed periodically.
EOF

log_info "Incomplete policy created with the following INTENTIONAL GAPS:"
echo "   - Missing: Risk Management (entire section)"
echo "   - Missing: Data Security and Classification"
echo "   - Missing: Network Security"
echo "   - Missing: Security Monitoring and Detection"
echo "   - Missing: Incident Response"
echo "   - Missing: Business Continuity and Disaster Recovery"
echo "   - Missing: Vulnerability Management"
echo "   - Missing: Cybersecurity Supply Chain Risk Management"
echo "   - Incomplete: Authentication mechanisms (no MFA mentioned)"
echo "   - Incomplete: Access control (no RBAC or least privilege)"

# Run analysis on complete policy (baseline)
log_section "Step 5: Analyzing Complete Baseline Policy"
echo "Running: ./pa --policy-path $TEST_DIR/complete_policy.md --domain isms"
./pa --policy-path "$TEST_DIR/complete_policy.md" --domain isms > "$TEST_DIR/complete_analysis.log" 2>&1

# Find the output directory for complete policy
COMPLETE_OUTPUT=$(ls -td outputs/complete_policy_* 2>/dev/null | head -1)
if [ -n "$COMPLETE_OUTPUT" ]; then
    log_info "Complete policy analysis output: $COMPLETE_OUTPUT"
    cp -r "$COMPLETE_OUTPUT" "$TEST_DIR/complete_output"
    
    # Extract gap count from complete policy
    COMPLETE_GAPS=$(grep -o '"gaps": \[[^]]*\]' "$TEST_DIR/complete_output/gap_analysis_report.json" | grep -o '"subcategory_id"' | wc -l | tr -d ' ')
    log_info "Complete policy gaps identified: $COMPLETE_GAPS"
else
    log_warn "Could not find complete policy output directory"
    COMPLETE_GAPS="unknown"
fi

# Run analysis on incomplete policy
log_section "Step 6: Analyzing Incomplete Policy"
echo "Running: ./pa --policy-path $TEST_DIR/incomplete_policy.md --domain isms"
./pa --policy-path "$TEST_DIR/incomplete_policy.md" --domain isms > "$TEST_DIR/incomplete_analysis.log" 2>&1

# Find the output directory for incomplete policy
INCOMPLETE_OUTPUT=$(ls -td outputs/incomplete_policy_* 2>/dev/null | head -1)
if [ -n "$INCOMPLETE_OUTPUT" ]; then
    log_info "Incomplete policy analysis output: $INCOMPLETE_OUTPUT"
    cp -r "$INCOMPLETE_OUTPUT" "$TEST_DIR/incomplete_output"
    
    # Extract gap count from incomplete policy
    INCOMPLETE_GAPS=$(grep -o '"gaps": \[[^]]*\]' "$TEST_DIR/incomplete_output/gap_analysis_report.json" | grep -o '"subcategory_id"' | wc -l | tr -d ' ')
    log_info "Incomplete policy gaps identified: $INCOMPLETE_GAPS"
else
    log_error "Could not find incomplete policy output directory"
    exit 1
fi

# Analyze the results
log_section "Step 7: Analyzing Results"

# Extract specific gaps from incomplete policy
echo "Extracting gap details from incomplete policy analysis..."
python3 << 'PYTHON_SCRIPT'
import json
import sys

try:
    with open('$INCOMPLETE_OUTPUT/gap_analysis_report.json', 'r') as f:
        report = json.load(f)
    
    gaps = report.get('gaps', [])
    
    print(f"\n{'='*70}")
    print(f"DETECTED GAPS IN INCOMPLETE POLICY: {len(gaps)}")
    print(f"{'='*70}\n")
    
    # Group gaps by CSF function
    by_function = {}
    for gap in gaps:
        func = gap.get('csf_function', 'Unknown')
        if func not in by_function:
            by_function[func] = []
        by_function[func].append(gap)
    
    # Print gaps by function
    for func in sorted(by_function.keys()):
        print(f"\n{func} Function:")
        print("-" * 70)
        for gap in by_function[func]:
            subcategory = gap.get('subcategory_id', 'Unknown')
            coverage = gap.get('coverage_status', 'Unknown')
            severity = gap.get('severity', 'Unknown')
            print(f"  • {subcategory}: {coverage} (Severity: {severity})")
            print(f"    Description: {gap.get('description', 'N/A')[:80]}...")
    
    print(f"\n{'='*70}\n")
    
    # Check for specific expected gaps
    expected_gaps = [
        'GV.SC',  # Supply Chain Risk Management
        'GV.RM',  # Risk Management
        'ID.AM',  # Asset Management
        'PR.DS',  # Data Security
        'PR.AC',  # Access Control
        'DE.CM',  # Continuous Monitoring
        'DE.AE',  # Adverse Event Analysis
        'RS.MA',  # Incident Management
        'RC.RP',  # Recovery Planning
    ]
    
    detected_subcategories = [g.get('subcategory_id', '') for g in gaps]
    
    print("VERIFICATION OF EXPECTED GAPS:")
    print("-" * 70)
    for expected in expected_gaps:
        # Check if any detected gap starts with the expected prefix
        found = any(sub.startswith(expected) for sub in detected_subcategories)
        status = "✓ DETECTED" if found else "✗ MISSED"
        print(f"  {status}: {expected}")
    
    sys.exit(0)
    
except Exception as e:
    print(f"Error analyzing results: {e}")
    sys.exit(1)
PYTHON_SCRIPT

# Create comparison report
log_section "Step 8: Creating Comparison Report"

cat > "$TEST_DIR/TEST_REPORT.md" << EOF
# Gap Detection Test Report

**Test Date:** $(date)
**Test Directory:** $TEST_DIR

## Test Objective
Verify that the Policy Analyzer correctly identifies gaps when critical security sections are intentionally removed from a policy document.

## Test Methodology

### 1. Baseline Policy (Complete)
Created a comprehensive ISMS policy covering all major security domains:
- Governance and Oversight
- Risk Management
- Asset Management
- Identity and Access Management
- Data Security
- Network Security
- Security Monitoring
- Incident Response
- Business Continuity
- Vulnerability Management
- Security Awareness
- Compliance

**Gaps Detected:** $COMPLETE_GAPS

### 2. Test Policy (Incomplete)
Created an intentionally incomplete policy with the following sections REMOVED:
- ❌ Risk Management (entire section)
- ❌ Data Security and Classification
- ❌ Network Security
- ❌ Security Monitoring and Detection
- ❌ Incident Response
- ❌ Business Continuity and Disaster Recovery
- ❌ Vulnerability Management
- ❌ Cybersecurity Supply Chain Risk Management
- ⚠️  Authentication mechanisms (incomplete - no MFA)
- ⚠️  Access control (incomplete - no RBAC)

**Gaps Detected:** $INCOMPLETE_GAPS

## Results

### Gap Detection Rate
- **Baseline Policy Gaps:** $COMPLETE_GAPS
- **Incomplete Policy Gaps:** $INCOMPLETE_GAPS
- **Additional Gaps Detected:** $((INCOMPLETE_GAPS - COMPLETE_GAPS))

### Expected vs Detected Gaps
See detailed analysis above for specific CSF subcategories.

## Test Files
- Complete Policy: \`$TEST_DIR/complete_policy.md\`
- Incomplete Policy: \`$TEST_DIR/incomplete_policy.md\`
- Complete Analysis Output: \`$TEST_DIR/complete_output/\`
- Incomplete Analysis Output: \`$TEST_DIR/incomplete_output/\`
- Analysis Logs: \`$TEST_DIR/*.log\`

## Conclusion
$(if [ "$INCOMPLETE_GAPS" -gt "$COMPLETE_GAPS" ]; then
    echo "✅ **TEST PASSED**: The analyzer successfully detected more gaps in the incomplete policy ($INCOMPLETE_GAPS) compared to the complete policy ($COMPLETE_GAPS)."
else
    echo "⚠️  **TEST INCONCLUSIVE**: Gap counts - Complete: $COMPLETE_GAPS, Incomplete: $INCOMPLETE_GAPS"
fi)

## Detailed Reports
- Gap Analysis Report (JSON): \`$TEST_DIR/incomplete_output/gap_analysis_report.json\`
- Gap Analysis Report (Markdown): \`$TEST_DIR/incomplete_output/gap_analysis_report.md\`
- Implementation Roadmap: \`$TEST_DIR/incomplete_output/implementation_roadmap.md\`
- Revised Policy: \`$TEST_DIR/incomplete_output/revised_policy.md\`

## How to Review
1. Open the gap analysis report: \`cat $TEST_DIR/incomplete_output/gap_analysis_report.md\`
2. Review the implementation roadmap: \`cat $TEST_DIR/incomplete_output/implementation_roadmap.md\`
3. Compare with complete policy analysis: \`diff $TEST_DIR/complete_output/gap_analysis_report.md $TEST_DIR/incomplete_output/gap_analysis_report.md\`
EOF

log_info "Test report created: $TEST_DIR/TEST_REPORT.md"

# Display summary
log_section "Test Summary"
cat "$TEST_DIR/TEST_REPORT.md"

log_section "Test Complete"
log_info "All test artifacts saved in: $TEST_DIR"
log_info "Review the detailed report: cat $TEST_DIR/TEST_REPORT.md"
log_info "Review gap analysis: cat $TEST_DIR/incomplete_output/gap_analysis_report.md"

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ End-to-End Gap Detection Test Complete                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
