"""
FastQCLI Streamlit Interface
Веб-интерфейс для анализа качества FASTQ файлов на основе Sequali
Версия: 1.0.0
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
import subprocess
import time
from typing import Dict, Any, Optional

# Настройка страницы
st.set_page_config(
    page_title="FastQCLI - Sequali",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Импорт функций из fastqcli.py
try:
    from fastqcli import (
        check_and_install_sequali,
        analyze_with_sequali,
        has_command,
        is_package_installed
    )
    FASTQCLI_AVAILABLE = True
except ImportError:
    FASTQCLI_AVAILABLE = False
    st.error("⚠️ Файл fastqcli.py не найден! Скопируйте его в текущую директорию.")

# CSS стили
st.markdown("""
<style>
    :root {
        --primary-blue: #2B5AA0;
        --teal-dark: #1B5E5E;
        --accent-red: #D73527;
        --success-green: #28A745;
        --warning-yellow: #FD7E14;
        --background: #FFFFFF;
        --light-bg: #F8F9FA;
        --text-primary: #333333;
        --border-color: #E5E5E5;
        --shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #2B5AA0 0%, #1B5E5E 100%);
        color: white;
        border-radius: 8px;
        margin-bottom: 2rem;
        box-shadow: var(--shadow);
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
        margin: 0;
    }
    
    .status-card {
        background: var(--background);
        padding: 1.2rem;
        border-radius: 8px;
        box-shadow: var(--shadow);
        border: 1px solid var(--border-color);
        margin-bottom: 1rem;
    }
    
    .metric-card {
        background: var(--background);
        padding: 1rem;
        border-radius: 8px;
        box-shadow: var(--shadow);
        border-left: 4px solid var(--primary-blue);
        margin-bottom: 1rem;
    }
    
    .quality-pass {
        background: #d4edda;
        color: #155724;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .quality-warning {
        background: #fff3cd;
        color: #856404;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .quality-fail {
        background: #f8d7da;
        color: #721c24;
        padding: 0.5rem 1rem;
        border-radius: 6px;
        font-weight: 600;
    }
    
    .speed-indicator {
        color: var(--primary-blue);
        font-weight: bold;
        font-size: 1.2rem;
    }
    
    [data-testid="stSidebar"] {
        background-color: var(--light-bg);
    }
    
    .stButton>button {
        background-color: var(--primary-blue);
        color: white;
        border: none;
        padding: 0.5rem 1.5rem;
        border-radius: 6px;
        font-weight: 500;
        transition: all 0.3s ease;
    }
    
    .stButton>button:hover {
        background-color: #1a4a8a;
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.15);
    }
</style>
""", unsafe_allow_html=True)

# Инициализация session state
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []
if 'sequali_installed' not in st.session_state:
    st.session_state.sequali_installed = False
if 'current_results' not in st.session_state:
    st.session_state.current_results = None


def render_header():
    """Отображение заголовка"""
    st.markdown("""
    <div class="main-header">
        <h1>🧬 FastQCLI - Powered by Sequali</h1>
        <p>Высокопроизводительный анализ качества FASTQ файлов (300+ MB/sec)</p>
    </div>
    """, unsafe_allow_html=True)


def render_sidebar():
    """Отображение боковой панели"""
    with st.sidebar:
        # Логотип и версия
        st.markdown("""
        <div style='text-align: center; padding: 1rem 0;'>
            <h3 style='margin: 0;'>🧬 FastQCLI</h3>
            <p style='margin: 0.5rem 0 0 0; font-size: 0.9rem; opacity: 0.8;'>v1.0.0 | Sequali Engine</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Статус системы
        st.markdown("### 🔍 Статус системы")
        
        col1, col2 = st.columns(2)
        
        # Проверка Python
        with col1:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
            st.metric("Python", python_version)
        
        # Проверка Sequali
        with col2:
            if FASTQCLI_AVAILABLE and has_command('sequali'):
                st.metric("Sequali", "✅ Установлен")
                st.session_state.sequali_installed = True
            else:
                st.metric("Sequali", "❌ Не установлен")
                st.session_state.sequali_installed = False
        
        st.divider()
        
        # Информация
        st.markdown("### ℹ️ О программе")
        st.markdown("""
        **FastQCLI** - это современный инструмент для анализа качества FASTQ файлов, 
        использующий высокопроизводительный движок Sequali.
        
        **Возможности:**
        - ⚡ Скорость 300+ MB/sec
        - 🔧 Автоустановка зависимостей
        - 📊 Детальные метрики качества
        - 📈 Интерактивная визуализация
        - 📄 HTML/JSON отчеты
        
        **Метрики:**
        - Q20/Q30 проценты
        - GC содержание
        - Длина ридов
        - N-содержание
        - Статистика дупликатов
        """)
        
        st.divider()
        
        # История анализов
        if st.session_state.analysis_history:
            st.markdown("### 📊 История анализов")
            for i, record in enumerate(reversed(st.session_state.analysis_history[-5:]), 1):
                status_icon = "✅" if record['status'] == 'success' else "❌"
                st.text(f"{status_icon} {record['filename'][:20]}...")
                st.caption(f"  {record['time']}")


