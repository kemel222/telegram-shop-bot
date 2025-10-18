from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import User, CashbackTransaction, Order, OrderItem, Category
from typing import Optional, Tuple


class CashbackService:
    # Специальные категории с пониженным кешбеком
    PODS_CATEGORIES = ["поды", "pods", "под-системы", "pod системы"]  # 2.5%
    PODS_CASHBACK_PERCENT = 2.5
    DEFAULT_CASHBACK_PERCENT = 3.5
    
    @staticmethod
    async def calculate_order_cashback(
        session: AsyncSession,
        order: Order
    ) -> float:
        """
        Рассчитать кешбек за заказ на основе категорий товаров
        """
        # Получаем все товары из заказа с их категориями
        result = await session.execute(
            select(OrderItem).where(OrderItem.order_id == order.id)
        )
        order_items = result.scalars().all()
        
        total_cashback = 0.0
        
        for item in order_items:
            # Получаем продукт и его категорию
            await session.refresh(item, ['product'])
            product = item.product
            await session.refresh(product, ['category'])
            category = product.category
            
            # Рассчитываем кешбек для этого товара
            item_total = item.price * item.quantity
            
            # Используем процент кешбека из категории
            cashback_percent = category.cashback_percent if category.cashback_percent else CashbackService.DEFAULT_CASHBACK_PERCENT
            
            item_cashback = item_total * (cashback_percent / 100)
            total_cashback += item_cashback
        
        return round(total_cashback, 2)
    
    @staticmethod
    async def process_cashback(
        session: AsyncSession,
        order: Order
    ) -> Optional[Tuple[User, float]]:
        """
        Обработать начисление кешбека при выполнении заказа
        Возвращает: (user, cashback_amount) или None
        """
        # Получаем пользователя
        result = await session.execute(
            select(User).where(User.id == order.user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        
        # Рассчитываем кешбек
        cashback_amount = await CashbackService.calculate_order_cashback(session, order)
        
        if cashback_amount <= 0:
            return None
        
        # Начисляем кешбек на баланс пользователя
        user.cashback_balance += cashback_amount
        user.balance += cashback_amount  # Также добавляем в общий баланс для использования
        
        # Сохраняем транзакцию кешбека
        # Вычисляем средний процент (для статистики)
        avg_percent = (cashback_amount / order.total * 100) if order.total > 0 else 0
        
        transaction = CashbackTransaction(
            user_id=user.id,
            order_id=order.id,
            amount=cashback_amount,
            cashback_percent=round(avg_percent, 2)
        )
        session.add(transaction)
        
        await session.commit()
        await session.refresh(user)
        
        return user, cashback_amount
    
    @staticmethod
    async def get_user_cashback_history(
        session: AsyncSession,
        user_id: int
    ) -> list:
        """Получить историю начислений кешбека пользователя"""
        result = await session.execute(
            select(CashbackTransaction)
            .where(CashbackTransaction.user_id == user_id)
            .order_by(CashbackTransaction.created_at.desc())
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_cashback_stats(
        session: AsyncSession,
        user_id: int
    ) -> dict:
        """Получить статистику по кешбеку пользователя"""
        transactions = await CashbackService.get_user_cashback_history(session, user_id)
        
        total_cashback = sum(t.amount for t in transactions)
        transactions_count = len(transactions)
        
        return {
            'total_cashback': round(total_cashback, 2),
            'transactions_count': transactions_count,
            'average_cashback': round(total_cashback / transactions_count, 2) if transactions_count > 0 else 0
        }
    
    @staticmethod
    async def update_category_cashback(
        session: AsyncSession,
        category_id: int,
        cashback_percent: float
    ) -> Optional[Category]:
        """Обновить процент кешбека для категории"""
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        category = result.scalar_one_or_none()
        
        if not category:
            return None
        
        category.cashback_percent = cashback_percent
        await session.commit()
        await session.refresh(category)
        
        return category
    
    @staticmethod
    async def format_cashback_info(session: AsyncSession, user: User) -> str:
        """Форматировать информацию о кешбеке пользователя"""
        stats = await CashbackService.get_cashback_stats(session, user.id)
        
        info = f"""
💰 Кешбек программа

📊 Ваша статистика:
• Всего кешбека получено: {stats['total_cashback']}₽
• Количество начислений: {stats['transactions_count']}
• Средний кешбек: {stats['average_cashback']}₽

💳 Текущий кешбек баланс: {user.cashback_balance}₽
💵 Общий баланс: {user.balance}₽

🎁 Условия начисления:
• На POD-системы: 2.5%
• На все остальные товары: 3.5%

✅ Кешбек начисляется автоматически после выполнения заказа!
💸 Используйте кешбек для оплаты следующих покупок!
"""
        
        return info

