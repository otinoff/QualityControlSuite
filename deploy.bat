@echo off
echo ========================================
echo   FastQCLI Deployment Script
echo ========================================
echo.

REM Проверяем Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден!
    echo Установите Python 3.8+ и попробуйте снова
    pause
    exit /b 1
)

REM Запускаем Python скрипт деплоя
echo [INFO] Запускаю скрипт деплоя...
python deploy_to_server.py %*

pause