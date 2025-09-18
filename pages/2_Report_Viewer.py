"""
Страница просмотра отчетов в полноэкранном режиме
Версия: 3.0.2
"""

import streamlit as st
import streamlit.components.v1 as components
from pathlib import Path
import json
from datetime import datetime

# Настройка страницы для полноэкранного режима
st.set_page_config(
    page_title="📊 Реестр отчетов FastQCLI",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Стили для полноэкранного режима
st.markdown("""
<style>
    /* Скрываем верхний padding */
    .main > div {
        padding-top: 0rem;
    }
    
    /* Убираем отступы */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 1rem;
        padding-right: 1rem;
    }
    
    /* Стиль для кнопки закрытия */
    .close-button {
        position: fixed;
        top: 10px;
        right: 10px;
        z-index: 999999;
        background: #ff4b4b;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
        font-weight: bold;
        border: none;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.2);
    }
    
    .close-button:hover {
        background: #ff2222;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
    }
    
    /* Полноэкранный iframe */
    .fullscreen-container {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        width: 100%;
        height: 100vh;
        padding: 0;
        margin: 0;
    }
    
    /* Заголовок отчета */
    .report-header {
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 50px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        display: flex;
        align-items: center;
        padding: 0 20px;
        z-index: 1000;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }
    
    .report-header h2 {
        margin: 0;
        font-size: 1.2rem;
    }
</style>
""", unsafe_allow_html=True)

def load_metadata():
    """Загрузка метаданных"""
    metadata_file = Path("data/metadata.json")
    if metadata_file.exists():
        try:
            with open(metadata_file, 'r', encoding='utf-8') as f:
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

def display_report_fullscreen(report_path: str, report_info: dict = None):
    """Отображение отчета на весь экран"""
    
    # Заголовок с информацией об отчете
    col1, col2, col3 = st.columns([6, 1, 1])
    
    with col1:
        if report_info:
            st.markdown(f"""
            <div style='color: #667eea; font-size: 1.2rem; font-weight: bold;'>
                📊 Отчет: {report_info.get('filename', 'Unknown')}
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f"""
            <div style='color: #667eea; font-size: 1.2rem; font-weight: bold;'>
                📊 Просмотр отчета
            </div>
            """, unsafe_allow_html=True)
    
    with col2:
        if report_info:
            # Кнопка скачивания
            if Path(report_path).exists():
                with open(report_path, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                
                st.download_button(
                    label="📥 Скачать",
                    data=html_content,
                    file_name=f"report_{report_info.get('filename', 'unknown')}.html",
                    mime="text/html",
                    use_container_width=True
                )
    
    with col3:
        # Кнопка возврата
        if st.button("🏠 На главную", type="primary", use_container_width=True):
            st.query_params.clear()
            st.switch_page("streamlit_fastqcli.py")
    
    st.markdown("---")
    
    # Отображение отчета
    if Path(report_path).exists():
        try:
            with open(report_path, 'r', encoding='utf-8') as f:
                html_content = f.read()
            
            # Добавляем JavaScript для обработки внутренних ссылок
            html_content = html_content.replace(
                '<head>',
                '''<head>
                <base target="_self">
                <script>
                // Предотвращаем конфликты с Streamlit навигацией
                document.addEventListener('DOMContentLoaded', function() {
                    // Обрабатываем все внутренние ссылки
                    var links = document.getElementsByTagName('a');
                    for (var i = 0; i < links.length; i++) {
                        var link = links[i];
                        var href = link.getAttribute('href');
                        
                        // Если это внутренняя ссылка (якорь)
                        if (href && href.startsWith('#')) {
                            link.onclick = function(e) {
                                e.preventDefault();
                                e.stopPropagation();
                                var target = document.querySelector(this.getAttribute('href'));
                                if (target) {
                                    target.scrollIntoView({behavior: 'smooth'});
                                }
                                return false;
                            };
                        }
                        // Если это внешняя ссылка
                        else if (href && (href.startsWith('http') || href.startsWith('https'))) {
                            link.setAttribute('target', '_blank');
                        }
                    }
                });
                </script>'''
            )
            
            # Встраиваем HTML отчет с максимальной высотой
            components.html(
                html_content,
                height=900,  # Высокое значение для полноэкранного режима
                scrolling=True
            )
            
        except Exception as e:
            st.error(f"❌ Ошибка при отображении отчета: {str(e)}")
    else:
        st.error("❌ Файл отчета не найден")

# Главная логика страницы
def main():
    # Проверяем параметры запроса
    params = st.query_params
    
    # Получаем ID отчета из параметров
    report_id = params.get("report_id", None)
    
    if report_id:
        # Загружаем метаданные
        metadata = load_metadata()
        reports = metadata.get("reports", {})
        
        if report_id in reports:
            report_info = reports[report_id]
            report_path = report_info.get("report_path", "")
            
            if report_path:
                display_report_fullscreen(report_path, report_info)
            else:
                st.error("❌ Путь к отчету не найден в метаданных")
        else:
            st.error(f"❌ Отчет с ID {report_id} не найден")
    else:
        # Если нет ID отчета, показываем реестр всех отчетов
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    color: white; padding: 2rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h1 style='margin: 0; font-size: 2rem;'>📊 Реестр отчетов FastQCLI</h1>
            <p style='margin-top: 0.5rem; opacity: 0.95;'>Все сгенерированные отчеты анализа FASTQ файлов</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Кнопка возврата на главную
        if st.button("🏠 Вернуться на главную", type="secondary"):
            st.query_params.clear()
            st.switch_page("streamlit_fastqcli.py")
        
        st.markdown("---")
        
        metadata = load_metadata()
        reports = metadata.get("reports", {})
        
        if reports:
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
            
            # Поиск и фильтрация
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                search_query = st.text_input("🔍 Поиск по имени файла", "")
            with col2:
                st.markdown(f"**Всего отчетов:** {len(reports)}")
            with col3:
                st.markdown(" ")  # Пустое место для выравнивания
            
            # Фильтрация по поиску
            if search_query:
                sorted_reports = [(rid, rinfo) for rid, rinfo in sorted_reports
                                 if search_query.lower() in rinfo.get("filename", "").lower()]
            
            if sorted_reports:
                st.markdown(f"**Найдено отчетов:** {len(sorted_reports)}")
                st.markdown("---")
                
                # Отображаем отчеты в виде карточек
                for report_id, report_info in sorted_reports:
                    with st.container():
                        # Создаем карточку отчета
                        st.markdown(f"""
                        <div style='background: white; padding: 1.5rem; border-radius: 8px;
                                    margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.05);
                                    border-left: 4px solid #28a745;'>
                            <h4 style='margin: 0; color: #2c3e50;'>📄 {report_info.get('filename', 'Unknown')}</h4>
                            <p style='color: #7f8c8d; margin: 0.5rem 0;'>
                                <strong>Создан:</strong> {report_info.get('creation_time', 'Unknown')} |
                                <strong>Время анализа:</strong> {report_info.get('elapsed_time', 0):.1f} сек |
                                <strong>ID:</strong> {report_id[:8]}...
                            </p>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        col1, col2, col3 = st.columns([1, 1, 1])
                        
                        with col1:
                            if st.button(f"👁️ Открыть отчет", key=f"view_{report_id}", type="primary", use_container_width=True):
                                st.query_params["report_id"] = report_id
                                st.rerun()
                        
                        with col2:
                            # Скачать отчет
                            if Path(report_info["report_path"]).exists():
                                with open(report_info["report_path"], 'r', encoding='utf-8') as f:
                                    html_content = f.read()
                                
                                st.download_button(
                                    label="📥 Скачать HTML",
                                    data=html_content,
                                    file_name=f"report_{report_info['filename']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
                                    mime="text/html",
                                    key=f"download_{report_id}",
                                    use_container_width=True
                                )
                            else:
                                st.error("Файл не найден", icon="❌")
                        
                        with col3:
                            # Проверка статуса
                            if Path(report_info["report_path"]).exists():
                                st.success("✅ Доступен", icon="✅")
                            else:
                                st.error("❌ Недоступен", icon="❌")
                        
                        st.markdown("---")
            else:
                st.warning("🔍 Отчеты не найдены по вашему запросу")
        else:
            # Нет отчетов
            st.info("""
            📝 **Реестр отчетов пуст**
            
            Здесь будут отображаться все сгенерированные отчеты анализа FASTQ файлов.
            
            Чтобы создать первый отчет:
            1. Вернитесь на главную страницу
            2. Загрузите FASTQ файл
            3. Запустите анализ
            """)

if __name__ == "__main__":
    main()