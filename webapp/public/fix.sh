#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔍 ДИАГНОСТИКА АВТОРИЗАЦИИ MINI APP"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home/hotspot/shop

echo "[1/5] Остановка сервисов..."
systemctl stop hotspot-api hotspot-shop-bot hotspot-admin-bot

echo ""
echo "[2/5] Пересборка веб-приложения..."
cd webapp
chmod +x build-simple.sh
./build-simple.sh

echo ""
echo "[3/5] Запуск сервисов..."
cd ..
systemctl start hotspot-api
systemctl start hotspot-shop-bot
systemctl start hotspot-admin-bot
systemctl reload nginx

echo ""
echo "[4/5] Ожидание запуска..."
sleep 3

echo ""
echo "[5/5] Проверка API..."
curl -s https://hotspotovich.shop/api/health || echo "❌ API не работает"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ДИАГНОСТИКА ЗАВЕРШЕНА!"
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
echo "  ✅ Детальное логирование для диагностики"
echo "  ✅ Проверка всех параметров initData"
echo "  ✅ Улучшенные сообщения об ошибках"
echo "  ✅ Отладочная информация в консоли"
echo ""
echo "📱 Инструкции для диагностики:"
echo "  1. Откройте Mini App в Telegram"
echo "  2. Откройте консоль браузера (F12)"
echo "  3. Посмотрите логи с префиксом '=== TELEGRAM WEBAPP DEBUG ==='"
echo "  4. Проверьте, что initData содержит данные пользователя"
echo ""
echo "🔧 Если initData пустой:"
echo "  1. Проверьте настройки BotFather:"
echo "     - /mybots → выберите бота → Bot Settings → Menu Button"
echo "     - URL должен быть: https://hotspotovich.shop"
echo "  2. Убедитесь, что открываете через кнопку в боте"
echo "  3. НЕ открывайте по прямой ссылке в браузере"
echo ""
echo "📱 Проверьте Mini App:"
echo "   https://hotspotovich.shop"
echo ""
echo "🧪 Тестовая страница:"
echo "   https://hotspotovich.shop/test.html"
echo ""
