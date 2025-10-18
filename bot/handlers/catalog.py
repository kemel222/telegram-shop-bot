from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline_kb import (
    get_categories_keyboard,
    get_products_keyboard,
    get_product_detail_keyboard
)
from services.product_service import ProductService
from services.user_service import UserService
from database.database import async_session_maker

router = Router()


@router.callback_query(F.data == "categories")
async def show_categories(callback: CallbackQuery):
    """Показать категории товаров"""
    async with async_session_maker() as session:
        categories = await ProductService.get_all_categories(session)
        
        if not categories:
            await callback.message.edit_text("📭 Категории пока отсутствуют")
            return
        
        keyboard = get_categories_keyboard(categories)
        await callback.message.edit_text(
            "🏪 Выберите категорию:",
            reply_markup=keyboard
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("category_"))
async def show_category_products(callback: CallbackQuery):
    """Показать товары категории"""
    category_id = int(callback.data.split("_")[1])
    
    async with async_session_maker() as session:
        category = await ProductService.get_category_by_id(session, category_id)
        
        if not category:
            await callback.answer("❌ Категория не найдена", show_alert=True)
            return
        
        products = await ProductService.get_products_by_category(session, category_id)
        
        if not products:
            await callback.message.edit_text(
                f"📭 В категории '{category.name}' пока нет товаров",
                reply_markup=get_products_keyboard([], category_id)
            )
            return
        
        keyboard = get_products_keyboard(products, category_id)
        await callback.message.edit_text(
            f"🛍 Категория: {category.name}\n\nВыберите товар:",
            reply_markup=keyboard
        )
    
    await callback.answer()


@router.callback_query(F.data.startswith("product_"))
async def show_product_detail(callback: CallbackQuery):
    """Показать детали товара"""
    product_id = int(callback.data.split("_")[1])
    
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        product = await ProductService.get_product_by_id(session, product_id)
        
        if not product:
            await callback.answer("❌ Товар не найден", show_alert=True)
            return
        
        # Проверяем, в корзине ли товар и в избранном ли
        from services.cart_service import CartService
        cart_items = await CartService.get_cart_items(session, user.id)
        is_in_cart = any(item.product_id == product_id for item in cart_items)
        
        is_favorite = await ProductService.is_in_favorites(session, user.id, product_id)
        
        # Формируем текст
        product_text = f"""
🛍 *{product.name}*

{product.description or 'Описание отсутствует'}

💰 Цена: *{product.price}₽*
📦 В наличии: {product.quantity} шт.
"""
        
        if not product.is_available or product.quantity == 0:
            product_text += "\n❌ Товар закончился"
        
        keyboard = get_product_detail_keyboard(product_id, is_in_cart, is_favorite)
        
        # Если есть изображение, отправляем с фото
        if product.image_url:
            try:
                await callback.message.delete()
                await callback.message.answer_photo(
                    product.image_url,
                    caption=product_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
            except:
                await callback.message.edit_text(
                    product_text,
                    reply_markup=keyboard,
                    parse_mode="Markdown"
                )
        else:
            await callback.message.edit_text(
                product_text,
                reply_markup=keyboard,
                parse_mode="Markdown"
            )
    
    await callback.answer()


@router.callback_query(F.data.startswith("add_to_fav_"))
async def add_to_favorites(callback: CallbackQuery):
    """Добавить товар в избранное"""
    product_id = int(callback.data.split("_")[3])
    
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        success = await ProductService.add_to_favorites(session, user.id, product_id)
        
        if success:
            await callback.answer("❤️ Товар добавлен в избранное")
            # Обновляем клавиатуру
            from services.cart_service import CartService
            cart_items = await CartService.get_cart_items(session, user.id)
            is_in_cart = any(item.product_id == product_id for item in cart_items)
            
            keyboard = get_product_detail_keyboard(product_id, is_in_cart, True)
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        else:
            await callback.answer("❌ Не удалось добавить в избранное", show_alert=True)


@router.callback_query(F.data.startswith("remove_from_fav_"))
async def remove_from_favorites(callback: CallbackQuery):
    """Удалить товар из избранного"""
    product_id = int(callback.data.split("_")[3])
    
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, callback.from_user.id)
        
        if not user:
            await callback.answer("❌ Пользователь не найден", show_alert=True)
            return
        
        success = await ProductService.remove_from_favorites(session, user.id, product_id)
        
        if success:
            await callback.answer("💔 Товар удален из избранного")
            # Обновляем клавиатуру
            from services.cart_service import CartService
            cart_items = await CartService.get_cart_items(session, user.id)
            is_in_cart = any(item.product_id == product_id for item in cart_items)
            
            keyboard = get_product_detail_keyboard(product_id, is_in_cart, False)
            await callback.message.edit_reply_markup(reply_markup=keyboard)
        else:
            await callback.answer("❌ Не удалось удалить из избранного", show_alert=True)


@router.message(F.text == "❤️ Избранное")
async def show_favorites(message: Message):
    """Показать избранные товары"""
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        products = await ProductService.get_user_favorites(session, user.id)
        
        if not products:
            await message.answer("💔 У вас пока нет избранных товаров")
            return
        
        favorites_text = "❤️ *Ваши избранные товары:*\n\n"
        
        for product in products:
            favorites_text += f"🛍 {product.name}\n"
            favorites_text += f"💰 Цена: {product.price}₽\n"
            if product.quantity == 0:
                favorites_text += "❌ Нет в наличии\n"
            favorites_text += "\n"
        
        keyboard = get_products_keyboard(products)
        await message.answer(favorites_text, reply_markup=keyboard, parse_mode="Markdown")

