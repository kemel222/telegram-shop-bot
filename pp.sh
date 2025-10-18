#!/bin/bash

# Скрипт для загрузки проекта на GitHub с Personal Access Token
# Использование: ./push_to_github_token.sh YOUR_TOKEN

set -e  # Остановить при ошибке

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Настройки
GITHUB_USER="kemel222"
GITHUB_EMAIL="kemelyt222@gmail.com"
REPO_NAME="telegram-shop-bot"
REPO_URL="https://github.com/kemel222/telegram-shop-bot.git"

# Проверяем наличие токена
if [ -z "$1" ]; then
    echo -e "${RED}❌ Ошибка: Не указан Personal Access Token${NC}"
    echo -e "${YELLOW}💡 Использование: ./push_to_github_token.sh YOUR_TOKEN${NC}"
    echo ""
    echo -e "${BLUE}🔧 Как получить Personal Access Token:${NC}"
    echo -e "${BLUE}   1. Перейдите в GitHub Settings > Developer settings > Personal access tokens > Tokens (classic)${NC}"
    echo -e "${BLUE}   2. Нажмите 'Generate new token (classic)'${NC}"
    echo -e "${BLUE}   3. Выберите права: 'repo' (полный доступ к репозиториям)${NC}"
    echo -e "${BLUE}   4. Скопируйте токен и используйте его в команде${NC}"
    exit 1
fi

GITHUB_TOKEN="$1"

echo -e "${BLUE}🚀 Загрузка проекта на GitHub с токеном...${NC}"
echo -e "${YELLOW}📧 Email: ${GITHUB_EMAIL}${NC}"
echo -e "${YELLOW}👤 Username: ${GITHUB_USER}${NC}"
echo -e "${YELLOW}📦 Repository: ${REPO_URL}${NC}"
echo -e "${YELLOW}🔑 Token: ${GITHUB_TOKEN:0:8}...${NC}"
echo ""

# Проверяем, что мы в правильной директории
if [ ! -f "run_api.py" ]; then
    echo -e "${RED}❌ Ошибка: Скрипт должен быть запущен из корневой директории проекта${NC}"
    echo -e "${RED}   Убедитесь, что файл run_api.py находится в текущей директории${NC}"
    exit 1
fi

# Настраиваем Git
echo -e "${BLUE}⚙️ Настройка Git...${NC}"
git config --global user.email "${GITHUB_EMAIL}"
git config --global user.name "${GITHUB_USER}"

# Инициализируем Git репозиторий (если еще не инициализирован)
if [ ! -d ".git" ]; then
    echo -e "${BLUE}📁 Инициализация Git репозитория...${NC}"
    git init
fi

# Добавляем remote origin с токеном
AUTHENTICATED_URL="https://${GITHUB_TOKEN}@github.com/${GITHUB_USER}/${REPO_NAME}.git"

if ! git remote get-url origin >/dev/null 2>&1; then
    echo -e "${BLUE}🔗 Добавление remote origin...${NC}"
    git remote add origin "${AUTHENTICATED_URL}"
else
    echo -e "${BLUE}🔄 Обновление remote origin...${NC}"
    git remote set-url origin "${AUTHENTICATED_URL}"
fi

# Создаем .gitignore если его нет
if [ ! -f ".gitignore" ]; then
    echo -e "${BLUE}📝 Создание .gitignore...${NC}"
    cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
env/
ENV/

# Environment variables
.env
.env.local
.env.production

# Database
*.db
*.sqlite3

# Logs
*.log
logs/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db

# Node modules (for webapp)
webapp/node_modules/
webapp/build/
webapp/dist/

# Temporary files
*.tmp
*.temp
EOF
fi

# Добавляем все файлы
echo -e "${BLUE}📦 Добавление файлов в Git...${NC}"
git add .

# Проверяем статус
echo -e "${BLUE}📊 Статус Git:${NC}"
git status

# Коммитим изменения
echo -e "${BLUE}💾 Создание коммита...${NC}"
git commit -m "feat: Полнофункциональный Telegram Shop Bot с Mini App

✨ Новые возможности:
- 🛍️ Каталог товаров с категориями и поиском
- 🛒 Корзина и избранное
- 💰 Промокоды (скидка в % или рублях, пополнение баланса)
- 💳 Система кешбека (2.5-3.5% с каждой покупки)
- 💵 Оплата: СБП онлайн/при получении, наличные, баланс
- 🚚 Доставка (300₽) или самовывоз (Центр/ТЦ)
- 📦 Управление запасами товаров через админ-панель
- 👤 Профиль пользователя с балансом и кешбеком
- 🎯 Admin Bot с полным CRUD управлением товарами
- 🔥 Промо-баннер с автоматической ротацией акций

🔧 Технические улучшения:
- FastAPI backend с async/await
- SQLAlchemy ORM с миграциями Alembic
- Telegram Mini App с React frontend
- Система аутентификации через Telegram
- Полная интеграция с Telegram Bot API
- Responsive дизайн для мобильных устройств

📱 Готово к продакшену:
- Настроена система кешбека
- Реализованы все платежные методы
- Добавлено управление заказами
- Создана админ-панель для управления товарами"

# Пушим на GitHub
echo -e "${BLUE}🚀 Загрузка на GitHub...${NC}"

# Пробуем push
if git push -u origin main; then
    echo -e "${GREEN}✅ Успешно загружено на GitHub!${NC}"
    echo -e "${GREEN}🔗 Репозиторий: https://github.com/kemel222/telegram-shop-bot${NC}"
elif git push -u origin master; then
    echo -e "${GREEN}✅ Успешно загружено на GitHub!${NC}"
    echo -e "${GREEN}🔗 Репозиторий: https://github.com/kemel222/telegram-shop-bot${NC}"
else
    echo -e "${RED}❌ Ошибка при загрузке на GitHub${NC}"
    echo -e "${YELLOW}💡 Возможные причины:${NC}"
    echo -e "${YELLOW}   1. Неверный Personal Access Token${NC}"
    echo -e "${YELLOW}   2. Репозиторий не существует на GitHub${NC}"
    echo -e "${YELLOW}   3. Нет прав на запись в репозиторий${NC}"
    exit 1
fi

echo ""
echo -e "${GREEN}🎉 Проект успешно загружен на GitHub!${NC}"
echo -e "${BLUE}📋 Следующие шаги:${NC}"
echo -e "${BLUE}   1. Проверьте репозиторий: https://github.com/kemel222/telegram-shop-bot${NC}"
echo -e "${BLUE}   2. Настройте GitHub Actions для CI/CD (опционально)${NC}"
echo -e "${BLUE}   3. Добавьте README.md с инструкциями по установке${NC}"
echo -e "${BLUE}   4. Настройте Issues и Projects для управления проектом${NC}"
echo ""
echo -e "${GREEN}✨ Готово! Ваш Telegram Shop Bot теперь на GitHub!${NC}"
