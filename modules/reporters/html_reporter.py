#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
HTML Reporter
Generates HTML format reports for QC results with visualization
"""

import logging
from typing import Dict, Any
from .base_reporter import BaseReporter

logger = logging.getLogger(__name__)


class HTMLReporter(BaseReporter):
    """
    HTML report generator for quality control results.
    """
    
    def __init__(self):
        """Initialize HTML reporter."""
        super().__init__()
        self.report_format = "html"
    
    def generate_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """
        Generate HTML report from QC results.
        
        Args:
            results: QC results dictionary
            output_path: Path to save HTML report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filename = results.get('filename', 'Unknown File')
            
            # Start HTML document
            html_content = [
                "<!DOCTYPE html>",
                "<html>",
                "<head>",
                "    <meta charset='UTF-8'>",
                "    <title>Quality Control Report</title>",
                "    <style>",
                "        body { font-family: Arial, sans-serif; margin: 20px; }",
                "        h1, h2, h3 { color: #2B5AA0; }",
                "        .header { background: linear-gradient(135deg, #2B5AA0 0%, #1B5E5E 100%); color: white; padding: 20px; border-radius: 8px; }",
                "        .section { margin: 20px 0; padding: 15px; border: 1px solid #ddd; border-radius: 5px; }",
                "        .metric { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #eee; }",
                "        .metric-name { font-weight: bold; }",
                "        .metric-value { color: #666; }",
                "        .status-pass { color: #28A745; font-weight: bold; }",
                "        .status-warning { color: #FD7E14; font-weight: bold; }",
                "        .status-fail { color: #DC3545; font-weight: bold; }",
                "        .error { color: #DC3545; background-color: #F8D7DA; padding: 10px; border-radius: 5px; margin: 10px 0; }",
                "        table { width: 100%; border-collapse: collapse; margin: 15px 0; }",
                "        th, td { padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }",
                "        th { background-color: #f2f2f2; }",
                "    </style>",
                "</head>",
                "<body>",
                f"    <div class='header'>",
                f"        <h1>🧬 Quality Control Report</h1>",
                f"        <p><strong>File:</strong> {filename}</p>",
                f"    </div>",
                ""
            ]
            
            # Add quality status
            quality_status = results.get('quality_status', 'UNKNOWN')
            status_class = {
                'PASS': 'status-pass',
                'WARNING': 'status-warning',
                'FAIL': 'status-fail'
            }.get(quality_status, '')
            
            html_content.extend([
                f"    <div class='section'>",
                f"        <h2>Quality Status</h2>",
                f"        <p class='{status_class}'>{quality_status}</p>",
                f"    </div>",
                ""
            ])
            
            # Add validation results
            if 'validation' in results:
                validation = results['validation']
                html_content.extend([
                    "    <div class='section'>",
                    "        <h2>Validation Results</h2>",
                    f"        <p><strong>Valid:</strong> {'Yes' if validation.get('valid', False) else 'No'}</p>"
                ])
                
                if 'format' in validation:
                    html_content.append(f"        <p><strong>Format:</strong> {validation['format']}</p>")
                
                if 'errors' in validation and validation['errors']:
                    html_content.append("        <h3>Errors:</h3>")
                    html_content.append("        <ul>")
                    for error in validation['errors']:
                        html_content.append(f"            <li class='error'>{error}</li>")
                    html_content.append("        </ul>")
                
                if 'warnings' in validation and validation['warnings']:
                    html_content.append("        <h3>Warnings:</h3>")
                    html_content.append("        <ul>")
                    for warning in validation['warnings']:
                        html_content.append(f"            <li>{warning}</li>")
                    html_content.append("        </ul>")
                
                html_content.extend([
                    "    </div>",
                    ""
                ])
            
            # Add QC metrics
            if 'metrics' in results and results['metrics']:
                html_content.extend([
                    "    <div class='section'>",
                    "        <h2>QC Metrics</h2>",
                    "        <table>",
                    "            <thead>",
                    "                <tr>",
                    "                    <th>Metric</th>",
                    "                    <th>Value</th>",
                    "                </tr>",
                    "            </thead>",
                    "            <tbody>"
                ])
                
                for key, value in results['metrics'].items():
                    formatted_name = self._format_metric_name(key)
                    formatted_value = self._format_metric_value(value)
                    html_content.append(f"                <tr>")
                    html_content.append(f"                    <td>{formatted_name}</td>")
                    html_content.append(f"                    <td>{formatted_value}</td>")
                    html_content.append(f"                </tr>")
                
                html_content.extend([
                    "            </tbody>",
                    "        </table>",
                    "    </div>",
                    ""
                ])
            
            # Close HTML document
            html_content.extend([
                "    <div style='margin-top: 30px; padding: 15px; background-color: #f8f9fa; border-radius: 5px;'>",
                "        <p><strong>Generated by:</strong> QualityControlSuite v1.0.0</p>",
                "        <p><strong>Date:</strong> " + self._get_current_date() + "</p>",
                "    </div>",
                "</body>",
                "</html>"
            ])
            
            # Write HTML report
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(html_content))
            
            logger.info(f"HTML report generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating HTML report: {str(e)}")
            return False
    
    def _format_metric_value(self, value) -> str:
        """Format metric value for display."""
        if isinstance(value, float):
            return f"{value:.2f}"
        elif isinstance(value, int):
            return f"{value:,}"
        else:
            return str(value)
    
    def _get_current_date(self) -> str:
        """Get current date as string."""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")