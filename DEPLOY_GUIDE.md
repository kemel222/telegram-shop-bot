# Руководство по развертыванию на Ubuntu 22 (без Docker)

## Информация о сервере

- **ОС:** Ubuntu 22.04
- **IP:** 87.120.84.39
- **Домен:** hotspotovich.shop
- **Стек:** LEMP (Linux, Nginx, MySQL, PHP)

## Шаг 1: Подготовка сервера

### 1.1 Подключение к серверу

```bash
ssh root@87.120.84.39
```

### 1.2 Обновление системы

```bash
apt update && apt upgrade -y
```

### 1.3 Установка необходимых пакетов

```bash
# Базовые утилиты
apt install -y git curl wget software-properties-common build-essential

# Python 3.11 и зависимости
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip

# Node.js 18.x (для React приложения)
curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
apt install -y nodejs

# PM2 для управления процессами
npm install -g pm2

# Certbot для SSL
apt install -y certbot python3-certbot-nginx

# MySQL клиент (если еще не установлен)
apt install -y mysql-client libmysqlclient-dev
```

## Шаг 2: Создание пользователя для приложения

```bash
# Создаем пользователя
adduser --disabled-password --gecos "" hotspot

# Добавляем в группу www-data (для Nginx)
usermod -aG www-data hotspot

# Переключаемся на пользователя
su - hotspot
```

## Шаг 3: Клонирование проекта

```bash
cd /home/hotspot

# Клонируем репозиторий (замените на ваш URL)
git clone https://github.com/your-username/telegram-shop-bot.git shop

cd shop
```

## Шаг 4: Настройка Python окружения

```bash
# Создаем виртуальное окружение
python3.11 -m venv venv

# Активируем
source venv/bin/activate

# Обновляем pip
pip install --upgrade pip

# Устанавливаем зависимости
pip install -r requirements.txt
```

## Шаг 5: Настройка базы данных MySQL

Вернитесь под root:

```bash
exit  # Выход из пользователя hotspot
```

### 5.1 Создание базы данных

```bash
mysql -u root -p
```

В MySQL консоли:

```sql
-- Создаем базу данных
CREATE DATABASE shop_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Создаем пользователя
CREATE USER 'shop_user'@'localhost' IDENTIFIED BY 'your_strong_password_here';

-- Выдаем права
GRANT ALL PRIVILEGES ON shop_db.* TO 'shop_user'@'localhost';

-- Применяем изменения
FLUSH PRIVILEGES;

-- Выходим
EXIT;
```

## Шаг 6: Настройка переменных окружения

Вернитесь под пользователя hotspot:

```bash
su - hotspot
cd /home/hotspot/shop
```

Создайте файл `.env`:

```bash
nano .env
```

Содержимое `.env`:

```env
# Telegram Bots
SHOP_BOT_TOKEN=your_shop_bot_token_here
ADMIN_BOT_TOKEN=your_admin_bot_token_here
ADMIN_IDS=your_telegram_id,another_admin_id

# Manager
MANAGER_USERNAME=your_telegram_username
MANAGER_ID=your_telegram_id

# Database
DATABASE_URL=mysql+aiomysql://shop_user:your_strong_password_here@localhost:3306/shop_db

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_super_secret_key_here_generate_random_string

# Payment
SBP_PHONE=+79991234567
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
WEBAPP_URL=https://hotspotovich.shop
```

Сохраните (Ctrl+O, Enter, Ctrl+X)

### Генерация SECRET_KEY:

```bash
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

## Шаг 7: Применение миграций базы данных

```bash
# Активируем виртуальное окружение (если не активировано)
source venv/bin/activate

# Применяем миграции
alembic upgrade head

# Инициализируем категории (опционально)
python init_categories.py
```

## Шаг 8: Настройка systemd сервисов

Вернитесь под root:

```bash
exit
```

### 8.1 Shop Bot сервис

```bash
nano /etc/systemd/system/hotspot-shop-bot.service
```

```ini
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
```

### 8.2 Admin Bot сервис

```bash
nano /etc/systemd/system/hotspot-admin-bot.service
```

```ini
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
```

### 8.3 FastAPI сервис

```bash
nano /etc/systemd/system/hotspot-api.service
```

```ini
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
```

### 8.4 Активация сервисов

```bash
# Перезагружаем systemd
systemctl daemon-reload

