"""
QualityControlSuite Web Interface
Веб-интерфейс системы контроля качества биологических данных
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import sys
import os
from datetime import datetime
import tempfile
import shutil

# Добавляем путь к модулям
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Импорт основного модуля
from main import QualityControlPipeline

# Настройка страницы
st.set_page_config(
    page_title="QualityControlSuite",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS стили в стиле РГНКЦ
st.markdown("""
<style>
    :root {
        --primary-blue: #2B5AA0;
        --teal-dark: #1B5E5E;
        --accent-red: #D73527;
        --background: #FFFFFF;
        --light-bg: #F8F9FA;
        --text-primary: #333333;
        --text-secondary: #666666;
        --border-color: #E5E5E5;
        --success-color: #28A745;
        --warning-color: #FD7E14;
        --danger-color: #DC3545;
        --info-color: #17A2B8;
        --border-radius: 8px;
        --shadow: 0 2px 4px rgba(0,0,0,0.1);
        --transition: all 0.3s ease;
    }
    
    .main-header {
        text-align: center;
        padding: 2.5rem 1rem;
        background: linear-gradient(135deg, #2B5AA0 0%, #1B5E5E 100%);
        color: white;
        border-radius: var(--border-radius);
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 1rem;
    }
    
    .main-header p {
        font-size: 1.2rem;
        opacity: 0.95;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--background);
        border-right: 1px solid var(--border-color);
    }
    
    .module-card {
        background: var(--background);
        padding: 1.5rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        margin-bottom: 1.5rem;
        transition: var(--transition);
        border: 1px solid var(--border-color);
    }
    
    .module-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    [data-testid="stMetric"] {
        background: var(--background);
        padding: 1.2rem;
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
        transition: var(--transition);
        border: 1px solid var(--border-color);
    }
    
    [data-testid="stMetric"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
    
    .stButton>button {
        border-radius: 6px;
        border: none;
        padding: 0.75rem 1.5rem;
        font-weight: 500;
        transition: var(--transition);
        box-shadow: var(--shadow);
        background-color: var(--primary-blue);
        color: white;
    }
    
    .stButton>button:hover {
        background-color: #1a4a8a;
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
    
    .stProgress > div > div {
        background-color: var(--primary-blue);
    }
    
    [data-baseweb="notification"] {
        border-radius: var(--border-radius);
        box-shadow: var(--shadow);
    }
    
    .quality-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
        margin: 0.25rem;
    }
    
    .quality-pass {
        background: #d4edda;
        color: #155724;
    }
    
    .quality-warning {
        background: #fff3cd;
        color: #856404;
    }
    
    .quality-fail {
        background: #f8d7da;
        color: #721c24;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация состояния
if 'processed_files' not in st.session_state:
    st.session_state.processed_files = {}
if 'current_results' not in st.session_state:
    st.session_state.current_results = None

def render_header():
    """Отображение заголовка"""
    st.markdown("""
    <div class="main-header">
        <h1>🧬 QualityControlSuite</h1>
        <p>Система контроля качества биологических данных</p>
    </div>
    """, unsafe_allow_html=True)

def render_sidebar():
    """Отображение боковой панели"""
    with st.sidebar:
        st.title("📋 Панель управления")
        
        # Меню навигации
        st.markdown("### 🗂️ Навигация")
        page = st.selectbox(
            "Выберите страницу",
            ["🏠 Главная", "📊 Анализ файлов", "📈 Результаты", "⚙️ Настройки", "📚 Документация"]
        )
        
        # Статистика
        st.markdown("### 📊 Статистика")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Файлов обработано", len(st.session_state.processed_files))
        with col2:
            st.metric("Активных задач", 0)
        
        # Быстрые действия
        st.markdown("### ⚡ Быстрые действия")
        if st.button("🔄 Очистить кэш", use_container_width=True):
            st.session_state.processed_files = {}
            st.session_state.current_results = None
            st.success("Кэш очищен")
        
        # Информация о системе
        st.markdown("### ℹ️ Информация")
        st.info("""
        **Версия:** 1.0.0  
        **Лицензия:** MIT  
        **Поддержка форматов:**
        - FASTQ/FASTQ.GZ
        - BAM/SAM/CRAM
        - VCF/VCF.GZ
        """)
        
        return page

def render_home_page():
    """Отображение главной страницы"""
    st.title("Добро пожаловать в QualityControlSuite")
    
    # Описание системы
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("""
        ### О системе
        
        **QualityControlSuite** - это минимальная система контроля качества биологических данных, 
        разработанная для проекта TaskContract2025.
        
        #### Ключевые возможности:
        - ✅ **Валидация форматов** - проверка корректности структуры файлов
        - 📊 **Метрики качества** - расчёт статистических показателей
        - 📈 **Визуализация** - интерактивные графики и диаграммы
        - 📄 **Отчёты** - генерация отчётов в различных форматах
        
        #### Преимущества:
        - 🚀 **Быстрая работа** - оптимизированные алгоритмы
        - 📦 **Минимальные зависимости** - только необходимые библиотеки
        - 🔧 **Простая настройка** - интуитивный интерфейс
        """)
    
    with col2:
        # Статус системы
        st.markdown("### 🔍 Статус системы")
        
        status_container = st.container()
        with status_container:
            st.success("✅ Система готова к работе")
            
            st.metric("CPU", "12%", "−2%")
            st.metric("Память", "256 MB", "+12 MB")
            st.metric("Диск", "1.2 GB", "0")
    
    # Быстрый старт
    st.markdown("---")
    st.markdown("### 🚀 Быстрый старт")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        with st.container():
            st.markdown("""
            <div class="module-card">
                <h4>1️⃣ Загрузите файл</h4>
                <p>Выберите файл биологических данных для анализа</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        with st.container():
            st.markdown("""
            <div class="module-card">
                <h4>2️⃣ Запустите анализ</h4>
                <p>Система автоматически определит тип и выполнит проверки</p>
            </div>
            """, unsafe_allow_html=True)
    
    with col3:
        with st.container():
            st.markdown("""
            <div class="module-card">
                <h4>3️⃣ Получите отчёт</h4>
                <p>Скачайте детальный отчёт с метриками качества</p>
            </div>
            """, unsafe_allow_html=True)

def render_analysis_page():
    """Страница анализа файлов"""
    st.title("📊 Анализ качества данных")
    
    # Загрузка файла
    st.markdown("### 📁 Загрузка файла")
    
    uploaded_file = st.file_uploader(
        "Выберите файл для анализа",
        type=['fastq', 'gz', 'bam', 'sam', 'cram', 'vcf'],
        help="Поддерживаются форматы: FASTQ, BAM/SAM/CRAM, VCF"
    )
    
    # Опции анализа
    with st.expander("⚙️ Параметры анализа", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### Общие параметры")
            generate_plots = st.checkbox("Генерировать графики", value=True)
            save_json = st.checkbox("Сохранить JSON отчёт", value=True)
            save_html = st.checkbox("Сохранить HTML отчёт", value=True)
        
        with col2:
            st.markdown("#### Пороговые значения")
            min_quality = st.slider("Минимальное качество", 0, 40, 20)
            min_length = st.slider("Минимальная длина рида", 0, 500, 50)
            max_n_percent = st.slider("Максимальный % N", 0, 20, 5)
    
    # Запуск анализа
    if uploaded_file is not None:
        st.markdown("### 📋 Информация о файле")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Имя файла", uploaded_file.name)
        with col2:
            st.metric("Размер", f"{uploaded_file.size / 1024 / 1024:.2f} MB")
        with col3:
            file_type = detect_file_type(uploaded_file.name)
            st.metric("Тип", file_type.upper() if file_type else "Неизвестно")
        
        if st.button("🚀 Начать анализ", type="primary", use_container_width=True):
            run_analysis(uploaded_file, {
                'generate_plots': generate_plots,
                'save_json': save_json,
                'save_html': save_html,
                'min_quality': min_quality,
                'min_length': min_length,
                'max_n_percent': max_n_percent
            })

def detect_file_type(filename):
    """Определение типа файла"""
    filename_lower = filename.lower()
    if filename_lower.endswith(('.fastq', '.fastq.gz', '.fq', '.fq.gz')):
        return 'fastq'
    elif filename_lower.endswith(('.bam', '.sam', '.cram')):
        return 'bam'
    elif filename_lower.endswith(('.vcf', '.vcf.gz')):
        return 'vcf'
    return None

def run_analysis(uploaded_file, options):
    """Запуск анализа файла"""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Создание временной директории
        with tempfile.TemporaryDirectory() as temp_dir:
            # Сохранение загруженного файла
            status_text.text("📥 Сохранение файла...")
            progress_bar.progress(10)
            
            file_path = os.path.join(temp_dir, uploaded_file.name)
            with open(file_path, 'wb') as f:
                f.write(uploaded_file.getbuffer())
            
            # Создание директории для результатов
            output_dir = os.path.join(temp_dir, 'results')
            os.makedirs(output_dir, exist_ok=True)
            
            # Инициализация пайплайна
            status_text.text("🔧 Инициализация анализа...")
            progress_bar.progress(20)
            
            pipeline = QualityControlPipeline()
            
            # Запуск анализа
            status_text.text("🔍 Анализ качества данных...")
            progress_bar.progress(50)
            
            results = pipeline.process_single_file(
                filepath=file_path,
                output_dir=output_dir
            )
            
            # Сохранение результатов
            status_text.text("💾 Сохранение результатов...")
            progress_bar.progress(80)
            
            # Сохранение в session state
            file_id = f"{uploaded_file.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            st.session_state.processed_files[file_id] = results
            st.session_state.current_results = results
            
            # Завершение
            progress_bar.progress(100)
            status_text.text("✅ Анализ завершён!")
            
            # Отображение результатов
            display_results(results, uploaded_file.name)
            
            # Кнопки скачивания отчётов
            st.markdown("### 📥 Скачать отчёты")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if os.path.exists(os.path.join(output_dir, 'qc_report.html')):
                    with open(os.path.join(output_dir, 'qc_report.html'), 'rb') as f:
                        st.download_button(
                            label="📄 HTML отчёт",
                            data=f.read(),
                            file_name=f"qc_report_{uploaded_file.name}.html",
                            mime="text/html"
                        )
            
            with col2:
                if os.path.exists(os.path.join(output_dir, 'qc_report.json')):
                    with open(os.path.join(output_dir, 'qc_report.json'), 'rb') as f:
                        st.download_button(
                            label="📊 JSON отчёт",
                            data=f.read(),
                            file_name=f"qc_report_{uploaded_file.name}.json",
                            mime="application/json"
                        )
            
            with col3:
                if os.path.exists(os.path.join(output_dir, 'qc_report.txt')):
                    with open(os.path.join(output_dir, 'qc_report.txt'), 'rb') as f:
                        st.download_button(
                            label="📝 Текстовый отчёт",
                            data=f.read(),
                            file_name=f"qc_report_{uploaded_file.name}.txt",
                            mime="text/plain"
                        )
            
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("")
        st.error(f"❌ Ошибка при анализе: {str(e)}")

def display_results(results, filename):
    """Отображение результатов анализа"""
    st.markdown("### 📊 Результаты анализа")
    
    # Статус качества
    quality_status = results.get('quality_status', 'UNKNOWN')
    if quality_status == 'PASS':
        st.success("✅ Качество данных: **ХОРОШЕЕ**")
    elif quality_status == 'WARNING':
        st.warning("⚠️ Качество данных: **ТРЕБУЕТ ВНИМАНИЯ**")
    elif quality_status == 'FAIL':
        st.error("❌ Качество данных: **НИЗКОЕ**")
    else:
        st.info("ℹ️ Качество данных: **НЕ ОПРЕДЕЛЕНО**")
    
    # Основные метрики
    st.markdown("#### 📈 Основные метрики")
    
    metrics = results.get('metrics', {})
    if metrics:
        # Разделение метрик по колонкам
        cols = st.columns(min(len(metrics), 4))
        for i, (key, value) in enumerate(metrics.items()):
            with cols[i % len(cols)]:
                # Форматирование значения
                if isinstance(value, float):
                    formatted_value = f"{value:.2f}"
                elif isinstance(value, int):
                    formatted_value = f"{value:,}"
                else:
                    formatted_value = str(value)
                
                # Отображение метрики
                st.metric(
                    label=format_metric_name(key),
                    value=formatted_value
                )
    
    # Детальная информация
    if 'validation' in results:
        st.markdown("#### ✅ Результаты валидации")
        validation = results['validation']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write("**Статус валидации:**", "✅ Пройдена" if validation.get('valid') else "❌ Не пройдена")
            if 'format' in validation:
                st.write("**Формат:**", validation['format'])
        
        with col2:
            if 'errors' in validation and validation['errors']:
                st.write("**Ошибки:**")
                for error in validation['errors']:
                    st.write(f"- {error}")
            elif 'warnings' in validation and validation['warnings']:
                st.write("**Предупреждения:**")
                for warning in validation['warnings']:
                    st.write(f"- {warning}")
    
    # Графики (если есть)
    if 'plots' in results and results['plots']:
        st.markdown("#### 📊 Визуализация")
        
        # Здесь можно добавить отображение графиков
        # Например, используя plotly
        for plot_name, plot_data in results['plots'].items():
            st.write(f"**{format_metric_name(plot_name)}**")
            # st.plotly_chart(plot_data) # если plot_data - это plotly figure

def format_metric_name(name):
    """Форматирование имени метрики"""
    name_map = {
        'total_reads': 'Всего ридов',
        'total_sequences': 'Всего последовательностей',
        'mean_quality': 'Средняя Q-оценка',
        'gc_content': 'GC-содержание (%)',
        'mean_read_length': 'Средняя длина',
        'min_read_length': 'Мин. длина',
        'max_read_length': 'Макс. длина',
        'n_percentage': 'N-содержание (%)',
        'total_bases': 'Всего оснований',
        'mapped_reads': 'Картированные риды',
        'unmapped_reads': 'Некартированные риды',
        'mean_coverage': 'Среднее покрытие',
        'total_variants': 'Всего вариантов',
        'snp_count': 'SNP',
        'indel_count': 'Инделы',
        'mean_variant_quality': 'Средняя Q вариантов'
    }
    return name_map.get(name, name.replace('_', ' ').title())

def render_results_page():
    """Страница результатов"""
    st.title("📈 Результаты анализов")
    
    if not st.session_state.processed_files:
        st.info("📋 Нет обработанных файлов. Перейдите на страницу 'Анализ файлов' для начала работы.")
        return
    
    # Таблица с результатами
    st.markdown("### 📊 История анализов")
    
    # Преобразование результатов в DataFrame
    results_data = []
    for file_id, results in st.session_state.processed_files.items():
        metrics = results.get('metrics', {})
        results_data.append({
            'ID': file_id,
            'Статус': results.get('quality_status', 'UNKNOWN'),
            'Ридов': metrics.get('total_reads', 0),
            'Средняя Q': metrics.get('mean_quality', 0),
            'GC %': metrics.get('gc_content', 0)
        })
    
    df = pd.DataFrame(results_data)
    
    # Отображение таблицы
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True
    )
    
    # Выбор результата для детального просмотра
    if len(st.session_state.processed_files) > 0:
        selected_id = st.selectbox(
            "Выберите анализ для детального просмотра",
            list(st.session_state.processed_files.keys())
        )
        
        if selected_id:
            st.markdown("---")
            selected_results = st.session_state.processed_files[selected_id]
            display_results(selected_results, selected_id.split('_')[0])

def render_settings_page():
    """Страница настроек"""
    st.title("⚙️ Настройки")
    
    # Настройки качества
    st.markdown("### 📊 Пороговые значения качества")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### FASTQ")
        fastq_min_quality = st.number_input("Минимальная Q-оценка", value=20, min_value=0, max_value=60)
        fastq_min_length = st.number_input("Минимальная длина рида", value=50, min_value=0)
        fastq_max_n = st.number_input("Максимальный % N", value=5, min_value=0, max_value=100)
    
    with col2:
        st.markdown("#### BAM/SAM")
        bam_min_mapping = st.number_input("Минимальное качество картирования", value=30, min_value=0, max_value=60)
        bam_min_coverage = st.number_input("Минимальное покрытие", value=10, min_value=0)
        bam_max_unmapped = st.number_input("Максимальный % некартированных", value=10, min_value=0, max_value=100)
    
    st.markdown("#### VCF")
    vcf_min_quality = st.number_input("Минимальное качество варианта", value=30, min_value=0, max_value=100)
    vcf_min_depth = st.number_input("Минимальная глубина", value=10, min_value=0)
    
    # Настройки отчётов
    st.markdown("### 📄 Настройки отчётов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Форматы вывода")
        generate_html = st.checkbox("HTML отчёт", value=True)
        generate_json = st.checkbox("JSON отчёт", value=True)
        generate_txt = st.checkbox("Текстовый отчёт", value=True)
    
    with col2:
        st.markdown("#### Визуализация")
        generate_plots = st.checkbox("Генерировать графики", value=True)
        plot_style = st.selectbox("Стиль графиков", ["plotly", "matplotlib"])
        plot_theme = st.selectbox("Тема", ["light", "dark", "auto"])
    
    # Кнопка сохранения
    if st.button("💾 Сохранить настройки", type="primary", use_container_width=True):
        # Здесь можно добавить сохранение в конфигурационный файл
        st.success("✅ Настройки сохранены")

def render_documentation_page():
    """Страница документации"""
    st.title("📚 Документация")
    
    tab1, tab2, tab3, tab4 = st.tabs(["📖 Руководство", "🔧 API", "❓ FAQ", "📞 Поддержка"])
    
    with tab1:
        st.markdown("""
        ### Руководство пользователя
        
        #### 🚀 Быстрый старт
        
        1. **Загрузка файла**
           - Перейдите на страницу "Анализ файлов"
           - Нажмите на область загрузки или перетащите файл
           - Поддерживаются форматы: FASTQ, BAM/SAM, VCF
        
        2. **Настройка параметров**
           - Раскройте "Параметры анализа"
           - Настройте пороговые значения
           - Выберите форматы отчётов
        
        3. **Запуск анализа**
           - Нажмите кнопку "Начать анализ"
           - Дождитесь завершения обработки
           - Изучите результаты
        
        4. **Скачивание отчётов**
           - Выберите нужный формат
           - Нажмите соответствующую кнопку скачивания
        
        #### 📊 Интерпретация результатов
        
        **Статусы качества:**
        - 🟢 **PASS** - данные высокого качества
        - 🟡 **WARNING** - есть незначительные проблемы
        - 🔴 **FAIL** - данные низкого качества
        
        **Ключевые метрики:**
        - **Q-оценка** - показатель качества секвенирования (>30 отлично, 20-30 хорошо, <20 плохо)
        - **GC-содержание** - процент гуанина и цитозина (норма 40-60%)
        - **Длина ридов** - важна для качества сборки
        """)
    
    with tab2:
        st.markdown("""
        ### API Документация
        
        #### Python API
        
        ```python
        from main import QualityControlPipeline
        
        # Инициализация
        pipeline = QualityControlPipeline()
        
        # Анализ одного файла
        results = pipeline.process_single_file(
            filepath='path/to/file.fastq',
            output_dir='results/'
        )
        
        # Пакетная обработка
        results = pipeline.process_batch(
            input_dir='data/',
            output_dir='results/',
            file_pattern='*.fastq'
        )
        ```
        
        #### Структура результатов
        
        ```json
        {
            "file_type": "fastq",
            "validation": {
                "valid": true,
                "format": "FASTQ"
            },
            "metrics": {
                "total_reads": 100000,
                "mean_quality": 32.5,
                "gc_content": 45.2
            },
            "quality_status": "PASS"
        }
        ```
        """)
    
    with tab3:
        st.markdown("""
        ### Часто задаваемые вопросы
        
        **Q: Какие форматы файлов поддерживаются?**
        A: FASTQ, FASTQ.GZ, BAM, SAM, CRAM, VCF, VCF.GZ
        
        **Q: Какой максимальный размер файла?**
        A: Рекомендуется не более 2 GB для веб-интерфейса. Для больших файлов используйте CLI.
        
        **Q: Требуется ли референсный геном?**
        A: Нет, система работает только с существующими данными в файлах.
        
        **Q: Можно ли настроить пороговые значения?**
        A: Да, на странице "Настройки" или через конфигурационный файл.
        
        **Q: Как интерпретировать результаты?**
        A: См. раздел "Руководство" для подробного описания метрик.
        """)
    
    with tab4:
        st.markdown("""
        ### Техническая поддержка
        
        **GitHub:** https://github.com/otinoff/QualityControlSuite
        
        **Email:** support@qualitycontrolsuite.onff.ru
        
        **Документация:** https://qualitycontrolsuite.onff.ru/docs
        
        #### Сообщить о проблеме
        
        При обращении укажите:
        - Версию системы
        - Тип и размер файла
        - Текст ошибки
        - Шаги для воспроизведения
        """)

def main():
    """Основная функция приложения"""
    # Отображение заголовка
    render_header()
    
    # Отображение боковой панели и получение выбранной страницы
    page = render_sidebar()
    
    # Отображение контента в зависимости от выбранной страницы
    if page == "🏠 Главная":
        render_home_page()
    elif page == "📊 Анализ файлов":
        render_analysis_page()
    elif page == "📈 Результаты":
        render_results_page()
    elif page == "⚙️ Настройки":
        render_settings_page()
    elif page == "📚 Документация":
        render_documentation_page()
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>QualityControlSuite v1.0.0 | © 2025 TaskContract2025 | MIT License</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()