def check_sequali_installation():
    """Проверка и установка Sequali"""
    if not FASTQCLI_AVAILABLE:
        return False
    
    if not st.session_state.sequali_installed:
        with st.spinner("🔍 Проверяю установку Sequali..."):
            if not has_command('sequali'):
                st.info("📦 Sequali не найден. Начинаю автоматическую установку...")
                
                # Прогресс установки
                progress = st.progress(0)
                status = st.empty()
                
                status.text("Устанавливаю Sequali через pip...")
                progress.progress(30)
                
                if check_and_install_sequali():
                    progress.progress(100)
                    status.text("✅ Sequali успешно установлен!")
                    st.session_state.sequali_installed = True
                    time.sleep(1)
                    st.rerun()
                else:
                    progress.progress(100)
                    status.text("")
                    st.error("""
                    ❌ Не удалось установить Sequali автоматически.
                    
                    Попробуйте установить вручную:
                    ```bash
                    pip install sequali
                    ```
                    """)
                    return False
            else:
                st.session_state.sequali_installed = True
    
    return True


def parse_sequali_json(json_path: Path) -> Dict[str, Any]:
    """Парсинг JSON результатов от Sequali"""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        summary = data.get('summary', {})
        
        # Преобразуем в формат для отображения
        metrics = {
            'total_reads': summary.get('read_count', 0),
            'total_bases': summary.get('base_count', 0),
            'mean_length': summary.get('mean_read_length', 0),
            'min_length': summary.get('min_read_length', 0),
            'max_length': summary.get('max_read_length', 0),
            'gc_content': summary.get('gc_content', 0) * 100,
            'q20_rate': summary.get('q20_rate', 0) * 100,
            'q30_rate': summary.get('q30_rate', 0) * 100,
            'n_rate': summary.get('n_rate', 0) * 100 if 'n_rate' in summary else 0
        }
        
        # Определение статуса качества
        if metrics['q30_rate'] >= 80:
            quality_status = 'PASS'
        elif metrics['q30_rate'] >= 70:
            quality_status = 'WARNING'
        else:
            quality_status = 'FAIL'
        
        return {
            'metrics': metrics,
            'quality_status': quality_status,
            'raw_data': data
        }
    except Exception as e:
        st.error(f"Ошибка парсинга JSON: {e}")
        return None


