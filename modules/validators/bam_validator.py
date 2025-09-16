"""
BAM/SAM файлов валидатор
"""

import os
import logging
from typing import Dict, Any, List
from .base_validator import BaseValidator

logger = logging.getLogger(__name__)

class BamValidator(BaseValidator):
    """Валидатор для BAM/SAM файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.bam', '.sam', '.cram']
    
    def validate_format(self, filepath: str) -> bool:
        """
        Validate BAM/SAM file format.
        
        Args:
            filepath: Path to the file to validate
            
        Returns:
            True if file format is valid, False otherwise
        """
        self.clear_errors()
        self.warnings = []
        
        # Check file existence
        if not self.check_file_exists(filepath):
            return False
        if not self.check_file_not_empty(filepath):
            return False
        if not self.check_file_readable(filepath):
            return False
        
        # Check file extension
        file_ext = os.path.splitext(filepath)[1].lower()
        if file_ext not in self.supported_extensions:
            self.errors.append(f"Unsupported extension: {file_ext}")
            return False
        
        try:
            import pysam
            
            # Open file
            if file_ext == '.bam':
                samfile = pysam.AlignmentFile(filepath, "rb")
            elif file_ext == '.sam':
                samfile = pysam.AlignmentFile(filepath, "r")
            elif file_ext == '.cram':
                samfile = pysam.AlignmentFile(filepath, "rc")
            else:
                self.errors.append(f"Unknown format: {file_ext}")
                return False
            
            # Check header
            if not samfile.header:
                self.errors.append("Missing file header")
                samfile.close()
                return False
            
            # Check first few reads
            read_count = 0
            for read in samfile.fetch(until_eof=True):
                read_count += 1
                if read_count >= 100:
                    break
            
            samfile.close()
            
            # Check for index
            if not os.path.exists(filepath + '.bai') and not os.path.exists(filepath + '.csi'):
                self.warnings.append("Index file missing")
            
            return True
            
        except ImportError:
            self.errors.append("pysam library not installed")
            return False
        except Exception as e:
            self.errors.append(f"Validation error: {str(e)}")
            return False
    
    def validate(self, filepath: str) -> Dict[str, Any]:
        """
        Валидация BAM/SAM файла
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Словарь с результатами валидации
        """
        is_valid = self.validate_format(filepath)
        
        result = {
            'valid': is_valid,
            'format': None,
            'errors': self.get_validation_errors(),
            'warnings': self.get_validation_warnings(),
            'metadata': {}
        }
        
        # Определение формата по расширению
        file_ext = os.path.splitext(filepath)[1].lower()
        if file_ext in self.supported_extensions:
            result['format'] = file_ext[1:].upper()
        
        if is_valid:
            try:
                import pysam
                
                # Открытие файла
                if file_ext == '.bam':
                    samfile = pysam.AlignmentFile(filepath, "rb")
                elif file_ext == '.sam':
                    samfile = pysam.AlignmentFile(filepath, "r")
                elif file_ext == '.cram':
                    samfile = pysam.AlignmentFile(filepath, "rc")
                
                # Извлечение метаданных
                result['metadata']['references'] = len(samfile.references) if samfile.references else 0
                result['metadata']['has_index'] = os.path.exists(filepath + '.bai') or os.path.exists(filepath + '.csi')
                
                # Подсчёт записей (первые 1000 для быстрой проверки)
                read_count = 0
                mapped_count = 0
                unmapped_count = 0
                
                for read in samfile.fetch(until_eof=True):
                    read_count += 1
                    if read.is_unmapped:
                        unmapped_count += 1
                    else:
                        mapped_count += 1
                    
                    if read_count >= 1000:
                        break
                
                result['metadata']['sample_reads'] = read_count
                result['metadata']['sample_mapped'] = mapped_count
                result['metadata']['sample_unmapped'] = unmapped_count
                
                samfile.close()
                
            except Exception as e:
                result['errors'].append(f"Metadata extraction error: {str(e)}")
        
        return result
    
    def get_format_info(self) -> Dict[str, Any]:
        """Получение информации о формате"""
        return {
            'name': 'BAM/SAM',
            'extensions': self.supported_extensions,
            'description': 'Binary/Sequence Alignment Map format',
            'binary': True,
            'compressed': True
        }