# Включаем автозапуск
systemctl enable hotspot-shop-bot
systemctl enable hotspot-admin-bot
systemctl enable hotspot-api

# Запускаем сервисы
systemctl start hotspot-shop-bot
systemctl start hotspot-admin-bot
systemctl start hotspot-api

# Проверяем статус
systemctl status hotspot-shop-bot
systemctl status hotspot-admin-bot
systemctl status hotspot-api
```

## Шаг 9: Сборка React приложения

```bash
su - hotspot
cd /home/hotspot/shop/webapp

# Установка зависимостей
npm install

# Создание production билда
npm run build
```

## Шаг 10: Настройка Nginx

Вернитесь под root:

```bash
exit
```

### 10.1 Создание конфигурации Nginx

```bash
nano /etc/nginx/sites-available/hotspotovich.shop
```

```nginx
# API Backend
upstream api_backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name hotspotovich.shop www.hotspotovich.shop;

    # Лимиты
    client_max_body_size 10M;

    # Логи
    access_log /var/log/nginx/hotspot_access.log;
    error_log /var/log/nginx/hotspot_error.log;

    # React приложение (корень)
    location / {
        root /home/hotspot/shop/webapp/build;
        try_files $uri $uri/ /index.html;
        
        # Кеширование статики
        location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
            expires 1y;
            add_header Cache-Control "public, immutable";
        }
    }

    # API
    location /api/ {
        proxy_pass http://api_backend/api/;
        proxy_http_version 1.1;
        
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Таймауты
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Защита от скрытых файлов
    location ~ /\. {
        deny all;
        access_log off;
        log_not_found off;
    }
}
```

### 10.2 Активация конфигурации

```bash
# Создаем симлинк
ln -s /etc/nginx/sites-available/hotspotovich.shop /etc/nginx/sites-enabled/

# Удаляем дефолтную конфигурацию (если есть)
rm -f /etc/nginx/sites-enabled/default

# Проверяем конфигурацию
nginx -t

# Перезагружаем Nginx
systemctl reload nginx
```

## Шаг 11: Установка SSL сертификата

```bash
# Получаем SSL сертификат
certbot --nginx -d hotspotovich.shop -d www.hotspotovich.shop

# При запросе email введите ваш email
# Согласитесь с Terms of Service
# Выберите опцию 2 (Redirect) для автоматического редиректа HTTP -> HTTPS

# Проверка автообновления
certbot renew --dry-run
```

## Шаг 12: Настройка файрвола (UFW)

```bash
# Включаем UFW
ufw --force enable

# Разрешаем SSH
ufw allow 22/tcp

# Разрешаем HTTP и HTTPS
ufw allow 80/tcp
ufw allow 443/tcp

# Проверяем статус
ufw status
```

## Шаг 13: Проверка работы

### 13.1 Проверка сервисов

```bash
# Статус ботов
systemctl status hotspot-shop-bot
systemctl status hotspot-admin-bot
systemctl status hotspot-api

# Логи
journalctl -u hotspot-shop-bot -f
journalctl -u hotspot-admin-bot -f
journalctl -u hotspot-api -f
```

### 13.2 Проверка сайта

Откройте в браузере:
- https://hotspotovich.shop
- https://hotspotovich.shop/api/docs (Swagger документация API)

### 13.3 Проверка ботов

Напишите в Telegram ботах:
- Shop Bot: `/start`
- Admin Bot: `/start`

## Шаг 14: Настройка автоматических бэкапов

```bash
nano /root/backup-shop-db.sh
```

```bash
#!/bin/bash

# Переменные
BACKUP_DIR="/home/hotspot/backups"
DB_NAME="shop_db"
DB_USER="shop_user"
DB_PASS="your_strong_password_here"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/shop_db_$DATE.sql.gz"

# Создаем директорию если не существует
mkdir -p $BACKUP_DIR