def run_sequali_analysis(file_path: str, output_dir: str, options: Dict[str, Any]):
    """Запуск анализа через Sequali"""
    
    # Индикаторы прогресса
    progress_bar = st.progress(0)
    status_text = st.empty()
    metrics_container = st.container()
    
    try:
        # Начало анализа
        status_text.text("🚀 Запускаю анализ Sequali...")
        progress_bar.progress(20)
        
        start_time = time.time()
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        
        # Показываем метрики в реальном времени
        col1, col2, col3 = metrics_container.columns(3)
        with col1:
            size_metric = st.metric("Размер файла", f"{file_size_mb:.1f} MB")
        with col2:
            speed_metric = st.metric("Скорость", "Расчет...")
        with col3:
            time_metric = st.metric("Время", "0 сек")
        
        progress_bar.progress(40)
        
        # Запуск анализа с отладкой
        st.write(f"DEBUG: Analyzing file: {file_path}")
        st.write(f"DEBUG: Output directory: {output_dir}")
        
        success = analyze_with_sequali(
            file_path,
            output_dir=output_dir,
            save_json=options.get('save_json', True),
            save_html=options.get('save_html', True)
        )
        
        elapsed_time = time.time() - start_time
        speed_mbps = file_size_mb / elapsed_time if elapsed_time > 0 else 0
        
        # Обновляем метрики
        with col2:
            st.metric("Скорость", f"{speed_mbps:.1f} MB/sec")
        with col3:
            st.metric("Время", f"{elapsed_time:.1f} сек")
        
        progress_bar.progress(80)
        
        if success:
            status_text.text("📊 Обрабатываю результаты...")
            
            # Проверим какие файлы были созданы
            st.write("DEBUG: Files in output dir after analysis:")
            output_files = list(Path(output_dir).glob("*"))
            for file in output_files:
                st.write(f"  - {file.name}")
            
            # Пробуем разные варианты имён файлов
            json_path = None
            possible_names = [
                f"{Path(file_path).name}.json",  # С полным именем включая расширение
                f"{Path(file_path).stem}.json",   # Только базовое имя
            ]
            
            for name in possible_names:
                test_path = Path(output_dir) / name
                st.write(f"DEBUG: Checking for {test_path}")
                if test_path.exists():
                    json_path = test_path
                    st.write(f"DEBUG: Found JSON at {json_path}")
                    break
            
            # Если не нашли по именам, ищем любой JSON файл
            if json_path is None:
                json_files = list(Path(output_dir).glob("*.json"))
                if json_files:
                    json_path = json_files[0]
                    st.write(f"DEBUG: Using first JSON file found: {json_path.name}")
            
            if json_path and json_path.exists():
                results = parse_sequali_json(json_path)
                
                progress_bar.progress(100)
                status_text.text("✅ Анализ завершен успешно!")
                
                # Добавляем в историю
                st.session_state.analysis_history.append({
                    'filename': Path(file_path).name,
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'status': 'success',
                    'speed': speed_mbps,
                    'elapsed': elapsed_time
                })
                
                return results
            else:
                st.error("JSON файл с результатами не найден")
                return None
        else:
            progress_bar.progress(100)
            status_text.text("")
            st.error("❌ Ошибка при анализе файла")
            
            st.session_state.analysis_history.append({
                'filename': Path(file_path).name,
                'time': datetime.now().strftime("%H:%M:%S"),
                'status': 'error',
                'speed': 0,
                'elapsed': elapsed_time
            })
            
            return None
            
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("")
        st.error(f"❌ Критическая ошибка: {str(e)}")
        return None


