from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command
from services.order_service import OrderService
from services.product_service import ProductService
from services.promo_service import PromoService
from services.user_service import UserService
from database.models import OrderStatus, PromoCodeType
from database.database import async_session_maker
from config import settings
from bot.keyboards.inline_kb import get_admin_order_keyboard

router = Router()


def is_admin(user_id: int) -> bool:
    """Проверить, является ли пользователь администратором"""
    return user_id in settings.admin_ids_list


class AdminStates(StatesGroup):
    waiting_for_promo_code = State()
    waiting_for_promo_type = State()
    waiting_for_promo_value = State()


@router.message(F.text == "⚙️ Админ-панель")
async def admin_panel(message: Message):
    """Показать админ-панель"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    admin_text = """
⚙️ *Админ-панель*

Доступные команды:

📦 /pending_orders - Заказы, ожидающие обработки
🎟 /create_promo - Создать промокод
📊 /stats - Статистика

Вы также можете управлять заказами через уведомления.
"""
    
    await message.answer(admin_text, parse_mode="Markdown")


@router.message(Command("pending_orders"))
async def show_pending_orders(message: Message):
    """Показать заказы, ожидающие обработки"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    async with async_session_maker() as session:
        orders = await OrderService.get_all_pending_orders(session)
        
        if not orders:
            await message.answer("📭 Нет заказов, ожидающих обработки")
            return
        
        for order in orders:
            order_info = await OrderService.format_order_info(session, order)
            keyboard = get_admin_order_keyboard(order.id)
            await message.answer(order_info, reply_markup=keyboard)


@router.callback_query(F.data.startswith("admin_approve_"))
async def approve_payment(callback: CallbackQuery):
    """Подтвердить оплату"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        order = await OrderService.update_payment_status(session, order_id, "paid")
        
        if order:
            # Уведомляем пользователя
            try:
                await callback.bot.send_message(
                    order.user.telegram_id,
                    f"✅ Ваша оплата по заказу #{order_id} подтверждена!\n"
                    f"Статус заказа изменён на: {order.status.value}"
                )
            except:
                pass
            
            await callback.message.edit_text(
                callback.message.text + "\n\n✅ Оплата подтверждена"
            )
        else:
            await callback.answer("❌ Заказ не найден", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("admin_reject_"))
async def reject_payment(callback: CallbackQuery):
    """Отклонить оплату"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        success = await OrderService.cancel_order(session, order_id)
        
        if success:
            order = await OrderService.get_order_by_id(session, order_id)
            
            # Уведомляем пользователя
            try:
                await callback.bot.send_message(
                    order.user.telegram_id,
                    f"❌ Ваша оплата по заказу #{order_id} отклонена.\n"
                    f"Заказ отменён. Если вы считаете, что это ошибка, свяжитесь с поддержкой."
                )
            except:
                pass
            
            await callback.message.edit_text(
                callback.message.text + "\n\n❌ Оплата отклонена, заказ отменён"
            )
        else:
            await callback.answer("❌ Не удалось отменить заказ", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("admin_ready_"))
async def mark_order_ready(callback: CallbackQuery):
    """Отметить заказ готовым к выдаче"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        order = await OrderService.update_order_status(session, order_id, OrderStatus.READY)
        
        if order:
            # Уведомляем пользователя
            try:
                await callback.bot.send_message(
                    order.user.telegram_id,
                    f"📦 Ваш заказ #{order_id} готов к выдаче!\n"
                    f"Вы можете забрать его в указанное время."
                )
            except:
                pass
            
            await callback.message.edit_text(
                callback.message.text + "\n\n📦 Заказ готов к выдаче"
            )
        else:
            await callback.answer("❌ Заказ не найден", show_alert=True)
    
    await callback.answer()


@router.callback_query(F.data.startswith("admin_complete_"))
async def complete_order(callback: CallbackQuery):
    """Завершить заказ"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        order = await OrderService.update_order_status(session, order_id, OrderStatus.COMPLETED)
        
        if order:
            # Уведомляем пользователя
            try:
                await callback.bot.send_message(
                    order.user.telegram_id,
                    f"✅ Заказ #{order_id} завершён!\n"
                    f"Спасибо за покупку! Будем рады видеть вас снова."
                )
            except:
                pass
            
            await callback.message.edit_text(
                callback.message.text + "\n\n✅ Заказ завершён"
            )
        else:
            await callback.answer("❌ Заказ не найден", show_alert=True)
    
    await callback.answer()


