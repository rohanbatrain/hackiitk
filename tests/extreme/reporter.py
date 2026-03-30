"""
Test Reporter for Extreme Testing Framework

This module generates comprehensive test reports in multiple formats
(HTML, JSON, JUnit XML).
"""

import json
from typing import Dict, Any
from pathlib import Path
from datetime import datetime

from .models import TestReport, TestStatus


class ExtremeTestReporter:
    """Generates comprehensive test reports."""
    
    def __init__(self, output_dir: str = "test_outputs/extreme"):
        """
        Initialize test reporter.
        
        Args:
            output_dir: Directory for report output
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, report: TestReport) -> Dict[str, str]:
        """
        Generate comprehensive test report in multiple formats.
        
        Args:
            report: TestReport to generate from
            
        Returns:
            Dictionary mapping format to file path
        """
        report_files = {}
        
        # Generate JSON report
        json_path = self._generate_json_report(report)
        report_files['json'] = str(json_path)
        
        # Generate HTML report
        html_path = self._generate_html_report(report)
        report_files['html'] = str(html_path)
        
        # Generate JUnit XML report
        xml_path = self._generate_junit_xml(report)
        report_files['junit_xml'] = str(xml_path)
        
        return report_files
    
    def _generate_json_report(self, report: TestReport) -> Path:
        """Generate JSON report."""
        timestamp = report.execution_date.strftime('%Y%m%d_%H%M%S')
        json_file = self.output_dir / f"test_report_{timestamp}.json"
        
        with open(json_file, 'w') as f:
            json.dump(report.to_dict(), f, indent=2)
        
        return json_file
    
    def _generate_html_report(self, report: TestReport) -> Path:
        """Generate HTML report."""
        timestamp = report.execution_date.strftime('%Y%m%d_%H%M%S')
        html_file = self.output_dir / f"test_report_{timestamp}.html"
        
        # Calculate pass rate
        pass_rate = (report.passed / report.total_tests * 100) if report.total_tests > 0 else 0
        
        html_content = f"""<!DOCTYPE html>
