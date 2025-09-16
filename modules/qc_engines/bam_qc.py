#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
BAM QC Engine
Calculates quality metrics for BAM/SAM files WITHOUT processing
"""

import logging
from typing import Dict, Any
from .base_qc import BaseQCEngine

logger = logging.getLogger(__name__)


class BamQCEngine(BaseQCEngine):
    """
    Quality control engine for BAM/SAM files.
    Calculates metrics from existing alignments WITHOUT additional processing.
    """
    
    def __init__(self, sample_size: int = 1000):
        """
        Initialize BAM QC engine.
        
        Args:
            sample_size: Number of reads to sample for metrics
        """
        super().__init__()
        self.sample_size = sample_size
    
    def calculate_metrics(self, filepath: str) -> Dict[str, Any]:
        """
        Calculate quality metrics from BAM/SAM file.
        
        NO alignment, NO processing, ONLY metrics from existing data!
        
        Args:
            filepath: Path to BAM/SAM file
            
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {
            'file_size_mb': self.get_file_size_mb(filepath),
            'total_reads': 0,
            'mapped_reads': 0,
            'unmapped_reads': 0,
            'duplicate_reads': 0,
            'properly_paired': 0,
            'mean_mapping_quality': 0,
            'mean_coverage': 0,
            'insert_size_mean': 0,
            'insert_size_std': 0
        }
        
        try:
            import pysam
            
            # Determine file type from extension
            file_ext = filepath.lower().split('.')[-1]
            
            # Open file
            if file_ext == 'bam':
                samfile = pysam.AlignmentFile(filepath, "rb")
            elif file_ext in ['sam', 'cram']:
                samfile = pysam.AlignmentFile(filepath, "r")
            else:
                raise ValueError(f"Unsupported file type: {file_ext}")
            
            # Statistics counters
            total_reads = 0
            mapped_reads = 0
            unmapped_reads = 0
            duplicate_reads = 0
            properly_paired = 0
            total_mapq = 0
            read_lengths = []
            
            # Process reads
            for read in samfile.fetch(until_eof=True):
                if total_reads >= self.sample_size:
                    break
                    
                total_reads += 1
                read_lengths.append(read.query_length)
                
                if read.is_unmapped:
                    unmapped_reads += 1
                else:
                    mapped_reads += 1
                    total_mapq += read.mapping_quality
                    
                    if read.is_duplicate:
                        duplicate_reads += 1
                    
                    if read.is_proper_pair:
                        properly_paired += 1
            
            # Calculate final metrics
            metrics['total_reads'] = total_reads
            metrics['mapped_reads'] = mapped_reads
            metrics['unmapped_reads'] = unmapped_reads
            metrics['duplicate_reads'] = duplicate_reads
            metrics['properly_paired'] = properly_paired
            
            if mapped_reads > 0:
                metrics['mean_mapping_quality'] = total_mapq / mapped_reads
            
            if read_lengths:
                metrics['mean_read_length'] = sum(read_lengths) / len(read_lengths)
            
            # Calculate percentages
            if total_reads > 0:
                metrics['mapped_percentage'] = (mapped_reads / total_reads) * 100
                metrics['unmapped_percentage'] = (unmapped_reads / total_reads) * 100
                metrics['duplicate_percentage'] = (duplicate_reads / total_reads) * 100
                metrics['properly_paired_percentage'] = (properly_paired / total_reads) * 100
            
            samfile.close()
            logger.info(f"Calculated BAM metrics for {total_reads} reads from {filepath}")
            
        except ImportError:
            logger.error("pysam library not installed")
            metrics['error'] = "pysam library not installed"
        except Exception as e:
            logger.error(f"Error calculating BAM metrics: {str(e)}")
            metrics['error'] = str(e)
        
        return metrics
    
    def check_thresholds(self, metrics: Dict[str, Any], 
                        thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check BAM metrics against thresholds.
        
        Args:
            metrics: Calculated metrics
            thresholds: Quality thresholds
            
        Returns:
            QC status and failed checks
        """
        qc_status = 'passed'
        failed_checks = []
        
        # Check minimum mapping quality
        if 'min_mapping_quality' in thresholds:
            if metrics.get('mean_mapping_quality', 0) < thresholds['min_mapping_quality']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Mean mapping quality ({metrics['mean_mapping_quality']:.1f}) < "
                    f"threshold ({thresholds['min_mapping_quality']})"
                )
        
        # Check minimum coverage
        if 'min_coverage' in thresholds:
            if metrics.get('mean_coverage', 0) < thresholds['min_coverage']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Mean coverage ({metrics['mean_coverage']:.1f}) < "
                    f"threshold ({thresholds['min_coverage']})"
                )
        
        # Check maximum unmapped percentage
        if 'max_unmapped_percentage' in thresholds:
            if metrics.get('unmapped_percentage', 100) > thresholds['max_unmapped_percentage']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Unmapped percentage ({metrics['unmapped_percentage']:.1f}%) > "
                    f"threshold ({thresholds['max_unmapped_percentage']}%)"
                )
        
        return {
            'status': qc_status,
            'failed_checks': failed_checks
        }