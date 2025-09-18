# 🚀 FastQCLI Deployment Guide

## 📋 Содержание
- [Автоматический деплой через GitHub Actions](#автоматический-деплой-через-github-actions)
- [Ручной деплой](#ручной-деплой)
- [Настройка сервера](#настройка-сервера)
- [Конфигурация](#конфигурация)
- [Troubleshooting](#troubleshooting)

## 🔄 Автоматический деплой через GitHub Actions

### Как это работает
При каждом пуше в ветку `master` GitHub Actions автоматически:
1. Запускает тесты
2. Создает пакет развертывания
3. Отправляет его на сервер

### Настройка GitHub Secrets
Для работы автоматического деплоя необходимо настроить следующие секреты в репозитории:

1. Перейдите в `Settings` → `Secrets and variables` → `Actions`
2. Добавьте следующие секреты:

| Секрет | Описание | Пример |
|--------|----------|---------|
| `SERVER_USER` | Пользователь SSH | `deploy` |
| `SERVER_HOST` | IP или домен сервера | `192.168.1.100` |
| `SERVER_PATH` | Путь к директории приложения | `/var/www/fastqcli` |
| `SERVER_SSH_KEY` | Приватный SSH ключ | `-----BEGIN OPENSSH PRIVATE KEY-----...` |

### Ручной запуск через GitHub Actions
1. Перейдите в `Actions` → `Deploy FastQCLI to Server`
2. Нажмите `Run workflow`
3. Выберите среду (production/staging/development)
4. Нажмите `Run workflow`

## 🛠️ Ручной деплой

### Локальный деплой
```bash
# Клонируем репозиторий
git clone https://github.com/otinoff/QualityControlSuite.git
cd QualityControlSuite

# Запускаем скрипт деплоя
python deploy_to_server.py /path/to/target/directory
```

### Деплой через батник (Windows)
```bash
# Клонируем репозиторий
git clone https://github.com/otinoff/QualityControlSuite.git
cd QualityControlSuite

# Запускаем батник
deploy.bat
```

## 🖥️ Настройка сервера

### Требования к серверу
- Python 3.8+
- Доступ по SSH
- Достаточно свободного места (минимум 1GB)
- Интернет для установки зависимостей

### Подготовка сервера (Ubuntu/Debian)
```bash
# Обновляем систему
sudo apt update && sudo apt upgrade -y

# Устанавливаем Python и Git
sudo apt install python3 python3-pip git -y

# Создаем пользователя для деплоя
sudo adduser deploy
sudo usermod -aG sudo deploy

# Переключаемся на пользователя deploy
su - deploy

# Создаем директорию для приложения
mkdir -p /var/www/fastqcli
```

### Настройка SSH доступа
```bash
# На сервере (от пользователя deploy)
mkdir -p ~/.ssh
chmod 700 ~/.ssh
touch ~/.ssh/authorized_keys
chmod 600 ~/.ssh/authorized_keys

# Добавьте публичный ключ в authorized_keys
```

## ⚙️ Конфигурация

### Локальная конфигурация
Создайте файл `.deploy_config` в корне репозитория:
```bash
SERVER_USER="deploy"
SERVER_HOST="your-server.com"
SERVER_PATH="/var/www/fastqcli"
SSH_KEY_PATH="~/.ssh/id_rsa"
```

### Переменные окружения
```bash
export SERVER_USER="deploy"
export SERVER_HOST="your-server.com"
export SERVER_PATH="/var/www/fastqcli"
```

## 🔧 Troubleshooting

### Проблемы с SSH
```bash
# Проверка подключения
ssh deploy@your-server.com

# Проверка прав доступа к ключу
chmod 600 ~/.ssh/id_rsa

# Подробный лог SSH
ssh -v deploy@your-server.com
```

### Проблемы с зависимостями
```bash
# Установка зависимостей вручную
pip install -r requirements.txt
pip install -r requirements_exe.txt
pip install sequali
```

### Проблемы с правами доступа
```bash
# Проверка прав на директорию
ls -la /var/www/fastqcli

# Изменение владельца
sudo chown -R deploy:deploy /var/www/fastqcli
```

### Логи деплоя
```bash
# Просмотр логов GitHub Actions
# В разделе Actions репозитория

# Локальные логи
tail -f /var/log/fastqcli/deploy.log
```

## 📊 Мониторинг

### Проверка состояния сервиса
```bash
# Проверка запущенного процесса
ps aux | grep fastqcli

# Проверка портов
netstat -tlnp | grep :8501
```

### Логи приложения
```bash
# Логи Streamlit
tail -f /var/log/fastqcli/streamlit.log

# Логи CLI
tail -f /var/log/fastqcli/cli.log
```

## 🔄 Обновление

### Ручное обновление
```bash
# На сервере
cd /var/www/fastqcli
git pull origin master
pip install -r requirements.txt --user
```

### Откат изменений
```bash
# Использование бэкапа
cd /var/www/fastqcli
rm -rf fastqcli
mv fastqcli_backup fastqcli
```

## 🛡️ Безопасность

### Рекомендации
- Используйте SSH ключи вместо паролей
- Ограничьте права доступа к директориям
- Регулярно обновляйте зависимости
- Используйте брандмауэр

### Пример настройки брандмауэра (UFW)
```bash
# Разрешаем SSH и HTTP/HTTPS
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https

# Разрешаем порт Streamlit (по умолчанию 8501)
sudo ufw allow 8501

# Включаем брандмауэр
sudo ufw enable
```

---
**FastQCLI Deployment Guide** | © 2025 TaskContract2025