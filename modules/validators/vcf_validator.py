"""
VCF файлов валидатор
"""

import os
import gzip
import logging
from typing import Dict, Any, List
from .base_validator import BaseValidator

logger = logging.getLogger(__name__)

class VcfValidator(BaseValidator):
    """Валидатор для VCF файлов"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions = ['.vcf', '.vcf.gz']
    
    def validate_format(self, filepath: str) -> bool:
        """
        Validate VCF file format.
        
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
        is_supported = False
        for ext in self.supported_extensions:
            if filepath.endswith(ext):
                is_supported = True
                break
        
        if not is_supported:
            self.errors.append(f"Unsupported extension for file: {filepath}")
            return False
        
        try:
            # Check file compression
            is_gzipped = filepath.endswith('.gz')
            
            # Open file
            if is_gzipped:
                file_handle = gzip.open(filepath, 'rt')
            else:
                file_handle = open(filepath, 'r')
            
            # Check for VCF header
            has_header = False
            line_count = 0
            
            for line in file_handle:
                line = line.strip()
                line_count += 1
                
                if line.startswith('##fileformat='):
                    has_header = True
                    break
                
                # Limit check to first 100 lines
                if line_count >= 100:
                    break
            
            file_handle.close()
            
            if not has_header:
                self.errors.append("Missing VCF fileformat header")
                return False
            
            return True
            
        except Exception as e:
            self.errors.append(f"Validation error: {str(e)}")
            return False
    
    def validate(self, filepath: str) -> Dict[str, Any]:
        """
        Валидация VCF файла
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Словарь с результатами валидации
        """
        is_valid = self.validate_format(filepath)
        
        result = {
            'valid': is_valid,
            'format': 'VCF',
            'errors': self.get_validation_errors(),
            'warnings': self.get_validation_warnings(),
            'metadata': {}
        }
        
        if is_valid:
            try:
                # Определение сжатия
                is_gzipped = filepath.endswith('.gz')
                result['metadata']['compressed'] = is_gzipped
                
                # Открытие файла
                if is_gzipped:
                    file_handle = gzip.open(filepath, 'rt')
                else:
                    file_handle = open(filepath, 'r')
                
                # Проверка заголовка
                header_lines = []
                sample_names = []
                variant_count = 0
                
                for line in file_handle:
                    line = line.strip()
                    
                    if line.startswith('##'):
                        # Мета-информация
                        header_lines.append(line)
                        if line.startswith('##fileformat='):
                            result['metadata']['file_format'] = line.split('=')[1]
                        elif line.startswith('##reference='):
                            result['metadata']['reference'] = line.split('=')[1]
                            
                    elif line.startswith('#CHROM'):
                        # Заголовок с образцами
                        columns = line.split('\t')
                        if len(columns) < 8:
                            result['errors'].append("Неверный формат заголовка")
                            file_handle.close()
                            return result
                        
                        # Извлечение имён образцов
                        if len(columns) > 9:
                            sample_names = columns[9:]
                            result['metadata']['samples'] = sample_names
                            result['metadata']['sample_count'] = len(sample_names)
                        
                    elif not line.startswith('#'):
                        # Строки с вариантами
                        variant_count += 1
                        
                        # Проверка формата первых 10 вариантов
                        if variant_count <= 10:
                            columns = line.split('\t')
                            if len(columns) < 8:
                                result['warnings'].append(f"Неверный формат строки {variant_count}")
                            
                            # Проверка качества
                            if len(columns) > 5:
                                qual = columns[5]
                                if qual != '.' and float(qual) < 20:
                                    result['warnings'].append(f"Низкое качество варианта в строке {variant_count}")
                        
                        # Ограничение проверки для больших файлов
                        if variant_count >= 1000:
                            break
                
                file_handle.close()
                
                # Сохранение метаданных
                result['metadata']['header_lines'] = len(header_lines)
                result['metadata']['variant_count_sample'] = variant_count
                
                # Предупреждения
                if variant_count == 0:
                    result['warnings'].append("Файл не содержит вариантов")
                
                if 'file_format' not in result['metadata']:
                    result['warnings'].append("Не указана версия формата VCF")
                
            except Exception as e:
                result['errors'].append(f"Ошибка валидации: {str(e)}")
        
        return result
    
    def get_format_info(self) -> Dict[str, Any]:
        """Получение информации о формате"""
        return {
            'name': 'VCF',
            'extensions': self.supported_extensions,
            'description': 'Variant Call Format',
            'binary': False,
            'compressed': 'optional'
        }