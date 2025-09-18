#!/usr/bin/env python3
"""
FastQCLI - Self-Installing FASTQ Quality Control Tool
Автоматически устанавливает Sequali и все зависимости при первом запуске
Version: 3.0.0
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import importlib.util

# =============================================================================
# БЛОК 1: АВТОУСТАНОВКА ЗАВИСИМОСТЕЙ
# =============================================================================

TOOL_NAME = "FastQCLI"
VERSION = "3.0.0"
POWERED_BY = "Sequali Engine"

def print_banner():
    """Печатаем красивый баннер"""
    print(f"""
    ============================================
      {TOOL_NAME} v{VERSION}
      Powered by {POWERED_BY}
    ============================================
    """)

def check_python_version():
    """Проверяем версию Python"""
    if sys.version_info < (3, 6):
        print(f"[ERROR] Требуется Python 3.6+. У вас: {sys.version}")
        sys.exit(1)

def is_package_installed(package_name):
    """Проверяем установлен ли пакет"""
    spec = importlib.util.find_spec(package_name)
    return spec is not None

def has_command(command):
    """Проверяем доступность команды в системе"""
    try:
        subprocess.run([command, '--version'], 
                      capture_output=True, 
                      check=False)
        return True
    except (FileNotFoundError, subprocess.SubprocessError):
        return False

def install_package(package_name, pip_name=None):
    """Устанавливаем пакет через pip"""
    if pip_name is None:
        pip_name = package_name
    
    print(f"[INSTALL] Устанавливаю {package_name}...")
    
    try:
        # Пробуем установить в user space если нет прав админа
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--user', pip_name],
            capture_output=True,
            text=True,
            check=True
        )
        print(f"[OK] {package_name} успешно установлен!")
        return True
    except subprocess.CalledProcessError:
        # Если не получилось с --user, пробуем без него
        try:
            result = subprocess.run(
                [sys.executable, '-m', 'pip', 'install', pip_name],
                capture_output=True,
                text=True,
                check=True
            )
            print(f"[OK] {package_name} успешно установлен!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"[ERROR] Ошибка установки {package_name}: {e.stderr}")
            return False

def ensure_pip():
    """Убеждаемся что pip установлен"""
    try:
        import pip
        return True
    except ImportError:
        print("[INSTALL] pip не найден. Устанавливаю...")
        try:
            import ensurepip
            ensurepip.bootstrap()
            print("[OK] pip установлен!")
            return True
        except Exception as e:
            print(f"[ERROR] Не удалось установить pip: {e}")
            print("Попробуйте установить pip вручную")
            return False

def check_and_install_sequali():
    """Проверяем и устанавливаем Sequali"""
    if not has_command('sequali'):
        print("\n[SEARCH] Sequali не найден. Начинаю автоматическую установку...")
        
        # Проверяем pip
        if not ensure_pip():
            print("[ERROR] Не могу установить Sequali без pip")
            sys.exit(1)
        
        # Устанавливаем Sequali
        if install_package('sequali', 'sequali'):
            # Проверяем что установка прошла успешно
            if has_command('sequali'):
                print("[OK] Sequali успешно установлен и готов к работе!")
                return True
            else:
                print("[WARNING] Sequali установлен, но не найден в PATH")
                print("Попробуйте перезапустить терминал или добавить путь к sequali в PATH")
                return False
        else:
            print("[ERROR] Не удалось установить Sequali")
            print("Попробуйте установить вручную: pip install sequali")
            return False
    return True

def ensure_click():
    """Убеждаемся что Click установлен для CLI"""
    if not is_package_installed('click'):
        print("[INSTALL] Устанавливаю Click для CLI интерфейса...")
        return install_package('click', 'click>=8.0')
    return True

# =============================================================================
# БЛОК 2: ОСНОВНАЯ ФУНКЦИОНАЛЬНОСТЬ
# =============================================================================

def analyze_with_sequali(fastq_file, output_dir=None, save_json=True, save_html=True):
    """Анализируем FASTQ файл используя Sequali"""
    
    file_path = Path(fastq_file)
    if not file_path.exists():
        print(f"[ERROR] Файл не найден: {fastq_file}")
        return False
    
    print(f"\n[ANALYZE] Анализирую: {file_path.name}")
    print(f"[INFO] Размер файла: {file_path.stat().st_size / (1024**2):.1f} MB")
    print(f"[INFO] Параметры: save_json={save_json}, save_html={save_html}")
    
    # Формируем команду для Sequali
    cmd = ['sequali']
    
    # Добавляем директорию для вывода если указана
    if output_dir:
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        cmd.extend(['--dir', str(output_path)])
    else:
        output_path = Path.cwd()
    
    print(f"[INFO] Директория вывода: {output_path}")
    
    # Управляем форматами вывода через имена файлов
    base_name = file_path.stem
    full_name = file_path.name
    
    if save_html:
        html_file_name = f"{full_name}.html"
        cmd.extend(['--html', html_file_name])
        print(f"[INFO] HTML отчет: {html_file_name}")
    else:
        # Создаем временный HTML файл и удаляем его после анализа
        temp_html = f"{full_name}.temp.html"
        cmd.extend(['--html', temp_html])
        print(f"[INFO] Временный HTML отчет: {temp_html}")
    
    if save_json:
        json_file_name = f"{full_name}.json"
        cmd.extend(['--json', json_file_name])
        print(f"[INFO] JSON отчет: {json_file_name}")
    else:
        # Создаем временный JSON файл и удаляем его после анализа
        temp_json = f"{full_name}.temp.json"
        cmd.extend(['--json', temp_json])
        print(f"[INFO] Временный JSON отчет: {temp_json}")
    
    # Добавляем файл для анализа
    cmd.append(str(file_path))
    
    print(f"[DEBUG] Команда для запуска: {' '.join(cmd)}")
    
    try:
        # Запускаем Sequali
        print("[RUNNING] Запускаю анализ...")
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        
        print(f"[DEBUG] Return code: {result.returncode}")
        
        # Показываем прогресс от Sequali
        if result.stdout:
            print("[DEBUG] STDOUT от Sequali:")
            for line in result.stdout.splitlines():
                print(f"   {line}")
        
        if result.stderr:
            print("[DEBUG] STDERR от Sequali:")
            for line in result.stderr.splitlines():
                print(f"   {line}")
        
        # Удаляем временные файлы если они не нужны
        if not save_html:
            temp_html_path = output_path / f"{full_name}.temp.html"
            if temp_html_path.exists():
                temp_html_path.unlink()
                print(f"[INFO] Удален временный HTML файл: {temp_html_path}")
        
        if not save_json:
            temp_json_path = output_path / f"{full_name}.temp.json"
            if temp_json_path.exists():
                temp_json_path.unlink()
                print(f"[INFO] Удален временный JSON файл: {temp_json_path}")
        
        # Проверяем созданные файлы
        print(f"\n[DEBUG] Проверяю файлы в {output_path}:")
        
        # Проверяем что есть в директории
        all_files = list(output_path.glob("*"))
        if all_files:
            for f in all_files:
                print(f"   - {f.name} ({f.stat().st_size} байт)")
        else:
            print("   Директория пуста!")
        
        # Обрабатываем результаты
        results_generated = []
        
        # Проверяем HTML отчет (пробуем разные варианты имен)
        if save_html:
            html_found = False
            for possible_name in [f"{full_name}.html", f"{base_name}.html"]:
                html_file = output_path / possible_name
                print(f"[DEBUG] Проверяю HTML: {html_file}")
                if html_file.exists():
                    results_generated.append(f"[HTML] Отчет: {html_file}")
                    html_found = True
                    break
            
            if not html_found and save_html:
                print("[WARNING] HTML файл не найден после анализа")
        
        # Проверяем и обрабатываем JSON (только если save_json=True)
        if save_json:
            json_found = False
            for possible_name in [f"{full_name}.json", f"{base_name}.json"]:
                json_file = output_path / possible_name
                print(f"[DEBUG] Проверяю JSON: {json_file}")
                if json_file.exists():
                    results_generated.append(f"[JSON] Данные: {json_file}")
                    json_found = True
                    
                    # Читаем и показываем ключевые метрики
                    try:
                        with open(json_file, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                            show_key_metrics(data)
                    except Exception as e:
                        print(f"[WARNING] Не удалось прочитать JSON: {e}")
                    break
            
            if not json_found and save_json:
                print("[WARNING] JSON файл не найден после анализа")
        
        # Выводим информацию о созданных файлах
        if results_generated:
            print("\n[OK] Анализ завершен! Созданные файлы:")
            for result in results_generated:
                print(f"   {result}")
            return True
        else:
            print("\n[WARNING] Анализ завершен, но файлы не найдены")
            return True  # Все равно возвращаем True, так как команда выполнилась без ошибок
        
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Ошибка при запуске Sequali: {e}")
        if e.stderr:
            print(f"Детали: {e.stderr}")
        return False
    except Exception as e:
        print(f"[ERROR] Неожиданная ошибка: {e}")
        return False

def show_key_metrics(data):
    """Показываем ключевые метрики из JSON"""
    print("\n[METRICS] Ключевые метрики:")
    
    summary = data.get('summary', {})
    
    # Основные метрики
    total_reads = summary.get('total_reads', 0)
    total_bases = summary.get('total_bases', 0)
    mean_length = summary.get('mean_length', 0)
    
    print(f"   * Всего ридов: {total_reads:,}")
    print(f"   * Всего оснований: {total_bases:,}")
    print(f"   * Средняя длина: {mean_length:.1f} bp")
    
    # Качество
    if total_bases > 0:
        q20_bases = summary.get('q20_bases', 0)
        q30_bases = summary.get('q30_bases', 0)
        q20_pct = (q20_bases / total_bases) * 100
        
        # Пытаемся посчитать Q30 если есть данные
        if q30_bases > 0:
            q30_pct = (q30_bases / total_bases) * 100
            print(f"   * Q30: {q30_pct:.1f}%")
        
        print(f"   * Q20: {q20_pct:.1f}%")
        
        # GC содержание
        gc_bases = summary.get('total_gc_bases', 0)
        gc_pct = (gc_bases / total_bases) * 100
        print(f"   * GC содержание: {gc_pct:.1f}%")
        
        # N содержание
        n_bases = summary.get('total_n_bases', 0)
        n_pct = (n_bases / total_bases) * 100
        print(f"   * N содержание: {n_pct:.3f}%")
        
        # Предупреждения
        if q20_pct < 90:
            print("   [WARNING] Внимание: Q20 ниже 90%")
        if n_pct > 5:
            print("   [WARNING] Внимание: высокое содержание N")

def batch_analyze(file_pattern='*.fastq', output_dir=None, recursive=False):
    """Пакетный анализ нескольких файлов"""
    
    # Находим файлы
    current_dir = Path.cwd()
    
    if recursive:
        files = list(current_dir.rglob(file_pattern))
    else:
        files = list(current_dir.glob(file_pattern))
    
    if not files:
        print(f"[ERROR] Не найдено файлов по паттерну: {file_pattern}")
        return False
    
    print(f"\n[INFO] Найдено файлов для анализа: {len(files)}")
    
    # Анализируем каждый файл
    successful = 0
    failed = 0
    
    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{len(files)}] Обрабатываю: {file_path.name}")
        print("-" * 50)
        
        if analyze_with_sequali(str(file_path), output_dir):
            successful += 1
        else:
            failed += 1
    
    # Итоги
    print("\n" + "=" * 50)
    print("[SUMMARY] ИТОГИ ПАКЕТНОЙ ОБРАБОТКИ:")
    print(f"   [OK] Успешно: {successful}")
    if failed > 0:
        print(f"   [FAIL] Ошибки: {failed}")
    print("=" * 50)
    
    return failed == 0

# =============================================================================
# БЛОК 3: CLI ИНТЕРФЕЙС
# =============================================================================

def setup_cli():
    """Настраиваем CLI интерфейс используя Click"""
    try:
        import click
    except ImportError:
        print("[ERROR] Click не установлен. Используйте fallback режим")
        return None
    
    @click.group(invoke_without_command=True)
    @click.pass_context
    @click.version_option(version=VERSION, prog_name=TOOL_NAME)
    def cli(ctx):
        """FastQCLI - мощный инструмент для анализа FASTQ файлов"""
        if ctx.invoked_subcommand is None:
            print_banner()
            print(ctx.get_help())
    
    @cli.command()
    @click.argument('fastq_file', type=click.Path(exists=True))
    @click.option('-o', '--output', help='Директория для результатов')
    @click.option('--json/--no-json', default=True, help='Сохранять JSON')
    @click.option('--html/--no-html', default=True, help='Создавать HTML отчет')
    def analyze(fastq_file, output, json, html):
        """Анализировать один FASTQ файл"""
        print_banner()
        analyze_with_sequali(fastq_file, output, json, html)
    
    @cli.command()
    @click.option('-p', '--pattern', default='*.fastq', help='Паттерн для поиска файлов')
    @click.option('-o', '--output', help='Директория для результатов')
    @click.option('-r', '--recursive', is_flag=True, help='Рекурсивный поиск')
    def batch(pattern, output, recursive):
        """Пакетный анализ нескольких файлов"""
        print_banner()
        batch_analyze(pattern, output, recursive)
    
    @cli.command()
    def info():
        """Информация о системе и зависимостях"""
        print_banner()
        print("\n[INFO] ИНФОРМАЦИЯ О СИСТЕМЕ:")
        print(f"   * Python: {sys.version}")
        print(f"   * ОС: {sys.platform}")
        
        print("\n[INFO] СТАТУС ЗАВИСИМОСТЕЙ:")
        
        # Проверяем Sequali
        if has_command('sequali'):
            try:
                result = subprocess.run(['sequali', '--version'],
                                      capture_output=True, text=True)
                version = result.stdout.strip() if result.stdout else "неизвестно"
                print(f"   [OK] Sequali: {version}")
            except:
                print("   [OK] Sequali: установлен")
        else:
            print("   [FAIL] Sequali: не установлен")
        
        # Проверяем Click
        if is_package_installed('click'):
            try:
                import click
                print(f"   [OK] Click: {click.__version__}")
            except:
                print("   [OK] Click: установлен")
        else:
            print("   [FAIL] Click: не установлен")
    
    return cli

# =============================================================================
# БЛОК 4: FALLBACK РЕЖИМ (если Click недоступен)
# =============================================================================

def fallback_cli():
    """Простой CLI без Click"""
    print_banner()
    
    if len(sys.argv) < 2:
        print("Использование:")
        print(f"  python {sys.argv[0]} <fastq_file> [--json] [--html] [-o output_dir]")
        print(f"  python {sys.argv[0]} batch [pattern]")
        print(f"  python {sys.argv[0]} info")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == 'info':
        # Показываем информацию
        print("\n[INFO] ИНФОРМАЦИЯ О СИСТЕМЕ:")
        print(f"   * Python: {sys.version}")
        print(f"   * Sequali: {'[OK] установлен' if has_command('sequali') else '[FAIL] не установлен'}")
    
    elif command == 'batch':
        # Пакетный анализ
        pattern = sys.argv[2] if len(sys.argv) > 2 else '*.fastq'
        batch_analyze(pattern)
    
    elif command.endswith('.fastq') or command.endswith('.fq'):
        # Анализ одного файла
        output_dir = None
        save_json = True
        save_html = True
        
        # Парсим аргументы
        for i, arg in enumerate(sys.argv[2:]):
            if arg == '-o' and i + 1 < len(sys.argv[2:]):
                output_dir = sys.argv[2:][i + 1]
            elif arg == '--no-json':
                save_json = False
            elif arg == '--no-html':
                save_html = False
        
        analyze_with_sequali(command, output_dir, save_json, save_html)
    
    else:
        print(f"[ERROR] Неизвестная команда: {command}")
        sys.exit(1)

# =============================================================================
# БЛОК 5: ГЛАВНАЯ ТОЧКА ВХОДА
# =============================================================================

def main():
    """Главная функция"""
    
    # Проверяем Python версию
    check_python_version()
    
    # Первый запуск - проверяем и устанавливаем зависимости
    print("[CHECK] Проверяю зависимости...")
    
    sequali_ready = check_and_install_sequali()
    if not sequali_ready:
        print("\n[WARNING] FastQCLI требует Sequali для работы")
        print("Установите его вручную: pip install sequali")
        sys.exit(1)
    
    click_ready = ensure_click()
    
    # Запускаем CLI
    if click_ready:
        # Используем Click если доступен
        cli = setup_cli()
        if cli:
            cli()
        else:
            fallback_cli()
    else:
        # Fallback режим без Click
        print("[WARNING] Работаю в упрощенном режиме без Click")
        fallback_cli()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n[EXIT] Прервано пользователем")
        sys.exit(0)
    except Exception as e:
        print(f"\n[ERROR] Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)