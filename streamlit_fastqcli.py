"""
FastQCLI Advanced Streamlit Interface
Веб-интерфейс с системой хранения файлов, реестром отчетов и полноэкранным просмотром
Версия: 3.0.0
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import sys
import os
from datetime import datetime
import tempfile
import time
import json
import hashlib
import shutil
from typing import Optional, Dict, List
import uuid

# Настройка страницы
st.set_page_config(
    page_title="FastQCLI Advanced",
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

# Константы
DATA_DIR = Path("data")
UPLOADED_FILES_DIR = DATA_DIR / "uploaded_files"
REPORTS_DIR = DATA_DIR / "reports"
METADATA_FILE = DATA_DIR / "metadata.json"

# CSS стили
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
    
    .file-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #667eea;
    }
    
    .report-card {
        background: white;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1rem 0;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
        border-left: 4px solid #28a745;
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
    
    .fullscreen-iframe {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: 9999;
        background: white;
    }
    
    .tab-content {
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)


def init_directories():
    """Инициализация директорий для хранения данных"""
    UPLOADED_FILES_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)
    DATA_DIR.mkdir(parents=True, exist_ok=True)


def get_file_hash(file_content: bytes) -> str:
    """Получение хеша файла для проверки уникальности"""
    return hashlib.md5(file_content).hexdigest()


def load_metadata() -> Dict:
    """Загрузка метаданных из файла"""
    if METADATA_FILE.exists():
        try:
            with open(METADATA_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                # Конвертируем строковые даты обратно в datetime объекты
                for file_id, file_info in data.get("files", {}).items():
                    if "upload_time" in file_info and isinstance(file_info["upload_time"], str):
                        try:
                            file_info["upload_time"] = datetime.fromisoformat(file_info["upload_time"])
                        except:
                            file_info["upload_time"] = datetime.now()
                
                for report_id, report_info in data.get("reports", {}).items():
                    if "creation_time" in report_info and isinstance(report_info["creation_time"], str):
                        try:
                            report_info["creation_time"] = datetime.fromisoformat(report_info["creation_time"])
                        except:
                            report_info["creation_time"] = datetime.now()
                
                return data
        except:
            return {"files": {}, "reports": {}}
    return {"files": {}, "reports": {}}


def save_metadata(metadata: Dict):
    """Сохранение метаданных в файл"""
    # Создаем копию для сериализации
    metadata_copy = {
        "files": {},
        "reports": {}
    }
    
    # Конвертируем datetime в ISO строки для сохранения
    for file_id, file_info in metadata.get("files", {}).items():
        metadata_copy["files"][file_id] = file_info.copy()
        if "upload_time" in metadata_copy["files"][file_id]:
            if isinstance(metadata_copy["files"][file_id]["upload_time"], datetime):
                metadata_copy["files"][file_id]["upload_time"] = metadata_copy["files"][file_id]["upload_time"].isoformat()
    
    for report_id, report_info in metadata.get("reports", {}).items():
        metadata_copy["reports"][report_id] = report_info.copy()
        if "creation_time" in metadata_copy["reports"][report_id]:
            if isinstance(metadata_copy["reports"][report_id]["creation_time"], datetime):
                metadata_copy["reports"][report_id]["creation_time"] = metadata_copy["reports"][report_id]["creation_time"].isoformat()
    
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata_copy, f, indent=2, default=str)


def init_session_state():
    """Инициализация session state"""
    if 'sequali_installed' not in st.session_state:
        st.session_state.sequali_installed = False
    
    if 'metadata' not in st.session_state:
        st.session_state.metadata = load_metadata()
    
    if 'current_tab' not in st.session_state:
        st.session_state.current_tab = "new_analysis"
    
    
    if 'analysis_in_progress' not in st.session_state:
        st.session_state.analysis_in_progress = False


def save_uploaded_file(uploaded_file) -> Optional[str]:
    """Сохранение загруженного файла"""
    try:
        # Получаем содержимое файла
        file_content = uploaded_file.getbuffer()
        file_hash = get_file_hash(file_content)
        
        # Проверяем, не загружен ли уже такой файл
        for file_id, file_info in st.session_state.metadata.get("files", {}).items():
            if file_info.get("hash") == file_hash:
                st.info(f"📌 Файл уже существует в истории: {file_info['filename']}")
                return file_id
        
        # Создаем уникальный ID для файла
        file_id = str(uuid.uuid4())
        
        # Сохраняем файл
        file_path = UPLOADED_FILES_DIR / f"{file_id}_{uploaded_file.name}"
        with open(file_path, 'wb') as f:
            f.write(file_content)
        
        # Добавляем в метаданные
        st.session_state.metadata["files"][file_id] = {
            "filename": uploaded_file.name,
            "path": str(file_path),
            "size_mb": len(file_content) / (1024 * 1024),
            "upload_time": datetime.now(),
            "hash": file_hash,
            "analysis_count": 0
        }
        
        save_metadata(st.session_state.metadata)
        return file_id
        
    except Exception as e:
        st.error(f"Ошибка при сохранении файла: {str(e)}")
        return None


def run_analysis_with_save(file_id: str) -> Optional[str]:
    """Запуск анализа с сохранением отчета"""
    
    file_info = st.session_state.metadata["files"].get(file_id)
    if not file_info:
        st.error("Файл не найден в метаданных")
        return None
    
    file_path = file_info["path"]
    
    # Создаем уникальный ID для отчета
    report_id = str(uuid.uuid4())
    report_dir = REPORTS_DIR / report_id
    report_dir.mkdir(parents=True, exist_ok=True)
    
    # Контейнер для логов
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
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # Начало анализа
        add_log(f"Начинаю анализ файла: {file_info['filename']}")
        add_log(f"ID файла: {file_id}")
        add_log(f"Директория отчета: {report_dir}")
        
        status_text.text("🚀 Запускаю анализ Sequali...")
        progress_bar.progress(20)
        
        # Показываем метрики
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("📁 Размер файла", f"{file_info['size_mb']:.1f} MB")
        with col2:
            st.metric("📊 Анализов", file_info.get('analysis_count', 0) + 1)
        with col3:
            time_placeholder = st.empty()
            time_placeholder.metric("⏱️ Время", "0 сек")
        
        progress_bar.progress(40)
        
        start_time = time.time()
        
        # Запускаем анализ
        add_log("Запускаю analyze_with_sequali (HTML only)")
        success = analyze_with_sequali(
            file_path,
            output_dir=str(report_dir),
            save_json=False,
            save_html=True
        )
        
        elapsed_time = time.time() - start_time
        time_placeholder.metric("⏱️ Время", f"{elapsed_time:.1f} сек")
        
        progress_bar.progress(80)
        
        if success:
            status_text.text("📊 Сохраняю отчет...")
            add_log("Анализ завершен успешно", "SUCCESS")
            
            # Ищем HTML файл
            html_files = list(report_dir.glob("*.html"))
            if html_files:
                html_path = html_files[0]
                add_log(f"HTML отчет найден: {html_path.name}", "SUCCESS")
                
                # Обновляем метаданные
                st.session_state.metadata["reports"][report_id] = {
                    "file_id": file_id,
                    "filename": file_info['filename'],
                    "report_path": str(html_path),
                    "creation_time": datetime.now(),
                    "elapsed_time": elapsed_time,
                    "status": "SUCCESS"
                }
                
                # Увеличиваем счетчик анализов
                st.session_state.metadata["files"][file_id]["analysis_count"] += 1
                
                save_metadata(st.session_state.metadata)
                
                progress_bar.progress(100)
                status_text.text("")
                
                return report_id
            else:
                add_log("HTML отчет не найден", "ERROR")
                return None
        else:
            progress_bar.progress(100)
            status_text.text("")
            add_log("Ошибка при анализе", "ERROR")
            return None
            
    except Exception as e:
        progress_bar.progress(100)
        status_text.text("")
        add_log(f"Критическая ошибка: {str(e)}", "ERROR")
        st.error(f"❌ Критическая ошибка: {str(e)}")
        return None


def display_html_report_fullscreen(report_path: str):
    """Отображение HTML отчета на весь экран"""
    try:
        with open(report_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Добавляем кнопку закрытия
        close_button = """
        <div style='position: fixed; top: 10px; right: 10px; z-index: 10000;'>
            <button onclick='window.parent.postMessage("close_fullscreen", "*")' 
                    style='background: #dc3545; color: white; border: none; 
                           padding: 10px 20px; border-radius: 5px; cursor: pointer;
                           font-size: 16px; font-weight: bold;'>
                ✕ Закрыть
            </button>
        </div>
        """
        
        # Встраиваем отчет с кнопкой закрытия
        components.html(
            close_button + html_content,
            height=1000,
            scrolling=True
        )
        
    except Exception as e:
        st.error(f"Ошибка при отображении отчета: {str(e)}")


def render_header():
    """Отображение заголовка"""
    st.markdown("""
    <div class="main-header">
        <h1>🧬 FastQCLI Advanced</h1>
        <p>Система анализа FASTQ файлов с историей и реестром отчетов</p>
    </div>
    """, unsafe_allow_html=True)


def render_new_analysis_tab():
    """Вкладка нового анализа"""
    st.markdown("### 📁 Загрузка и анализ нового файла")
    
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
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("🚀 Начать анализ", type="primary", use_container_width=True):
                st.session_state.analysis_in_progress = True
                
                # Сохраняем файл
                file_id = save_uploaded_file(uploaded_file)
                
                if file_id:
                    st.success(f"✅ Файл сохранен с ID: {file_id}")
                    
                    # Запускаем анализ
                    st.markdown("---")
                    report_id = run_analysis_with_save(file_id)
                    
                    if report_id:
                        st.markdown("---")
                        st.markdown('<div class="success-message">✅ Анализ завершен успешно!</div>', 
                                   unsafe_allow_html=True)
                        
                        report_info = st.session_state.metadata["reports"][report_id]
                        
                        # Кнопка просмотра отчета - теперь сразу открываем конкретный отчет
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("📊 Открыть отчет", type="primary", use_container_width=True):
                                st.query_params["report_id"] = report_id
                                st.switch_page("pages/2_Report_Viewer.py")
                        with col2:
                            if st.button("📋 К реестру отчетов", type="secondary", use_container_width=True):
                                st.query_params.clear()
                                st.switch_page("pages/2_Report_Viewer.py")
                    else:
                        st.error("❌ Не удалось выполнить анализ")
                
                st.session_state.analysis_in_progress = False


def render_files_history_tab():
    """Вкладка истории файлов"""
    st.markdown("### 📂 История загруженных файлов")
    
    files = st.session_state.metadata.get("files", {})
    
    if not files:
        st.info("История файлов пуста. Загрузите файлы во вкладке 'Новый анализ'.")
        return
    
    # Сортируем файлы по времени загрузки (новые сверху)
    def get_file_time(item):
        upload_time = item[1].get("upload_time", None)
        if upload_time is None:
            return datetime.min
        if isinstance(upload_time, str):
            try:
                return datetime.fromisoformat(upload_time)
            except:
                return datetime.min
        if isinstance(upload_time, datetime):
            return upload_time
        return datetime.min
    
    sorted_files = sorted(
        files.items(),
        key=get_file_time,
        reverse=True
    )
    
    for file_id, file_info in sorted_files:
        with st.container():
            st.markdown(f"""
            <div class="file-card">
                <h4>📄 {file_info['filename']}</h4>
                <p><strong>ID:</strong> {file_id[:8]}...</p>
                <p><strong>Размер:</strong> {file_info['size_mb']:.2f} MB</p>
                <p><strong>Загружен:</strong> {file_info['upload_time']}</p>
                <p><strong>Анализов выполнено:</strong> {file_info.get('analysis_count', 0)}</p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"🔄 Повторный анализ", key=f"reanalyze_{file_id}"):
                    st.markdown("---")
                    st.info(f"Запускаю повторный анализ файла {file_info['filename']}...")
                    report_id = run_analysis_with_save(file_id)
                    
                    if report_id:
                        st.success("✅ Повторный анализ завершен!")
                        report_info = st.session_state.metadata["reports"][report_id]
                        
                        if st.button(f"📊 Открыть отчет", key=f"view_report_{report_id}"):
                            st.query_params["report_id"] = report_id
                            st.switch_page("pages/2_Report_Viewer.py")
                    else:
                        st.error("❌ Ошибка при повторном анализе")
            
            with col2:
                # Проверяем существование файла
                if Path(file_info['path']).exists():
                    st.success("✅ Файл доступен")
                else:
                    st.error("❌ Файл не найден")
            
            with col3:
                if st.button(f"🗑️ Удалить", key=f"delete_{file_id}"):
                    # Удаляем файл
                    try:
                        if Path(file_info['path']).exists():
                            Path(file_info['path']).unlink()
                        del st.session_state.metadata["files"][file_id]
                        
                        # Удаляем связанные отчеты
                        reports_to_delete = []
                        for report_id, report_info in st.session_state.metadata["reports"].items():
                            if report_info.get("file_id") == file_id:
                                reports_to_delete.append(report_id)
                        
                        for report_id in reports_to_delete:
                            del st.session_state.metadata["reports"][report_id]
                        
                        save_metadata(st.session_state.metadata)
                        st.success("✅ Файл удален")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при удалении: {str(e)}")


