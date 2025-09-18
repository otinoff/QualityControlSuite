#!/usr/bin/env python3
"""
Тестовый скрипт для проверки работы Sequali
"""

import subprocess
import sys
from pathlib import Path

def test_sequali():
    # Пути к файлам
    fastq_file = Path("data/uploaded_files/e2937f7a-b50b-40d4-a94e-f921c4d93422_Undetermined_S0_L001_R1_001.fastq")
    output_dir = Path("data/reports/test_output")
    
    # Создаем директорию для вывода
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Проверяем существование файла: {fastq_file}")
    print(f"Файл существует: {fastq_file.exists()}")
    if fastq_file.exists():
        print(f"Размер файла: {fastq_file.stat().st_size} байт")
    
    # Формируем команду
    cmd = [
        'sequali',
        '--dir', str(output_dir),
        '--html', 'test_report.html',
        str(fastq_file)
    ]
    
    print(f"Команда: {' '.join(cmd)}")
    
    # Запускаем Sequali
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False
        )
        
        print(f"Return code: {result.returncode}")
        print(f"STDOUT: {result.stdout}")
        print(f"STDERR: {result.stderr}")
        
        # Проверяем созданные файлы
        print(f"\nФайлы в директории {output_dir}:")
        for f in output_dir.glob("*"):
            print(f"  {f.name} ({f.stat().st_size} байт)")
            
    except Exception as e:
        print(f"Ошибка при запуске: {e}")

if __name__ == "__main__":
    test_sequali()