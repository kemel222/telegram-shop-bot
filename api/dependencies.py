from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from database.database import async_session_maker
from services.user_service import UserService
from database.models import User
from typing import Optional
import jwt
from config import settings


security = HTTPBearer()


async def get_db() -> AsyncSession:
    """Dependency для получения сессии БД"""
    async with async_session_maker() as session:
        try:
            yield session
        finally:
            await session.close()


def create_access_token(user_id: int, telegram_id: int) -> str:
    """Создать JWT токен"""
    payload = {
        "user_id": user_id,
        "telegram_id": telegram_id
    }
    token = jwt.encode(payload, settings.SECRET_KEY, algorithm="HS256")
    return token


def decode_access_token(token: str) -> dict:
    """Декодировать JWT токен"""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token"
        )


async def get_current_user(
    x_telegram_user_id: str = Header(..., alias="X-Telegram-User-ID"),
    session: AsyncSession = Depends(get_db)
) -> User:
    """Получить текущего пользователя из Telegram"""
    try:
        user_id = int(x_telegram_user_id)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid user ID")
    
    user = await UserService.get_user_by_telegram_id(session, user_id)
    if not user:
        # Создаем пользователя, если его нет
        user = await UserService.create_user(session, user_id)
    
    return user


async def get_optional_user(
    x_telegram_user_id: Optional[str] = Header(None, alias="X-Telegram-User-ID"),
    session: AsyncSession = Depends(get_db)
) -> Optional[User]:
    """Получить текущего пользователя (опционально)"""
    if not x_telegram_user_id:
        return None
    
    try:
        return await get_current_user(x_telegram_user_id, session)
    except HTTPException:
        return None