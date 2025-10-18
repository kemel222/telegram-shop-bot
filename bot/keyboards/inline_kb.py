from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database.models import Category, Product, Order
from typing import List


def get_categories_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """Клавиатура с категориями"""
    buttons = []
    
    for category in categories:
        buttons.append([
            InlineKeyboardButton(
                text=category.name,
                callback_data=f"category_{category.id}"
            )
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_products_keyboard(products: List[Product], category_id: int = None) -> InlineKeyboardMarkup:
    """Клавиатура с товарами"""
    buttons = []
    
    for product in products:
        buttons.append([
            InlineKeyboardButton(
                text=f"{product.name} - {product.price}₽",
                callback_data=f"product_{product.id}"
            )
        ])
    
    # Кнопка назад к категориям
    if category_id:
        buttons.append([
            InlineKeyboardButton(text="⬅️ Назад", callback_data="categories")
        ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_product_detail_keyboard(product_id: int, is_in_cart: bool = False, is_favorite: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура для карточки товара"""
    buttons = []
    
    # Кнопка добавления в корзину
    if not is_in_cart:
        buttons.append([
            InlineKeyboardButton(
                text="🛒 Добавить в корзину",
                callback_data=f"add_to_cart_{product_id}"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="✅ В корзине",
                callback_data=f"in_cart_{product_id}"
            )
        ])
    
    # Кнопка избранного
    if not is_favorite:
        buttons.append([
            InlineKeyboardButton(
                text="🤍 Добавить в избранное",
                callback_data=f"add_to_fav_{product_id}"
            )
        ])
    else:
        buttons.append([
            InlineKeyboardButton(
                text="❤️ Убрать из избранного",
                callback_data=f"remove_from_fav_{product_id}"
            )
        ])
    
    # Кнопка назад
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="categories")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_cart_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура для корзины"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Оформить заказ", callback_data="checkout")
        ],
        [
            InlineKeyboardButton(text="🗑 Очистить корзину", callback_data="clear_cart")
        ],
        [
            InlineKeyboardButton(text="⬅️ Продолжить покупки", callback_data="categories")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_delivery_type_keyboard() -> InlineKeyboardMarkup:
    """Клавиатура выбора типа доставки"""
    buttons = [
        [
            InlineKeyboardButton(text="🏢 Самовывоз из Центра", callback_data="delivery_pickup_center")
        ],
        [
            InlineKeyboardButton(text="🏬 Самовывоз из ТЦ", callback_data="delivery_pickup_tc")
        ],
        [
            InlineKeyboardButton(text="🚚 Доставка (300₽)", callback_data="delivery_delivery")
        ],
        [
            InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel_order")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_payment_method_keyboard(has_balance: bool = False) -> InlineKeyboardMarkup:
    """Клавиатура выбора способа оплаты"""
    buttons = [
        [
            InlineKeyboardButton(text="💳 СБП онлайн", callback_data="payment_sbp_online")
        ],
        [
            InlineKeyboardButton(text="💳 СБП при получении", callback_data="payment_sbp_receipt")
        ],
        [
            InlineKeyboardButton(text="💵 Наличными при получении", callback_data="payment_cash")
        ]
    ]
    
    if has_balance:
        buttons.append([
            InlineKeyboardButton(text="💰 Оплатить балансом", callback_data="payment_balance")
        ])
    
    buttons.append([
        InlineKeyboardButton(text="⬅️ Назад", callback_data="cancel_order")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_order_confirmation_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура подтверждения заказа"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm_order_{order_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_order_{order_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_admin_order_keyboard(order_id: int) -> InlineKeyboardMarkup:
    """Клавиатура для управления заказом (админ)"""
    buttons = [
        [
            InlineKeyboardButton(text="✅ Подтвердить оплату", callback_data=f"admin_approve_{order_id}")
        ],
        [
            InlineKeyboardButton(text="❌ Отклонить оплату", callback_data=f"admin_reject_{order_id}")
        ],
        [
            InlineKeyboardButton(text="📦 Готов к выдаче", callback_data=f"admin_ready_{order_id}")
        ],
        [
            InlineKeyboardButton(text="✅ Завершить заказ", callback_data=f"admin_complete_{order_id}")
        ]
    ]
    
    return InlineKeyboardMarkup(inline_keyboard=buttons)

