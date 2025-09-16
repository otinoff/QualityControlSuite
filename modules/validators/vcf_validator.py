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
    
    def validate(self, filepath: str) -> Dict[str, Any]:
        """
        Валидация VCF файла
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Словарь с результатами валидации
        """
        result = {
            'valid': False,
            'format': 'VCF',
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        # Проверка существования файла
        if not os.path.exists(filepath):
            result['errors'].append(f"Файл не найден: {filepath}")
            return result
        
        # Определение сжатия
        is_gzipped = filepath.endswith('.gz')
        result['metadata']['compressed'] = is_gzipped
        
        try:
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
            
            # Проверка наличия заголовка
            if not header_lines:
                result['errors'].append("Отсутствует заголовок VCF")
                return result
            
            # Сохранение метаданных
            result['metadata']['header_lines'] = len(header_lines)
            result['metadata']['variant_count_sample'] = variant_count
            
            # Предупреждения
            if variant_count == 0:
                result['warnings'].append("Файл не содержит вариантов")
            
            if 'file_format' not in result['metadata']:
                result['warnings'].append("Не указана версия формата VCF")
            
            result['valid'] = True
            
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