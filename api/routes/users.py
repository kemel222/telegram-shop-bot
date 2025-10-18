from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from api.dependencies import get_db, get_current_user, create_access_token
from services.user_service import UserService
from services.cashback_service import CashbackService
from database.models import User
from pydantic import BaseModel

router = APIRouter()


class AuthRequest(BaseModel):
    telegram_id: int
    username: str | None = None
    first_name: str | None = None


class AuthResponse(BaseModel):
    access_token: str
    user_id: int
    telegram_id: int
    balance: float
    cashback_balance: float


class UpdatePhoneRequest(BaseModel):
    phone: str


class UserProfileResponse(BaseModel):
    id: int
    telegram_id: int
    username: str | None
    first_name: str | None
    phone: str | None
    balance: float
    cashback_balance: float
    
    class Config:
        from_attributes = True


@router.post("/auth", response_model=AuthResponse)
async def authenticate(
    request: AuthRequest,
    session: AsyncSession = Depends(get_db)
):
    """Авторизация пользователя через Telegram"""
    user = await UserService.get_or_create_user(
        session,
        request.telegram_id,
        request.username,
        request.first_name
    )
    
    # Создаем токен
    token = create_access_token(user.id, user.telegram_id)
    
    return {
        "access_token": token,
        "user_id": user.id,
        "telegram_id": user.telegram_id,
        "balance": user.balance,
        "cashback_balance": user.cashback_balance
    }


@router.get("/profile", response_model=UserProfileResponse)
async def get_profile(
    user: User = Depends(get_current_user)
):
    """Получить профиль пользователя"""
    return user


@router.put("/profile/phone")
async def update_phone(
    request: UpdatePhoneRequest,
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Обновить номер телефона"""
    updated_user = await UserService.update_phone(session, user.id, request.phone)
    return {"message": "Phone updated", "phone": updated_user.phone}


@router.get("/balance")
async def get_balance(
    user: User = Depends(get_current_user)
):
    """Получить баланс пользователя"""
    return {
        "balance": user.balance,
        "cashback_balance": user.cashback_balance
    }


@router.get("/cashback")
async def get_cashback_info(
    session: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user)
):
    """Получить информацию о кешбеке пользователя"""
    stats = await CashbackService.get_cashback_stats(session, user.id)
    
    from config import settings
    
    return {
        "cashback_balance": user.cashback_balance,
        "stats": stats,
        "pods_percent": settings.CASHBACK_PODS_PERCENT,
        "default_percent": settings.CASHBACK_DEFAULT_PERCENT
    }

