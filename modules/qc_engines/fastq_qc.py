#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASTQ QC Engine
Calculates quality metrics for FASTQ files WITHOUT processing
"""

import gzip
from pathlib import Path
from typing import Dict, Any
import logging
from .base_qc import BaseQCEngine

logger = logging.getLogger(__name__)


class FastqQCEngine(BaseQCEngine):
    """
    Quality control engine for FASTQ files.
    Calculates metrics from existing sequences WITHOUT alignment.
    """
    
    def __init__(self, sample_size: int = 10000):
        """
        Initialize FASTQ QC engine.
        
        Args:
            sample_size: Number of reads to sample for metrics
        """
        super().__init__()
        self.sample_size = sample_size
    
    def calculate_metrics(self, filepath: str) -> Dict[str, Any]:
        """
        Calculate quality metrics from FASTQ file.
        
        NO alignment, NO processing, ONLY metrics from existing data!
        
        Args:
            filepath: Path to FASTQ file
            
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {
            'file_size_mb': self.get_file_size_mb(filepath),
            'total_reads': 0,
            'avg_read_length': 0,
            'min_read_length': float('inf'),
            'max_read_length': 0,
            'avg_quality_score': 0,
            'n_percentage': 0,
            'gc_content': 0,
            'q20_percentage': 0,
            'q30_percentage': 0
        }
        
        # Check if file is gzipped
        is_gzipped = filepath.endswith('.gz')
        
        try:
            if is_gzipped:
                file_handle = gzip.open(filepath, 'rt', encoding='utf-8', errors='replace')
            else:
                file_handle = open(filepath, 'r', encoding='utf-8', errors='replace')
            
            total_length = 0
            total_quality = 0
            total_n_count = 0
            total_gc_count = 0
            total_bases = 0
            total_q20 = 0
            total_q30 = 0
            reads_analyzed = 0
            
            while reads_analyzed < self.sample_size:
                # Read FASTQ record (4 lines)
                header = file_handle.readline()
                if not header:
                    break
                    
                sequence = file_handle.readline().strip()
                separator = file_handle.readline()
                quality = file_handle.readline().strip()
                
                if not all([sequence, separator, quality]):
                    break
                
                # Calculate metrics for this read
                read_length = len(sequence)
                total_length += read_length
                
                # Update min/max read length
                metrics['min_read_length'] = min(metrics['min_read_length'], read_length)
                metrics['max_read_length'] = max(metrics['max_read_length'], read_length)
                
                # Count N bases
                n_count = sequence.upper().count('N')
                total_n_count += n_count
                
                # Count GC content
                gc_count = sequence.upper().count('G') + sequence.upper().count('C')
                total_gc_count += gc_count
                
                # Calculate quality scores (Phred33 encoding)
                for qual_char in quality:
                    qual_score = ord(qual_char) - 33
                    total_quality += qual_score
                    if qual_score >= 20:
                        total_q20 += 1
                    if qual_score >= 30:
                        total_q30 += 1
                
                total_bases += read_length
                reads_analyzed += 1
            
            file_handle.close()
            
            # Calculate final metrics
            if reads_analyzed > 0:
                metrics['total_reads'] = reads_analyzed
                metrics['avg_read_length'] = total_length / reads_analyzed
                metrics['n_percentage'] = (total_n_count / total_bases) * 100 if total_bases > 0 else 0
                metrics['gc_content'] = (total_gc_count / total_bases) * 100 if total_bases > 0 else 0
                metrics['avg_quality_score'] = total_quality / total_bases if total_bases > 0 else 0
                metrics['q20_percentage'] = (total_q20 / total_bases) * 100 if total_bases > 0 else 0
                metrics['q30_percentage'] = (total_q30 / total_bases) * 100 if total_bases > 0 else 0
            
            # Fix min_read_length if no reads were found
            if metrics['min_read_length'] == float('inf'):
                metrics['min_read_length'] = 0
                
            logger.info(f"Calculated metrics for {reads_analyzed} reads from {filepath}")
            
        except Exception as e:
            logger.error(f"Error calculating FASTQ metrics: {str(e)}")
            metrics['error'] = str(e)
        
        return metrics
    
    def check_thresholds(self, metrics: Dict[str, Any], 
                        thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check FASTQ metrics against thresholds.
        
        Args:
            metrics: Calculated metrics
            thresholds: Quality thresholds
            
        Returns:
            QC status and failed checks
        """
        qc_status = 'passed'
        failed_checks = []
        
        # Check minimum quality score
        if 'min_quality_score' in thresholds:
            if metrics.get('avg_quality_score', 0) < thresholds['min_quality_score']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Average quality score ({metrics['avg_quality_score']:.1f}) < "
                    f"threshold ({thresholds['min_quality_score']})"
                )
        
        # Check minimum read length
        if 'min_read_length' in thresholds:
            if metrics.get('min_read_length', 0) < thresholds['min_read_length']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Minimum read length ({metrics['min_read_length']}) < "
                    f"threshold ({thresholds['min_read_length']})"
                )
        
        # Check maximum N percentage
        if 'max_n_percentage' in thresholds:
            if metrics.get('n_percentage', 100) > thresholds['max_n_percentage']:
                qc_status = 'failed'
                failed_checks.append(
                    f"N percentage ({metrics['n_percentage']:.1f}%) > "
                    f"threshold ({thresholds['max_n_percentage']}%)"
                )
        
        # Check GC content range
        if 'min_gc_content' in thresholds:
            if metrics.get('gc_content', 0) < thresholds['min_gc_content']:
                qc_status = 'warning'
                failed_checks.append(
                    f"GC content ({metrics['gc_content']:.1f}%) < "
                    f"threshold ({thresholds['min_gc_content']}%)"
                )
        
        if 'max_gc_content' in thresholds:
            if metrics.get('gc_content', 100) > thresholds['max_gc_content']:
                qc_status = 'warning'
                failed_checks.append(
                    f"GC content ({metrics['gc_content']:.1f}%) > "
                    f"threshold ({thresholds['max_gc_content']}%)"
                )
        
        return {
            'status': qc_status,
            'failed_checks': failed_checks
        }