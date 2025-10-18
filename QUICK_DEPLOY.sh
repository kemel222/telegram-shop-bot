#!/bin/bash

# Быстрый скрипт деплоя для Ubuntu 22
# Запуск: sudo bash QUICK_DEPLOY.sh

set -e

echo "=========================================="
echo "  Hotspot Shop Bot - Быстрый деплой"
echo "  Разработано @x32asm"
echo "=========================================="
echo ""

# Проверка root прав
if [[ $EUID -ne 0 ]]; then
   echo "Этот скрипт должен быть запущен с правами root (sudo)" 
   exit 1
fi

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Функция для вывода
print_step() {
    echo -e "${GREEN}[STEP]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Получение информации от пользователя
print_step "Сбор информации для деплоя..."
echo ""

read -p "Введите домен (например, hotspotovich.shop): " DOMAIN
read -p "Введите токен Shop Bot: " SHOP_BOT_TOKEN
read -p "Введите токен Admin Bot: " ADMIN_BOT_TOKEN
read -p "Введите ваш Telegram ID (для админа): " ADMIN_TELEGRAM_ID
read -p "Введите ваш Telegram username: " MANAGER_USERNAME
read -p "Введите пароль для MySQL пользователя shop_user: " -s MYSQL_PASSWORD
echo ""
read -p "Введите номер телефона для СБП (например, +79991234567): " SBP_PHONE

echo ""
print_step "Начинаем установку..."

# Шаг 1: Обновление системы
print_step "Обновление системы..."
apt update && apt upgrade -y

# Шаг 2: Установка зависимостей
print_step "Установка необходимых пакетов..."
apt install -y git curl wget software-properties-common build-essential
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs
npm install -g pm2
apt install -y certbot python3-certbot-nginx
apt install -y mysql-client libmysqlclient-dev

# Шаг 3: Создание пользователя
print_step "Создание пользователя hotspot..."
if id "hotspot" &>/dev/null; then
    print_warning "Пользователь hotspot уже существует"
else
    adduser --disabled-password --gecos "" hotspot
    usermod -aG www-data hotspot
fi

# Шаг 4: Клонирование проекта
print_step "Клонирование проекта..."
if [ -d "/home/hotspot/shop" ]; then
    print_warning "Директория /home/hotspot/shop уже существует, пропускаем клонирование"
else
    read -p "Введите URL git репозитория: " GIT_REPO
    su - hotspot -c "git clone $GIT_REPO /home/hotspot/shop"
fi

# Шаг 5: Настройка Python окружения
print_step "Настройка Python окружения..."
su - hotspot -c "cd /home/hotspot/shop && python3.11 -m venv venv"
su - hotspot -c "cd /home/hotspot/shop && source venv/bin/activate && pip install --upgrade pip && pip install -r requirements.txt"

# Шаг 6: Настройка MySQL
print_step "Настройка базы данных MySQL..."
MYSQL_ROOT_PASSWORD=""
read -p "Введите root пароль MySQL (если есть, иначе нажмите Enter): " -s MYSQL_ROOT_PASSWORD
echo ""

if [ -z "$MYSQL_ROOT_PASSWORD" ]; then
    MYSQL_CMD="mysql"
else
    MYSQL_CMD="mysql -u root -p$MYSQL_ROOT_PASSWORD"
fi

$MYSQL_CMD <<MYSQL_SCRIPT
CREATE DATABASE IF NOT EXISTS shop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER IF NOT EXISTS 'shop_user'@'localhost' IDENTIFIED BY '$MYSQL_PASSWORD';
GRANT ALL PRIVILEGES ON shop_db.* TO 'shop_user'@'localhost';
FLUSH PRIVILEGES;
MYSQL_SCRIPT

print_step "База данных настроена"

# Шаг 7: Создание .env файла
print_step "Создание конфигурационного файла .env..."
SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(32))")

cat > /home/hotspot/shop/.env <<EOF
# Telegram Bots
SHOP_BOT_TOKEN=$SHOP_BOT_TOKEN
ADMIN_BOT_TOKEN=$ADMIN_BOT_TOKEN
ADMIN_IDS=$ADMIN_TELEGRAM_ID

# Manager
MANAGER_USERNAME=$MANAGER_USERNAME
MANAGER_ID=$ADMIN_TELEGRAM_ID

# Database
DATABASE_URL=mysql+aiomysql://shop_user:$MYSQL_PASSWORD@localhost:3306/shop_db

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=$SECRET_KEY

# Payment
SBP_PHONE=$SBP_PHONE
SBP_BANK_NAME=Сбербанк

# Cashback System
CASHBACK_PODS_PERCENT=2.5
CASHBACK_DEFAULT_PERCENT=3.5

# Developer
DEVELOPER_USERNAME=x32asm
DEVELOPER_LINK=https://t.me/x32asm

# Delivery
DELIVERY_PRICE=300

# WebApp
WEBAPP_URL=https://$DOMAIN
EOF

chown hotspot:hotspot /home/hotspot/shop/.env
chmod 600 /home/hotspot/shop/.env

