"""
Скрипт для создания standalone .exe приложения
Использует PyInstaller для компиляции Python кода
"""

import os
import sys
import subprocess
from pathlib import Path

def install_pyinstaller():
    """Устанавливаем PyInstaller если его нет"""
    try:
        import PyInstaller
        print("[OK] PyInstaller уже установлен")
        return True
    except ImportError:
        print("[INSTALL] Устанавливаю PyInstaller...")
        try:
            subprocess.run(
                [sys.executable, '-m', 'pip', 'install', 'pyinstaller'],
                check=True
            )
            print("[OK] PyInstaller установлен")
            return True
        except Exception as e:
            print(f"[ERROR] Не удалось установить PyInstaller: {e}")
            return False

def build_cli_exe():
    """Создаем .exe для CLI версии"""
    print("\n=== Создаю FastQCLI.exe ===")
    
    cmd = [
        'pyinstaller',
        '--onefile',  # Один файл .exe
        '--console',  # Консольное приложение
        '--name', 'FastQCLI',  # Имя .exe файла
        '--icon', 'icon.ico' if Path('icon.ico').exists() else 'NONE',  # Иконка если есть
        '--add-data', 'fastqcli.py;.',  # Включаем основной файл
        '--hidden-import', 'click',  # Скрытые импорты
        '--hidden-import', 'sequali',
        '--clean',  # Очищаем кэш перед сборкой
        '--noconfirm',  # Не спрашивать подтверждение
        'fastqcli.py'  # Основной файл
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("[OK] FastQCLI.exe создан успешно!")
        print(f"[INFO] Файл находится в: dist/FastQCLI.exe")
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка при создании .exe: {e}")
        return False

def build_streamlit_exe():
    """Создаем .exe для Streamlit версии (сложнее)"""
    print("\n=== Создаю FastQCLI_Web.exe ===")
    
    # Создаем специальный launcher для Streamlit
    launcher_code = '''
import os
import sys
import subprocess
from pathlib import Path

def main():
    # Путь к директории с .exe
    if getattr(sys, 'frozen', False):
        app_dir = Path(sys._MEIPASS)
    else:
        app_dir = Path(__file__).parent
    
    # Запускаем Streamlit
    streamlit_path = app_dir / "streamlit_simple.py"
    subprocess.run([
        sys.executable, '-m', 'streamlit', 'run', 
        str(streamlit_path),
        '--server.maxUploadSize=5000'
    ])

if __name__ == "__main__":
    main()
'''
    
    # Создаем launcher файл
    with open('launcher.py', 'w') as f:
        f.write(launcher_code)
    
    cmd = [
        'pyinstaller',
        '--onefile',  # Один файл .exe
        '--windowed',  # GUI приложение (без консоли)
        '--name', 'FastQCLI_Web',  # Имя .exe файла
        '--icon', 'icon.ico' if Path('icon.ico').exists() else 'NONE',  # Иконка
        '--add-data', 'streamlit_simple.py;.',  # Streamlit скрипт
        '--add-data', 'fastqcli.py;.',  # CLI модуль
        '--hidden-import', 'streamlit',  # Скрытые импорты
        '--hidden-import', 'streamlit.components.v1',
        '--hidden-import', 'plotly',
        '--hidden-import', 'pandas',
        '--hidden-import', 'sequali',
        '--collect-all', 'streamlit',  # Собираем все файлы Streamlit
        '--clean',  # Очищаем кэш
        '--noconfirm',  # Без подтверждения
        'launcher.py'  # Launcher файл
    ]
    
    try:
        subprocess.run(cmd, check=True)
        print("[OK] FastQCLI_Web.exe создан успешно!")
        print(f"[INFO] Файл находится в: dist/FastQCLI_Web.exe")
        
        # Удаляем временный launcher
        os.remove('launcher.py')
        return True
    except Exception as e:
        print(f"[ERROR] Ошибка при создании .exe: {e}")
        return False

def create_portable_bundle():
    """Создаем портативную версию с всеми зависимостями"""
    print("\n=== Создаю портативную версию ===")
    
    # Создаем batch файл для запуска
    batch_content = '''@echo off
echo ========================================
echo   FastQCLI Portable v1.0.0
echo   Powered by Sequali Engine
echo ========================================
echo.

REM Проверяем Python
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python не найден!
    echo Скачайте portable Python с python.org
    pause
    exit /b 1
)

REM Устанавливаем зависимости если нужно
echo [INFO] Проверяю зависимости...
pip install sequali streamlit plotly pandas --quiet 2>nul

REM Меню выбора
echo.
echo Выберите режим:
echo 1. CLI режим (командная строка)
echo 2. Web режим (браузер)
echo.
set /p choice="Ваш выбор (1 или 2): "

if "%choice%"=="1" (
    echo.
    echo Запускаю CLI режим...
    python fastqcli.py %*
) else if "%choice%"=="2" (
    echo.
    echo Запускаю Web режим...
    echo Откройте браузер: http://localhost:8501
    streamlit run streamlit_simple.py
) else (
    echo Неверный выбор!
)

pause
'''
    
    with open('FastQCLI_Portable.bat', 'w') as f:
        f.write(batch_content)
    
    print("[OK] Создан FastQCLI_Portable.bat")
    print("[INFO] Портативная версия готова")
    return True

def main():
    print("=" * 50)
    print("  FastQCLI Builder для Windows 10")
    print("=" * 50)
    
    # Устанавливаем PyInstaller
    if not install_pyinstaller():
        print("[ERROR] Не могу продолжить без PyInstaller")
        return
    
    print("\nВыберите что собрать:")
    print("1. CLI версию (FastQCLI.exe)")
    print("2. Web версию (FastQCLI_Web.exe) - ЭКСПЕРИМЕНТАЛЬНО")
    print("3. Портативную версию (батник + Python скрипты)")
    print("4. Все варианты")
    
    choice = input("\nВаш выбор (1-4): ").strip()
    
    if choice == "1":
        build_cli_exe()
    elif choice == "2":
        build_streamlit_exe()
    elif choice == "3":
        create_portable_bundle()
    elif choice == "4":
        build_cli_exe()
        build_streamlit_exe()
        create_portable_bundle()
    else:
        print("Неверный выбор!")
    
    print("\n" + "=" * 50)
    print("Готово!")
    
    if Path('dist').exists():
        print(f"\n[INFO] Скомпилированные файлы в папке: dist/")
        for file in Path('dist').glob('*.exe'):
            size_mb = file.stat().st_size / (1024**2)
            print(f"  - {file.name} ({size_mb:.1f} MB)")

if __name__ == '__main__':
    main()