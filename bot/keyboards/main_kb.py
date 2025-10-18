from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, WebAppInfo
from config import settings


def get_main_keyboard() -> ReplyKeyboardMarkup:
    """Основная клавиатура для пользователя"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛍 Открыть магазин", web_app=WebAppInfo(url="https://your-webapp-url.com"))
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
            ]
        ],
        resize_keyboard=True
    )
    return keyboard


def get_admin_keyboard() -> ReplyKeyboardMarkup:
    """Клавиатура для администратора"""
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="🛍 Открыть магазин", web_app=WebAppInfo(url="https://your-webapp-url.com"))
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
                KeyboardButton(text="⚙️ Админ-панель")
            ]
        ],
        resize_keyboard=True
    )
    return keyboard

