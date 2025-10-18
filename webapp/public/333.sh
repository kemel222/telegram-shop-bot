#!/bin/bash
echo "🔧 Диагностика и исправление сервисов..."

cd /home/hotspot/shop

# Активация виртуального окружения
source venv/bin/activate

# Проверка зависимостей
echo "Проверка зависимостей..."
pip install -r requirements.txt

# Проверка конфигурации
echo "Проверка конфигурации..."
python -c "from api.main import app; print('API конфигурация OK')"

# Запуск сервисов
echo "Запуск сервисов..."
systemctl start hotspot-api
sleep 2
systemctl start hotspot-shop-bot
sleep 2
systemctl start hotspot-admin-bot

# Проверка статуса
echo "Проверка статуса..."
systemctl status hotspot-api --no-pager
systemctl status hotspot-shop-bot --no-pager
systemctl status hotspot-admin-bot --no-pager

# Проверка API
echo "Проверка API..."
curl -s https://hotspotovich.shop/api/health || echo "API не работает"
