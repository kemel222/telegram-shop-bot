#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ИСПРАВЛЕНИЕ MINI APP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home/hotspot/shop

echo "[1/6] Остановка сервисов..."
systemctl stop hotspot-shop-bot hotspot-admin-bot hotspot-api

echo ""
echo "[2/6] Обновление веб-приложения..."
cd webapp
chmod +x build-simple.sh
./build-simple.sh

echo ""
echo "[3/6] Копирование тестовой страницы..."
cp test.html /var/www/hotspotovich.shop/
chown www-data:www-data /var/www/hotspotovich.shop/test.html

echo ""
echo "[4/6] Проверка Nginx конфигурации..."
nginx -t

echo ""
echo "[5/6] Запуск сервисов..."
cd ..
systemctl start hotspot-shop-bot hotspot-admin-bot hotspot-api
systemctl reload nginx

echo ""
echo "[6/6] Ожидание запуска..."
sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ИСПРАВЛЕНИЕ ЗАВЕРШЕНО!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Проверка сервисов
check_service() {
    if systemctl is-active --quiet "$1"; then
        echo "  ✓ $1 работает"
    else
        echo "  ✗ $1 ОСТАНОВЛЕН"
        echo "    Логи: journalctl -u $1 -n 3 --no-pager"
    fi
}

echo "🔍 Проверка сервисов:"
check_service "hotspot-shop-bot"
check_service "hotspot-admin-bot"
check_service "hotspot-api"
check_service "nginx"

echo ""
echo "🧪 Тестирование:"
echo "  📱 Mini App: https://hotspotovich.shop"
echo "  🔍 Тестовая страница: https://hotspotovich.shop/test.html"
echo "  🔧 API Health: https://hotspotovich.shop/api/health"
echo ""

echo "📋 Инструкции:"
echo "  1. Откройте https://hotspotovich.shop/test.html в браузере"
echo "  2. Нажмите 'Тест Telegram API'"
echo "  3. Проверьте, что все тесты проходят"
echo "  4. Если тесты проходят, откройте Mini App в Telegram"
echo ""

echo "🔧 Если Mini App все еще не работает:"
echo "  1. Проверьте настройки в BotFather"
echo "  2. Убедитесь, что URL правильный: https://hotspotovich.shop"
echo "  3. Проверьте логи: journalctl -u hotspot-api -f"
echo ""
