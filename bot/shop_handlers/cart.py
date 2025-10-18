# Копируем из bot/handlers/cart.py
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from bot.keyboards.inline_kb import get_cart_keyboard, get_product_detail_keyboard
from services.cart_service import CartService
from services.product_service import ProductService
from services.user_service import UserService
from database.database import async_session_maker

router = Router()


class CartStates(StatesGroup):
    waiting_for_quantity = State()


@router.callback_query(F.data.startswith("add_to_cart_"))
async def add_to_cart(callback: CallbackQuery):
    """Добавить товар в корзину"""
    product_id = int(callback.data.split("_")[3])
    
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        cart_item = await CartService.add_to_cart(session, user.id, product_id, 1)
        
        if cart_item:
            await callback.answer("✅ Товар добавлен в корзину")
            
            is_favorite = await ProductService.is_in_favorites(session, user.id, product_id)
            keyboard = get_product_detail_keyboard(product_id, True, is_favorite)
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        else:
            await callback.answer(
                "❌ Не удалось добавить товар в корзину. Возможно, товара нет в наличии.",
                show_alert=True
            )


@router.message(F.text == "🛒 Корзина")
async def show_cart(message: Message):
    """Показать корзину"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        cart_items = await CartService.get_cart_items(session, user.id)
        
        if not cart_items:
            await message.answer("🛒 Ваша корзина пуста")
            return
        
        cart_text = "🛒 *Ваша корзина:*\n\n"
        total = 0.0
        
        for item in cart_items:
            product = await ProductService.get_product_by_id(session, item.product_id)
            if product:
                subtotal = product.price * item.quantity
                total += subtotal
                cart_text += f"🛍 {product.name}\n"
                cart_text += f"   💰 {product.price}₽ x {item.quantity} = {subtotal}₽\n\n"
        
        cart_text += f"💵 *Итого: {total}₽*"
        
        keyboard = get_cart_keyboard()
        await message.answer(cart_text, reply_markup=keyboard, parse_mode="Markdown")


@router.callback_query(F.data == "clear_cart")
async def clear_cart(callback: CallbackQuery):
    """Очистить корзину"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        await CartService.clear_cart(session, user.id)
        await callback.message.edit_text("🗑 Корзина очищена")
    
    await callback.answer()

