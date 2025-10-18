#!/usr/bin/env python3
"""
Скрипт для загрузки тестовых данных в базу данных
"""

import asyncio
import sys
import os

# Добавляем корневую директорию проекта в путь
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.database import async_session_maker
from database.models import Category, Product, ProductVariant, PromoCode
from sqlalchemy import select


async def load_test_data():
    """Загрузить тестовые данные"""
    async with async_session_maker() as session:
        try:
            # Проверяем, есть ли уже данные
            result = await session.execute(select(Category))
            existing_categories = result.scalars().all()
            
            if existing_categories:
                print("✅ Данные уже загружены!")
                return
            
            # Создаем категории
            categories_data = [
                {
                    "name": "Электронные сигареты",
                    "description": "Современные электронные сигареты и вейпы",
                    "image_url": None
                },
                {
                    "name": "Поды",
                    "description": "Одноразовые электронные сигареты",
                    "image_url": None
                },
                {
                    "name": "Жидкости",
                    "description": "Жидкости для электронных сигарет",
                    "image_url": None
                },
                {
                    "name": "Аксессуары",
                    "description": "Аксессуары для вейпинга",
                    "image_url": None
                }
            ]
            
            categories = []
            for cat_data in categories_data:
                category = Category(**cat_data)
                session.add(category)
                categories.append(category)
            
            await session.flush()  # Получаем ID категорий
            
            # Создаем товары
            products_data = [
                {
                    "category_id": categories[0].id,
                    "name": "Vaporesso XROS 3",
                    "description": "Компактный под-система с USB-C зарядкой",
                    "price": 2500.0,
                    "image_url": None,
                    "quantity": 10,
                    "is_available": True,
                    "has_variants": False
                },
                {
                    "category_id": categories[0].id,
                    "name": "GeekVape Aegis Legend 2",
                    "description": "Мощный бокс-мод с защитой от воды и пыли",
                    "price": 4500.0,
                    "image_url": None,
                    "quantity": 5,
                    "is_available": True,
                    "has_variants": False
                },
                {
                    "category_id": categories[1].id,
                    "name": "Elf Bar BC5000",
                    "description": "Одноразовая электронная сигарета",
                    "price": 1200.0,
                    "image_url": None,
                    "quantity": 20,
                    "is_available": True,
                    "has_variants": True
                },
                {
                    "category_id": categories[2].id,
                    "name": "Salt Liquid 30ml",
                    "description": "Солевая жидкость для под-систем",
                    "price": 800.0,
                    "image_url": None,
                    "quantity": 15,
                    "is_available": True,
                    "has_variants": True
                }
            ]
            
            products = []
            for prod_data in products_data:
                product = Product(**prod_data)
                session.add(product)
                products.append(product)
            
            await session.flush()
            
            # Создаем варианты для товаров с вариантами
            variants_data = [
                # Elf Bar BC5000 - вкусы
                {
                    "product_id": products[2].id,
                    "name": "Мята",
                    "price": 1200.0,
                    "quantity": 5,
                    "is_available": True
                },
                {
                    "product_id": products[2].id,
                    "name": "Клубника",
                    "price": 1200.0,
                    "quantity": 3,
                    "is_available": True
                },
                {
                    "product_id": products[2].id,
                    "name": "Манго",
                    "price": 1200.0,
                    "quantity": 0,  # Закончился
                    "is_available": False
                },
                # Salt Liquid - вкусы
                {
                    "product_id": products[3].id,
                    "name": "Табак",
                    "price": 800.0,
                    "quantity": 8,
                    "is_available": True
                },
                {
                    "product_id": products[3].id,
                    "name": "Ваниль",
                    "price": 800.0,
                    "quantity": 7,
                    "is_available": True
                }
            ]
            
            for var_data in variants_data:
                variant = ProductVariant(**var_data)
                session.add(variant)
            
            # Создаем промокоды
            promo_codes_data = [
                {
                    "code": "WELCOME10",
                    "description": "Скидка 10% для новых клиентов",
                    "discount_type": "percent",
                    "discount_value": 10.0,
                    "min_order_amount": 1000.0,
                    "max_uses": 100,
                    "used_count": 0,
                    "is_active": True
                },
                {
                    "code": "SAVE500",
                    "description": "Скидка 500 рублей",
                    "discount_type": "fixed",
                    "discount_value": 500.0,
                    "min_order_amount": 2000.0,
                    "max_uses": 50,
                    "used_count": 0,
                    "is_active": True
                },
                {
                    "code": "BONUS1000",
                    "description": "Пополнение баланса на 1000 рублей",
                    "discount_type": "balance",
                    "discount_value": 1000.0,
                    "min_order_amount": 0.0,
                    "max_uses": 20,
                    "used_count": 0,
                    "is_active": True
                }
            ]
            
            for promo_data in promo_codes_data:
                promo = PromoCode(**promo_data)
                session.add(promo)
            
            await session.commit()
            print("✅ Тестовые данные успешно загружены!")
            print(f"📦 Создано категорий: {len(categories)}")
            print(f"🛍️ Создано товаров: {len(products)}")
            print(f"🎯 Создано вариантов: {len(variants_data)}")
            print(f"🎫 Создано промокодов: {len(promo_codes_data)}")
            
        except Exception as e:
            await session.rollback()
            print(f"❌ Ошибка при загрузке данных: {e}")
            raise


if __name__ == "__main__":
    asyncio.run(load_test_data())
