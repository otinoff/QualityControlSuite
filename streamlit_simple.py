"""
FastQCLI Simplified Streamlit Interface
Веб-интерфейс для анализа качества FASTQ файлов с HTML проксированием
Версия: 2.0.0 - Упрощенная версия без JSON парсинга
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import sys
import os
from datetime import datetime
import tempfile
import time
from typing import Optional

# Настройка страницы
st.set_page_config(
    page_title="FastQCLI - Simple",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Импорт функций из fastqcli.py
try:
    from fastqcli import (
        check_and_install_sequali,
        analyze_with_sequali,
        has_command
    )
    FASTQCLI_AVAILABLE = True
except ImportError:
    FASTQCLI_AVAILABLE = False
    st.error("⚠️ Файл fastqcli.py не найден! Скопируйте его в текущую директорию.")

# CSS стили (минимальные)
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 1rem;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .main-header h1 {
        font-size: 2.5rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .main-header p {
        font-size: 1.1rem;
        opacity: 0.95;
    }
    
    .metrics-container {
        background: #f7f7f7;
        padding: 1rem;
        border-radius: 8px;
        margin: 1rem 0;
    }
    
    .success-message {
        background: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #28a745;
    }
    
    .error-message {
        background: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 6px;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)

# Инициализация session state
if 'sequali_installed' not in st.session_state:
    st.session_state.sequali_installed = False
if 'analysis_history' not in st.session_state:
    st.session_state.analysis_history = []


def render_header():
    """Отображение заголовка"""
    st.markdown("""
    <div class="main-header">
        <h1>🧬 FastQCLI Simplified</h1>
        <p>HTML проксирование отчетов Sequali - быстро и просто!</p>
    </div>
    """, unsafe_allow_html=True)


def check_sequali_installation():
    """Проверка и установка Sequali"""
    if not FASTQCLI_AVAILABLE:
        return False
    
    if not st.session_state.sequali_installed:
        with st.spinner("🔍 Проверяю установку Sequali..."):
            if not has_command('sequali'):
                st.info("📦 Устанавливаю Sequali...")
                if check_and_install_sequali():
                    st.session_state.sequali_installed = True
                    st.success("✅ Sequali установлен!")
                    time.sleep(1)
                    st.rerun()
                else:
                    st.error("❌ Не удалось установить Sequali автоматически")
                    return False
            else:
                st.session_state.sequali_installed = True
    
    return True


def run_simple_analysis(file_path: str, output_dir: str) -> Optional[str]:
    """
    Упрощенный анализ - только HTML, без JSON!
    Возвращает путь к HTML файлу или None
    """
    
    # Создаем контейнер для логов
    log_container = st.expander("🔍 Подробные логи анализа", expanded=True)
    logs = []
    
    def add_log(message: str, level: str = "INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_msg = f"[{timestamp}] [{level}] {message}"
        logs.append(log_msg)
        with log_container:
            if level == "ERROR":
                st.error(log_msg)
            elif level == "WARNING":
                st.warning(log_msg)
            elif level == "SUCCESS":
                st.success(log_msg)
            else:
                st.text(log_msg)
    
    # Индикаторы прогресса
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Начало анализа
        add_log(f"Начинаю анализ файла: {file_path}")
        add_log(f"Директория вывода: {output_dir}")
        
        status_text.text("🚀 Запускаю анализ Sequali...")
        progress_bar.progress(20)
        
        # Проверяем существование файла
        if not Path(file_path).exists():
            add_log(f"Файл не существует: {file_path}", "ERROR")
            raise FileNotFoundError(f"Файл не найден: {file_path}")
        
        start_time = time.time()
        file_size_mb = Path(file_path).stat().st_size / (1024 * 1024)
        add_log(f"Размер файла: {file_size_mb:.2f} MB")
        
        # Показываем базовые метрики
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Размер файла", f"{file_size_mb:.1f} MB")
        with col2:
            speed_placeholder = st.empty()
            speed_placeholder.metric("⚡ Скорость", "Обработка...")
        with col3:
            time_placeholder = st.empty()
            time_placeholder.metric("⏱️ Время", "0 сек")
        
        progress_bar.progress(40)
        
        # ВАЖНО: Запускаем БЕЗ JSON!
        add_log("Запускаю analyze_with_sequali (HTML only, без JSON)")
        add_log(f"Параметры: save_json=False, save_html=True")
        
        try:
            success = analyze_with_sequali(
                file_path,
                output_dir=output_dir,
                save_json=False,  # НЕ СОЗДАЕМ JSON!
                save_html=True    # Только HTML
            )
            add_log(f"Результат analyze_with_sequali: {success}")
        except Exception as e:
            add_log(f"Ошибка при вызове analyze_with_sequali: {str(e)}", "ERROR")
            raise
        
        elapsed_time = time.time() - start_time
        speed_mbps = file_size_mb / elapsed_time if elapsed_time > 0 else 0
        
        # Обновляем метрики
        speed_placeholder.metric("⚡ Скорость", f"{speed_mbps:.1f} MB/sec")
        time_placeholder.metric("⏱️ Время", f"{elapsed_time:.1f} сек")
        add_log(f"Скорость обработки: {speed_mbps:.1f} MB/sec")
        add_log(f"Время обработки: {elapsed_time:.1f} сек")
        
        progress_bar.progress(80)
        
        if success:
            status_text.text("📊 Загружаю HTML отчет...")
            add_log("Анализ завершен успешно, ищу HTML файл", "SUCCESS")
            
            # Проверяем содержимое директории
            add_log(f"Содержимое директории {output_dir}:")
            try:
                files_in_dir = list(Path(output_dir).glob("*"))
                if files_in_dir:
                    for f in files_in_dir:
                        add_log(f"  - {f.name} ({f.stat().st_size} байт)")
                else:
                    add_log("  Директория пуста!", "WARNING")
            except Exception as e:
                add_log(f"Ошибка при чтении директории: {e}", "ERROR")
            
            # Ищем HTML файл
            html_path = None
            possible_names = [
                f"{Path(file_path).name}.html",
                f"{Path(file_path).stem}.html",
            ]
            
            add_log("Пробую найти HTML по именам:")
            for name in possible_names:
                test_path = Path(output_dir) / name
                add_log(f"  Проверяю: {test_path}")
                if test_path.exists():
                    html_path = test_path
                    add_log(f"  ✓ Найден: {html_path}", "SUCCESS")
                    break
                else:
                    add_log(f"  ✗ Не найден")
            
            # Если не нашли по именам, берем первый HTML
            if not html_path:
                add_log("Не нашел по именам, ищу любой HTML файл")
                html_files = list(Path(output_dir).glob("*.html"))
                if html_files:
                    html_path = html_files[0]
                    add_log(f"Найден HTML файл: {html_path.name}", "SUCCESS")
                else:
                    add_log("HTML файлы не найдены в директории!", "ERROR")
            
            progress_bar.progress(100)
            status_text.text("")
            
            if html_path and html_path.exists():
                # Добавляем в историю
                st.session_state.analysis_history.append({
                    'filename': Path(file_path).name,
                    'time': datetime.now().strftime("%H:%M:%S"),
                    'speed': f"{speed_mbps:.1f} MB/sec",
                    'elapsed': f"{elapsed_time:.1f} сек"
                })
                
                add_log(f"Возвращаю путь к HTML: {html_path}", "SUCCESS")
                return str(html_path)
            else:
                add_log("HTML отчет не найден после всех попыток", "ERROR")
                st.error("HTML отчет не найден")
                return None
        else:
            progress_bar.progress(100)
            status_text.text("")
            add_log("analyze_with_sequali вернул False", "ERROR")
            st.error("❌ Ошибка при анализе файла")
            return None
            
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("")
        add_log(f"Критическая ошибка: {str(e)}", "ERROR")
        st.error(f"❌ Критическая ошибка: {str(e)}")
        return None


def display_html_report(html_path: str):
    """
    Отображение HTML отчета в Streamlit
    """
    try:
        # Читаем HTML файл
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        st.markdown("### 📊 Отчет Sequali")
        
        # Опции отображения
        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("💡 Отчет встроен ниже. Вы можете прокручивать его для просмотра всех деталей.")
        with col2:
            # Кнопка скачивания
            st.download_button(
                label="📥 Скачать HTML",
                data=html_content,
                file_name=f"sequali_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                mime="text/html"
            )
        
        # Встраиваем HTML через iframe
        components.html(
            html_content,
            height=900,  # Высота окна
            scrolling=True
        )
        
        return True
        
    except Exception as e:
        st.error(f"Ошибка при отображении HTML: {str(e)}")
        return False


def render_sidebar():
    """Боковая панель"""
    with st.sidebar:
        st.markdown("### 🧬 FastQCLI Simplified")
        st.caption("v2.0.0 | HTML Proxy Mode")
        
        st.divider()
        
        # Статус системы
        st.markdown("#### 📊 Статус")
        
        col1, col2 = st.columns(2)
        with col1:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            st.metric("Python", python_version)
        
        with col2:
            if FASTQCLI_AVAILABLE and has_command('sequali'):
                st.metric("Sequali", "✅")
            else:
                st.metric("Sequali", "❌")
        
        st.divider()
        
        # История анализов
        if st.session_state.analysis_history:
            st.markdown("#### 📜 История")
            for record in reversed(st.session_state.analysis_history[-5:]):
                with st.expander(f"📄 {record['filename'][:20]}..."):
                    st.text(f"⏰ {record['time']}")
                    st.text(f"⚡ {record['speed']}")
                    st.text(f"⏱️ {record['elapsed']}")
        
        st.divider()
        
        st.markdown("""
        #### ℹ️ О программе
        
        **Упрощенная версия** FastQCLI:
        - Без JSON парсинга
        - Прямое HTML проксирование
        - Максимальная скорость
        - Все возможности Sequali
        
        **Преимущества:**
        - ✅ Простота
        - ✅ Надежность
        - ✅ Скорость 300+ MB/sec
        - ✅ Полный функционал
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
    
    # Проверка установки Sequali
    if not check_sequali_installation():
        st.error("Sequali не установлен. Установите его для продолжения работы.")
        st.stop()
    
    # Основной интерфейс
    st.markdown("### 📁 Загрузка и анализ файла")
    
    uploaded_file = st.file_uploader(
        "Выберите FASTQ файл для анализа",
        type=['fastq', 'fq', 'gz'],
        help="Поддерживаются форматы: .fastq, .fq, .fastq.gz, .fq.gz"
    )
    
    if uploaded_file is not None:
        st.markdown("---")
        
        # Информация о файле
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"**Файл:** {uploaded_file.name}")
        with col2:
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.markdown(f"**Размер:** {file_size_mb:.2f} MB")
        with col3:
            estimated_time = file_size_mb / 300
            st.markdown(f"**Оценка:** ~{estimated_time:.1f} сек")
        
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
                
                # Запуск упрощенного анализа
                st.markdown("---")
                html_path = run_simple_analysis(file_path, output_dir)
                
                # Отображение HTML отчета
                if html_path:
                    st.markdown("---")
                    st.markdown('<div class="success-message">✅ Анализ завершен успешно!</div>', 
                               unsafe_allow_html=True)
                    
                    # Показываем HTML отчет
                    display_html_report(html_path)
                else:
                    st.markdown('<div class="error-message">❌ Не удалось выполнить анализ</div>', 
                               unsafe_allow_html=True)
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>FastQCLI Simplified v2.0.0 | HTML Proxy Mode | © 2025 TaskContract2025</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()