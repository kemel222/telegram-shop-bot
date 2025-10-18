from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import settings


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура для пользователя"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(
                    text="🛍 Открыть магазин", 
                    web_app=WebAppInfo(url=settings.WEBAPP_URL)
                )
            ],
            [
                KeyboardButton(text="🛒 Корзина"),
                KeyboardButton(text="❤️ Избранное")
            ],
            [
                KeyboardButton(text="👤 Профиль"),
                KeyboardButton(text="📦 Мои заказы")
            ],
            [
                KeyboardButton(text="🎁 Реферальная программа")
            ],
            [
                KeyboardButton(text="📞 Связаться с менеджером")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

