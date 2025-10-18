"""
Админский бот для управления
@Hotspotovich_admin_bot
"""
import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from bot.admin_handlers import admin
from config import settings

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


async def main():
    """Главная функция запуска админского бота"""
    # Инициализация бота и диспетчера
    bot = Bot(token=settings.ADMIN_BOT_TOKEN)
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    
    # Регистрация роутеров
    dp.include_router(admin.router)
    
    logger.info("⚙️ Админский бот запущен (@Hotspotovich_admin_bot)!")
    
    # Запуск поллинга
    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        await bot.session.close()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Админский бот остановлен")

