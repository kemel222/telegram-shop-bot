"""
Админский бот для управления магазином
@Hotspotovich_admin_bot
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command, CommandStart
from services.order_service import OrderService
from services.product_service import ProductService
from services.promo_service import PromoService
from services.user_service import UserService
from services.cashback_service import CashbackService
from database.models import OrderStatus, PromoCodeType, Category, Product
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
    waiting_for_category_name = State()
    waiting_for_category_description = State()
    waiting_for_category_cashback = State()
    waiting_for_product_category = State()
    waiting_for_product_name = State()
    waiting_for_product_description = State()
    waiting_for_product_price = State()
    waiting_for_product_quantity = State()
    waiting_for_product_image = State()
    waiting_for_edit_product_id = State()
    waiting_for_edit_product_field = State()
    waiting_for_edit_product_value = State()
    waiting_for_cashback_category = State()
    waiting_for_cashback_percent = State()


@router.message(CommandStart())
@router.message(Command("start"))
async def cmd_start(message: Message):
    """Старт админ-бота"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    admin_text = """
⚙️ *Админ-панель Hotspot*

Добро пожаловать в панель управления магазином!

📋 Доступные команды:

📦 *Заказы:*
/pending_orders - Активные заказы
/all_orders - Все заказы

🛍 *Товары:*
/add_category - Добавить категорию
/add_product - Добавить товар
/edit_product - Редактировать товар
/delete_product - Удалить товар
/categories - Список категорий
/products - Список товаров

💰 *Кешбек:*
/set_cashback - Настроить кешбек по категории

🎟 *Промокоды:*
/create_promo - Создать промокод
/promo_list - Список промокодов

📊 *Статистика:*
/stats - Общая статистика
/users_stats - Статистика пользователей

