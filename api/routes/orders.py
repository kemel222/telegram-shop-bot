from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from services.order_service import OrderService
from services.promo_service import PromoService
from services.referral_service import ReferralService
from database.models import User, DeliveryType, PaymentMethod
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class CreateOrderRequest(BaseModel):
    delivery_type: DeliveryType
    customer_name: str
    customer_phone: str
    payment_method: PaymentMethod
    delivery_address: Optional[str] = None
    delivery_time_slot: Optional[str] = None
    promo_code: Optional[str] = None
    use_balance: bool = False


class OrderResponse(BaseModel):
    id: int
    status: str
    delivery_type: str
    customer_name: str
    customer_phone: str
    payment_method: str
    subtotal: float
    delivery_cost: float
    discount: float
    total: float
    created_at: str
    
    class Config:
        from_attributes = True


@router.post("", response_model=OrderResponse)
async def create_order(
    request: CreateOrderRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Создать заказ из корзины"""
    
    # Получаем предварительную стоимость корзины
    from services.cart_service import CartService
    cart_total = await CartService.get_cart_total(session, user.id)
    
    if cart_total == 0:
        raise HTTPException(status_code=400, detail="Cart is empty")
    
    # Добавляем стоимость доставки
    from config import settings
    if request.delivery_type == DeliveryType.DELIVERY:
        cart_total += settings.DELIVERY_PRICE
    
    discount = 0.0
    
    # Применяем реферальную скидку для первой покупки
    if user.is_first_purchase and user.referred_by_id:
        referral_discount = await ReferralService.apply_referral_discount(cart_total, user)
        discount += referral_discount
    
    # Применяем промокод, если указан
    if request.promo_code:
        is_valid, message, promo_discount = await PromoService.apply_promo_code(
            session,
            user.id,
            request.promo_code,
            cart_total - discount
        )
        
        if is_valid:
            discount += promo_discount
    
    # Используем баланс, если указано
    balance_used = 0.0
    if request.use_balance and user.balance > 0:
        balance_used, remaining = await PromoService.partial_balance_payment(
            session,
            user.id,
            cart_total - discount
        )
    
    # Создаем заказ
    order = await OrderService.create_order_from_cart(
        session,
        user.id,
        request.delivery_type,
        request.customer_name,
        request.customer_phone,
        request.payment_method,
        request.delivery_address,
        request.delivery_time_slot,
        request.promo_code,
        discount
    )
    
    if not order:
        raise HTTPException(
            status_code=400,
            detail="Cannot create order. Some products may be unavailable."
        )
    
    # Если оплата балансом, списываем средства
    if request.payment_method == PaymentMethod.BALANCE:
        success, message = await PromoService.use_balance(session, user.id, order.total)
        if not success:
            # Отменяем заказ
            await OrderService.cancel_order(session, order.id)
            raise HTTPException(status_code=400, detail=message)
        
        # Обновляем статус оплаты
        await OrderService.update_payment_status(session, order.id, "paid")
    
    # Обрабатываем реферальный бонус, если заказ оплачен
    if order.payment_status == "paid":
        await ReferralService.process_referral_bonus(session, order)
    
    return {
        "id": order.id,
        "status": order.status.value,
        "delivery_type": order.delivery_type.value,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "payment_method": order.payment_method.value,
        "subtotal": order.subtotal,
        "delivery_cost": order.delivery_cost,
        "discount": order.discount,
        "total": order.total,
        "created_at": order.created_at.isoformat()
    }


@router.get("", response_model=List[OrderResponse])
async def get_orders(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить все заказы пользователя"""
    orders = await OrderService.get_user_orders(session, user.id)
    
    return [
        {
            "id": order.id,
            "status": order.status.value,
            "delivery_type": order.delivery_type.value,
            "customer_name": order.customer_name,
            "customer_phone": order.customer_phone,
            "payment_method": order.payment_method.value,
            "subtotal": order.subtotal,
            "delivery_cost": order.delivery_cost,
            "discount": order.discount,
            "total": order.total,
            "created_at": order.created_at.isoformat()
        }
        for order in orders
    ]


@router.get("/{order_id}")
async def get_order(
    order_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить детали заказа"""
    order = await OrderService.get_order_by_id(session, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    # Получаем товары заказа
    order_items = await OrderService.get_order_items(session, order_id)
    
    from services.product_service import ProductService
    items_data = []
    for item in order_items:
        product = await ProductService.get_product_by_id(session, item.product_id)
        if product:
            items_data.append({
                "product_id": product.id,
                "product_name": product.name,
                "product_image": product.image_url,
                "quantity": item.quantity,
                "price": item.price,
                "subtotal": item.price * item.quantity
            })
    
    return {
        "id": order.id,
        "status": order.status.value,
        "delivery_type": order.delivery_type.value,
        "delivery_address": order.delivery_address,
        "delivery_time_slot": order.delivery_time_slot,
        "customer_name": order.customer_name,
        "customer_phone": order.customer_phone,
        "payment_method": order.payment_method.value,
        "payment_status": order.payment_status,
        "subtotal": order.subtotal,
        "delivery_cost": order.delivery_cost,
        "discount": order.discount,
        "total": order.total,
        "items": items_data,
        "created_at": order.created_at.isoformat()
    }


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Отменить заказ"""
    order = await OrderService.get_order_by_id(session, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if order.user_id != user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = await OrderService.cancel_order(session, order_id)
    
    if not success:
        raise HTTPException(
            status_code=400,
            detail="Cannot cancel order. Order may already be completed or cancelled."
        )
    
    return {"message": "Order cancelled"}