@router.message(Command("create_promo"))
async def create_promo_start(message: Message, state: FSMContext):
    """Начать создание промокода"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await message.answer("🎟 Введите код промокода (например: SALE20):")
    await state.set_state(AdminStates.waiting_for_promo_code)


@router.message(AdminStates.waiting_for_promo_code)
async def process_promo_code(message: Message, state: FSMContext):
    """Обработать код промокода"""
    await state.update_data(code=message.text.upper())
    
    await message.answer(
        "📋 Выберите тип промокода:\n\n"
        "1️⃣ percent - Скидка в процентах\n"
        "2️⃣ fixed - Фиксированная скидка в рублях\n"
        "3️⃣ balance - Пополнение баланса\n\n"
        "Введите тип (percent/fixed/balance):"
    )
    await state.set_state(AdminStates.waiting_for_promo_type)


@router.message(AdminStates.waiting_for_promo_type)
async def process_promo_type(message: Message, state: FSMContext):
    """Обработать тип промокода"""
    promo_type = message.text.lower()
    
    if promo_type not in ['percent', 'fixed', 'balance']:
        await message.answer("❌ Неверный тип. Используйте: percent, fixed или balance")
        return
    
    await state.update_data(type=promo_type)
    
    if promo_type == 'percent':
        await message.answer("💯 Введите процент скидки (например: 20):")
    elif promo_type == 'fixed':
        await message.answer("💰 Введите сумму скидки в рублях (например: 500):")
    else:
        await message.answer("💰 Введите сумму пополнения баланса в рублях (например: 1000):")
    
    await state.set_state(AdminStates.waiting_for_promo_value)


@router.message(AdminStates.waiting_for_promo_value)
async def process_promo_value(message: Message, state: FSMContext):
    """Обработать значение промокода и создать его"""
    try:
        value = float(message.text)
    except ValueError:
        await message.answer("❌ Введите корректное число")
        return
    
    data = await state.get_data()
    
    # Маппинг типа
    type_mapping = {
        'percent': PromoCodeType.PERCENT,
        'fixed': PromoCodeType.FIXED,
        'balance': PromoCodeType.BALANCE
    }
    
    promo_type = type_mapping[data['type']]
    
    async with async_session_maker() as session:
        promo = await PromoService.create_promo_code(
            session,
            data['code'],
            promo_type,
            value
        )
        
        await message.answer(
            f"✅ Промокод создан!\n\n"
            f"🎟 Код: {promo.code}\n"
            f"📋 Тип: {promo.type.value}\n"
            f"💰 Значение: {promo.value}\n"
            f"🔄 Использований: {promo.usage_count}"
        )
    
    await state.clear()


@router.message(Command("stats"))
async def show_stats(message: Message):
    """Показать статистику"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    async with async_session_maker() as session:
        from sqlalchemy import select, func
        from database.models import User, Order, Product
        
        # Количество пользователей
        result = await session.execute(select(func.count(User.id)))
        total_users = result.scalar()
        
        # Количество заказов
        result = await session.execute(select(func.count(Order.id)))
        total_orders = result.scalar()
        
        # Сумма всех заказов
        result = await session.execute(select(func.sum(Order.total)))
        total_revenue = result.scalar() or 0
        
        # Количество товаров
        result = await session.execute(select(func.count(Product.id)))
        total_products = result.scalar()
        
        stats_text = f"""
📊 *Статистика*

👥 Всего пользователей: {total_users}
📦 Всего заказов: {total_orders}
💰 Общая выручка: {total_revenue}₽
🛍 Товаров в каталоге: {total_products}
"""
        
        await message.answer(stats_text, parse_mode="Markdown")