💻 Разработано @{settings.DEVELOPER_USERNAME}
"""
    
    await message.answer(admin_text, parse_mode="Markdown")


@router.message(Command("pending_orders"))
async def show_pending_orders(message: Message):
    """Показать активные заказы"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    async with async_session_maker() as session:
        orders = await OrderService.get_all_pending_orders(session)
        
        if not orders:
            await message.answer("📭 Нет активных заказов")
            return
        
        await message.answer(f"📦 Найдено активных заказов: {len(orders)}")
        
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
            # Уведомляем пользователя через основной бот
            try:
                from aiogram import Bot
                shop_bot = Bot(token=settings.SHOP_BOT_TOKEN)
                
                await shop_bot.send_message(
                    order.user.telegram_id,
                    f"✅ Ваша оплата по заказу #{order_id} подтверждена!\n"
                    f"Статус заказа: {order.status.value}\n\n"
                    f"📞 Если есть вопросы, пишите @{settings.MANAGER_USERNAME}"
                )
                
                await shop_bot.session.close()
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
                from aiogram import Bot
                shop_bot = Bot(token=settings.SHOP_BOT_TOKEN)
                
                await shop_bot.send_message(
                    order.user.telegram_id,
                    f"❌ Ваша оплата по заказу #{order_id} отклонена.\n"
                    f"Заказ отменён. Если вы считаете, что это ошибка, свяжитесь с @{settings.MANAGER_USERNAME}"
                )
                
                await shop_bot.session.close()
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
            try:
                from aiogram import Bot
                shop_bot = Bot(token=settings.SHOP_BOT_TOKEN)
                
                await shop_bot.send_message(
                    order.user.telegram_id,
                    f"📦 Ваш заказ #{order_id} готов к выдаче!\n"
                    f"Вы можете забрать его в указанное время.\n\n"
                    f"📞 Вопросы? Пишите @{settings.MANAGER_USERNAME}"
                )
                
                await shop_bot.session.close()
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
    """Завершить заказ и начислить кешбек"""
    if not is_admin(callback.from_user.id):
        await callback.answer("❌ У вас нет прав администратора", show_alert=True)
        return
    
    order_id = int(callback.data.split("_")[2])
    
    async with async_session_maker() as session:
        order = await OrderService.update_order_status(session, order_id, OrderStatus.COMPLETED)
        
        if order:
            # Начисляем кешбек пользователю
            cashback_result = await CashbackService.process_cashback(session, order)
            
            cashback_message = ""
            if cashback_result:
                user, cashback_amount = cashback_result
                cashback_message = f"\n💰 Начислен кешбек: {cashback_amount}₽"
            
            try:
                from aiogram import Bot
                shop_bot = Bot(token=settings.SHOP_BOT_TOKEN)
                
                user_message = f"""✅ Заказ #{order_id} завершён!
Спасибо за покупку! Будем рады видеть вас снова.
{cashback_message}

💬 Оставьте отзыв или задайте вопрос: @{settings.MANAGER_USERNAME}
💻 Разработано @{settings.DEVELOPER_USERNAME}"""
                
                await shop_bot.send_message(
                    order.user.telegram_id,
                    user_message
                )
                
                await shop_bot.session.close()
            except:
                pass
            
            await callback.message.edit_text(
                callback.message.text + f"\n\n✅ Заказ завершён{cashback_message}"
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
        "Введите тип:"
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
        
        result = await session.execute(select(func.count(User.id)))
        total_users = result.scalar()
        
        result = await session.execute(select(func.count(Order.id)))
        total_orders = result.scalar()
        
        result = await session.execute(select(func.sum(Order.total)))
        total_revenue = result.scalar() or 0
        
        result = await session.execute(select(func.count(Product.id)))
        total_products = result.scalar()
        
        stats_text = f"""
📊 *Статистика Hotspot*

👥 Всего пользователей: {total_users}
📦 Всего заказов: {total_orders}
💰 Общая выручка: {total_revenue}₽
🛍 Товаров в каталоге: {total_products}

💻 Разработано @{settings.DEVELOPER_USERNAME}
"""
        
        await message.answer(stats_text, parse_mode="Markdown")


# ============== УПРАВЛЕНИЕ ТОВАРАМИ ==============

@router.message(Command("add_category"))
async def add_category_start(message: Message, state: FSMContext):
    """Начать добавление категории"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await message.answer("📁 Введите название категории:")
    await state.set_state(AdminStates.waiting_for_category_name)


@router.message(AdminStates.waiting_for_category_name)
async def process_category_name(message: Message, state: FSMContext):
    """Обработать название категории"""
    await state.update_data(name=message.text)
    await message.answer("📝 Введите описание категории (или '-' чтобы пропустить):")
    await state.set_state(AdminStates.waiting_for_category_description)


@router.message(AdminStates.waiting_for_category_description)
async def process_category_description(message: Message, state: FSMContext):
    """Обработать описание категории"""
    description = None if message.text == '-' else message.text
    await state.update_data(description=description)
    
    await message.answer(
        f"💰 Введите процент кешбека для категории\n"
        f"(по умолчанию {settings.CASHBACK_DEFAULT_PERCENT}%, для подов {settings.CASHBACK_PODS_PERCENT}%):"
    )
    await state.set_state(AdminStates.waiting_for_category_cashback)


@router.message(AdminStates.waiting_for_category_cashback)
async def process_category_cashback(message: Message, state: FSMContext):
    """Создать категорию"""
    try:
        cashback = float(message.text)
    except ValueError:
        cashback = settings.CASHBACK_DEFAULT_PERCENT
    
    data = await state.get_data()
    
    async with async_session_maker() as session:
        category = Category(
            name=data['name'],
            description=data.get('description'),
            cashback_percent=cashback
        )
        session.add(category)
        await session.commit()
        await session.refresh(category)
        
        await message.answer(
            f"✅ Категория создана!\n\n"
            f"📁 Название: {category.name}\n"
            f"📝 Описание: {category.description or 'Не указано'}\n"
            f"💰 Кешбек: {category.cashback_percent}%"
        )
    
    await state.clear()


@router.message(Command("categories"))
async def show_categories(message: Message):
    """Показать список категорий"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        
        if not categories:
            await message.answer("📭 Категории не найдены")
            return
        
        text = "📁 *Категории:*\n\n"
        for cat in categories:
            text += f"🆔 ID: {cat.id}\n"
            text += f"📝 {cat.name}\n"
            text += f"💰 Кешбек: {cat.cashback_percent}%\n\n"
        
        await message.answer(text, parse_mode="Markdown")


@router.message(Command("add_product"))
async def add_product_start(message: Message, state: FSMContext):
    """Начать добавление товара"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        
        if not categories:
            await message.answer("❌ Сначала создайте категорию с помощью /add_category")
            return
        
        text = "📁 Выберите категорию (введите ID):\n\n"
        for cat in categories:
            text += f"{cat.id}. {cat.name}\n"
        
        await message.answer(text)
        await state.set_state(AdminStates.waiting_for_product_category)


@router.message(AdminStates.waiting_for_product_category)
async def process_product_category(message: Message, state: FSMContext):
    """Обработать категорию товара"""
    try:
        category_id = int(message.text)
        await state.update_data(category_id=category_id)
        await message.answer("🏷 Введите название товара:")
        await state.set_state(AdminStates.waiting_for_product_name)
    except ValueError:
        await message.answer("❌ Введите корректный ID категории")


@router.message(AdminStates.waiting_for_product_name)
async def process_product_name(message: Message, state: FSMContext):
    """Обработать название товара"""
    await state.update_data(name=message.text)
    await message.answer("📝 Введите описание товара (или '-' чтобы пропустить):")
    await state.set_state(AdminStates.waiting_for_product_description)


@router.message(AdminStates.waiting_for_product_description)
async def process_product_description(message: Message, state: FSMContext):
    """Обработать описание товара"""
    description = None if message.text == '-' else message.text
    await state.update_data(description=description)
    await message.answer("💰 Введите цену товара (в рублях):")
    await state.set_state(AdminStates.waiting_for_product_price)


@router.message(AdminStates.waiting_for_product_price)
async def process_product_price(message: Message, state: FSMContext):
    """Обработать цену товара"""
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("📦 Введите количество товара на складе:")
        await state.set_state(AdminStates.waiting_for_product_quantity)
    except ValueError:
        await message.answer("❌ Введите корректную цену")


@router.message(AdminStates.waiting_for_product_quantity)
async def process_product_quantity(message: Message, state: FSMContext):
    """Создать товар"""
    try:
        quantity = int(message.text)
    except ValueError:
        await message.answer("❌ Введите корректное количество")
        return
    
    data = await state.get_data()
    
    async with async_session_maker() as session:
        product = Product(
            category_id=data['category_id'],
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            quantity=quantity,
            is_available=quantity > 0
        )
        session.add(product)
        await session.commit()
        await session.refresh(product)
        
        await message.answer(
            f"✅ Товар создан!\n\n"
            f"🆔 ID: {product.id}\n"
            f"🏷 Название: {product.name}\n"
            f"💰 Цена: {product.price}₽\n"
            f"📦 Количество: {product.quantity}"
        )
    
    await state.clear()


@router.message(Command("products"))
async def show_products(message: Message):
    """Показать список товаров"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    async with async_session_maker() as session:
        products = await ProductService.get_all_products(session)
        
        if not products:
            await message.answer("📭 Товары не найдены")
            return
        
        text = "🛍 *Товары:*\n\n"
        for prod in products:
            text += f"🆔 ID: {prod.id}\n"
            text += f"🏷 {prod.name}\n"
            text += f"💰 {prod.price}₽\n"
            text += f"📦 Остаток: {prod.quantity}\n"
            text += f"✅ Доступен: {'Да' if prod.is_available else 'Нет'}\n\n"
        
        await message.answer(text, parse_mode="Markdown")


@router.message(Command("edit_product"))
async def edit_product_start(message: Message, state: FSMContext):
    """Начать редактирование товара"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await message.answer("🆔 Введите ID товара для редактирования:")
    await state.set_state(AdminStates.waiting_for_edit_product_id)


@router.message(AdminStates.waiting_for_edit_product_id)
async def process_edit_product_id(message: Message, state: FSMContext):
    """Обработать ID товара"""
    try:
        product_id = int(message.text)
        
        async with async_session_maker() as session:
            product = await ProductService.get_product_by_id(session, product_id)
            
            if not product:
                await message.answer("❌ Товар не найден")
                await state.clear()
                return
            
            await state.update_data(product_id=product_id)
            await message.answer(
                f"📝 Товар: {product.name}\n\n"
                f"Что хотите изменить?\n"
                f"1. name - Название\n"
                f"2. description - Описание\n"
                f"3. price - Цена\n"
                f"4. quantity - Количество\n"
                f"5. available - Доступность (yes/no)\n\n"
                f"Введите название поля:"
            )
            await state.set_state(AdminStates.waiting_for_edit_product_field)
    except ValueError:
        await message.answer("❌ Введите корректный ID")


@router.message(AdminStates.waiting_for_edit_product_field)
async def process_edit_product_field(message: Message, state: FSMContext):
    """Обработать поле для редактирования"""
    field = message.text.lower()
    valid_fields = ['name', 'description', 'price', 'quantity', 'available']
    
    if field not in valid_fields:
        await message.answer("❌ Неверное поле. Выберите из списка.")
        return
    
    await state.update_data(field=field)
    await message.answer(f"✏️ Введите новое значение для {field}:")
    await state.set_state(AdminStates.waiting_for_edit_product_value)


@router.message(AdminStates.waiting_for_edit_product_value)
async def process_edit_product_value(message: Message, state: FSMContext):
    """Обновить товар"""
    data = await state.get_data()
    field = data['field']
    value = message.text
    
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(
            select(Product).where(Product.id == data['product_id'])
        )
        product = result.scalar_one_or_none()
        
        if not product:
            await message.answer("❌ Товар не найден")
            await state.clear()
            return
        
        try:
            if field == 'name':
                product.name = value
            elif field == 'description':
                product.description = value
            elif field == 'price':
                product.price = float(value)
            elif field == 'quantity':
                product.quantity = int(value)
                product.is_available = product.quantity > 0
            elif field == 'available':
                product.is_available = value.lower() in ['yes', 'да', 'true', '1']
            
            await session.commit()
            await message.answer(f"✅ Товар обновлён!\n{field} = {value}")
        except ValueError:
            await message.answer("❌ Неверный формат значения")
    
    await state.clear()


@router.message(Command("delete_product"))
async def delete_product(message: Message):
    """Удалить товар"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    await message.answer("🗑 Введите ID товара для удаления:")


# ============== УПРАВЛЕНИЕ КЕШБЕКОМ ==============

@router.message(Command("set_cashback"))
async def set_cashback_start(message: Message, state: FSMContext):
    """Начать настройку кешбека"""
    if not is_admin(message.from_user.id):
        await message.answer("❌ У вас нет прав администратора")
        return
    
    async with async_session_maker() as session:
        from sqlalchemy import select
        result = await session.execute(select(Category))
        categories = result.scalars().all()
        
        if not categories:
            await message.answer("❌ Категории не найдены")
            return
        
        text = "📁 Выберите категорию (введите ID):\n\n"
        for cat in categories:
            text += f"{cat.id}. {cat.name} (текущий кешбек: {cat.cashback_percent}%)\n"
        
        await message.answer(text)
        await state.set_state(AdminStates.waiting_for_cashback_category)


@router.message(AdminStates.waiting_for_cashback_category)
async def process_cashback_category(message: Message, state: FSMContext):
    """Обработать выбор категории"""
    try:
        category_id = int(message.text)
        await state.update_data(category_id=category_id)
        await message.answer("💰 Введите новый процент кешбека (например: 2.5):")
        await state.set_state(AdminStates.waiting_for_cashback_percent)
    except ValueError:
        await message.answer("❌ Введите корректный ID категории")


@router.message(AdminStates.waiting_for_cashback_percent)
async def process_cashback_percent(message: Message, state: FSMContext):
    """Обновить процент кешбека"""
    try:
        percent = float(message.text)
        data = await state.get_data()
        
        async with async_session_maker() as session:
            category = await CashbackService.update_category_cashback(
                session,
                data['category_id'],
                percent
            )
            
            if category:
                await message.answer(
                    f"✅ Кешбек обновлён!\n\n"
                    f"📁 Категория: {category.name}\n"
                    f"💰 Новый процент кешбека: {category.cashback_percent}%"
                )
            else:
                await message.answer("❌ Категория не найдена")
        
        await state.clear()
    except ValueError:
        await message.answer("❌ Введите корректное число")