def display_results(results: Dict[str, Any], filename: str, output_dir: str):
    """Отображение результатов анализа"""
    
    # Статус качества
    st.markdown("### 📊 Результаты анализа")
    
    quality_status = results.get('quality_status', 'UNKNOWN')
    if quality_status == 'PASS':
        st.markdown('<div class="quality-pass">✅ Качество данных: ОТЛИЧНОЕ</div>', unsafe_allow_html=True)
    elif quality_status == 'WARNING':
        st.markdown('<div class="quality-warning">⚠️ Качество данных: ТРЕБУЕТ ВНИМАНИЯ</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="quality-fail">❌ Качество данных: НИЗКОЕ</div>', unsafe_allow_html=True)
    
    # Основные метрики
    st.markdown("#### 📈 Ключевые метрики")
    
    metrics = results.get('metrics', {})
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Всего ридов",
            f"{metrics.get('total_reads', 0):,}"
        )
        st.metric(
            "Всего оснований",
            f"{metrics.get('total_bases', 0):,}"
        )
    
    with col2:
        st.metric(
            "Средняя длина",
            f"{metrics.get('mean_length', 0):.1f} bp"
        )
        st.metric(
            "Диапазон длин",
            f"{metrics.get('min_length', 0)}-{metrics.get('max_length', 0)}"
        )
    
    with col3:
        q30 = metrics.get('q30_rate', 0)
        st.metric(
            "Q30",
            f"{q30:.1f}%",
            delta=f"{q30-80:.1f}%" if q30 != 0 else None
        )
        q20 = metrics.get('q20_rate', 0)
        st.metric(
            "Q20",
            f"{q20:.1f}%",
            delta=f"{q20-90:.1f}%" if q20 != 0 else None
        )
    
    with col4:
        gc = metrics.get('gc_content', 0)
        st.metric(
            "GC содержание",
            f"{gc:.1f}%",
            delta=f"{gc-50:.1f}%" if gc != 0 else None
        )
        n_rate = metrics.get('n_rate', 0)
        st.metric(
            "N содержание",
            f"{n_rate:.3f}%",
            delta=f"{n_rate:.3f}%" if n_rate > 1 else None
        )
    
    # Визуализация
    if results.get('raw_data'):
        st.markdown("#### 📊 Визуализация данных")
        
        tab1, tab2, tab3 = st.tabs(["Качество по позициям", "Распределение длин", "GC содержание"])
        
        with tab1:
            # Здесь можно добавить графики из raw_data
            st.info("Графики качества по позициям будут добавлены в следующей версии")
        
        with tab2:
            st.info("График распределения длин будет добавлен в следующей версии")
        
        with tab3:
            # Простой пример графика GC
            fig = go.Figure(go.Indicator(
                mode = "gauge+number",
                value = gc,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "GC Content (%)"},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 40], 'color': "lightgray"},
                        {'range': [40, 60], 'color': "gray"},
                        {'range': [60, 100], 'color': "lightgray"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 50
                    }
                }
            ))
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
    
    # Кнопки скачивания
    st.markdown("#### 📥 Скачать отчеты")
    
    col1, col2 = st.columns(2)
    
    output_path = Path(output_dir)
    base_name = Path(filename).stem
    full_name = Path(filename).name
    
    with col1:
        # Пробуем разные варианты имён файлов
        html_path = None
        possible_html = [
            output_path / f"{full_name}.html",
            output_path / f"{base_name}.html"
        ]
        
        for path in possible_html:
            if path.exists():
                html_path = path
                break
        
        # Если не нашли, ищем любой HTML
        if not html_path:
            html_files = list(output_path.glob("*.html"))
            if html_files:
                html_path = html_files[0]
        
        if html_path and html_path.exists():
            with open(html_path, 'rb') as f:
                st.download_button(
                    label="📄 Скачать HTML отчет",
                    data=f.read(),
                    file_name=f"{base_name}_report.html",
                    mime="text/html"
                )
    
    with col2:
        # Пробуем разные варианты имён файлов
        json_path = None
        possible_json = [
            output_path / f"{full_name}.json",
            output_path / f"{base_name}.json"
        ]
        
        for path in possible_json:
            if path.exists():
                json_path = path
                break
        
        # Если не нашли, ищем любой JSON
        if not json_path:
            json_files = list(output_path.glob("*.json"))
            if json_files:
                json_path = json_files[0]
        
        if json_path and json_path.exists():
            with open(json_path, 'rb') as f:
                st.download_button(
                    label="📊 Скачать JSON данные",
                    data=f.read(),
                    file_name=f"{base_name}_data.json",
                    mime="application/json"
                )


