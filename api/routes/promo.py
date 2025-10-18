from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user
from services.promo_service import PromoService
from database.models import User
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()


class PromoCodeResponse(BaseModel):
    id: int
    code: str
    type: str
    value: float
    is_active: bool
    usage_limit: Optional[int]
    usage_count: int
    expires_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PromoCodeValidationRequest(BaseModel):
    code: str


class PromoCodeValidationResponse(BaseModel):
    is_valid: bool
    type: Optional[str] = None
    value: Optional[float] = None
    discount_amount: Optional[float] = None
    message: str


@router.get("/promo-codes", response_model=List[PromoCodeResponse])
async def get_promo_codes(session: AsyncSession = Depends(get_db)):
    """Получить все активные промокоды"""
    promo_codes = await PromoService.get_active_promo_codes(session)
    return promo_codes


@router.post("/validate", response_model=PromoCodeValidationResponse)
async def validate_promo_code(
    request: PromoCodeValidationRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Проверить валидность промокода"""
    promo_code = await PromoService.get_promo_code_by_code(session, request.code)
    
    if not promo_code:
        return PromoCodeValidationResponse(
            is_valid=False,
            message="Промокод не найден"
        )
    
    if not promo_code.is_active:
        return PromoCodeValidationResponse(
            is_valid=False,
            message="Промокод неактивен"
        )
    
    if promo_code.expires_at and promo_code.expires_at < datetime.utcnow():
        return PromoCodeValidationResponse(
            is_valid=False,
            message="Промокод истек"
        )
    
    if promo_code.usage_limit and promo_code.usage_count >= promo_code.usage_limit:
        return PromoCodeValidationResponse(
            is_valid=False,
            message="Промокод исчерпан"
        )
    
    return PromoCodeValidationResponse(
        is_valid=True,
        type=promo_code.type.value,
        value=promo_code.value,
        message="Промокод действителен"
    )


@router.post("/apply")
async def apply_promo_code(
    request: PromoCodeValidationRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Применить промокод к заказу"""
    promo_code = await PromoService.get_promo_code_by_code(session, request.code)
    
    if not promo_code:
        raise HTTPException(status_code=404, detail="Промокод не найден")
    
    if not promo_code.is_active:
        raise HTTPException(status_code=400, detail="Промокод неактивен")
    
    if promo_code.expires_at and promo_code.expires_at < datetime.utcnow():
        raise HTTPException(status_code=400, detail="Промокод истек")
    
    if promo_code.usage_limit and promo_code.usage_count >= promo_code.usage_limit:
        raise HTTPException(status_code=400, detail="Промокод исчерпан")
    
    # Увеличиваем счетчик использований
    promo_code.usage_count += 1
    await session.commit()
    
    return {
        "message": "Промокод применен",
        "promo_code": promo_code.code,
        "type": promo_code.type.value,
        "value": promo_code.value
    }