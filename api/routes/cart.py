from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from services.cart_service import CartService
from services.product_service import ProductService
from database.models import User
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class AddToCartRequest(BaseModel):
    product_id: int
    variant_id: Optional[int] = None
    quantity: int = 1


class UpdateCartItemRequest(BaseModel):
    quantity: int


class CartItemResponse(BaseModel):
    id: int
    product_id: int
    product_name: str
    product_price: float
    product_image: str | None
    variant_id: Optional[int] = None
    variant_name: Optional[str] = None
    quantity: int
    subtotal: float


class CartResponse(BaseModel):
    items: List[CartItemResponse]
    total: float


@router.post("/add")
async def add_to_cart(
    request: AddToCartRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Добавить товар в корзину"""
    cart_item = await CartService.add_to_cart(
        session,
        user.id,
        request.product_id,
        request.variant_id,
        request.quantity
    )
    
    if not cart_item:
        raise HTTPException(
            status_code=400,
            detail="Cannot add product to cart. Product may be unavailable or insufficient quantity."
        )
    
    return {"message": "Product added to cart", "cart_item_id": cart_item.id}


@router.delete("/{product_id}")
async def remove_from_cart(
    product_id: int,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Удалить товар из корзины"""
    success = await CartService.remove_from_cart(session, user.id, product_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Product not in cart")
    
    return {"message": "Product removed from cart"}


@router.put("/{product_id}")
async def update_cart_item(
    product_id: int,
    request: UpdateCartItemRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Обновить количество товара в корзине"""
    cart_item = await CartService.update_cart_item_quantity(
        session,
        user.id,
        product_id,
        request.quantity
    )
    
    if not cart_item and request.quantity > 0:
        raise HTTPException(
            status_code=400,
            detail="Cannot update cart item. Insufficient quantity or product not found."
        )
    
    return {"message": "Cart item updated"}


@router.get("", response_model=CartResponse)
async def get_cart(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить корзину"""
    cart_items = await CartService.get_cart_items(session, user.id)
    
    items_response = []
    total = 0.0
    
    for cart_item in cart_items:
        product = await ProductService.get_product_by_id(session, cart_item.product_id)
        if product:
            # Определяем цену (вариант или основной товар)
            price = product.price
            variant_name = None
            
            if cart_item.variant_id:
                variant = await ProductService.get_variant_by_id(session, cart_item.variant_id)
                if variant:
                    price = variant.price or product.price
                    variant_name = variant.name
            
            subtotal = price * cart_item.quantity
            total += subtotal
            
            items_response.append({
                "id": cart_item.id,
                "product_id": product.id,
                "product_name": product.name,
                "product_price": price,
                "product_image": product.image_url,
                "variant_id": cart_item.variant_id,
                "variant_name": variant_name,
                "quantity": cart_item.quantity,
                "subtotal": subtotal
            })
    
    return {
        "items": items_response,
        "total": total
    }


@router.delete("/clear")
async def clear_cart(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Очистить корзину"""
    await CartService.clear_cart(session, user.id)
    return {"message": "Cart cleared"}

