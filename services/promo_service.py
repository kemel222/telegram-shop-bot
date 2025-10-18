from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import PromoCode, User
from typing import List, Optional
from datetime import datetime


class PromoService:
    @staticmethod
    async def get_active_promo_codes(session: AsyncSession) -> List[PromoCode]:
        """Получить все активные промокоды"""
        result = await session.execute(
            select(PromoCode).where(
                PromoCode.is_active == True,
                PromoCode.expires_at > datetime.utcnow()
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_promo_code_by_code(session: AsyncSession, code: str) -> Optional[PromoCode]:
        """Получить промокод по коду"""
        result = await session.execute(
            select(PromoCode).where(PromoCode.code == code)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def validate_promo_code(session: AsyncSession, code: str) -> dict:
        """Проверить валидность промокода"""
        promo_code = await PromoService.get_promo_code_by_code(session, code)
        
        if not promo_code:
            return {
                "is_valid": False,
                "message": "Промокод не найден"
            }
        
        if not promo_code.is_active:
            return {
                "is_valid": False,
                "message": "Промокод неактивен"
            }
        
        if promo_code.expires_at and promo_code.expires_at < datetime.utcnow():
            return {
                "is_valid": False,
                "message": "Промокод истек"
            }
        
        if promo_code.usage_limit and promo_code.usage_count >= promo_code.usage_limit:
            return {
                "is_valid": False,
                "message": "Промокод исчерпан"
            }
        
        return {
            "is_valid": True,
            "type": promo_code.type.value,
            "value": promo_code.value,
            "message": "Промокод действителен"
        }
    
    @staticmethod
    async def calculate_discount(
        session: AsyncSession, 
        code: str, 
        order_total: float
    ) -> dict:
        """Рассчитать скидку от промокода"""
        promo_code = await PromoService.get_promo_code_by_code(session, code)
        
        if not promo_code:
            return {
                "discount_amount": 0,
                "message": "Промокод не найден"
            }
        
        if not promo_code.is_active:
            return {
                "discount_amount": 0,
                "message": "Промокод неактивен"
            }
        
        if promo_code.expires_at and promo_code.expires_at < datetime.utcnow():
            return {
                "discount_amount": 0,
                "message": "Промокод истек"
            }
        
        if promo_code.usage_limit and promo_code.usage_count >= promo_code.usage_limit:
            return {
                "discount_amount": 0,
                "message": "Промокод исчерпан"
            }
        
        # Рассчитываем скидку
        if promo_code.type.value == "percent":
            discount_amount = order_total * (promo_code.value / 100)
        elif promo_code.type.value == "fixed":
            discount_amount = min(promo_code.value, order_total)
        else:  # balance
            discount_amount = 0  # Для баланса скидка не применяется
        
        return {
            "discount_amount": discount_amount,
            "promo_code": promo_code.code,
            "type": promo_code.type.value,
            "value": promo_code.value,
            "message": "Скидка рассчитана"
        }
    
    @staticmethod
    async def apply_promo_code(session: AsyncSession, code: str) -> bool:
        """Применить промокод (увеличить счетчик использований)"""
        promo_code = await PromoService.get_promo_code_by_code(session, code)
        
        if not promo_code:
            return False
        
        promo_code.usage_count += 1
        await session.commit()
        return True
    
    @staticmethod
    async def apply_promo_code_to_user(
        session: AsyncSession, 
        user_id: int, 
        code: str, 
        order_total: float
    ) -> tuple[bool, str, float]:
        """Применить промокод к пользователю"""
        promo_code = await PromoService.get_promo_code_by_code(session, code)
        
        if not promo_code:
            return False, "Промокод не найден", 0.0
        
        if not promo_code.is_active:
            return False, "Промокод неактивен", 0.0
        
        if promo_code.expires_at and promo_code.expires_at < datetime.utcnow():
            return False, "Промокод истек", 0.0
        
        if promo_code.usage_limit and promo_code.usage_count >= promo_code.usage_limit:
            return False, "Промокод исчерпан", 0.0
        
        # Рассчитываем скидку или бонус
        if promo_code.type.value == "percent":
            discount = order_total * (promo_code.value / 100)
            promo_code.usage_count += 1
            await session.commit()
            return True, "Процентная скидка применена", discount
        
        elif promo_code.type.value == "fixed":
            discount = min(promo_code.value, order_total)
            promo_code.usage_count += 1
            await session.commit()
            return True, "Фиксированная скидка применена", discount
        
        elif promo_code.type.value == "balance":
            # Пополняем баланс пользователя
            user = await session.execute(
                select(User).where(User.id == user_id)
            )
            user = user.scalar_one_or_none()
            
            if user:
                user.balance += promo_code.value
                promo_code.usage_count += 1
                await session.commit()
                return True, f"Баланс пополнен на {promo_code.value}₽", 0.0
        
        return False, "Неизвестный тип промокода", 0.0
    
    @staticmethod
    async def use_balance(session: AsyncSession, user_id: int, amount: float) -> tuple[bool, str]:
        """Использовать баланс для оплаты"""
        user = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user:
            return False, "Пользователь не найден"
        
        if user.balance < amount:
            return False, f"Недостаточно средств на балансе. Доступно: {user.balance}₽"
        
        user.balance -= amount
        await session.commit()
        return True, "Средства списаны с баланса"
    
    @staticmethod
    async def partial_balance_payment(
        session: AsyncSession, 
        user_id: int, 
        total_amount: float
    ) -> tuple[float, float]:
        """Частичная оплата балансом"""
        user = await session.execute(
            select(User).where(User.id == user_id)
        )
        user = user.scalar_one_or_none()
        
        if not user or user.balance <= 0:
            return 0.0, total_amount
        
        balance_used = min(user.balance, total_amount)
        remaining = total_amount - balance_used
        
        user.balance -= balance_used
        await session.commit()
        
        return balance_used, remaining