# Шаг 8: Применение миграций
print_step "Применение миграций базы данных..."
su - hotspot -c "cd /home/hotspot/shop && source venv/bin/activate && alembic upgrade head"

# Опционально: инициализация категорий
read -p "Инициализировать тестовые категории? (y/n): " INIT_CATEGORIES
if [ "$INIT_CATEGORIES" = "y" ]; then
    su - hotspot -c "cd /home/hotspot/shop && source venv/bin/activate && python init_categories.py"
fi

# Шаг 9: Создание systemd сервисов
print_step "Создание systemd сервисов..."

# Shop Bot
cat > /etc/systemd/system/hotspot-shop-bot.service <<EOF
[Unit]
Description=Hotspot Shop Telegram Bot
After=network.target mysql.service

[Service]
Type=simple
User=hotspot
WorkingDirectory=/home/hotspot/shop
Environment="PATH=/home/hotspot/shop/venv/bin"
ExecStart=/home/hotspot/shop/venv/bin/python /home/hotspot/shop/run_shop_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Admin Bot
cat > /etc/systemd/system/hotspot-admin-bot.service <<EOF
[Unit]
Description=Hotspot Admin Telegram Bot
After=network.target mysql.service

[Service]
Type=simple
User=hotspot
WorkingDirectory=/home/hotspot/shop
Environment="PATH=/home/hotspot/shop/venv/bin"
ExecStart=/home/hotspot/shop/venv/bin/python /home/hotspot/shop/run_admin_bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# API
cat > /etc/systemd/system/hotspot-api.service <<EOF
[Unit]
Description=Hotspot FastAPI Application
After=network.target mysql.service

[Service]
Type=simple
User=hotspot
WorkingDirectory=/home/hotspot/shop
Environment="PATH=/home/hotspot/shop/venv/bin"
ExecStart=/home/hotspot/shop/venv/bin/uvicorn api.main:app --host 0.0.0.0 --port 8000
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Активация сервисов
systemctl daemon-reload
systemctl enable hotspot-shop-bot hotspot-admin-bot hotspot-api
systemctl start hotspot-shop-bot hotspot-admin-bot hotspot-api

# Шаг 10: Сборка React приложения
print_step "Сборка React приложения..."
su - hotspot -c "cd /home/hotspot/shop/webapp && npm install && npm run build"

# Шаг 11: Настройка Nginx
print_step "Настройка Nginx..."
cat > /etc/nginx/sites-available/$DOMAIN <<EOF
upstream api_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN;

    client_max_body_size 10M;

    access_log /var/log/nginx/hotspot_access.log;
    error_log /var/log/nginx/hotspot_error.log;

    location / {
        root /home/hotspot/shop/webapp/build;
        try_files \$uri \$uri/ /index.html;
        
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    location /api/ {
        proxy_pass http://api_backend/api/;
        proxy_http_version 1.1;
        
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
EOF

ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default

nginx -t && systemctl reload nginx

# Шаг 12: SSL сертификат
print_step "Установка SSL сертификата..."
read -p "Введите email для Let's Encrypt: " LETSENCRYPT_EMAIL
certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos --email $LETSENCRYPT_EMAIL --redirect

# Шаг 13: Настройка файрвола
print_step "Настройка файрвола..."
ufw --force enable
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp

# Шаг 14: Создание скрипта бэкапа
print_step "Создание скрипта автоматического бэкапа..."
cat > /root/backup-shop-db.sh <<EOF
#!/bin/bash
BACKUP_DIR="/home/hotspot/backups"
DB_NAME="shop_db"
DB_USER="shop_user"
DB_PASS="$MYSQL_PASSWORD"
DATE=\$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="\$BACKUP_DIR/shop_db_\$DATE.sql.gz"

mkdir -p \$BACKUP_DIR
mysqldump -u \$DB_USER -p\$DB_PASS \$DB_NAME | gzip > \$BACKUP_FILE
find \$BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: \$BACKUP_FILE"
EOF

chmod +x /root/backup-shop-db.sh

# Добавление в cron
(crontab -l 2>/dev/null; echo "0 3 * * * /root/backup-shop-db.sh >> /var/log/shop-backup.log 2>&1") | crontab -

# Финальная проверка
echo ""
echo "=========================================="
echo -e "${GREEN}  Установка завершена!${NC}"
echo "=========================================="
echo ""
print_step "Проверка статуса сервисов:"
systemctl status hotspot-shop-bot --no-pager | head -3
systemctl status hotspot-admin-bot --no-pager | head -3
systemctl status hotspot-api --no-pager | head -3
echo ""
echo "🌐 Ваш сайт доступен по адресу: https://$DOMAIN"
echo "📚 API документация: https://$DOMAIN/api/docs"
echo ""
echo "📋 Полезные команды:"
echo "  - Логи Shop Bot: journalctl -u hotspot-shop-bot -f"
echo "  - Логи Admin Bot: journalctl -u hotspot-admin-bot -f"
echo "  - Логи API: journalctl -u hotspot-api -f"
echo "  - Перезапуск всех сервисов: systemctl restart hotspot-shop-bot hotspot-admin-bot hotspot-api"
echo ""
echo "💻 Разработано @x32asm | https://t.me/x32asm"
echo ""

