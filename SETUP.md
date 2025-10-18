# Инструкция по установке и запуску

## Требования

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Telegram Bot Token (получить у [@BotFather](https://t.me/BotFather))

## 1. Установка зависимостей Python

```bash
# Создайте виртуальное окружение
python -m venv venv

# Активируйте виртуальное окружение
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Установите зависимости
pip install -r requirements.txt
```

## 2. Настройка базы данных

### Установка PostgreSQL

Скачайте и установите PostgreSQL с [официального сайта](https://www.postgresql.org/download/).

### Создание базы данных

```sql
-- Подключитесь к PostgreSQL
psql -U postgres

-- Создайте базу данных
CREATE DATABASE shop_db;

-- Создайте пользователя (опционально)
CREATE USER shop_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE shop_db TO shop_user;
```

## 3. Настройка переменных окружения

Скопируйте `.env.example` в `.env`:

```bash
cp .env.example .env
```

Отредактируйте `.env` файл:

```env
# Telegram Bot
BOT_TOKEN=your_bot_token_from_botfather
ADMIN_IDS=your_telegram_id,another_admin_id

# Database
DATABASE_URL=postgresql+asyncpg://shop_user:your_password@localhost:5432/shop_db

# API
API_HOST=0.0.0.0
API_PORT=8000
SECRET_KEY=your_random_secret_key_here

# Payment
SBP_PHONE=+79991234567
SBP_BANK_NAME=Сбербанк

# Referral System
REFERRAL_FIRST_PURCHASE_DISCOUNT=20
REFERRAL_BONUS_PERCENT=10

# Delivery
DELIVERY_PRICE=300
```

### Как получить Bot Token:

1. Напишите [@BotFather](https://t.me/BotFather) в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте полученный токен в `.env`

### Как узнать свой Telegram ID:

1. Напишите [@userinfobot](https://t.me/userinfobot)
2. Скопируйте свой ID в `.env`

## 4. Применение миграций

```bash
# Инициализация Alembic (если нужно создать первую миграцию)
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head
```

## 5. Запуск API сервера

```bash
# В отдельном терминале
python run_api.py
```

API будет доступен по адресу: `http://localhost:8000`
Документация API: `http://localhost:8000/docs`

## 6. Запуск Telegram бота

```bash
# В другом терминале
python run_bot.py
```

## 7. Настройка веб-приложения (Mini App)

```bash
cd webapp

# Установите зависимости
npm install

# Создайте .env файл
echo "REACT_APP_API_URL=http://localhost:8000/api" > .env

# Запустите в режиме разработки
npm start
```

Приложение будет доступно по адресу: `http://localhost:3000`

## 8. Публикация веб-приложения

### Вариант 1: Сборка и хостинг

```bash
cd webapp
npm run build

# Полученную папку build можно разместить на любом хостинге:
# - Netlify
# - Vercel
# - GitHub Pages
# - Любой статический хостинг
```

### Вариант 2: Использование ngrok для разработки

```bash
# Установите ngrok: https://ngrok.com/download

# Запустите туннель для веб-приложения
ngrok http 3000

# Скопируйте полученный URL (например: https://abc123.ngrok.io)
```

## 9. Настройка Mini App в Telegram

1. Откройте [@BotFather](https://t.me/BotFather)
2. Отправьте команду `/mybots`
3. Выберите вашего бота
4. Нажмите **Bot Settings** → **Menu Button**
5. Отправьте URL вашего веб-приложения (например: `https://your-app.netlify.app`)
6. Отправьте текст для кнопки (например: "Открыть магазин")

## 10. Добавление тестовых данных

### Через админ-панель бота:

1. Запустите бота
2. Отправьте команду `/create_promo` для создания промокодов
3. Используйте API эндпоинты `/api/admin/categories` и `/api/admin/products` для добавления товаров

### Или создайте скрипт для добавления тестовых данных:

```python
# add_test_data.py
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import async_session_maker
from database.models import Category, Product, PromoCode, PromoCodeType

async def add_test_data():
    async with async_session_maker() as session:
        # Добавляем категории
        category1 = Category(name="Электроника", description="Смартфоны, планшеты и другие гаджеты")
        category2 = Category(name="Одежда", description="Модная одежда для всех")
        
        session.add(category1)
        session.add(category2)
        await session.flush()
        
        # Добавляем товары
        product1 = Product(
            category_id=category1.id,
            name="iPhone 15 Pro",
            description="Флагманский смартфон от Apple",
            price=99990,
            quantity=10,
            is_available=True
        )
        
        product2 = Product(
            category_id=category2.id,
            name="Футболка Nike",
            description="Спортивная футболка",
            price=2990,
            quantity=50,
            is_available=True
        )
        
        session.add(product1)
        session.add(product2)
        
        # Добавляем промокоды
        promo1 = PromoCode(
            code="SALE20",
            type=PromoCodeType.PERCENT,
            value=20,
            is_active=True
        )
        
        promo2 = PromoCode(
            code="BONUS1000",
            type=PromoCodeType.BALANCE,
            value=1000,
            is_active=True
        )
        
        session.add(promo1)
        session.add(promo2)
        
        await session.commit()
        print("✅ Тестовые данные добавлены!")

if __name__ == "__main__":
    asyncio.run(add_test_data())
```

Запустите скрипт:

```bash
python add_test_data.py
```

## 11. Проверка работы

1. **Проверьте API**: Откройте `http://localhost:8000/docs` - должна открыться документация Swagger
2. **Проверьте бота**: Напишите `/start` вашему боту в Telegram
3. **Проверьте веб-приложение**: Откройте веб-приложение через кнопку Menu в боте

## Возможные проблемы

### Ошибка подключения к базе данных

- Проверьте, что PostgreSQL запущен
- Проверьте правильность `DATABASE_URL` в `.env`
- Убедитесь, что база данных создана

### Бот не отвечает

- Проверьте правильность `BOT_TOKEN` в `.env`
- Убедитесь, что `run_bot.py` запущен и работает

### Веб-приложение не загружается

- Проверьте, что API сервер запущен
- Проверьте `REACT_APP_API_URL` в `.env` веб-приложения
- Проверьте консоль браузера на наличие ошибок

## Продакшн

Для продакшн-окружения:

1. Используйте gunicorn или uvicorn workers для API
2. Настройте nginx как reverse proxy
3. Используйте systemd для автозапуска сервисов
4. Настройте SSL сертификаты (Let's Encrypt)
5. Используйте продакшн базу данных с бэкапами
6. Настройте мониторинг и логирование

### Пример запуска API в продакшн:

```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Пример systemd сервиса для бота:

```ini
[Unit]
Description=Telegram Shop Bot
After=network.target

[Service]
Type=simple
User=youruser
WorkingDirectory=/path/to/telegram-shop-bot
Environment="PATH=/path/to/telegram-shop-bot/venv/bin"
ExecStart=/path/to/telegram-shop-bot/venv/bin/python run_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

## Поддержка

Если у вас возникли вопросы или проблемы, проверьте:
- Логи бота в терминале
- Логи API сервера
- Консоль браузера для веб-приложения

