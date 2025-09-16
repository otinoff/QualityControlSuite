#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Base Validator Class
Abstract base class for all file format validators
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class BaseValidator(ABC):
    """
    Abstract base class for file format validation.
    All validators should inherit from this class.
    """
    
    def __init__(self):
        """Initialize validator with empty error list."""
        self.errors: List[str] = []
        self.warnings: List[str] = []
        
    @abstractmethod
    def validate_format(self, filepath: str) -> bool:
        """
        Validate file format and structure.
        
        Args:
            filepath: Path to the file to validate
            
        Returns:
            True if file format is valid, False otherwise
        """
        pass
    
    def check_file_exists(self, filepath: str) -> bool:
        """Check if file exists."""
        if not Path(filepath).exists():
            self.errors.append(f"File does not exist: {filepath}")
            return False
        return True
    
    def check_file_not_empty(self, filepath: str) -> bool:
        """Check if file is not empty."""
        file_size = Path(filepath).stat().st_size
        if file_size == 0:
            self.errors.append(f"File is empty: {filepath}")
            return False
        return True
    
    def check_file_readable(self, filepath: str) -> bool:
        """Check if file is readable."""
        try:
            with open(filepath, 'rb') as f:
                f.read(1)
            return True
        except Exception as e:
            self.errors.append(f"File is not readable: {str(e)}")
            return False
    
    def get_validation_errors(self) -> List[str]:
        """Get list of validation errors."""
        return self.errors
    
    def get_validation_warnings(self) -> List[str]:
        """Get list of validation warnings."""
        return self.warnings
    
    def clear_errors(self):
        """Clear all errors and warnings."""
        self.errors = []
        self.warnings = []
    
    def is_valid(self) -> bool:
        """Check if validation passed without errors."""
        return len(self.errors) == 0