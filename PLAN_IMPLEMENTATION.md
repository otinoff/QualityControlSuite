# План создания QualityControlSuite
## Усечённая версия системы контроля качества (без обработки данных)

### Дата: 16.12.2025
### Версия: 1.0

---

## 1. Цель проекта

Создать минимальную автономную систему контроля качества биологических данных, которая:
- ✅ Валидирует форматы файлов
- ✅ Рассчитывает метрики качества из существующих данных
- ✅ Фильтрует данные по пороговым значениям
- ✅ Генерирует унифицированные отчёты
- ❌ НЕ выполняет выравнивание, вызов вариантов или другую обработку
- ❌ НЕ требует референсных геномов

---

## 2. Структура директорий

```
M/TaskContract2025/QualityControlSuite/
├── README.md                    # Документация проекта
├── requirements.txt              # Зависимости Python
├── setup.py                     # Установщик пакета
├── config/
│   └── qc_thresholds.yaml      # Конфигурация порогов качества
│
├── modules/
│   ├── __init__.py
│   ├── validators/              # Валидация форматов
│   │   ├── __init__.py
│   │   ├── base_validator.py   # Базовый класс валидатора
│   │   ├── fastq_validator.py  # Валидация FASTQ
│   │   ├── bam_validator.py    # Валидация BAM/SAM/CRAM
│   │   ├── vcf_validator.py    # Валидация VCF
│   │   ├── table_validator.py  # Валидация табличных данных
│   │   └── format_detector.py  # Определение типа файла
│   │
│   ├── qc_engines/             # Движки контроля качества
│   │   ├── __init__.py
│   │   ├── fastq_qc.py        # QC для FASTQ
│   │   ├── bam_qc.py          # QC для BAM
│   │   ├── vcf_qc.py          # QC для VCF
│   │   ├── table_qc.py        # QC для таблиц
│   │   └── metrics.py         # Общие метрики
│   │
│   ├── filters/                # Фильтрация данных
│   │   ├── __init__.py
│   │   ├── threshold_filter.py # Фильтрация по порогам
│   │   ├── outlier_filter.py   # Фильтрация выбросов
│   │   └── quality_filter.py   # Фильтрация по качеству
│   │
│   └── reporters/              # Генерация отчётов
│       ├── __init__.py
│       ├── base_reporter.py    # Базовый класс отчёта
│       ├── html_reporter.py    # HTML отчёты
│       ├── json_reporter.py    # JSON отчёты
│       └── unified_report.py   # Унифицированный отчёт
│
├── main.py                     # Основная точка входа
├── cli.py                      # CLI интерфейс
│
├── tests/                      # Тесты
│   ├── __init__.py
│   ├── test_validators.py
│   ├── test_qc_engines.py
│   ├── test_filters.py
│   └── test_reporters.py
│
├── examples/                   # Примеры использования
│   ├── example_fastq.py
│   ├── example_bam.py
│   └── example_vcf.py
│
└── docs/                       # Документация
    ├── API.md
    ├── USER_GUIDE.md
    └── EXAMPLES.md
```

---

## 3. План реализации по этапам

### Этап 1: Базовая инфраструктура (День 1)
- [ ] Создать структуру директорий
- [ ] Настроить requirements.txt с минимальными зависимостями
- [ ] Создать базовые классы и интерфейсы
- [ ] Настроить логирование

### Этап 2: Модули валидации (День 2)
- [ ] format_detector.py - определение типа файла
- [ ] fastq_validator.py - валидация FASTQ
- [ ] bam_validator.py - валидация BAM/SAM
- [ ] vcf_validator.py - валидация VCF
- [ ] table_validator.py - валидация CSV/TSV

### Этап 3: Движки контроля качества (День 3-4)
- [ ] fastq_qc.py - метрики FASTQ (Q-scores, длина, GC%)
- [ ] bam_qc.py - метрики BAM (флаги, дупликаты)
- [ ] vcf_qc.py - метрики VCF (количество, качество)
- [ ] table_qc.py - метрики таблиц (полнота, выбросы)
- [ ] metrics.py - общие метрики

### Этап 4: Фильтрация (День 5)
- [ ] threshold_filter.py - пороговая фильтрация
- [ ] quality_filter.py - фильтрация по качеству
- [ ] outlier_filter.py - статистическая фильтрация

### Этап 5: Генерация отчётов (День 6)
- [ ] html_reporter.py - HTML отчёты с графиками
- [ ] json_reporter.py - структурированные JSON
- [ ] unified_report.py - единый формат отчёта

### Этап 6: Интеграция и CLI (День 7)
- [ ] main.py - основной pipeline
- [ ] cli.py - командный интерфейс
- [ ] config/qc_thresholds.yaml - конфигурация

### Этап 7: Тестирование и документация (День 8)
- [ ] Написать unit-тесты
- [ ] Создать примеры использования
- [ ] Написать документацию

---

## 4. Минимальные зависимости

```txt
# requirements.txt
pysam>=0.19.0          # Для работы с BAM/SAM
biopython>=1.79        # Для базовой работы с последовательностями
pandas>=1.3.0          # Для табличных данных
numpy>=1.21.0          # Для статистики
matplotlib>=3.4.0      # Для графиков в отчётах
pyyaml>=5.4           # Для конфигурации
click>=8.0            # Для CLI
```

