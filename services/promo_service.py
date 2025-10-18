from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import PromoCode, PromoCodeType, User
from datetime import datetime
from typing import Optional, Tuple


class PromoService:
    @staticmethod
    async def get_promo_code(session: AsyncSession, code: str) -> Optional[PromoCode]:
        """Получить промокод по коду"""
        result = await session.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def validate_promo_code(session: AsyncSession, code: str) -> Tuple[bool, str, Optional[PromoCode]]:
        """
        Проверить валидность промокода
        Возвращает: (is_valid, error_message, promo_code)
        """
        promo = await PromoService.get_promo_code(session, code)
        
        if not promo:
            return False, "Промокод не найден", None
        
        if not promo.is_active:
            return False, "Промокод неактивен", None
        
        if promo.expires_at and promo.expires_at < datetime.utcnow():
            return False, "Срок действия промокода истек", None
        
        if promo.usage_limit and promo.usage_count >= promo.usage_limit:
            return False, "Лимит использований промокода исчерпан", None
        
        return True, "", promo
    
    @staticmethod
    async def apply_promo_code(
        session: AsyncSession,
        user_id: int,
        code: str,
        order_total: float
    ) -> Tuple[bool, str, float]:
        """
        Применить промокод
        Возвращает: (success, message, discount_amount)
        """
        is_valid, error_msg, promo = await PromoService.validate_promo_code(session, code)
        
        if not is_valid:
            return False, error_msg, 0.0
        
        discount = 0.0
        
        if promo.type == PromoCodeType.PERCENT:
            # Скидка в процентах
            discount = order_total * (promo.value / 100)
        elif promo.type == PromoCodeType.FIXED:
            # Фиксированная скидка
            discount = min(promo.value, order_total)  # Не больше суммы заказа
        elif promo.type == PromoCodeType.BALANCE:
            # Пополнение баланса
            result = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = result.scalar_one_or_none()
            
            if user:
                user.balance += promo.value
                promo.usage_count += 1
                await session.commit()
                return True, f"Баланс пополнен на {promo.value}₽", 0.0
        
        # Увеличиваем счетчик использований
        if promo.type != PromoCodeType.BALANCE:
            promo.usage_count += 1
            await session.commit()
        
        return True, f"Промокод применен! Скидка: {discount}₽", discount
    
    @staticmethod
    async def create_promo_code(
        session: AsyncSession,
        code: str,
        type: PromoCodeType,
        value: float,
        usage_limit: Optional[int] = None,
        expires_at: Optional[datetime] = None
    ) -> PromoCode:
        """Создать новый промокод"""
        promo = PromoCode(
            code=code.upper(),
            type=type,
            value=value,
            usage_limit=usage_limit,
            expires_at=expires_at
        )
        session.add(promo)
        await session.commit()
        await session.refresh(promo)
        return promo
    
    @staticmethod
    async def deactivate_promo_code(session: AsyncSession, code: str) -> bool:
        """Деактивировать промокод"""
        promo = await PromoService.get_promo_code(session, code)
        
        if promo:
            promo.is_active = False
            await session.commit()
            return True
        
        return False
    
    @staticmethod
    async def use_balance(
        session: AsyncSession,
        user_id: int,
        amount: float
    ) -> Tuple[bool, str]:
        """
        Использовать баланс для оплаты
        Возвращает: (success, message)
        """
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return False, "Пользователь не найден"
        
        if user.balance < amount:
            return False, f"Недостаточно средств. Ваш баланс: {user.balance}₽"
        
        user.balance -= amount
        await session.commit()
        return True, f"Оплачено с баланса: {amount}₽"
    
    @staticmethod
    async def partial_balance_payment(
        session: AsyncSession,
        user_id: int,
        total_amount: float
    ) -> Tuple[float, float]:
        """
        Частичная оплата балансом
        Возвращает: (amount_from_balance, remaining_amount)
        """
        result = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user or user.balance <= 0:
            return 0.0, total_amount
        
        # Используем весь доступный баланс, но не больше суммы заказа
        amount_from_balance = min(user.balance, total_amount)
        remaining_amount = total_amount - amount_from_balance
        
        return amount_from_balance, remaining_amount

