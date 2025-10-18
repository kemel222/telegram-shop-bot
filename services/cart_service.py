from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Cart, CartItem, Product
from typing import List, Optional


class CartService:
    @staticmethod
    async def get_or_create_cart(session: AsyncSession, user_id: int) -> Cart:
        """Получить или создать корзину пользователя"""
        result = await session.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        cart = result.scalar_one_or_none()
        
        if not cart:
            cart = Cart(user_id=user_id)
            session.add(cart)
            await session.commit()
            await session.refresh(cart)
        
        return cart
    
    @staticmethod
    async def add_to_cart(
        session: AsyncSession,
        user_id: int,
        product_id: int,
        quantity: int = 1
    ) -> Optional[CartItem]:
        """Добавить товар в корзину"""
        # Проверяем наличие товара
        product = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        product = product.scalar_one_or_none()
        
        if not product or not product.is_available or product.quantity < quantity:
            return None
        
        # Получаем или создаем корзину
        cart = await CartService.get_or_create_cart(session, user_id)
        
        # Проверяем, есть ли уже этот товар в корзине
        result = await session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            # Обновляем количество
            new_quantity = cart_item.quantity + quantity
            if new_quantity > product.quantity:
                return None  # Недостаточно товара
            cart_item.quantity = new_quantity
        else:
            # Создаем новый элемент корзины
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=product_id,
                quantity=quantity
            )
            session.add(cart_item)
        
        await session.commit()
        await session.refresh(cart_item)
        return cart_item
    
    @staticmethod
    async def remove_from_cart(session: AsyncSession, user_id: int, product_id: int) -> bool:
        """Удалить товар из корзины"""
        cart = await CartService.get_or_create_cart(session, user_id)
        
        result = await session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            await session.delete(cart_item)
            await session.commit()
            return True
        
        return False
    
    @staticmethod
    async def update_cart_item_quantity(
        session: AsyncSession,
        user_id: int,
        product_id: int,
        quantity: int
    ) -> Optional[CartItem]:
        """Обновить количество товара в корзине"""
        if quantity <= 0:
            await CartService.remove_from_cart(session, user_id, product_id)
            return None
        
        cart = await CartService.get_or_create_cart(session, user_id)
        
        result = await session.execute(
            select(CartItem).where(
                CartItem.cart_id == cart.id,
                CartItem.product_id == product_id
            )
        )
        cart_item = result.scalar_one_or_none()
        
        if cart_item:
            # Проверяем наличие товара
            product = await session.execute(
                select(Product).where(Product.id == product_id)
            )
            product = product.scalar_one_or_none()
            
            if product and product.quantity >= quantity:
                cart_item.quantity = quantity
                await session.commit()
                await session.refresh(cart_item)
                return cart_item
        
        return None
    
    @staticmethod
    async def get_cart_items(session: AsyncSession, user_id: int) -> List[CartItem]:
        """Получить все товары в корзине"""
        cart = await CartService.get_or_create_cart(session, user_id)
        
        result = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_cart_total(session: AsyncSession, user_id: int) -> float:
        """Получить общую стоимость корзины"""
        cart_items = await CartService.get_cart_items(session, user_id)
        total = 0.0
        
        for item in cart_items:
            result = await session.execute(
                select(Product).where(Product.id == item.product_id)
            )
            product = result.scalar_one_or_none()
            if product:
                total += product.price * item.quantity
        
        return total
    
    @staticmethod
    async def clear_cart(session: AsyncSession, user_id: int):
        """Очистить корзину"""
        cart = await CartService.get_or_create_cart(session, user_id)
        
        result = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        cart_items = result.scalars().all()
        
        for item in cart_items:
            await session.delete(item)
        
        await session.commit()

