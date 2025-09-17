@echo off
echo ========================================
echo   FastQCLI Streamlit Web Interface
echo   Powered by Sequali Engine
echo ========================================
echo.

REM Проверка Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден! Установите Python 3.8+
    pause
    exit /b 1
)

REM Проверка Streamlit
python -c "import streamlit" >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO] Streamlit не установлен. Устанавливаю...
    pip install streamlit plotly pandas
    if %errorlevel% neq 0 (
        echo [ERROR] Не удалось установить Streamlit
        pause
        exit /b 1
    )
)

REM Запуск приложения
echo [INFO] Запускаю Streamlit приложение...
echo [INFO] Откройте браузер: http://localhost:8501
echo.
echo Для остановки нажмите Ctrl+C
echo ========================================
streamlit run streamlit_fastqcli.py --server.maxUploadSize=5000

pause