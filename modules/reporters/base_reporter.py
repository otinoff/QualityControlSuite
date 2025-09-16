#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base Reporter Class
Abstract base class for all report generators
"""

from abc import ABC, abstractmethod
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class BaseReporter(ABC):
    """
    Abstract base class for report generation.
    All reporters should inherit from this class.
    """
    
    def __init__(self):
        """Initialize reporter."""
        self.report_format = "base"
    
    @abstractmethod
    def generate_report(self, results: Dict[str, Any], output_path: str) -> bool:
        """
        Generate report from QC results.
        
        Args:
            results: QC results dictionary
            output_path: Path to save report
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    def _format_metric_name(self, name: str) -> str:
        """
        Format metric name for display.
        
        Args:
            name: Metric name
            
        Returns:
            Formatted metric name
        """
        name_map = {
            'total_reads': 'Total Reads',
            'total_sequences': 'Total Sequences',
            'mean_quality': 'Mean Quality Score',
            'gc_content': 'GC Content (%)',
            'mean_read_length': 'Mean Read Length',
            'min_read_length': 'Min Read Length',
            'max_read_length': 'Max Read Length',
            'n_percentage': 'N Percentage (%)',
            'total_bases': 'Total Bases',
            'mapped_reads': 'Mapped Reads',
            'unmapped_reads': 'Unmapped Reads',
            'mean_coverage': 'Mean Coverage',
            'total_variants': 'Total Variants',
            'snp_count': 'SNP Count',
            'indel_count': 'Indel Count',
            'mean_variant_quality': 'Mean Variant Quality',
            'file_size_mb': 'File Size (MB)'
        }
        return name_map.get(name, name.replace('_', ' ').title())