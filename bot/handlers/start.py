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
        # Проверяем, есть ли реферальный код в команде
        referral_code = None
        if message.text and len(message.text.split()) > 1:
            args = message.text.split()[1]
            if args.startswith("ref_"):
                referral_code = args[4:]
        
        # Создаем или получаем пользователя
        user = await UserService.get_or_create_user(
            session,
            message.from_user.id,
            message.from_user.username,
            message.from_user.first_name,
            referral_code
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
• Приглашать друзей и получать бонусы

💰 Ваш баланс: {user.balance}₽
🎁 Ваш реферальный код: {user.referral_code}
"""
        
        if referral_code and user.referred_by_id:
            welcome_text += f"\n🎉 Вы были приглашены по реферальной ссылке! При первой покупке вы получите скидку {settings.REFERRAL_FIRST_PURCHASE_DISCOUNT}%!"
        
        if is_admin:
            welcome_text += "\n\n⚙️ У вас есть права администратора"
            keyboard = get_admin_keyboard()
        else:
            keyboard = get_main_keyboard()
        
        await message.answer(welcome_text, reply_markup=keyboard)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Обработка команды /help"""
    help_text = """
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

👥 *Реферальная программа*:
• Приглашайте друзей по своей реферальной ссылке
• Они получают {settings.REFERRAL_FIRST_PURCHASE_DISCOUNT}% скидку на первую покупку
• Вы получаете {settings.REFERRAL_BONUS_PERCENT}% от их первой покупки на баланс

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
        
        profile_text = f"""
👤 *Ваш профиль*

🆔 ID: {user.telegram_id}
👤 Имя: {user.first_name or 'Не указано'}
📱 Телефон: {user.phone or 'Не указан'}
💰 Баланс: {user.balance}₽

🎁 Реферальный код: `{user.referral_code}`

Используйте /help для получения справки
"""
        
        await message.answer(profile_text, parse_mode="Markdown")


@router.message(F.text == "🎁 Реферальная программа")
async def show_referral_program(message: Message):
    """Показать информацию о реферальной программе"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        from services.referral_service import ReferralService
        referral_info = await ReferralService.format_referral_info(session, user)
        
        await message.answer(referral_info, parse_mode="Markdown")