def render_reports_registry_tab():
    """Вкладка реестра отчетов"""
    st.markdown("### 📊 Реестр отчетов")
    
    reports = st.session_state.metadata.get("reports", {})
    
    if not reports:
        st.info("Реестр отчетов пуст. Выполните анализ файлов для создания отчетов.")
        return
    
    # Сортируем отчеты по времени создания (новые сверху)
    def get_report_time(item):
        creation_time = item[1].get("creation_time", None)
        if creation_time is None:
            return datetime.min
        if isinstance(creation_time, str):
            try:
                return datetime.fromisoformat(creation_time)
            except:
                return datetime.min
        if isinstance(creation_time, datetime):
            return creation_time
        return datetime.min
    
    sorted_reports = sorted(
        reports.items(),
        key=get_report_time,
        reverse=True
    )
    
    # Фильтры
    col1, col2 = st.columns(2)
    with col1:
        search_query = st.text_input("🔍 Поиск по имени файла", "")
    
    # Фильтрация
    if search_query:
        sorted_reports = [(rid, rinfo) for rid, rinfo in sorted_reports 
                         if search_query.lower() in rinfo.get("filename", "").lower()]
    
    # Статистика
    st.markdown(f"**Всего отчетов:** {len(sorted_reports)}")
    
    for report_id, report_info in sorted_reports:
        with st.container():
            status_color = "#28a745" if report_info.get("status") == "SUCCESS" else "#dc3545"
            
            st.markdown(f"""
            <div class="report-card">
                <h4>📊 Отчет для: {report_info['filename']}</h4>
                <p><strong>ID отчета:</strong> {report_id[:8]}...</p>
                <p><strong>Создан:</strong> {report_info.get('creation_time', 'Неизвестно')}</p>
                <p><strong>Время анализа:</strong> {report_info.get('elapsed_time', 0):.1f} сек</p>
                <p><strong>Статус:</strong> <span style="color: {status_color}; font-weight: bold;">
                    {report_info.get('status', 'UNKNOWN')}</span></p>
            </div>
            """, unsafe_allow_html=True)
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"👁️ Открыть полноэкранно", key=f"view_{report_id}"):
                    st.query_params["report_id"] = report_id
                    st.switch_page("pages/2_Report_Viewer.py")
            
            with col2:
                # Скачать отчет
                if Path(report_info["report_path"]).exists():
                    with open(report_info["report_path"], 'r', encoding='utf-8') as f:
                        html_content = f.read()
                    
                    st.download_button(
                        label="📥 Скачать",
                        data=html_content,
                        file_name=f"report_{report_info['filename']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                        mime="text/html",
                        key=f"download_{report_id}"
                    )
                else:
                    st.error("Файл отчета не найден")
            
            with col3:
                if st.button(f"🗑️ Удалить", key=f"delete_report_{report_id}"):
                    try:
                        # Удаляем файл отчета
                        report_path = Path(report_info["report_path"])
                        if report_path.exists():
                            # Удаляем директорию отчета
                            shutil.rmtree(report_path.parent)
                        
                        del st.session_state.metadata["reports"][report_id]
                        save_metadata(st.session_state.metadata)
                        st.success("✅ Отчет удален")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Ошибка при удалении: {str(e)}")


