# QualityControlSuite

[![Deploy Status](https://github.com/otinoff/QualityControlSuite/actions/workflows/deploy.yml/badge.svg)](https://github.com/otinoff/QualityControlSuite/actions)

Минимальная система контроля качества биологических данных для TaskContract2025.

## 🎯 Назначение

QualityControlSuite - это **легковесная** система контроля качества для биологических данных (FASTQ, BAM/SAM, VCF), которая:
- ✅ **ТОЛЬКО** проверяет форматы и рассчитывает метрики качества
- ❌ **НЕ** выполняет выравнивание, вызов вариантов или другую обработку
- 📦 Имеет минимальные зависимости (7 пакетов вместо 20+)
- 🚀 Работает быстро и эффективно

## 📋 Возможности

### Поддерживаемые форматы
- **FASTQ** (.fastq, .fastq.gz) - данные секвенирования
- **BAM/SAM/CRAM** - выровненные последовательности
- **VCF** (.vcf, .vcf.gz) - варианты генома

### Метрики качества
- **FASTQ**: Q-scores, GC-контент, длины ридов, распределение качества
- **BAM**: Статистика выравнивания, покрытие, качество маппинга
- **VCF**: Статистика вариантов, качество вызовов, распределение по типам

### Форматы отчётов
- HTML отчёт с визуализацией
- JSON для программной обработки
- Текстовый отчёт для консоли

## 🛠️ Установка

### Локальная установка

```bash
# Клонирование репозитория
git clone https://github.com/otinoff/QualityControlSuite.git
cd QualityControlSuite

# Создание виртуального окружения
python -m venv venv
source venv/bin/activate  # Linux/Mac
# или
venv\Scripts\activate  # Windows

# Установка зависимостей
pip install -r requirements.txt
```

### Установка на сервер

```bash
# Запуск скрипта установки (требует sudo)
sudo bash scripts/server_setup.sh
```

## 💻 Использование

### CLI интерфейс

```bash
# Анализ одного файла
python main.py single input.fastq --output-dir ./results

# Пакетная обработка
python main.py batch ./data --output-dir ./results --file-pattern "*.fastq"

# С пользовательскими порогами
python main.py single input.bam --config ./config/custom_thresholds.yaml
```

### Веб-интерфейс Streamlit

```bash
# Запуск веб-интерфейса
streamlit run web_interface.py

# Интерфейс будет доступен на http://localhost:8501
```

### Возможности веб-интерфейса

- 📁 Загрузка файлов через drag-and-drop
- 📊 Интерактивная визуализация результатов
- 📈 Метрики качества в реальном времени
- 📄 Скачивание отчётов в разных форматах (HTML, JSON, TXT)
- ⚙️ Настройка пороговых значений

## 📁 Структура проекта

```
QualityControlSuite/
├── main.py                    # Основной CLI интерфейс
├── web_interface.py          # Streamlit веб-интерфейс
├── requirements.txt          # Зависимости
├── config/
│   └── qc_thresholds.yaml   # Пороги качества
├── modules/
│   ├── validators/           # Валидаторы форматов
│   │   ├── fastq_validator.py
│   │   ├── bam_validator.py
│   │   └── vcf_validator.py
│   ├── qc_engines/          # Движки контроля качества
│   │   ├── fastq_qc.py
│   │   ├── bam_qc.py
│   │   └── vcf_qc.py
│   └── reporters/           # Генераторы отчётов
│       ├── html_reporter.py
│       ├── json_reporter.py
│       └── text_reporter.py
└── scripts/
    └── server_setup.sh      # Скрипт установки на сервер
```

## ⚙️ Конфигурация

### Пороги качества (config/qc_thresholds.yaml)

```yaml
fastq:
  min_quality_score: 20
  min_read_length: 50
  max_n_percentage: 5

bam:
  min_mapping_quality: 30
  min_coverage: 10
  max_unmapped_percentage: 10

vcf:
  min_quality: 30
  min_depth: 10
  max_missing_percentage: 20
```

## 🚀 Deployment

### GitHub Actions

Проект настроен для автоматического деплоя через GitHub Actions при push в main ветку.

Необходимые секреты в GitHub:
- `SERVER_HOST` - адрес сервера
- `SERVER_USER` - пользователь SSH
- `SERVER_SSH_KEY` - приватный SSH ключ
- `SERVER_PORT` - порт SSH (обычно 22)

### Systemd сервис

После установки сервис управляется через systemd:

```bash
# Статус сервиса
sudo systemctl status qualitycontrolsuite

# Перезапуск
sudo systemctl restart qualitycontrolsuite

# Логи
sudo journalctl -u qualitycontrolsuite -f
```

## 📊 Примеры отчётов

### HTML отчёт
- Интерактивные графики качества
- Таблицы со статистикой
- Цветовая индикация проблем

### JSON отчёт
```json
{
  "file_type": "fastq",
  "total_reads": 1000000,
  "metrics": {
    "mean_quality": 32.5,
    "gc_content": 45.2,
    "mean_read_length": 150
  },
  "quality_status": "PASS"
}
```

## 🔧 Разработка

### Запуск тестов
```bash
pytest tests/
```

### Добавление новых метрик
1. Добавить расчёт в соответствующий QC движок
2. Обновить пороги в config/qc_thresholds.yaml
3. Обновить генератор отчётов

## 📝 Лицензия

MIT License - см. файл LICENSE

## 👤 Автор

Разработано для проекта TaskContract2025

## 🤝 Вклад

Приветствуются pull requests. Для больших изменений сначала создайте issue.

## 📞 Поддержка

- GitHub Issues: https://github.com/otinoff/QualityControlSuite/issues
- Домен: https://qualitycontrolsuite.onff.ru

## ⚠️ Важные замечания

1. **Это НЕ полная платформа интеграции** - только контроль качества
2. **НЕ требует референсных геномов** - работает с существующими данными
3. **Минимальные зависимости** - легко устанавливается и обновляется
4. **Быстрая работа** - оптимизировано для больших файлов

---

**QualityControlSuite** - Простой, быстрый, эффективный контроль качества биологических данных.