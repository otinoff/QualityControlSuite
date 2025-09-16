#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base QC Engine Class
Abstract base class for all quality control engines
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class BaseQCEngine(ABC):
    """
    Abstract base class for quality control engines.
    Calculates metrics from existing data WITHOUT processing.
    """
    
    def __init__(self):
        """Initialize QC engine."""
        self.metrics: Dict[str, Any] = {}
        
    @abstractmethod
    def calculate_metrics(self, filepath: str) -> Dict[str, Any]:
        """
        Calculate quality metrics from file.
        
        IMPORTANT: This method should ONLY read and calculate metrics
        from existing data. It should NOT perform any processing like
        alignment or variant calling.
        
        Args:
            filepath: Path to the file to analyze
            
        Returns:
            Dictionary containing calculated metrics
        """
        pass
    
    @abstractmethod
    def check_thresholds(self, metrics: Dict[str, Any], 
                        thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check metrics against quality thresholds.
        
        Args:
            metrics: Calculated metrics
            thresholds: Quality thresholds
            
        Returns:
            Dictionary with QC status and failed checks
        """
        pass
    
    def get_file_size_mb(self, filepath: str) -> float:
        """Get file size in megabytes."""
        from pathlib import Path
        return Path(filepath).stat().st_size / (1024 * 1024)
    
    def check_single_threshold(self, 
                              metric_value: float,
                              threshold_value: float,
                              comparison: str = 'min') -> bool:
        """
        Check single metric against threshold.
        
        Args:
            metric_value: Calculated metric value
            threshold_value: Threshold value
            comparison: 'min' or 'max'
            
        Returns:
            True if metric passes threshold
        """
        if comparison == 'min':
            return metric_value >= threshold_value
        elif comparison == 'max':
            return metric_value <= threshold_value
        else:
            raise ValueError(f"Invalid comparison type: {comparison}")