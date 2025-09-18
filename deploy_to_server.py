#!/usr/bin/env python3
"""
Скрипт для деплоя FastQCLI на сервер
Обновляет код из GitHub репозитория
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def run_command(cmd, cwd=None):
    """Запуск команды и возврат результата"""
    try:
        result = subprocess.run(
            cmd, 
            shell=True, 
            cwd=cwd,
            capture_output=True, 
            text=True, 
            check=True
        )
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка выполнения команды: {e}")
        print(f"STDERR: {e.stderr}")
        return None

def check_git():
    """Проверка наличия Git"""
    try:
        result = subprocess.run(['git', '--version'], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"[OK] Git найден: {result.stdout.strip()}")
            return True
        else:
            print("[ERROR] Git не найден")
            return False
    except FileNotFoundError:
        print("[ERROR] Git не установлен")
        return False

def deploy_to_server(server_path, github_repo="https://github.com/otinoff/QualityControlSuite.git"):
    """Деплой кода на сервер"""
    
    server_path = Path(server_path)
    print(f"=== Деплой FastQCLI на сервер ===")
    print(f"Путь на сервере: {server_path}")
    print(f"Репозиторий: {github_repo}")
    
    # Создаем директорию если её нет
    server_path.mkdir(parents=True, exist_ok=True)
    
    # Проверяем есть ли уже репозиторий
    git_dir = server_path / ".git"
    if git_dir.exists():
        print("[INFO] Найден существующий репозиторий, обновляем...")
        # Обновляем существующий репозиторий
        result = run_command("git fetch origin", cwd=server_path)
        if result is None:
            return False
            
        result = run_command("git reset --hard origin/master", cwd=server_path)
        if result is None:
            return False
            
        print("[OK] Репозиторий обновлен")
    else:
        print("[INFO] Клонируем новый репозиторий...")
        # Удаляем содержимое директории
        for item in server_path.iterdir():
            if item.name != ".git":
                if item.is_dir():
                    shutil.rmtree(item)
                else:
                    item.unlink()
        
        # Клонируем репозиторий
        result = run_command(f"git clone {github_repo} .", cwd=server_path)
        if result is None:
            print("[ERROR] Не удалось клонировать репозиторий")
            return False
        print("[OK] Репозиторий клонирован")
    
    # Устанавливаем зависимости
    print("[INFO] Устанавливаем зависимости...")
    requirements_files = [
        "requirements.txt",
        "requirements_exe.txt"
    ]
    
    for req_file in requirements_files:
        req_path = server_path / req_file
        if req_path.exists():
            print(f"[INFO] Устанавливаем зависимости из {req_file}...")
            result = run_command(f"{sys.executable} -m pip install -r {req_file}", cwd=server_path)
            if result is not None:
                print(f"[OK] Зависимости из {req_file} установлены")
            else:
                print(f"[WARNING] Не удалось установить зависимости из {req_file}")
    
    # Проверяем установку Sequali
    print("[INFO] Проверяем установку Sequali...")
    result = run_command(f"{sys.executable} -c \"import sequali; print('Sequali установлен')\"", cwd=server_path)
    if result is None:
        print("[INFO] Устанавливаем Sequali...")
        result = run_command(f"{sys.executable} -m pip install sequali", cwd=server_path)
        if result is not None:
            print("[OK] Sequali установлен")
        else:
            print("[ERROR] Не удалось установить Sequali")
            return False
    
    # Создаем папку для тестовых файлов если её нет
    test_dir = server_path / "test_files"
    test_dir.mkdir(exist_ok=True)
    
    print("[OK] Деплой завершен успешно!")
    print(f"\nФайлы доступны в: {server_path}")
    print("\nДля запуска используйте:")
    print(f"  cd {server_path}")
    print("  python fastqcli.py --help")
    print("  streamlit run streamlit_simple.py")
    
    return True

def main():
    """Главная функция"""
    print("=== FastQCLI Deployment Script ===")
    
    # Проверяем Git
    if not check_git():
        print("[ERROR] Установите Git для продолжения")
        return
    
    # Получаем путь для деплоя
    if len(sys.argv) > 1:
        server_path = sys.argv[1]
    else:
        server_path = input("Введите путь для деплоя (или оставьте пустым для текущей директории): ").strip()
        if not server_path:
            server_path = "."
    
    # Выполняем деплой
    if deploy_to_server(server_path):
        print("\n✅ Деплой успешно завершен!")
    else:
        print("\n❌ Ошибка при деплое!")
        sys.exit(1)

if __name__ == "__main__":
    main()