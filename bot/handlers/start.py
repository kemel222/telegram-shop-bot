from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from bot.keyboards.main_kb import get_main_keyboard, get_admin_keyboard
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
        
        # Проверяем, является ли пользователь администратором
        is_admin = message.from_user.id in settings.admin_ids_list
        
        welcome_text = f"""
👋 Добро пожаловать, {message.from_user.first_name}!

🛍 Это бот интернет-магазина. Здесь вы можете:

• Просматривать каталог товаров
• Добавлять товары в корзину и избранное
• Оформлять заказы с доставкой или самовывозом
• Использовать промокоды и получать скидки
• Получать кешбек с каждой покупки

💰 Ваш баланс: {user.balance}₽
💵 Кешбек баланс: {user.cashback_balance}₽
"""
        
        if is_admin:
            welcome_text += "\n\n⚙️ У вас есть права администратора"
            keyboard = get_admin_keyboard()
        else:
            keyboard = get_main_keyboard()
        
        await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help"""
    help_text = f"""
📖 Помощь по использованию бота:

🛍 *Покупки*:
• Используйте кнопку "🛍 Открыть магазин" для просмотра каталога
• Добавляйте товары в корзину или избранное
• Оформляйте заказ через корзину

📦 *Доставка*:
• Самовывоз из Центра (12:00-17:00)
• Самовывоз из ТЦ (16:30-21:00)
• Доставка курьером (300₽)

💳 *Оплата*:
• СБП онлайн
• СБП при получении
• Наличными при получении
• Баланс сайта

🎁 *Промокоды*:
• Вводите промокод при оформлении заказа
• Промокоды дают скидку или пополняют баланс

💰 *Кешбек программа*:
• Получайте {settings.CASHBACK_PODS_PERCENT}% кешбек на "поды"
• {settings.CASHBACK_DEFAULT_PERCENT}% кешбек на остальные товары
• Кешбек начисляется после завершения заказа

👨‍💻 *Разработано*: @{settings.DEVELOPER_USERNAME}

По всем вопросам обращайтесь к администратору.
"""
    
    await message.answer(help_text, parse_mode="Markdown")


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
💵 Кешбек баланс: {user.cashback_balance}₽

{cashback_info}

👨‍💻 *Разработано*: @{settings.DEVELOPER_USERNAME}

Используйте /help для получения справки
"""
        
        await message.answer(profile_text, parse_mode="Markdown")


@router.message(F.text == "💰 Кешбек")
async def show_cashback_program(message: Message):
    """Показать информацию о программе кешбека"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        from services.cashback_service import CashbackService
        cashback_info = await CashbackService.format_cashback_info(session, user)
        
        await message.answer(cashback_info, parse_mode="Markdown")

