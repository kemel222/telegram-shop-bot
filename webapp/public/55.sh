#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎨 ДОБАВЛЕНИЕ ВЕРХНЕЙ ПАНЕЛИ С ПОЛЬЗОВАТЕЛЕМ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home/hotspot/shop

echo "[1/4] Остановка сервисов..."
systemctl stop hotspot-api hotspot-shop-bot hotspot-admin-bot

echo ""
echo "[2/4] Пересборка веб-приложения..."
cd webapp
chmod +x build-simple.sh
./build-simple.sh

echo ""
echo "[3/4] Запуск сервисов..."
cd ..
systemctl start hotspot-api
systemctl start hotspot-shop-bot
systemctl start hotspot-admin-bot
systemctl reload nginx

echo ""
echo "[4/4] Ожидание запуска..."
sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ОБНОВЛЕНИЕ ЗАВЕРШЕНО!"
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
check_service "hotspot-api"
check_service "hotspot-shop-bot"
check_service "hotspot-admin-bot"
check_service "nginx"

echo ""
echo "🎉 Что добавлено:"
echo "  ✅ Верхняя панель с информацией о пользователе"
echo "  ✅ Аватарка пользователя (или первая буква имени)"
echo "  ✅ ID пользователя из Telegram"
echo "  ✅ Username пользователя"
echo "  ✅ Баланс и кешбек в верхней панели"
echo "  ✅ Убран баланс из нижнего меню"
echo ""
echo "📱 Проверьте Mini App:"
echo "   https://hotspotovich.shop"
echo ""
echo "🔧 Если Mini App все еще не работает:"
echo "   1. Откройте консоль браузера (F12)"
echo "   2. Посмотрите логи с префиксом '=== TELEGRAM WEBAPP DEBUG ==='"
echo "   3. Проверьте, что initData содержит данные пользователя"
echo ""
