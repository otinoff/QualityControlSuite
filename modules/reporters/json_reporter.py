#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
JSON Reporter
Generates JSON format reports for QC results
"""

import json
import logging
from typing import Dict, Any
from .base_reporter import BaseReporter

logger = logging.getLogger(__name__)


class JSONReporter(BaseReporter):
    """
    JSON report generator for quality control results.
    """
    
    def __init__(self):
        """Initialize JSON reporter."""
        super().__init__()
        self.report_format = "json"
    
    def generate_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """
        Generate JSON report from QC results.
        
        Args:
            results: QC results dictionary
            output_path: Path to save JSON report
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Write JSON report
            with open(output_path, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            
            logger.info(f"JSON report generated: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating JSON report: {str(e)}")
            return False