# Создаем бэкап
mysqldump -u $DB_USER -p$DB_PASS $DB_NAME | gzip > $BACKUP_FILE

# Удаляем бэкапы старше 7 дней
find $BACKUP_DIR -type f -name "*.sql.gz" -mtime +7 -delete

echo "Backup completed: $BACKUP_FILE"
```

```bash
# Делаем исполняемым
chmod +x /root/backup-shop-db.sh

# Добавляем в cron (ежедневно в 3:00)
crontab -e
```

Добавьте строку:
```
0 3 * * * /root/backup-shop-db.sh >> /var/log/shop-backup.log 2>&1
```

## Шаг 15: Мониторинг и обслуживание

### Полезные команды:

```bash
# Перезапуск всех сервисов
systemctl restart hotspot-shop-bot hotspot-admin-bot hotspot-api

# Просмотр логов
journalctl -u hotspot-shop-bot --since today
journalctl -u hotspot-admin-bot --since today
journalctl -u hotspot-api --since today

# Проверка использования ресурсов
htop

# Проверка дискового пространства
df -h

# Проверка MySQL
systemctl status mysql
```

### Обновление приложения:

```bash
# Под пользователем hotspot
su - hotspot
cd /home/hotspot/shop

# Получаем обновления
git pull

# Активируем виртуальное окружение
source venv/bin/activate

# Обновляем зависимости
pip install -r requirements.txt

# Применяем миграции
alembic upgrade head

# Пересобираем React приложение
cd webapp
npm install
npm run build

# Возвращаемся под root
exit

# Перезапускаем сервисы
systemctl restart hotspot-shop-bot hotspot-admin-bot hotspot-api
```

## Шаг 16: Оптимизация производительности

### 16.1 MySQL оптимизация

```bash
nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

Добавьте в секцию [mysqld]:
```ini
max_connections = 200
innodb_buffer_pool_size = 512M
innodb_log_file_size = 128M
query_cache_size = 32M
```

Перезапустите MySQL:
```bash
systemctl restart mysql
```

### 16.2 Nginx оптимизация

```bash
nano /etc/nginx/nginx.conf
```

Проверьте/измените:
```nginx
worker_processes auto;
worker_connections 2048;

# Gzip сжатие
gzip on;
gzip_vary on;
gzip_min_length 1024;
gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
```

```bash
systemctl reload nginx
```

## Troubleshooting

### Проблема: Боты не запускаются

```bash
# Проверить логи
journalctl -u hotspot-shop-bot -n 50

# Проверить токены в .env
cat /home/hotspot/shop/.env | grep BOT_TOKEN

# Проверить подключение к БД
mysql -u shop_user -p shop_db
```

### Проблема: API не отвечает

```bash
# Проверить, запущен ли сервис
systemctl status hotspot-api

# Проверить порт
netstat -tlnp | grep 8000

# Проверить логи
journalctl -u hotspot-api -n 50
```

### Проблема: React приложение не загружается

```bash
# Проверить сборку
ls -la /home/hotspot/shop/webapp/build/

# Проверить права
chown -R hotspot:www-data /home/hotspot/shop/webapp/build/

# Проверить конфигурацию Nginx
nginx -t

# Проверить логи Nginx
tail -f /var/log/nginx/hotspot_error.log
```

## Безопасность

### Дополнительные рекомендации:

1. **Fail2Ban для защиты SSH:**
```bash
apt install fail2ban
systemctl enable fail2ban
systemctl start fail2ban
```

2. **Регулярные обновления:**
```bash
apt update && apt upgrade -y
```

3. **Мониторинг логов:**
```bash
# Установить logwatch
apt install logwatch
```

4. **Изменить SSH порт** (опционально):
```bash
nano /etc/ssh/sshd_config
# Измените Port 22 на другой порт
systemctl restart sshd
ufw allow YOUR_NEW_PORT/tcp
```

## Контакты и поддержка

💻 Разработано [@x32asm](https://t.me/x32asm)

При возникновении проблем:
1. Проверьте логи сервисов
2. Проверьте конфигурационные файлы
3. Свяжитесь с разработчиком

---

**Поздравляем! Ваш магазин развернут на hotspotovich.shop** 🎉

