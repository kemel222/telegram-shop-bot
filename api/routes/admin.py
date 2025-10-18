from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from services.order_service import OrderService
from services.product_service import ProductService
from services.promo_service import PromoService
from database.models import User, OrderStatus, PromoCodeType, Category, Product
from config import settings
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

router = APIRouter()


def check_admin(user: User):
    """Проверить, является ли пользователь администратором"""
    if user.telegram_id not in settings.admin_ids_list:
        raise HTTPException(status_code=403, detail="Access denied. Admin only.")


class UpdateOrderStatusRequest(BaseModel):
    status: OrderStatus


class VerifyPaymentRequest(BaseModel):
    is_approved: bool


class CreatePromoCodeRequest(BaseModel):
    code: str
    type: PromoCodeType
    value: float
    usage_limit: Optional[int] = None
    expires_at: Optional[datetime] = None


class CreateCategoryRequest(BaseModel):
    name: str
    description: Optional[str] = None
    image_url: Optional[str] = None


class CreateProductRequest(BaseModel):
    category_id: int
    name: str
    description: Optional[str] = None
    price: float
    image_url: Optional[str] = None
    quantity: int


class UpdateProductRequest(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image_url: Optional[str] = None
    quantity: Optional[int] = None
    is_available: Optional[bool] = None


@router.get("/orders/pending")
async def get_pending_orders(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить все заказы, ожидающие обработки"""
    check_admin(user)
    
    orders = await OrderService.get_all_pending_orders(session)
    
    orders_data = []
    for order in orders:
        order_info = await OrderService.format_order_info(session, order)
        orders_data.append({
            "order_id": order.id,
            "info": order_info
        })
    
    return orders_data


@router.put("/orders/{order_id}/status")
async def update_order_status(
    order_id: int,
    request: UpdateOrderStatusRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Обновить статус заказа"""
    check_admin(user)
    
    order = await OrderService.update_order_status(session, order_id, request.status)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    return {"message": "Order status updated", "new_status": order.status.value}


@router.post("/orders/{order_id}/verify-payment")
async def verify_payment(
    order_id: int,
    request: VerifyPaymentRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Подтвердить или отклонить оплату по скриншоту"""
    check_admin(user)
    
    order = await OrderService.get_order_by_id(session, order_id)
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    if request.is_approved:
        await OrderService.update_payment_status(session, order_id, "paid")
        
        # Обрабатываем реферальный бонус
        from services.referral_service import ReferralService
        await ReferralService.process_referral_bonus(session, order)
        
        return {"message": "Payment approved", "status": "paid"}
    else:
        await OrderService.cancel_order(session, order_id)
        return {"message": "Payment rejected, order cancelled"}


@router.post("/promo")
async def create_promo_code(
    request: CreatePromoCodeRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Создать новый промокод"""
    check_admin(user)
    
    promo = await PromoService.create_promo_code(
        session,
        request.code,
        request.type,
        request.value,
        request.usage_limit,
        request.expires_at
    )
    
    return {
        "message": "Promo code created",
        "code": promo.code,
        "type": promo.type.value,
        "value": promo.value
    }


@router.delete("/promo/{code}")
async def deactivate_promo_code(
    code: str,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Деактивировать промокод"""
    check_admin(user)
    
    success = await PromoService.deactivate_promo_code(session, code)
    
    if not success:
        raise HTTPException(status_code=404, detail="Promo code not found")
    
    return {"message": "Promo code deactivated"}


@router.post("/categories")
async def create_category(
    request: CreateCategoryRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Создать новую категорию"""
    check_admin(user)
    
    category = Category(
        name=request.name,
        description=request.description,
        image_url=request.image_url
    )
    
    session.add(category)
    await session.commit()
    await session.refresh(category)
    
    return {
        "message": "Category created",
        "category_id": category.id,
        "name": category.name
    }


@router.post("/products")
async def create_product(
    request: CreateProductRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Создать новый товар"""
    check_admin(user)
    
    product = Product(
        category_id=request.category_id,
        name=request.name,
        description=request.description,
        price=request.price,
        image_url=request.image_url,
        quantity=request.quantity,
        is_available=request.quantity > 0
    )
    
    session.add(product)
    await session.commit()
    await session.refresh(product)
    
    return {
        "message": "Product created",
        "product_id": product.id,
        "name": product.name
    }


@router.put("/products/{product_id}")
async def update_product(
    product_id: int,
    request: UpdateProductRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Обновить товар"""
    check_admin(user)
    
    product = await ProductService.get_product_by_id(session, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    if request.name is not None:
        product.name = request.name
    if request.description is not None:
        product.description = request.description
    if request.price is not None:
        product.price = request.price
    if request.image_url is not None:
        product.image_url = request.image_url
    if request.quantity is not None:
        product.quantity = request.quantity
        product.is_available = request.quantity > 0
    if request.is_available is not None:
        product.is_available = request.is_available
    
    await session.commit()
    await session.refresh(product)
    
    return {"message": "Product updated"}


@router.delete("/products/{product_id}")
async def delete_product(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Удалить товар (сделать недоступным)"""
    check_admin(user)
    
    product = await ProductService.get_product_by_id(session, product_id)
    
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    product.is_available = False
    product.quantity = 0
    
    await session.commit()
    
    return {"message": "Product deleted"}

