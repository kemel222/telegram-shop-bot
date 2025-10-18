from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from database.models import Product, Category, Favorite, ProductVariant
from typing import List, Optional


class ProductService:
    @staticmethod
    async def get_all_categories(session: AsyncSession) -> List[Category]:
        """Получить все категории"""
        result = await session.execute(select(Category))
        return result.scalars().all()
    
    @staticmethod
    async def get_all_products(session: AsyncSession) -> List[Product]:
        """Получить все товары"""
        result = await session.execute(
            select(Product).where(
                Product.is_available == True,
                Product.quantity > 0
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_category_by_id(session: AsyncSession, category_id: int) -> Optional[Category]:
        """Получить категорию по ID"""
        result = await session.execute(
            select(Category).where(Category.id == category_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def get_products_by_category(
        session: AsyncSession,
        category_id: int,
        only_available: bool = True
    ) -> List[Product]:
        """Получить товары по категории"""
        query = select(Product).where(Product.category_id == category_id)
        
        if only_available:
            query = query.where(Product.is_available == True, Product.quantity > 0)
        
        result = await session.execute(query)
        return result.scalars().all()
    
    @staticmethod
    async def get_product_by_id(session: AsyncSession, product_id: int) -> Optional[Product]:
        """Получить товар по ID"""
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def search_products(session: AsyncSession, query_text: str) -> List[Product]:
        """Поиск товаров по названию"""
        result = await session.execute(
            select(Product).where(
                Product.name.ilike(f"%{query_text}%"),
                Product.is_available == True,
                Product.quantity > 0
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def decrease_quantity(session: AsyncSession, product_id: int, quantity: int) -> bool:
        """Уменьшить количество товара на складе"""
        product = await ProductService.get_product_by_id(session, product_id)
        
        if not product or product.quantity < quantity:
            return False
        
        product.quantity -= quantity
        
        # Если товар закончился, делаем его недоступным
        if product.quantity == 0:
            product.is_available = False
        
        await session.commit()
        return True
    
    @staticmethod
    async def increase_quantity(session: AsyncSession, product_id: int, quantity: int):
        """Увеличить количество товара на складе (возврат)"""
        product = await ProductService.get_product_by_id(session, product_id)
        
        if product:
            product.quantity += quantity
            if product.quantity > 0:
                product.is_available = True
            await session.commit()
    
    @staticmethod
    async def add_to_favorites(session: AsyncSession, user_id: int, product_id: int) -> bool:
        """Добавить товар в избранное"""
        # Проверяем, не добавлен ли уже товар
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id
            )
        )
        
        if result.scalar_one_or_none():
            return False  # Уже в избранном
        
        favorite = Favorite(user_id=user_id, product_id=product_id)
        session.add(favorite)
        await session.commit()
        return True
    
    @staticmethod
    async def remove_from_favorites(session: AsyncSession, user_id: int, product_id: int) -> bool:
        """Удалить товар из избранного"""
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id
            )
        )
        favorite = result.scalar_one_or_none()
        
        if favorite:
            await session.delete(favorite)
            await session.commit()
            return True
        
        return False
    
    @staticmethod
    async def get_user_favorites(session: AsyncSession, user_id: int) -> List[Product]:
        """Получить избранные товары пользователя"""
        result = await session.execute(
            select(Product).join(Favorite).where(
                Favorite.user_id == user_id,
                Product.is_available == True
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_product_variants(session: AsyncSession, product_id: int) -> List[ProductVariant]:
        """Получить варианты товара"""
        result = await session.execute(
            select(ProductVariant).where(
                ProductVariant.product_id == product_id,
                ProductVariant.is_available == True
            )
        )
        return result.scalars().all()
    
    @staticmethod
    async def get_variant_by_id(session: AsyncSession, variant_id: int) -> Optional[ProductVariant]:
        """Получить вариант товара по ID"""
        result = await session.execute(
            select(ProductVariant).where(ProductVariant.id == variant_id)
        )
        return result.scalar_one_or_none()
    
    @staticmethod
    async def decrease_variant_quantity(session: AsyncSession, variant_id: int, quantity: int) -> bool:
        """Уменьшить количество варианта товара на складе"""
        variant = await ProductService.get_variant_by_id(session, variant_id)
        
        if not variant or variant.quantity < quantity:
            return False
        
        variant.quantity -= quantity
        
        # Если вариант закончился, делаем его недоступным
        if variant.quantity == 0:
            variant.is_available = False
        
        await session.commit()
        return True
    
    @staticmethod
    async def increase_variant_quantity(session: AsyncSession, variant_id: int, quantity: int):
        """Увеличить количество варианта товара на складе (возврат)"""
        variant = await ProductService.get_variant_by_id(session, variant_id)
        
        if variant:
            variant.quantity += quantity
            if variant.quantity > 0:
                variant.is_available = True
            await session.commit()
    
    @staticmethod
    async def is_in_favorites(session: AsyncSession, user_id: int, product_id: int) -> bool:
        """Проверить, находится ли товар в избранном"""
        result = await session.execute(
            select(Favorite).where(
                Favorite.user_id == user_id,
                Favorite.product_id == product_id
            )
        )
        return result.scalar_one_or_none() is not None

