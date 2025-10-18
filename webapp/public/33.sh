#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔧 ОБНОВЛЕНИЕ АВТОРИЗАЦИИ И ИНТЕРФЕЙСА"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home/hotspot/shop

echo "[1/5] Остановка сервисов..."
systemctl stop hotspot-api hotspot-shop-bot hotspot-admin-bot



echo ""
echo "[3/5] Пересборка веб-приложения..."
cd webapp
chmod +x build-simple.sh
./build-simple.sh

echo ""
echo "[4/5] Запуск сервисов..."
cd ..
systemctl start hotspot-api
systemctl start hotspot-shop-bot
systemctl start hotspot-admin-bot
systemctl reload nginx

echo ""
echo "[5/5] Ожидание запуска..."
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
echo "🎉 Что обновлено:"
echo "  ✅ Авторизация привязана к Python API"
echo "  ✅ Уведомление о разработчике снизу экрана"
echo "  ✅ Прозрачность и автоисчезновение через 3 сек"
echo "  ✅ Навигационная кнопка корзины с бейджем"
echo "  ✅ Обновление бейджей корзины и избранного"
echo "  ✅ Правильная авторизация для всех API запросов"
echo ""
echo "📱 Проверьте Mini App:"
echo "   https://hotspotovich.shop"
echo ""
echo "🧪 Тестовая страница:"
echo "   https://hotspotovich.shop/test.html"
echo ""
