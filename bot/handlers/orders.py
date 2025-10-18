from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.inline_kb import (
    get_delivery_type_keyboard,
    get_payment_method_keyboard,
    get_order_confirmation_keyboard
)
from services.cart_service import CartService
from services.order_service import OrderService
from services.user_service import UserService
from services.promo_service import PromoService
from services.referral_service import ReferralService
from database.models import DeliveryType, PaymentMethod, OrderStatus
from database.database import async_session_maker
from config import settings

router = Router()


class OrderStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_phone = State()
    waiting_for_address = State()
    waiting_for_time_slot = State()
    waiting_for_promo = State()
    waiting_for_payment_screenshot = State()


@router.callback_query(F.data == "checkout")
async def start_checkout(callback: CallbackQuery, state: FSMContext):
    """Начать оформление заказа"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        cart_items = await CartService.get_cart_items(session, user.id)
        
        if not cart_items:
            await callback.answer("❌ Ваша корзина пуста", show_alert=True)
            return
        
        # Выбор типа доставки
        await callback.message.edit_text(
            "📦 Выберите способ получения заказа:",
            reply_markup=get_delivery_type_keyboard()
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("delivery_"))
async def choose_delivery_type(callback: CallbackQuery, state: FSMContext):
    """Выбрать тип доставки"""
    delivery_type = callback.data.split("_", 1)[1]
    
    # Сохраняем тип доставки
    await state.update_data(delivery_type=delivery_type)
    
    # Запрашиваем имя
    await callback.message.edit_text("👤 Введите ваше имя:")
    await state.set_state(OrderStates.waiting_for_name)
    await callback.answer()


@router.message(OrderStates.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    """Обработать введённое имя"""
    await state.update_data(customer_name=message.text)
    
    # Запрашиваем телефон
    await message.answer("📱 Введите ваш номер телефона:")
    await state.set_state(OrderStates.waiting_for_phone)


@router.message(OrderStates.waiting_for_phone)
async def process_phone(message: Message, state: FSMContext):
    """Обработать введённый телефон"""
    await state.update_data(customer_phone=message.text)
    
    data = await state.get_data()
    delivery_type = data['delivery_type']
    
    # Если доставка - запрашиваем адрес
    if delivery_type == "delivery":
        await message.answer("📍 Введите адрес доставки:")
        await state.set_state(OrderStates.waiting_for_address)
    # Если самовывоз - запрашиваем временной слот
    elif delivery_type == "pickup_center":
        await message.answer("🕐 Выберите удобное время для самовывоза из Центра (12:00-17:00):\nНапример: 14:00")
        await state.set_state(OrderStates.waiting_for_time_slot)
    elif delivery_type == "pickup_tc":
        await message.answer("🕐 Выберите удобное время для самовывоза из ТЦ (16:30-21:00):\nНапример: 18:00")
        await state.set_state(OrderStates.waiting_for_time_slot)


@router.message(OrderStates.waiting_for_address)
async def process_address(message: Message, state: FSMContext):
    """Обработать введённый адрес"""
    await state.update_data(delivery_address=message.text)
    
    # Запрашиваем промокод
    await message.answer("🎟 Введите промокод (или напишите 'нет', если у вас его нет):")
    await state.set_state(OrderStates.waiting_for_promo)


@router.message(OrderStates.waiting_for_time_slot)
async def process_time_slot(message: Message, state: FSMContext):
    """Обработать временной слот"""
    await state.update_data(delivery_time_slot=message.text)
    
    # Запрашиваем промокод
    await message.answer("🎟 Введите промокод (или напишите 'нет', если у вас его нет):")
    await state.set_state(OrderStates.waiting_for_promo)


@router.message(OrderStates.waiting_for_promo)
async def process_promo(message: Message, state: FSMContext):
    """Обработать промокод"""
    promo_code = None
    discount = 0.0
    
    if message.text.lower() not in ['нет', 'no', 'skip', '-']:
        async with async_session_maker() as session:
            user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
            cart_total = await CartService.get_cart_total(session, user.id)
            
            # Проверяем промокод
            is_valid, error_msg, promo = await PromoService.validate_promo_code(session, message.text)
            
            if is_valid:
                promo_code = message.text
                # Применяем промокод для расчёта скидки
                _, _, discount = await PromoService.apply_promo_code(
                    session, user.id, promo_code, cart_total
                )
                await message.answer(f"✅ Промокод применён! Скидка: {discount}₽")
            else:
                await message.answer(f"❌ {error_msg}\nПродолжаем без промокода.")
    
    await state.update_data(promo_code=promo_code, discount=discount)
    
    # Выбор способа оплаты
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        has_balance = user.balance > 0
    
    await message.answer(
        "💳 Выберите способ оплаты:",
        reply_markup=get_payment_method_keyboard(has_balance)
    )


@router.callback_query(F.data.startswith("payment_"))
async def choose_payment_method(callback: CallbackQuery, state: FSMContext):
    """Выбрать способ оплаты и создать заказ"""
    payment_method_str = callback.data.split("_", 1)[1]
    
    # Маппинг строки на enum
    payment_mapping = {
        "sbp_online": PaymentMethod.SBP_ONLINE,
        "sbp_receipt": PaymentMethod.SBP_ON_RECEIPT,
        "cash": PaymentMethod.CASH,
        "balance": PaymentMethod.BALANCE
    }
    
    payment_method = payment_mapping.get(payment_method_str)
    
    if not payment_method:
        await callback.answer("❌ Неверный способ оплаты", show_alert=True)
        return
    
    data = await state.get_data()
    
    # Маппинг типа доставки
    delivery_mapping = {
        "pickup_center": DeliveryType.PICKUP_CENTER,
        "pickup_tc": DeliveryType.PICKUP_TC,
        "delivery": DeliveryType.DELIVERY
    }
    
    delivery_type = delivery_mapping.get(data['delivery_type'])
    
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        # Создаём заказ
        order = await OrderService.create_order_from_cart(
            session,
            user.id,
            delivery_type,
            data['customer_name'],
            data['customer_phone'],
            payment_method,
            data.get('delivery_address'),
            data.get('delivery_time_slot'),
            data.get('promo_code'),
            data.get('discount', 0.0)
        )
        
        if not order:
            await callback.message.edit_text("❌ Не удалось создать заказ. Возможно, некоторые товары закончились.")
            await state.clear()
            return
        
        # Если оплата балансом, списываем средства
        if payment_method == PaymentMethod.BALANCE:
            success, message_text = await PromoService.use_balance(session, user.id, order.total)
            
            if not success:
                await OrderService.cancel_order(session, order.id)
                await callback.message.edit_text(f"❌ {message_text}")
                await state.clear()
                return
            
            await OrderService.update_payment_status(session, order.id, "paid")
            
            # Обрабатываем реферальный бонус
            await ReferralService.process_referral_bonus(session, order)
        
        # Формируем информацию о заказе
        order_info = await OrderService.format_order_info(session, order)
        
        # Дополнительная информация в зависимости от способа оплаты
        if payment_method == PaymentMethod.SBP_ONLINE:
            order_info += f"\n\n💳 Для оплаты переведите {order.total}₽ на номер:\n{settings.SBP_PHONE} ({settings.SBP_BANK_NAME})\n\nПосле оплаты отправьте скриншот."
            await state.set_state(OrderStates.waiting_for_payment_screenshot)
            await state.update_data(order_id=order.id)
        elif payment_method == PaymentMethod.BALANCE:
            order_info += "\n\n✅ Заказ оплачен с баланса!"
        else:
            order_info += "\n\n✅ Заказ создан! Ожидайте подтверждения."
        
        await callback.message.edit_text(order_info)
    
    if payment_method != PaymentMethod.SBP_ONLINE:
        await state.clear()
    
    await callback.answer()


@router.message(OrderStates.waiting_for_payment_screenshot, F.photo)
async def process_payment_screenshot(message: Message, state: FSMContext):
    """Обработать скриншот оплаты"""
    data = await state.get_data()
    order_id = data.get('order_id')
    
    if not order_id:
        await message.answer("❌ Ошибка: заказ не найден")
        await state.clear()
        return
    
    # Сохраняем скриншот
    from database.models import PaymentScreenshot
    
    async with async_session_maker() as session:
        photo = message.photo[-1]  # Самое большое фото
        
        screenshot = PaymentScreenshot(
            order_id=order_id,
            file_id=photo.file_id
        )
        
        session.add(screenshot)
        await session.commit()
        
        # Уведомляем пользователя
        await message.answer("✅ Скриншот получен! Ожидайте подтверждения оплаты от администратора.")
        
        # Уведомляем администраторов
        from aiogram import Bot
        bot = message.bot
        
        for admin_id in settings.admin_ids_list:
            try:
                from bot.keyboards.inline_kb import get_admin_order_keyboard
                order = await OrderService.get_order_by_id(session, order_id)
                order_info = await OrderService.format_order_info(session, order)
                
                await bot.send_photo(
                    admin_id,
                    photo.file_id,
                    caption=f"💳 Новый скриншот оплаты\n\n{order_info}",
                    reply_markup=get_admin_order_keyboard(order_id)
                )
            except:
                pass
    
    await state.clear()


@router.message(F.text == "📦 Мои заказы")
async def show_orders(message: Message):
    """Показать заказы пользователя"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        orders = await OrderService.get_user_orders(session, user.id)
        
        if not orders:
            await message.answer("📭 У вас пока нет заказов")
            return
        
        for order in orders[:10]:  # Показываем последние 10 заказов
            order_info = await OrderService.format_order_info(session, order)
            await message.answer(order_info)


@router.callback_query(F.data == "cancel_order")
async def cancel_order_process(callback: CallbackQuery, state: FSMContext):
    """Отменить процесс оформления заказа"""
    await state.clear()
    await callback.message.edit_text("❌ Оформление заказа отменено")
    await callback.answer()

