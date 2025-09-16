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
    
    def validate(self, filepath: str) -> Dict[str, Any]:
        """
        Валидация BAM/SAM файла
        
        Args:
            filepath: Путь к файлу
            
        Returns:
            Словарь с результатами валидации
        """
        result = {
            'valid': False,
            'format': None,
            'errors': [],
            'warnings': [],
            'metadata': {}
        }
        
        # Проверка существования файла
        if not os.path.exists(filepath):
            result['errors'].append(f"Файл не найден: {filepath}")
            return result
        
        # Определение формата по расширению
        file_ext = os.path.splitext(filepath)[1].lower()
        if file_ext not in self.supported_extensions:
            result['errors'].append(f"Неподдерживаемое расширение: {file_ext}")
            return result
        
        result['format'] = file_ext[1:].upper()
        
        try:
            import pysam
            
            # Открытие файла
            if file_ext == '.bam':
                samfile = pysam.AlignmentFile(filepath, "rb")
            elif file_ext == '.sam':
                samfile = pysam.AlignmentFile(filepath, "r")
            elif file_ext == '.cram':
                samfile = pysam.AlignmentFile(filepath, "rc")
            else:
                result['errors'].append(f"Неизвестный формат: {file_ext}")
                return result
            
            # Проверка заголовка
            if not samfile.header:
                result['errors'].append("Отсутствует заголовок файла")
                samfile.close()
                return result
            
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
            
            # Предупреждения
            if not result['metadata']['has_index']:
                result['warnings'].append("Отсутствует индексный файл")
            
            if unmapped_count > mapped_count:
                result['warnings'].append("Большое количество некартированных ридов")
            
            samfile.close()
            result['valid'] = True
            
        except ImportError:
            result['errors'].append("Библиотека pysam не установлена")
        except Exception as e:
            result['errors'].append(f"Ошибка валидации: {str(e)}")
        
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