---

## 5. Ключевые классы и интерфейсы

### 5.1 Базовый валидатор
```python
# modules/validators/base_validator.py
from abc import ABC, abstractmethod

class BaseValidator(ABC):
    """Базовый класс для валидации файлов"""
    
    @abstractmethod
    def validate_format(self, filepath: str) -> bool:
        """Проверка формата файла"""
        pass
    
    @abstractmethod
    def get_validation_errors(self) -> list:
        """Получить список ошибок валидации"""
        pass
```

### 5.2 Базовый QC движок
```python
# modules/qc_engines/base_qc.py
from abc import ABC, abstractmethod

class BaseQCEngine(ABC):
    """Базовый класс для расчёта метрик качества"""
    
    @abstractmethod
    def calculate_metrics(self, filepath: str) -> dict:
        """Рассчитать метрики качества"""
        pass
    
    @abstractmethod
    def check_thresholds(self, metrics: dict, thresholds: dict) -> dict:
        """Проверить метрики по порогам"""
        pass
```

### 5.3 Главный pipeline
```python
# main.py
class QualityControlPipeline:
    """Основной pipeline контроля качества"""
    
    def __init__(self, config_path: str):
        self.config = self.load_config(config_path)
        self.validator = None
        self.qc_engine = None
        self.filter = None
        self.reporter = None
    
    def run(self, input_file: str, output_dir: str):
        # 1. Определить тип файла
        file_type = self.detect_format(input_file)
        
        # 2. Валидировать формат
        is_valid = self.validate(input_file, file_type)
        if not is_valid:
            return {"status": "failed", "stage": "validation"}
        
        # 3. Рассчитать метрики (БЕЗ обработки!)
        metrics = self.calculate_metrics(input_file, file_type)
        
        # 4. Применить фильтры
        qc_status = self.apply_filters(metrics)
        
        # 5. Сгенерировать отчёт
        report = self.generate_report(metrics, qc_status, output_dir)
        
        return {"status": "success", "report": report, "metrics": metrics}
```

---

## 6. Пример использования

### CLI интерфейс
```bash
# Проверка качества FASTQ файла
python -m qcsuite check fastq sample.fastq --output reports/

# Проверка качества BAM файла  
python -m qcsuite check bam sample.bam --output reports/

# Проверка с кастомными порогами
python -m qcsuite check vcf sample.vcf --config custom_thresholds.yaml

# Batch обработка
python -m qcsuite batch --input-dir data/ --output-dir reports/
```

### Python API
```python
from qcsuite import QualityControlPipeline

# Инициализация
qc = QualityControlPipeline("config/qc_thresholds.yaml")

# Проверка одного файла
result = qc.run("sample.fastq", "output/")

# Проверка результата
if result["status"] == "success":
    print(f"QC passed! Report: {result['report']}")
    print(f"Metrics: {result['metrics']}")
else:
    print(f"QC failed at stage: {result['stage']}")
```

---

## 7. Конфигурация порогов

```yaml
# config/qc_thresholds.yaml
fastq:
  min_quality_score: 30
  min_read_length: 50
  max_n_percentage: 5
  min_gc_content: 20
  max_gc_content: 80

bam:
  min_mapping_quality: 30
  max_duplicate_rate: 30
  min_coverage: 10

vcf:
  min_variant_quality: 30
  min_depth: 10
  max_missing_rate: 10

tables:
  max_missing_values: 20
  outlier_threshold: 3  # стандартных отклонений
```

---

## 8. Отличия от OmicsIntegrationSuite

| Функция | OmicsIntegrationSuite | QualityControlSuite |
|---------|----------------------|---------------------|
| Валидация форматов | ✅ | ✅ |
| Расчёт метрик QC | ✅ | ✅ |
| Фильтрация по порогам | ✅ | ✅ |
| Генерация отчётов | ✅ | ✅ |
| Выравнивание (BWA) | ✅ | ❌ |
| Вызов вариантов | ✅ | ❌ |
| Референсные геномы | ✅ | ❌ |
| Интеграция данных | ✅ | ❌ |
| Размер кода | ~5000 строк | ~1000 строк |
| Зависимости | 20+ пакетов | 7 пакетов |

---

## 9. Критерии успеха

1. **Функциональность**:
   - Корректная валидация всех форматов
   - Точный расчёт метрик без внешней обработки
   - Работа без референсных геномов

2. **Производительность**:
   - Обработка FASTQ 1GB < 1 минута
   - Обработка BAM 1GB < 2 минуты
   - Использование RAM < 4GB

3. **Простота**:
   - Минимум зависимостей
   - Простая установка
   - Понятный API

4. **Автономность**:
   - Работа offline
   - Не требует внешних баз данных
   - Не требует дополнительных инструментов

---

## 10. Следующие шаги

1. **Немедленно**: Создать структуру директорий
2. **День 1**: Реализовать базовые классы
3. **Дни 2-7**: Последовательная реализация модулей
4. **День 8**: Тестирование и документация

---

*План подготовлен для создания минимальной системы контроля качества*