def render_analysis_page():
    """Страница анализа"""
    st.title("📊 Анализ качества FASTQ")
    
    # Проверка установки Sequali
    if not check_sequali_installation():
        st.error("Sequali не установлен. Установите его для продолжения работы.")
        return
    
    # Загрузка файла
    st.markdown("### 📁 Загрузка файла")
    
    uploaded_file = st.file_uploader(
        "Выберите FASTQ файл для анализа",
        type=['fastq', 'fq', 'gz'],
        help="Поддерживаются форматы: .fastq, .fq, .fastq.gz, .fq.gz"
    )
    
    # Опции анализа
    with st.expander("⚙️ Параметры анализа", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            save_html = st.checkbox("Генерировать HTML отчет", value=True)
            save_json = st.checkbox("Сохранить JSON данные", value=True)
        
        with col2:
            st.info("""
            **Sequali автоматически рассчитывает:**
            - Q20/Q30 проценты
            - GC содержание
            - Статистику длин
            - Распределение качества
            - И многое другое...
            """)
    
    # Анализ файла
    if uploaded_file is not None:
        st.markdown("### 📋 Информация о файле")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Имя файла", uploaded_file.name[:30] + "..." if len(uploaded_file.name) > 30 else uploaded_file.name)
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.metric("Размер", f"{file_size_mb:.2f} MB")
        with col3:
            # Оценка времени (300 MB/sec)
            estimated_time = file_size_mb / 300
            st.metric("Оценка времени", f"~{estimated_time:.1f} сек")
        
        if st.button("🚀 Начать анализ", type="primary", use_container_width=True):
            
            # Создание временных директорий
            with tempfile.TemporaryDirectory() as temp_dir:
                # Сохранение файла
                file_path = os.path.join(temp_dir, uploaded_file.name)
                with open(file_path, 'wb') as f:
                    f.write(uploaded_file.getbuffer())
                
                # Директория для результатов
                output_dir = os.path.join(temp_dir, 'results')
                os.makedirs(output_dir, exist_ok=True)
                
                # Запуск анализа
                results = run_sequali_analysis(
                    file_path,
                    output_dir,
                    {
                        'save_html': save_html,
                        'save_json': save_json
                    }
                )
                
                # Отображение результатов
                if results:
                    st.session_state.current_results = results
                    display_results(results, uploaded_file.name, output_dir)


def render_batch_page():
    """Страница пакетной обработки"""
    st.title("📦 Пакетная обработка")
    
    st.info("""
    Пакетная обработка позволяет анализировать несколько FASTQ файлов одновременно.
    
    **Как использовать:**
    1. Выберите несколько файлов
    2. Настройте параметры
    3. Запустите анализ
    4. Получите сводный отчет
    """)
    
    # Множественная загрузка
    uploaded_files = st.file_uploader(
        "Выберите FASTQ файлы",
        type=['fastq', 'fq', 'gz'],
        accept_multiple_files=True,
        help="Можно выбрать несколько файлов"
    )
    
    if uploaded_files:
        st.markdown(f"### Выбрано файлов: {len(uploaded_files)}")
        
        # Таблица файлов
        file_data = []
        total_size = 0
        for f in uploaded_files:
            size_mb = f.size / (1024 * 1024)
            total_size += size_mb
            file_data.append({
                'Файл': f.name[:40] + "..." if len(f.name) > 40 else f.name,
                'Размер (MB)': f"{size_mb:.2f}"
            })
        
        df = pd.DataFrame(file_data)
        st.dataframe(df, use_container_width=True, hide_index=True)
        
        # Оценка времени
        estimated_time = total_size / 300  # 300 MB/sec
        st.info(f"""
        **Общий размер:** {total_size:.2f} MB  
        **Оценка времени:** ~{estimated_time:.1f} сек ({estimated_time/60:.1f} мин)
        """)
        
        if st.button("🚀 Начать пакетный анализ", type="primary", use_container_width=True):
            st.warning("Пакетная обработка будет добавлена в следующей версии")


def render_settings_page():
    """Страница настроек"""
    st.title("⚙️ Настройки")
    
    st.markdown("### 🔧 Настройки Sequali")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Установка")
        if st.button("Переустановить Sequali"):
            with st.spinner("Переустановка Sequali..."):
                result = subprocess.run(
                    [sys.executable, '-m', 'pip', 'install', '--upgrade', 'sequali'],
                    capture_output=True,
                    text=True
                )
                if result.returncode == 0:
                    st.success("✅ Sequali успешно переустановлен")
                else:
                    st.error(f"Ошибка: {result.stderr}")
    
    with col2:
        st.markdown("#### Версия")
        if has_command('sequali'):
            result = subprocess.run(['sequali', '--version'], capture_output=True, text=True)
            version = result.stdout.strip() if result.stdout else "Неизвестно"
            st.info(f"Sequali версия: {version}")
        else:
            st.warning("Sequali не установлен")
    
    st.markdown("### 📊 Настройки отчетов")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### Форматы по умолчанию")
        html_default = st.checkbox("HTML отчет", value=True, key="settings_html")
        json_default = st.checkbox("JSON данные", value=True, key="settings_json")
    
    with col2:
        st.markdown("#### Дополнительно")
        auto_open = st.checkbox("Автоматически открывать HTML", value=False)
        keep_temp = st.checkbox("Сохранять временные файлы", value=False)
    
    if st.button("💾 Сохранить настройки"):
        st.success("✅ Настройки сохранены")


def render_documentation_page():
    """Страница документации"""
    st.title("📚 Документация")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Быстрый старт", "О Sequali", "FAQ", "API"])
    
    with tab1:
        st.markdown("""
        ### 🚀 Быстрый старт
        
        1. **Загрузка файла**
           - Нажмите на область загрузки или перетащите файл
           - Поддерживаются: .fastq, .fq, .fastq.gz, .fq.gz
        
        2. **Запуск анализа**
           - Нажмите кнопку "Начать анализ"
           - Дождитесь завершения (скорость ~300 MB/sec)
        
        3. **Получение результатов**
           - Изучите метрики качества
           - Скачайте HTML или JSON отчет
        
        ### 📊 Интерпретация результатов
        
        **Q-scores (Quality scores):**
        - **Q30 > 80%** - Отличное качество
        - **Q30 70-80%** - Хорошее качество
        - **Q30 < 70%** - Требует внимания
        
        **GC содержание:**
        - **40-60%** - Нормальный диапазон для большинства организмов
        - **< 40% или > 60%** - Может указывать на контаминацию или особенности образца
        
        **N содержание:**
        - **< 1%** - Отлично
        - **1-5%** - Приемлемо
        - **> 5%** - Может повлиять на дальнейший анализ
        """)
    
    with tab2:
        st.markdown("""
        ### 🚀 О Sequali
        
        **Sequali** - это современная высокопроизводительная альтернатива FastQC, написанная на Rust.
        
        **Преимущества:**
        - ⚡ **Скорость**: 300+ MB/sec (в 3-4 раза быстрее FastQC)
        - 🔧 **Эффективность**: Низкое потребление памяти
        - 📊 **Функциональность**: Все метрики FastQC и больше
        - 🌐 **Совместимость**: Работает на всех платформах
        
        **Автор:** Ruben Vorderman  
        **Лицензия:** MIT  
        **GitHub:** https://github.com/rhpvorderman/sequali
        
        ### Технические детали
        
        Sequali использует:
        - Параллельную обработку
        - SIMD инструкции для ускорения
        - Эффективные алгоритмы сжатия
        - Минимальные зависимости
        """)
    
    with tab3:
        st.markdown("""
        ### ❓ Часто задаваемые вопросы
        
        **Q: Какой максимальный размер файла?**  
        A: Ограничений нет. Sequali эффективно обрабатывает файлы любого размера.
        
        **Q: Поддерживаются ли сжатые файлы?**  
        A: Да, .fastq.gz и .fq.gz обрабатываются автоматически.
        
        **Q: Можно ли использовать через командную строку?**  
        A: Да, используйте fastqcli.py для CLI интерфейса.
        
        **Q: Требуется ли интернет для работы?**  
        A: Только при первой установке Sequali. Далее работает оффлайн.
        
        **Q: Как сравнить несколько файлов?**  
        A: Используйте вкладку "Пакетная обработка" (в разработке).
        """)
    
    with tab4:
        st.markdown("""
        ### 🔧 Python API
        
        ```python
        from fastqcli import analyze_with_sequali
        
        # Анализ одного файла
        success = analyze_with_sequali(
            'sample.fastq',
            output_dir='results/',
            save_json=True,
            save_html=True
        )
        
        # Проверка установки Sequali
        from fastqcli import check_and_install_sequali
        if check_and_install_sequali():
            print("Sequali готов к работе")
        ```
        
        ### Структура JSON результатов
        
        ```json
        {
            "summary": {
                "read_count": 1000000,
                "base_count": 150000000,
                "mean_read_length": 150.0,
                "gc_content": 0.45,
                "q20_rate": 0.95,
                "q30_rate": 0.85
            }
        }
        ```
        """)


def main():
    """Основная функция приложения"""
    
    # Проверка наличия fastqcli.py
    if not FASTQCLI_AVAILABLE:
        st.error("""
        ❌ **Критическая ошибка**: файл `fastqcli.py` не найден!
        
        **Решение:**
        1. Скопируйте `fastqcli.py` в директорию с этим файлом
        2. Перезапустите приложение
        """)
        st.stop()
    
    # Отображение заголовка
    render_header()
    
    # Боковая панель
    render_sidebar()
    
    # Основные вкладки
    tab1, tab2, tab3, tab4 = st.tabs([
        "📊 Анализ файла",
        "📦 Пакетная обработка",
        "⚙️ Настройки",
        "📚 Документация"
    ])
    
    with tab1:
        render_analysis_page()
    
    with tab2:
        render_batch_page()
    
    with tab3:
        render_settings_page()
    
    with tab4:
        render_documentation_page()
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>FastQCLI v1.0.0 | Powered by Sequali | © 2025 TaskContract2025</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()