def render_sidebar():
    """Боковая панель"""
    with st.sidebar:
        st.markdown("### 🧬 FastQCLI Advanced")
        st.caption("v3.0.1 | Extended Features")
        
        st.divider()
        
        # Статус системы
        st.markdown("#### 📊 Статус системы")
        
        col1, col2 = st.columns(2)
        with col1:
            python_version = f"{sys.version_info.major}.{sys.version_info.minor}"
            st.metric("Python", python_version)
        
        with col2:
            if FASTQCLI_AVAILABLE and has_command('sequali'):
                st.metric("Sequali", "✅")
            else:
                st.metric("Sequali", "❌")
        
        # Статистика
        st.divider()
        st.markdown("#### 📈 Статистика")
        
        files_count = len(st.session_state.metadata.get("files", {}))
        reports_count = len(st.session_state.metadata.get("reports", {}))
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Файлов", files_count)
        with col2:
            st.metric("Отчетов", reports_count)
        
        # Кнопка перехода к реестру отчетов
        st.divider()
        if st.button("📊 Открыть реестр всех отчетов", type="primary", use_container_width=True):
            # Переходим на страницу без параметров для показа списка
            st.query_params.clear()
            st.switch_page("pages/2_Report_Viewer.py")
        
        # Управление данными
        st.divider()
        st.markdown("#### 🗂️ Управление данными")
        
        if st.button("🗑️ Очистить все данные", use_container_width=True):
            if st.checkbox("Подтвердить удаление"):
                try:
                    # Очищаем директории
                    if UPLOADED_FILES_DIR.exists():
                        shutil.rmtree(UPLOADED_FILES_DIR)
                    if REPORTS_DIR.exists():
                        shutil.rmtree(REPORTS_DIR)
                    
                    # Очищаем метаданные
                    st.session_state.metadata = {"files": {}, "reports": {}}
                    save_metadata(st.session_state.metadata)
                    
                    # Пересоздаем директории
                    init_directories()
                    
                    st.success("✅ Все данные удалены")
                    st.rerun()
                except Exception as e:
                    st.error(f"Ошибка: {str(e)}")
        
        # Экспорт/импорт метаданных
        st.divider()
        st.markdown("#### 💾 Экспорт/Импорт")
        
        # Экспорт
        metadata_json = json.dumps(st.session_state.metadata, indent=2, default=str)
        st.download_button(
            label="📤 Экспорт метаданных",
            data=metadata_json,
            file_name=f"metadata_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
            mime="application/json",
            use_container_width=True
        )
        
        st.divider()
        
        st.markdown("""
        #### ℹ️ О программе
        
        **Advanced версия** FastQCLI:
        - 📂 История файлов
        - 📊 Реестр отчетов
        - 🔄 Повторный анализ
        - 🖼️ Полноэкранный просмотр
        - 💾 Постоянное хранение
        
        **Новые возможности:**
        - ✅ Система вкладок
        - ✅ Управление данными
        - ✅ Поиск и фильтрация
        - ✅ Экспорт/импорт
        - ✅ Статистика использования
        """)


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


def main():
    """Основная функция приложения"""
    
    # Инициализация
    init_directories()
    init_session_state()
    
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
    
    # Убираем проверку полноэкранного режима - теперь это на отдельной странице
    
    # Основной интерфейс с вкладками
    tab1, tab2, tab3 = st.tabs([
        "🆕 Новый анализ",
        "📂 История файлов",
        "📊 Реестр отчетов"
    ])
    
    with tab1:
        render_new_analysis_tab()
    
    with tab2:
        render_files_history_tab()
    
    with tab3:
        render_reports_registry_tab()
    
    # Футер
    st.markdown("---")
    st.markdown("""
    <div style='text-align: center; color: #666; padding: 1rem;'>
        <p>FastQCLI Advanced v3.0.1 | Extended Features | © 2025 TaskContract2025</p>
    </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()