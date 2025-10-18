from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import (
    Order, OrderItem, Cart, CartItem, Product, ProductVariant,
    DeliveryType, PaymentMethod, OrderStatus
)
from services.product_service import ProductService
from typing import List, Optional
from datetime import datetime
from config import settings


class OrderService:
    @staticmethod
    async def create_order_from_cart(
        session: AsyncSession,
        user_id: int,
        delivery_type: DeliveryType,
        customer_name: str,
        customer_phone: str,
        payment_method: PaymentMethod,
        delivery_address: Optional[str] = None,
        delivery_time_slot: Optional[str] = None,
        promo_code: Optional[str] = None,
        discount: float = 0.0
    ) -> Optional[Order]:
        """Создать заказ из корзины"""
        
        # Получаем корзину пользователя
        cart = await session.execute(
            select(Cart).where(Cart.user_id == user_id)
        )
        cart = cart.scalar_one_or_none()
        
        if not cart:
            return None
        
        # Получаем товары корзины
        cart_items = await session.execute(
            select(CartItem).where(CartItem.cart_id == cart.id)
        )
        cart_items = cart_items.scalars().all()
        
        if not cart_items:
            return None
        
        # Рассчитываем стоимость
        subtotal = 0.0
        delivery_cost = 0.0
        
        if delivery_type == DeliveryType.DELIVERY:
            delivery_cost = settings.DELIVERY_PRICE
        
        # Проверяем доступность товаров и рассчитываем стоимость
        order_items_data = []
        for cart_item in cart_items:
            product = await ProductService.get_product_by_id(session, cart_item.product_id)
            if not product or not product.is_available:
                return None
            
            # Определяем цену и доступность
            price = product.price
            available_quantity = product.quantity
            
            if cart_item.variant_id:
                variant = await ProductService.get_variant_by_id(session, cart_item.variant_id)
                if not variant or not variant.is_available:
                    return None
                
                price = variant.price or product.price
                available_quantity = variant.quantity
            
            if available_quantity < cart_item.quantity:
                return None
            
            subtotal += price * cart_item.quantity
            
            order_items_data.append({
                'product_id': product.id,
                'variant_id': cart_item.variant_id,
                'quantity': cart_item.quantity,
                'price': price,
                'variant_name': variant.name if cart_item.variant_id and variant else None
            })
        
        total = subtotal + delivery_cost - discount
        
        # Создаем заказ
        order = Order(
            user_id=user_id,
            delivery_type=delivery_type,
            delivery_address=delivery_address,
            delivery_time_slot=delivery_time_slot,
            customer_name=customer_name,
            customer_phone=customer_phone,
            payment_method=payment_method,
            subtotal=subtotal,
            delivery_cost=delivery_cost,
            discount=discount,
            total=total,
            promo_code_used=promo_code,
            status=OrderStatus.PENDING
        )
        
        session.add(order)
        await session.flush()  # Получаем ID заказа
        
        # Создаем элементы заказа
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product_id'],
                variant_id=item_data['variant_id'],
                quantity=item_data['quantity'],
                price=item_data['price'],
                variant_name=item_data['variant_name']
            )
            session.add(order_item)
        
        # Уменьшаем количество товаров на складе
        for cart_item in cart_items:
            if cart_item.variant_id:
                success = await ProductService.decrease_variant_quantity(
                    session, cart_item.variant_id, cart_item.quantity
                )
            else:
                success = await ProductService.decrease_quantity(
                    session, cart_item.product_id, cart_item.quantity
                )
            
            if not success:
                # Откатываем изменения
                await session.rollback()
                return None
        
        # Очищаем корзину
        for cart_item in cart_items:
            await session.delete(cart_item)
        
        await session.commit()
        return order
    
    @staticmethod
    async def get_order_by_id(session: AsyncSession, order_id: int) -> Optional[Order]:
        """Получить заказ по ID"""
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_orders(session: AsyncSession, user_id: int) -> List[Order]:
        """Получить все заказы пользователя"""
        result = await session.execute(
            select(Order).where(Order.user_id == user_id)
            .order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_order_items(session: AsyncSession, order_id: int) -> List[OrderItem]:
        """Получить товары заказа"""
        result = await session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()
    
    @staticmethod
    async def cancel_order(session: AsyncSession, order_id: int) -> bool:
        """Отменить заказ"""
        order = await OrderService.get_order_by_id(session, order_id)
        
        if not order or order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            return False
        
        # Возвращаем товары на склад
        order_items = await OrderService.get_order_items(session, order_id)
        
        for item in order_items:
            if item.variant_id:
                await ProductService.increase_variant_quantity(
                    session, item.variant_id, item.quantity
                )
            else:
                await ProductService.increase_quantity(
                    session, item.product_id, item.quantity
                )
        
        # Обновляем статус заказа
        order.status = OrderStatus.CANCELLED
        await session.commit()
        
        return True
    
    @staticmethod
    async def update_payment_status(session: AsyncSession, order_id: int, status: str) -> bool:
        """Обновить статус оплаты"""
        order = await OrderService.get_order_by_id(session, order_id)
        
        if not order:
            return False
        
        order.payment_status = status
        await session.commit()
        return True
    
    @staticmethod
    async def update_order_status(session: AsyncSession, order_id: int, status: OrderStatus) -> bool:
        """Обновить статус заказа"""
        order = await OrderService.get_order_by_id(session, order_id)
        
        if not order:
            return False
        
        order.status = status
        await session.commit()
        return True