<html>
<head>
    <title>Extreme Testing Report - {report.execution_date.strftime('%Y-%m-%d %H:%M:%S')}</title>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background-color: white;
            padding: 20px;
            box-shadow: 0 0 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        h2 {{
            color: #555;
            margin-top: 30px;
        }}
        .summary {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 20px 0;
        }}
        .metric {{
            background-color: #f9f9f9;
            padding: 15px;
            border-radius: 5px;
            border-left: 4px solid #4CAF50;
        }}
        .metric.failed {{
            border-left-color: #f44336;
        }}
        .metric.skipped {{
            border-left-color: #ff9800;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
        }}
        .metric-value {{
            font-size: 32px;
            font-weight: bold;
            color: #333;
        }}
        .pass-rate {{
            font-size: 48px;
            font-weight: bold;
            color: {'#4CAF50' if pass_rate >= 95 else '#ff9800' if pass_rate >= 80 else '#f44336'};
            text-align: center;
            margin: 20px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #4CAF50;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .status-pass {{
            color: #4CAF50;
            font-weight: bold;
        }}
        .status-fail {{
            color: #f44336;
            font-weight: bold;
        }}
        .status-skip {{
            color: #ff9800;
            font-weight: bold;
        }}
        .status-error {{
            color: #9c27b0;
            font-weight: bold;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Extreme Testing Framework - Test Report</h1>
        <p><strong>Execution Date:</strong> {report.execution_date.strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Duration:</strong> {report.duration_seconds:.2f} seconds</p>
        
        <div class="pass-rate">{pass_rate:.1f}% Pass Rate</div>
        
        <h2>Executive Summary</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-label">Total Tests</div>
                <div class="metric-value">{report.total_tests}</div>
            </div>
            <div class="metric">
                <div class="metric-label">Passed</div>
                <div class="metric-value">{report.passed}</div>
            </div>
            <div class="metric failed">
                <div class="metric-label">Failed</div>
                <div class="metric-value">{report.failed}</div>
            </div>
            <div class="metric skipped">
                <div class="metric-label">Skipped</div>
                <div class="metric-value">{report.skipped}</div>
            </div>
            <div class="metric failed">
                <div class="metric-label">Errors</div>
                <div class="metric-value">{report.errors}</div>
            </div>
        </div>
        
        <h2>Category Results</h2>
        <table>
            <thead>
                <tr>
                    <th>Category</th>
                    <th>Total</th>
                    <th>Passed</th>
                    <th>Failed</th>
                    <th>Skipped</th>
                    <th>Errors</th>
                    <th>Duration (s)</th>
                </tr>
            </thead>
            <tbody>
"""
        
        for category, cat_report in report.category_results.items():
            html_content += f"""
                <tr>
                    <td><strong>{category}</strong></td>
                    <td>{cat_report.total_tests}</td>
                    <td class="status-pass">{cat_report.passed}</td>
                    <td class="status-fail">{cat_report.failed}</td>
                    <td class="status-skip">{cat_report.skipped}</td>
                    <td class="status-error">{cat_report.errors}</td>
                    <td>{cat_report.duration_seconds:.2f}</td>
                </tr>
"""
        
        html_content += """
            </tbody>
        </table>
        
        <h2>Breaking Points</h2>
"""
        
        if report.breaking_points:
            html_content += """
        <table>
            <thead>
                <tr>
                    <th>Dimension</th>
                    <th>Maximum Value</th>
                    <th>Failure Mode</th>
                </tr>
            </thead>
            <tbody>
"""
            for bp in report.breaking_points:
                html_content += f"""
                <tr>
                    <td>{bp.dimension}</td>
                    <td>{bp.maximum_viable_value}</td>
                    <td>{bp.failure_mode.value}</td>
                </tr>
"""
            html_content += """
            </tbody>
        </table>
"""
        else:
            html_content += "<p>No breaking points identified.</p>"
        
        html_content += """
        <h2>Artifacts</h2>
        <p><strong>Artifacts Directory:</strong> {}</p>
    </div>
</body>
</html>
""".format(report.artifacts_dir)
        
        with open(html_file, 'w') as f:
            f.write(html_content)
        
        return html_file
    
    def _generate_junit_xml(self, report: TestReport) -> Path:
        """Generate JUnit XML report for CI integration."""
        timestamp = report.execution_date.strftime('%Y%m%d_%H%M%S')
        xml_file = self.output_dir / f"test_report_{timestamp}.xml"
        
        xml_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<testsuites name="Extreme Testing Framework" tests="{report.total_tests}" failures="{report.failed}" errors="{report.errors}" skipped="{report.skipped}" time="{report.duration_seconds:.3f}">
"""
        
        for category, cat_report in report.category_results.items():
            xml_content += f"""  <testsuite name="{category}" tests="{cat_report.total_tests}" failures="{cat_report.failed}" errors="{cat_report.errors}" skipped="{cat_report.skipped}" time="{cat_report.duration_seconds:.3f}">
"""
            
            for test_result in cat_report.test_results:
                xml_content += f"""    <testcase name="{test_result.test_id}" classname="{category}" time="{test_result.duration_seconds:.3f}">
"""
                
                if test_result.status == TestStatus.FAIL:
                    xml_content += f"""      <failure message="{test_result.error_message or 'Test failed'}">{test_result.error_message or 'Test failed'}</failure>
"""
                elif test_result.status == TestStatus.ERROR:
                    xml_content += f"""      <error message="{test_result.error_message or 'Test error'}">{test_result.error_message or 'Test error'}</error>
"""
                elif test_result.status == TestStatus.SKIP:
                    xml_content += f"""      <skipped message="{test_result.error_message or 'Test skipped'}" />
"""
                
                xml_content += """    </testcase>
"""
            
            xml_content += """  </testsuite>
"""
        
        xml_content += """</testsuites>
"""
        
        with open(xml_file, 'w') as f:
            f.write(xml_content)
        
        return xml_file
