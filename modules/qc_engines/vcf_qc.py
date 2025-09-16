#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
VCF QC Engine
Calculates quality metrics for VCF files WITHOUT processing
"""

import gzip
import logging
from typing import Dict, Any
from .base_qc import BaseQCEngine

logger = logging.getLogger(__name__)


class VcfQCEngine(BaseQCEngine):
    """
    Quality control engine for VCF files.
    Calculates metrics from existing variants WITHOUT additional processing.
    """
    
    def __init__(self, sample_size: int = 1000):
        """
        Initialize VCF QC engine.
        
        Args:
            sample_size: Number of variants to sample for metrics
        """
        super().__init__()
        self.sample_size = sample_size
    
    def calculate_metrics(self, filepath: str) -> Dict[str, Any]:
        """
        Calculate quality metrics from VCF file.
        
        NO variant calling, NO processing, ONLY metrics from existing data!
        
        Args:
            filepath: Path to VCF file
            
        Returns:
            Dictionary with calculated metrics
        """
        metrics = {
            'file_size_mb': self.get_file_size_mb(filepath),
            'total_variants': 0,
            'snp_count': 0,
            'indel_count': 0,
            'mean_variant_quality': 0,
            'mean_depth': 0,
            'missing_data_percentage': 0,
            'transition_transversion_ratio': 0
        }
        
        # Check if file is gzipped
        is_gzipped = filepath.endswith('.gz')
        
        try:
            # Open file
            if is_gzipped:
                file_handle = gzip.open(filepath, 'rt', encoding='utf-8', errors='replace')
            else:
                file_handle = open(filepath, 'r', encoding='utf-8', errors='replace')
            
            # Counters
            total_variants = 0
            snp_count = 0
            indel_count = 0
            total_qual = 0
            total_dp = 0
            missing_samples = 0
            total_samples = 0
            transitions = 0
            transversions = 0
            
            # Parse file
            for line in file_handle:
                line = line.strip()
                
                # Skip headers
                if line.startswith('##'):
                    continue
                
                # Parse header line to get sample count
                if line.startswith('#CHROM'):
                    columns = line.split('\t')
                    if len(columns) > 9:
                        total_samples = len(columns) - 9
                    continue
                
                # Process variant lines
                if not line.startswith('#') and total_variants < self.sample_size:
                    columns = line.split('\t')
                    if len(columns) < 8:
                        continue
                    
                    total_variants += 1
                    
                    # Parse REF and ALT
                    ref = columns[3]
                    alt = columns[4]
                    
                    # Classify variant type
                    if len(ref) == 1 and len(alt) == 1 and ref != alt:
                        snp_count += 1
                        
                        # Check for transitions/transversions
                        if (ref in 'AG' and alt in 'AG') or (ref in 'CT' and alt in 'CT'):
                            transitions += 1
                        elif (ref in 'ACGT' and alt in 'ACGT'):
                            transversions += 1
                    elif len(ref) != len(alt):
                        indel_count += 1
                    
                    # Parse QUAL
                    qual_str = columns[5]
                    if qual_str != '.':
                        try:
                            qual = float(qual_str)
                            total_qual += qual
                        except ValueError:
                            pass
                    
                    # Parse INFO field for DP (depth)
                    info = columns[7]
                    if 'DP=' in info:
                        try:
                            dp_start = info.find('DP=') + 3
                            dp_end = info.find(';', dp_start)
                            if dp_end == -1:
                                dp_end = len(info)
                            dp = int(info[dp_start:dp_end])
                            total_dp += dp
                        except ValueError:
                            pass
                    
                    # Count missing data in samples
                    if len(columns) > 9 and total_samples > 0:
                        for sample_data in columns[9:]:
                            if sample_data == '.' or sample_data.startswith('./.'):
                                missing_samples += 1
            
            file_handle.close()
            
            # Calculate final metrics
            metrics['total_variants'] = total_variants
            metrics['snp_count'] = snp_count
            metrics['indel_count'] = indel_count
            
            if total_variants > 0:
                metrics['mean_variant_quality'] = total_qual / total_variants
                metrics['mean_depth'] = total_dp / total_variants
            
            if total_samples > 0 and total_variants > 0:
                total_genotypes = total_variants * total_samples
                if total_genotypes > 0:
                    metrics['missing_data_percentage'] = (missing_samples / total_genotypes) * 100
            
            if transitions > 0 and transversions > 0:
                metrics['transition_transversion_ratio'] = transitions / transversions
            
            logger.info(f"Calculated VCF metrics for {total_variants} variants from {filepath}")
            
        except Exception as e:
            logger.error(f"Error calculating VCF metrics: {str(e)}")
            metrics['error'] = str(e)
        
        return metrics
    
    def check_thresholds(self, metrics: Dict[str, Any], 
                        thresholds: Dict[str, Any]) -> Dict[str, Any]:
        """
        Check VCF metrics against thresholds.
        
        Args:
            metrics: Calculated metrics
            thresholds: Quality thresholds
            
        Returns:
            QC status and failed checks
        """
        qc_status = 'passed'
        failed_checks = []
        
        # Check minimum variant quality
        if 'min_variant_quality' in thresholds:
            if metrics.get('mean_variant_quality', 0) < thresholds['min_variant_quality']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Mean variant quality ({metrics['mean_variant_quality']:.1f}) < "
                    f"threshold ({thresholds['min_variant_quality']})"
                )
        
        # Check minimum depth
        if 'min_depth' in thresholds:
            if metrics.get('mean_depth', 0) < thresholds['min_depth']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Mean depth ({metrics['mean_depth']:.1f}) < "
                    f"threshold ({thresholds['min_depth']})"
                )
        
        # Check maximum missing data percentage
        if 'max_missing_rate' in thresholds:
            if metrics.get('missing_data_percentage', 100) > thresholds['max_missing_rate']:
                qc_status = 'failed'
                failed_checks.append(
                    f"Missing data percentage ({metrics['missing_data_percentage']:.1f}%) > "
                    f"threshold ({thresholds['max_missing_rate']}%)"
                )
        
        return {
            'status': qc_status,
            'failed_checks': failed_checks
        }