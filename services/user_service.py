from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User


class UserService:
    @staticmethod
    async def create_user(session: AsyncSession, telegram_id: int) -> User:
        """Создать нового пользователя"""
        new_user = User(
            telegram_id=telegram_id,
            username=None,
            first_name=None,
            balance=0.0,
            cashback_balance=0.0
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    @staticmethod
    async def get_or_create_user(
        session: AsyncSession,
        telegram_id: int,
        username: str = None,
        first_name: str = None
    ) -> User:
        """Получить или создать пользователя"""
        # Проверяем, существует ли пользователь
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        user = result.scalar_one_or_none()
        
        if user:
            # Обновляем данные, если они изменились
            if username and user.username != username:
                user.username = username
            if first_name and user.first_name != first_name:
                user.first_name = first_name
            await session.commit()
            await session.refresh(user)
            return user
        
        # Создаем нового пользователя
        new_user = User(
            telegram_id=telegram_id,
            username=username,
            first_name=first_name
        )
        
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        return new_user
    
    @staticmethod
    async def get_user_by_telegram_id(session: AsyncSession, telegram_id: int) -> User:
        """Получить пользователя по telegram_id"""
        result = await session.execute(
            select(User).where(User.telegram_id == telegram_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_user_by_id(session: AsyncSession, user_id: int) -> User:
        """Получить пользователя по ID"""
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def update_balance(session: AsyncSession, user_id: int, amount: float) -> User:
        """Обновить баланс пользователя"""
        user = await UserService.get_user_by_id(session, user_id)
        if user:
            user.balance += amount
            await session.commit()
            await session.refresh(user)
        return user
    
    @staticmethod
    async def update_phone(session: AsyncSession, user_id: int, phone: str) -> User:
        """Обновить номер телефона пользователя"""
        user = await UserService.get_user_by_id(session, user_id)
        if user:
            user.phone = phone
            await session.commit()
            await session.refresh(user)
        return user
    
    @staticmethod
    async def update_cashback_balance(session: AsyncSession, user_id: int, amount: float) -> User:
        """Обновить кешбек баланс пользователя"""
        user = await UserService.get_user_by_id(session, user_id)
        if user:
            user.cashback_balance += amount
            await session.commit()
            await session.refresh(user)
        return user

