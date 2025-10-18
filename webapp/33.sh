#!/bin/bash
set -e

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 ФИНАЛЬНОЕ ОБНОВЛЕНИЕ V2.0 - Hotspot Shop"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

cd /home/hotspot/shop


echo ""
echo "[2/8] Активация виртуального окружения..."
source venv/bin/activate

echo ""
echo "[3/8] Установка Python зависимостей..."
pip install -q -r requirements.txt

echo ""
echo "[4/8] Исправление базы данных..."
mysql -u shop_user -pFreebsd1954r -e "
USE shop_db;

-- Добавляем поле has_variants в products
ALTER TABLE products ADD COLUMN IF NOT EXISTS has_variants BOOLEAN DEFAULT FALSE;

-- Создаем таблицу product_variants
CREATE TABLE IF NOT EXISTS product_variants (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    price FLOAT NULL,
    quantity INT DEFAULT 0,
    is_available BOOLEAN DEFAULT TRUE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (product_id) REFERENCES products(id)
);

-- Добавляем поля в cart_items
ALTER TABLE cart_items ADD COLUMN IF NOT EXISTS variant_id INT NULL;
ALTER TABLE cart_items ADD CONSTRAINT IF NOT EXISTS fk_cart_items_variant_id FOREIGN KEY (variant_id) REFERENCES product_variants(id);

-- Добавляем поля в order_items
ALTER TABLE order_items ADD COLUMN IF NOT EXISTS variant_id INT NULL;
ALTER TABLE order_items ADD COLUMN IF NOT EXISTS variant_name VARCHAR(255) NULL;
ALTER TABLE order_items ADD CONSTRAINT IF NOT EXISTS fk_order_items_variant_id FOREIGN KEY (variant_id) REFERENCES product_variants(id);

-- Обновляем версию alembic
INSERT INTO alembic_version (version_num) VALUES ('003') ON DUPLICATE KEY UPDATE version_num = '003';

SELECT 'База данных обновлена!' as status;
" || echo "⚠️ Ошибка обновления БД, продолжаем..."

echo ""
echo "[5/8] Загрузка товаров..."
python3 load_products_from_pdf.py || {
    echo "⚠️ Ошибка загрузки товаров, пропускаем..."
}

echo ""
echo "[6/8] Сборка веб-приложения..."
cd webapp
chmod +x build-simple.sh
./build-simple.sh

echo ""
echo "[7/8] Перезапуск сервисов..."
cd ..
systemctl restart hotspot-shop-bot
systemctl restart hotspot-admin-bot
systemctl restart hotspot-api
systemctl reload nginx

echo ""
echo "[8/8] Ожидание запуска..."
sleep 3

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ ОБНОВЛЕНИЕ V2.0 ЗАВЕРШЕНО!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# Проверка сервисов
check_service() {
    if systemctl is-active --quiet "$1"; then
        echo "  ✓ $1 работает"
        return 0
    else
        echo "  ✗ $1 ОСТАНОВЛЕН"
        echo "    Логи:"
        journalctl -u "$1" -n 3 --no-pager | sed 's/^/      /'
        return 1
    fi
}

echo "🔍 Проверка сервисов:"
check_service "hotspot-shop-bot"
check_service "hotspot-admin-bot"
check_service "hotspot-api"
check_service "nginx"

echo ""
echo "🎉 Что нового в версии 2.0:"
echo "  ✅ Классический дизайн в синих тонах"
echo "  ✅ Font Awesome иконки"
echo "  ✅ Полноценный каталог на главной"
echo "  ✅ Поиск товаров по названию"
echo "  ✅ Корзина с вариантами товаров"
echo "  ✅ Промокоды (проценты и рубли)"
echo "  ✅ Реферальная система"
echo "  ✅ Баланс и кешбек"
echo "  ✅ Избранное с сердечками"
echo "  ✅ Управление количеством товаров"
echo "  ✅ Самовывоз (Центр/ТЦ) и доставка"
echo "  ✅ СБП онлайн/при получении + наличные"
echo "  ✅ Нижняя навигация (Главная/Поиск/Избранное/Профиль)"
echo "  ✅ Товары из PDF с реальными остатками"
echo ""
echo "📱 Проверьте Mini App в Telegram:"
echo "   https://hotspotovich.shop"
echo ""
echo "🤖 Админ-бот команды:"
echo "   /stats - Расширенная статистика"
echo "   /stock_report - Отчет по остаткам"
echo "   /update_stock - Обновить остатки"
echo "   /add_product - Добавить товар с вариантами"
echo ""
echo "🔧 Если что-то не работает:"
echo "   journalctl -u hotspot-admin-bot -f"
echo "   journalctl -u hotspot-api -f"
echo ""
