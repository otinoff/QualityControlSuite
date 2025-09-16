#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FASTQ Validator
Validates FASTQ file format and structure
"""

import gzip
from pathlib import Path
from typing import Optional
import logging
from .base_validator import BaseValidator

logger = logging.getLogger(__name__)


class FastqValidator(BaseValidator):
    """
    Validator for FASTQ file format.
    Checks structure without processing sequences.
    """
    
    def __init__(self, max_records_check: int = 1000):
        """
        Initialize FASTQ validator.
        
        Args:
            max_records_check: Maximum number of records to validate
        """
        super().__init__()
        self.max_records_check = max_records_check
        
    def validate_format(self, filepath: str) -> bool:
        """
        Validate FASTQ file format.
        
        Args:
            filepath: Path to FASTQ file
            
        Returns:
            True if valid FASTQ format, False otherwise
        """
        self.clear_errors()
        
        # Basic file checks
        if not self.check_file_exists(filepath):
            return False
        if not self.check_file_not_empty(filepath):
            return False
        if not self.check_file_readable(filepath):
            return False
        
        # Check if file is gzipped
        is_gzipped = filepath.endswith('.gz')
        
        try:
            if is_gzipped:
                file_handle = gzip.open(filepath, 'rt', encoding='utf-8', errors='replace')
            else:
                file_handle = open(filepath, 'r', encoding='utf-8', errors='replace')
            
            # Validate FASTQ records
            records_checked = 0
            line_number = 0
            
            while records_checked < self.max_records_check:
                # Read 4 lines for a FASTQ record
                header = file_handle.readline()
                if not header:
                    break  # End of file
                    
                sequence = file_handle.readline()
                separator = file_handle.readline()
                quality = file_handle.readline()
                
                line_number += 4
                
                # Check if we have all 4 lines
                if not all([header, sequence, separator, quality]):
                    self.errors.append(f"Incomplete FASTQ record at line {line_number-3}")
                    file_handle.close()
                    return False
                
                # Validate header (should start with @)
                if not header.startswith('@'):
                    self.errors.append(f"Invalid header at line {line_number-3}: doesn't start with @")
                    file_handle.close()
                    return False
                
                # Validate separator (should be +)
                if not separator.startswith('+'):
                    self.errors.append(f"Invalid separator at line {line_number-1}: doesn't start with +")
                    file_handle.close()
                    return False
                
                # Check sequence and quality lengths match
                seq_len = len(sequence.strip())
                qual_len = len(quality.strip())
                if seq_len != qual_len:
                    self.errors.append(f"Sequence and quality lengths don't match at line {line_number-3}")
                    file_handle.close()
                    return False
                
                # Check for valid nucleotide characters (allow N)
                valid_chars = set('ACGTNacgtn')
                seq_chars = set(sequence.strip())
                if not seq_chars.issubset(valid_chars):
                    invalid = seq_chars - valid_chars
                    self.warnings.append(f"Non-standard characters in sequence at line {line_number-2}: {invalid}")
                
                records_checked += 1
            
            file_handle.close()
            
            if records_checked == 0:
                self.errors.append("No valid FASTQ records found")
                return False
            
            logger.info(f"Successfully validated {records_checked} FASTQ records")
            return True
            
        except Exception as e:
            self.errors.append(f"Error reading FASTQ file: {str(e)}")
            return False