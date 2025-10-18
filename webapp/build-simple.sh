#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🌐 СБОРКА ПРОСТОГО WEB ПРИЛОЖЕНИЯ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home/hotspot/shop/webapp

echo "[1/3] Создание директории build..."
mkdir -p build

echo ""
echo "[2/3] Копирование файлов..."
cp -r public/* build/

echo ""
echo "[3/3] Копирование в /var/www..."
rm -rf /var/www/hotspotovich.shop/*
cp -r build/* /var/www/hotspotovich.shop/
chown -R www-data:www-data /var/www/hotspotovich.shop

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ WEB ПРИЛОЖЕНИЕ СОБРАНО!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📱 Проверьте Mini App:"
echo "   https://hotspotovich.shop"
echo ""

# Перезагрузка Nginx
systemctl reload nginx
echo "✓ Nginx перезагружен"
