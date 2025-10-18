from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bot.keyboards.shop_kb import get_main_keyboard
from services.user_service import UserService
from database.database import async_session_maker
from config import settings

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Обработка команды /start"""
    async with async_session_maker() as session:
        # Создаем или получаем пользователя
        user = await UserService.get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name
        )
        
        welcome_text = f"""
👋 Добро пожаловать в Hotspot, {message.from_user.first_name}!

🛍 Здесь вы можете купить:
• Жидкости для вейпа
• HQD и одноразки
• Картриджи и испарители
• POD-системы

💰 Ваш баланс: {user.balance}₽
💳 Кешбек баланс: {user.cashback_balance}₽

🎁 Получайте кешбек с каждой покупки:
• На POD-системы: {settings.CASHBACK_PODS_PERCENT}%
• На все остальное: {settings.CASHBACK_DEFAULT_PERCENT}%
"""
        
        keyboard = get_main_keyboard()
        
        await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help"""
    help_text = f"""
📖 Помощь по использованию:

🛍 *Покупки*:
• Нажмите "🛍 Открыть магазин" для просмотра каталога
• Добавляйте товары в корзину
• Оформляйте заказ

📦 *Доставка*:
• Самовывоз из Центра (12:00-17:00)
• Самовывоз из ТЦ (16:30-21:00)
• Доставка курьером (300₽)

💳 *Оплата*:
• СБП онлайн
• СБП при получении
• Наличными
• Баланс сайта

📞 *Поддержка*:
• Нажмите "📞 Связаться с менеджером" для консультации
• Менеджер: @{settings.MANAGER_USERNAME}

💰 *Кешбек программа*:
• На POD-системы: {settings.CASHBACK_PODS_PERCENT}%
• На все остальное: {settings.CASHBACK_DEFAULT_PERCENT}%
• Кешбек начисляется автоматически после выполнения заказа!
"""
    
    await message.answer(help_text, parse_mode="Markdown")


@router.message(F.text == "📞 Связаться с менеджером")
async def contact_manager(message: Message):
    """Связаться с менеджером"""
    manager_text = f"""
📞 Менеджер: @{settings.MANAGER_USERNAME}

Напишите менеджеру напрямую для:
• Консультации по товарам
• Вопросов по заказу
• Индивидуальных предложений
• Любых других вопросов

Мы всегда на связи! 😊
"""
    
    await message.answer(manager_text)


@router.message(F.text == "👤 Профиль")
async def show_profile(message: Message):
    """Показать профиль пользователя"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        from services.cashback_service import CashbackService
        cashback_info = await CashbackService.format_cashback_info(session, user)
        
        profile_text = f"""
👤 *Ваш профиль*

🆔 ID: {user.telegram_id}
👤 Имя: {user.first_name or 'Не указано'}
📱 Телефон: {user.phone or 'Не указан'}
💰 Баланс: {user.balance}₽
💳 Кешбек баланс: {user.cashback_balance}₽

{cashback_info}

Используйте /help для получения справки
"""
        
        await message.answer(profile_text, parse_mode="Markdown")


@router.message(F.text == "💰 Кешбек")
async def show_cashback_program(message: Message):
    """Показать информацию о кешбеке"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        from services.cashback_service import CashbackService
        cashback_info = await CashbackService.format_cashback_info(session, user)
        
        await message.answer(cashback_info, parse_mode="Markdown")

