from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from services.promo_service import PromoService
from database.models import User
from pydantic import BaseModel

router = APIRouter()


class ValidatePromoRequest(BaseModel):
    code: str
    order_total: float


class ApplyPromoRequest(BaseModel):
    code: str


@router.post("/validate")
async def validate_promo_code(
    request: ValidatePromoRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Проверить валидность промокода"""
    is_valid, message, promo = await PromoService.validate_promo_code(session, request.code)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    # Рассчитываем скидку
    from database.models import PromoCodeType
    discount = 0.0
    
    if promo.type == PromoCodeType.PERCENT:
        discount = request.order_total * (promo.value / 100)
    elif promo.type == PromoCodeType.FIXED:
        discount = min(promo.value, request.order_total)
    elif promo.type == PromoCodeType.BALANCE:
        return {
            "valid": True,
            "type": "balance",
            "value": promo.value,
            "message": f"Промокод пополнит баланс на {promo.value}₽"
        }
    
    return {
        "valid": True,
        "type": promo.type.value,
        "discount": discount,
        "message": f"Скидка составит {discount}₽"
    }


@router.post("/apply-balance-promo")
async def apply_balance_promo(
    request: ApplyPromoRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Применить промокод на пополнение баланса"""
    is_valid, message, promo = await PromoService.validate_promo_code(session, request.code)
    
    if not is_valid:
        raise HTTPException(status_code=400, detail=message)
    
    from database.models import PromoCodeType
    if promo.type != PromoCodeType.BALANCE:
        raise HTTPException(status_code=400, detail="Этот промокод не для пополнения баланса")
    
    # Применяем промокод
    success, msg, _ = await PromoService.apply_promo_code(session, user.id, request.code, 0)
    
    if not success:
        raise HTTPException(status_code=400, detail=msg)
    
    return {"message": msg, "new_balance": user.balance + promo.value}

