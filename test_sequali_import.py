#!/usr/bin/env python3
"""
Пример прямого импорта Sequali как Python модуля
"""

# Sequali можно импортировать как модуль, но документации мало
# Основной способ использования - через CLI

import subprocess
import json

def analyze_with_sequali_cli(fastq_file):
    """Используем Sequali через CLI (рекомендуемый способ)"""
    
    # Запускаем sequali и получаем JSON вывод
    cmd = ['sequali', '--json', '--no-html', fastq_file]
    result = subprocess.run(cmd, capture_output=True, text=True, check=True)
    
    # Ищем JSON файл
    json_file = fastq_file.replace('.fastq', '.json')
    with open(json_file, 'r') as f:
        data = json.load(f)
    
    return data

# Альтернативный подход - если бы был Python API (гипотетический):
# from sequali import FastqAnalyzer  # Такого импорта НЕТ в текущей версии
# analyzer = FastqAnalyzer()
# metrics = analyzer.analyze("file.fastq")

if __name__ == "__main__":
    # Тестируем CLI подход
    print("Sequali используется через subprocess.run() вызов CLI команды")
    print("Это потому что:")
    print("1. Sequali написан на Rust для скорости")
    print("2. Python биндинги минимальные")
    print("3. CLI интерфейс - официальный способ использования")
    print("\nПосле 'pip install sequali' вы получаете:")
    print("- Исполняемый файл 'sequali' в PATH")
    print("- Который можно вызывать из Python через subprocess")