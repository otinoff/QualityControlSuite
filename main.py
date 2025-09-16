#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
QualityControlSuite - Main Pipeline
Minimal QC system for biological data (FASTQ, BAM/SAM, VCF)
"""

import os
import sys
import yaml
import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Add modules to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import modules
from modules.validators.fastq_validator import FastqValidator
from modules.validators.bam_validator import BamValidator
from modules.validators.vcf_validator import VcfValidator
from modules.qc_engines.fastq_qc import FastqQCEngine
from modules.qc_engines.bam_qc import BamQCEngine
from modules.qc_engines.vcf_qc import VcfQCEngine
from modules.reporters.json_reporter import JSONReporter
from modules.reporters.html_reporter import HTMLReporter
from modules.reporters.text_reporter import TextReporter

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class QualityControlPipeline:
    """
    Main Quality Control Pipeline for biological data files.
    Handles validation, QC metrics calculation, and reporting.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize QC pipeline.
        
        Args:
            config_path: Path to configuration file (YAML)
        """
        self.config = self._load_config(config_path)
        self.validators = {
            'fastq': FastqValidator(),
            'bam': BamValidator(),
            'vcf': VcfValidator()
        }
        self.qc_engines = {
            'fastq': FastqQCEngine(),
            'bam': BamQCEngine(),
            'vcf': VcfQCEngine()
        }
        self.reporters = {
            'json': JSONReporter(),
            'html': HTMLReporter(),
            'text': TextReporter()
        }
        
    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from YAML file."""
        if config_path and os.path.exists(config_path):
            with open(config_path, 'r') as f:
                return yaml.safe_load(f)
        else:
            # Return default configuration
            return {
                'fastq': {
                    'min_quality_score': 20,
                    'min_read_length': 50,
                    'max_n_percentage': 5
                },
                'bam': {
                    'min_mapping_quality': 30,
                    'min_coverage': 10,
                    'max_unmapped_percentage': 10
                },
                'vcf': {
                    'min_quality': 30,
                    'min_depth': 10,
                    'max_missing_percentage': 20
                }
            }
    
    def detect_file_type(self, filepath: str) -> str:
        """
        Detect file type based on extension.
        
        Args:
            filepath: Path to file
            
        Returns:
            File type ('fastq', 'bam', 'vcf', or 'unknown')
        """
        filename_lower = filepath.lower()
        if filename_lower.endswith(('.fastq', '.fastq.gz', '.fq', '.fq.gz')):
            return 'fastq'
        elif filename_lower.endswith(('.bam', '.sam', '.cram')):
            return 'bam'
        elif filename_lower.endswith(('.vcf', '.vcf.gz')):
            return 'vcf'
        else:
            return 'unknown'
    
    def validate_file(self, filepath: str, file_type: str) -> Dict[str, Any]:
        """
        Validate file format.
        
        Args:
            filepath: Path to file
            file_type: Type of file ('fastq', 'bam', 'vcf')
            
        Returns:
            Validation results
        """
        if file_type not in self.validators:
            return {
                'valid': False,
                'format': file_type,
                'errors': [f'Unsupported file type: {file_type}'],
                'warnings': []
            }
        
        validator = self.validators[file_type]
        if hasattr(validator, 'validate'):
            # New style validators (BAM, VCF)
            return validator.validate(filepath)
        else:
            # Old style validators (FASTQ)
            is_valid = validator.validate_format(filepath)
            return {
                'valid': is_valid,
                'format': file_type.upper(),
                'errors': validator.get_validation_errors(),
                'warnings': validator.get_validation_warnings()
            }
    
    def calculate_qc_metrics(self, filepath: str, file_type: str) -> Dict[str, Any]:
        """
        Calculate QC metrics for file.
        
        Args:
            filepath: Path to file
            file_type: Type of file
            
        Returns:
            QC metrics
        """
        if file_type not in self.qc_engines:
            return {
                'error': f'QC engine not implemented for {file_type}',
                'metrics': {}
            }
        
        try:
            qc_engine = self.qc_engines[file_type]
            metrics = qc_engine.calculate_metrics(filepath)
            return {'metrics': metrics}
        except Exception as e:
            logger.error(f"Error calculating QC metrics: {str(e)}")
            return {
                'error': str(e),
                'metrics': {}
            }
    
    def check_quality_status(self, metrics: Dict[str, Any], file_type: str) -> str:
        """
        Check overall quality status based on thresholds.
        
        Args:
            metrics: Calculated metrics
            file_type: Type of file
            
        Returns:
            Quality status ('PASS', 'WARNING', 'FAIL')
        """
        thresholds = self.config.get(file_type, {})
        
        # Simple implementation - can be extended
        if 'error' in metrics:
            return 'FAIL'
        
        # For FASTQ, check some basic metrics
        if file_type == 'fastq':
            fastq_metrics = metrics.get('metrics', {})
            avg_quality = fastq_metrics.get('avg_quality_score', 0)
            min_quality = thresholds.get('min_quality_score', 20)
            
            if avg_quality < min_quality:
                return 'FAIL'
            elif avg_quality < min_quality + 10:
                return 'WARNING'
            else:
                return 'PASS'
        
        return 'PASS'
    
    def process_single_file(self, filepath: str, output_dir: str) -> Dict[str, Any]:
        """
        Process single file through complete QC pipeline.
        
        Args:
            filepath: Path to input file
            output_dir: Directory for output files
            
        Returns:
            Complete QC results
        """
        logger.info(f"Processing file: {filepath}")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Detect file type
        file_type = self.detect_file_type(filepath)
        if file_type == 'unknown':
            return {
                'error': f'Unknown file type for {filepath}',
                'quality_status': 'FAIL'
            }
        
        # Validate file format
        logger.info("Validating file format...")
        validation_result = self.validate_file(filepath, file_type)
        
        if not validation_result.get('valid', False):
            return {
                'file_type': file_type,
                'validation': validation_result,
                'quality_status': 'FAIL'
            }
        
        # Calculate QC metrics
        logger.info("Calculating QC metrics...")
        qc_result = self.calculate_qc_metrics(filepath, file_type)
        
        # Determine quality status
        quality_status = self.check_quality_status(qc_result, file_type)
        
        # Prepare results
        results = {
            'file_type': file_type,
            'validation': validation_result,
            'metrics': qc_result.get('metrics', {}),
            'quality_status': quality_status
        }
        
        # Generate reports
        self._generate_reports(results, filepath, output_dir)
        
        logger.info(f"Processing complete. Quality status: {quality_status}")
        return results
    
    def _generate_reports(self, results: Dict[str, Any], filepath: str, output_dir: str):
        """
        Generate reports in different formats.
        
        Args:
            results: QC results
            filepath: Input file path
            output_dir: Output directory
        """
        filename = os.path.basename(filepath)
        results['filename'] = filename
        
        # Generate reports using reporters
        for format_name, reporter in self.reporters.items():
            output_path = os.path.join(output_dir, f'qc_report.{format_name}')
            try:
                reporter.generate_report(results, output_path)
            except Exception as e:
                logger.error(f"Error generating {format_name} report: {str(e)}")


def main():
    """Main CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='QualityControlSuite - Biological Data QC')
    parser.add_argument('command', choices=['single', 'batch'], help='Command to run')
    parser.add_argument('input', help='Input file or directory')
    parser.add_argument('--output-dir', '-o', default='./output', help='Output directory')
    parser.add_argument('--config', '-c', help='Configuration file path')
    
    args = parser.parse_args()
    
    # Initialize pipeline
    pipeline = QualityControlPipeline(args.config)
    
    if args.command == 'single':
        # Process single file
        results = pipeline.process_single_file(args.input, args.output_dir)
        print(json.dumps(results, indent=2, default=str))
        
    elif args.command == 'batch':
        print("Batch processing not yet implemented")
        sys.exit(1)


if __name__ == "__main__":
    main()