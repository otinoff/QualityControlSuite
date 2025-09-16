#!/bin/bash

# Скрипт первоначальной настройки QualityControlSuite на сервере
# Запускать от root или с sudo

echo "=== QualityControlSuite Server Setup ==="

# Переменные
PROJECT_DIR="/var/QualityControlSuite"
SERVICE_USER="www-data"
DOMAIN="qualitycontrolsuite.onff.ru"
GITHUB_REPO="https://github.com/otinoff/QualityControlSuite.git"

# Проверка прав
if [ "$EUID" -ne 0 ]; then 
   echo "Пожалуйста, запустите скрипт с правами root (sudo)"
   exit 1
fi

# Установка системных зависимостей
echo "1. Установка системных зависимостей..."
apt-get update
apt-get install -y python3 python3-pip python3-venv git nginx

# Клонирование репозитория
echo "2. Клонирование репозитория..."
if [ -d "$PROJECT_DIR" ]; then
    echo "Директория $PROJECT_DIR уже существует. Обновляем..."
    cd $PROJECT_DIR
    git pull origin main
else
    git clone $GITHUB_REPO $PROJECT_DIR
    cd $PROJECT_DIR
fi

# Создание виртуального окружения
echo "3. Создание виртуального окружения..."
python3 -m venv venv
source venv/bin/activate

# Установка Python зависимостей
echo "4. Установка Python зависимостей..."
pip install --upgrade pip
pip install -r requirements.txt

# Создание директорий для данных
echo "5. Создание рабочих директорий..."
mkdir -p $PROJECT_DIR/data
mkdir -p $PROJECT_DIR/output
mkdir -p $PROJECT_DIR/logs
mkdir -p $PROJECT_DIR/temp

# Установка прав доступа
echo "6. Установка прав доступа..."
chown -R $SERVICE_USER:$SERVICE_USER $PROJECT_DIR
chmod -R 755 $PROJECT_DIR
chmod +x $PROJECT_DIR/main.py

# Создание systemd сервиса для Streamlit
echo "7. Создание systemd сервиса..."
cat > /etc/systemd/system/qualitycontrolsuite.service << 'EOF'
[Unit]
Description=QualityControlSuite - Biological Data Quality Control System (Streamlit)
After=network.target

[Service]
Type=simple
User=www-data
Group=www-data
WorkingDirectory=/var/QualityControlSuite
Environment="PATH=/var/QualityControlSuite/venv/bin"
ExecStart=/var/QualityControlSuite/venv/bin/streamlit run /var/QualityControlSuite/web_interface.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Создание Nginx конфигурации для Streamlit
echo "8. Настройка Nginx..."
cat > /etc/nginx/sites-available/qualitycontrolsuite << EOF
server {
    listen 80;
    server_name $DOMAIN;

    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        
        # Для загрузки больших файлов
        client_max_body_size 500M;
        proxy_read_timeout 300s;
        proxy_connect_timeout 300s;
        
        # WebSocket support for Streamlit
        proxy_buffering off;
        proxy_request_buffering off;
    }

    location /_stcore/stream {
        proxy_pass http://127.0.0.1:8501/_stcore/stream;
        proxy_http_version 1.1;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header Host \$host;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_read_timeout 86400;
    }

    location /output {
        alias $PROJECT_DIR/output;
        autoindex on;
    }

    # Логи
    access_log /var/log/nginx/qualitycontrolsuite_access.log;
    error_log /var/log/nginx/qualitycontrolsuite_error.log;
}
EOF

# Активация конфигурации Nginx
ln -sf /etc/nginx/sites-available/qualitycontrolsuite /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

# Перезагрузка сервисов
echo "9. Перезапуск сервисов..."
systemctl daemon-reload
systemctl enable qualitycontrolsuite
systemctl start qualitycontrolsuite
nginx -t && systemctl reload nginx

# Настройка файрвола (если ufw установлен)
if command -v ufw &> /dev/null; then
    echo "10. Настройка файрвола..."
    ufw allow 80/tcp
    ufw allow 443/tcp
    ufw allow 22/tcp
    ufw --force enable
fi

# Создание локального конфига (опционально)
echo "11. Создание локальной конфигурации..."
if [ ! -f "$PROJECT_DIR/config/local_settings.yaml" ]; then
    cat > $PROJECT_DIR/config/local_settings.yaml << 'EOF'
# Локальные настройки сервера
server:
  host: "0.0.0.0"
  port: 8000
  debug: false

paths:
  data_dir: "/var/QualityControlSuite/data"
  output_dir: "/var/QualityControlSuite/output"
  temp_dir: "/var/QualityControlSuite/temp"
  log_dir: "/var/QualityControlSuite/logs"

limits:
  max_file_size_mb: 500
  max_concurrent_jobs: 4
  job_timeout_seconds: 3600
EOF
    chown $SERVICE_USER:$SERVICE_USER $PROJECT_DIR/config/local_settings.yaml
fi

echo "=== Установка завершена! ==="
echo "Проверьте статус сервиса: systemctl status qualitycontrolsuite"
echo "Проверьте Nginx: nginx -t"
echo "Сайт должен быть доступен по адресу: http://$DOMAIN"
echo ""
echo "Для настройки SSL сертификата используйте:"
echo "certbot --nginx -d $DOMAIN"