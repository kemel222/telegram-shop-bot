from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import (
    Order, OrderItem, OrderStatus, DeliveryType, PaymentMethod,
    Product, User, CartItem, Cart
)
from services.cart_service import CartService
from services.product_service import ProductService
from typing import List, Optional, Dict
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
        # Получаем товары из корзины
        cart_items = await CartService.get_cart_items(session, user_id)
        
        if not cart_items:
            return None
        
        # Рассчитываем стоимость
        subtotal = 0.0
        order_items_data = []
        
        for cart_item in cart_items:
            product = await ProductService.get_product_by_id(session, cart_item.product_id)
            
            if not product or not product.is_available or product.quantity < cart_item.quantity:
                return None  # Товар недоступен
            
            item_total = product.price * cart_item.quantity
            subtotal += item_total
            
            order_items_data.append({
                'product': product,
                'quantity': cart_item.quantity,
                'price': product.price
            })
        
        # Добавляем стоимость доставки
        delivery_cost = settings.DELIVERY_PRICE if delivery_type == DeliveryType.DELIVERY else 0.0
        
        # Рассчитываем итоговую сумму
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
        
        # Создаем элементы заказа и списываем товары
        for item_data in order_items_data:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data['product'].id,
                quantity=item_data['quantity'],
                price=item_data['price']
            )
            session.add(order_item)
            
            # Списываем товар со склада
            await ProductService.decrease_quantity(
                session,
                item_data['product'].id,
                item_data['quantity']
            )
        
        # Очищаем корзину
        await CartService.clear_cart(session, user_id)
        
        await session.commit()
        await session.refresh(order)
        
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
            select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc())
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
    async def update_order_status(
        session: AsyncSession,
        order_id: int,
        status: OrderStatus
    ) -> Optional[Order]:
        """Обновить статус заказа"""
        order = await OrderService.get_order_by_id(session, order_id)
        
        if order:
            order.status = status
            await session.commit()
            await session.refresh(order)
        
        return order
    
    @staticmethod
    async def update_payment_status(
        session: AsyncSession,
        order_id: int,
        payment_status: str
    ) -> Optional[Order]:
        """Обновить статус оплаты"""
        order = await OrderService.get_order_by_id(session, order_id)
        
        if order:
            order.payment_status = payment_status
            if payment_status == "paid":
                order.status = OrderStatus.PAID
            await session.commit()
            await session.refresh(order)
        
        return order
    
    @staticmethod
    async def cancel_order(session: AsyncSession, order_id: int) -> bool:
        """Отменить заказ и вернуть товары на склад"""
        order = await OrderService.get_order_by_id(session, order_id)
        
        if not order or order.status in [OrderStatus.COMPLETED, OrderStatus.CANCELLED]:
            return False
        
        # Возвращаем товары на склад
        order_items = await OrderService.get_order_items(session, order_id)
        for item in order_items:
            await ProductService.increase_quantity(session, item.product_id, item.quantity)
        
        # Если оплата была с баланса, возвращаем средства
        if order.payment_method == PaymentMethod.BALANCE and order.payment_status == "paid":
            user = await session.execute(
                select(User).where(User.id == order.user_id)
            )
            user = user.scalar_one_or_none()
            if user:
                user.balance += order.total
        
        order.status = OrderStatus.CANCELLED
        await session.commit()
        
        return True
    
    @staticmethod
    async def get_all_pending_orders(session: AsyncSession) -> List[Order]:
        """Получить все заказы, ожидающие обработки"""
        result = await session.execute(
            select(Order).where(
                Order.status.in_([OrderStatus.PENDING, OrderStatus.PAYMENT_PENDING])
            ).order_by(Order.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def format_order_info(session: AsyncSession, order: Order) -> str:
        """Форматировать информацию о заказе для отображения"""
        order_items = await OrderService.get_order_items(session, order.id)
        
        items_text = ""
        for item in order_items:
            product = await ProductService.get_product_by_id(session, item.product_id)
            if product:
                items_text += f"• {product.name} x{item.quantity} = {item.price * item.quantity}₽\n"
        
        delivery_text = ""
        if order.delivery_type == DeliveryType.DELIVERY:
            delivery_text = f"📦 Доставка: {order.delivery_address}\nСтоимость доставки: {order.delivery_cost}₽"
        elif order.delivery_type == DeliveryType.PICKUP_CENTER:
            delivery_text = f"🏢 Самовывоз из Центра\nВремя: {order.delivery_time_slot}"
        elif order.delivery_type == DeliveryType.PICKUP_TC:
            delivery_text = f"🏬 Самовывоз из ТЦ\nВремя: {order.delivery_time_slot}"
        
        payment_text = {
            PaymentMethod.SBP_ONLINE: "💳 СБП онлайн",
            PaymentMethod.SBP_ON_RECEIPT: "💳 СБП при получении",
            PaymentMethod.CASH: "💵 Наличными",
            PaymentMethod.BALANCE: "💰 Баланс сайта"
        }.get(order.payment_method, "Неизвестно")
        
        status_text = {
            OrderStatus.PENDING: "⏳ Ожидает подтверждения",
            OrderStatus.PAYMENT_PENDING: "💳 Ожидает оплаты",
            OrderStatus.PAID: "✅ Оплачен",
            OrderStatus.PROCESSING: "🔄 В обработке",
            OrderStatus.READY: "📦 Готов к выдаче",
            OrderStatus.COMPLETED: "✅ Завершен",
            OrderStatus.CANCELLED: "❌ Отменен"
        }.get(order.status, "Неизвестно")
        
        info = f"""
📋 Заказ #{order.id}
Статус: {status_text}

👤 Клиент: {order.customer_name}
📱 Телефон: {order.customer_phone}

🛍 Товары:
{items_text}
Сумма товаров: {order.subtotal}₽

{delivery_text}

💰 Оплата: {payment_text}
"""
        
        if order.discount > 0:
            info += f"🎁 Скидка: {order.discount}₽\n"
        if order.promo_code_used:
            info += f"🎟 Промокод: {order.promo_code_used}\n"
        
        info += f"\n💵 Итого: {order.total}₽"
        
        return info

