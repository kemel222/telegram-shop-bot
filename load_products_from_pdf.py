#!/usr/bin/env python3
"""
Скрипт для загрузки товаров из PDF файла с вариантами вкусов
"""

import asyncio
import sys
import os
from datetime import datetime

# Добавляем путь к проекту
sys.path.append('/home/hotspot/shop')

from database.database import get_async_session
from database.models import Category, Product, ProductVariant
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

# Данные категорий и товаров
CATEGORIES_DATA = [
    {
        "name": "Жидкости для вейпа",
        "description": "Электронные жидкости для вейпа",
        "cashback_percent": 3.5
    },
    {
        "name": "POD-системы", 
        "description": "POD-системы и устройства",
        "cashback_percent": 2.5
    },
    {
        "name": "Картриджи",
        "description": "Картриджи для POD-систем",
        "cashback_percent": 3.5
    },
    {
        "name": "Жидкости для заправки",
        "description": "Жидкости для заправки картриджей",
        "cashback_percent": 3.5
    }
]

PRODUCTS_DATA = [
    # Жидкости для вейпа
    {
        "category": "Жидкости для вейпа",
        "name": "Elf Bar 600",
        "description": "Одноразовая электронная сигарета",
        "price": 350.0,
        "has_variants": True,
        "variants": [
            {"name": "Клубника-банан", "quantity": 15, "price": 350.0},
            {"name": "Манго-персик", "quantity": 12, "price": 350.0},
            {"name": "Виноград-лед", "quantity": 8, "price": 350.0},
            {"name": "Кола-лед", "quantity": 20, "price": 350.0},
            {"name": "Мята-ментол", "quantity": 10, "price": 350.0},
            {"name": "Яблоко-лед", "quantity": 18, "price": 350.0},
            {"name": "Ананас-кокос", "quantity": 5, "price": 350.0},
            {"name": "Киви-арбуз", "quantity": 7, "price": 350.0}
        ]
    },
    {
        "category": "Жидкости для вейпа",
        "name": "HQD Cuvie Plus",
        "description": "Одноразовая электронная сигарета",
        "price": 400.0,
        "has_variants": True,
        "variants": [
            {"name": "Клубника-молоко", "quantity": 22, "price": 400.0},
            {"name": "Манго-лед", "quantity": 16, "price": 400.0},
            {"name": "Виноград-лед", "quantity": 14, "price": 400.0},
            {"name": "Кола-лед", "quantity": 19, "price": 400.0},
            {"name": "Мята-лед", "quantity": 11, "price": 400.0},
            {"name": "Яблоко-лед", "quantity": 13, "price": 400.0},
            {"name": "Ананас-лед", "quantity": 9, "price": 400.0},
            {"name": "Киви-лед", "quantity": 6, "price": 400.0}
        ]
    },
    {
        "category": "Жидкости для вейпа",
        "name": "Lost Mary OS5000",
        "description": "Одноразовая электронная сигарета",
        "price": 450.0,
        "has_variants": True,
        "variants": [
            {"name": "Клубника-банан", "quantity": 17, "price": 450.0},
            {"name": "Манго-персик", "quantity": 21, "price": 450.0},
            {"name": "Виноград-лед", "quantity": 15, "price": 450.0},
            {"name": "Кола-лед", "quantity": 23, "price": 450.0},
            {"name": "Мята-ментол", "quantity": 12, "price": 450.0},
            {"name": "Яблоко-лед", "quantity": 18, "price": 450.0},
            {"name": "Ананас-кокос", "quantity": 8, "price": 450.0},
            {"name": "Киви-арбуз", "quantity": 10, "price": 450.0}
        ]
    },
    
    # POD-системы
    {
        "category": "POD-системы",
        "name": "Vaporesso XROS 3",
        "description": "POD-система с USB-C зарядкой",
        "price": 2500.0,
        "has_variants": True,
        "variants": [
            {"name": "Черный", "quantity": 8, "price": 2500.0},
            {"name": "Белый", "quantity": 6, "price": 2500.0},
            {"name": "Синий", "quantity": 4, "price": 2500.0},
            {"name": "Розовый", "quantity": 3, "price": 2500.0}
        ]
    },
    {
        "category": "POD-системы",
        "name": "Uwell Caliburn G2",
        "description": "POD-система с регулируемой мощностью",
        "price": 2800.0,
        "has_variants": True,
        "variants": [
            {"name": "Черный", "quantity": 5, "price": 2800.0},
            {"name": "Белый", "quantity": 7, "price": 2800.0},
            {"name": "Синий", "quantity": 4, "price": 2800.0},
            {"name": "Красный", "quantity": 2, "price": 2800.0}
        ]
    },
    {
        "category": "POD-системы",
        "name": "Smok Nord 4",
        "description": "POD-система с большим аккумулятором",
        "price": 3200.0,
        "has_variants": True,
        "variants": [
            {"name": "Черный", "quantity": 6, "price": 3200.0},
            {"name": "Белый", "quantity": 4, "price": 3200.0},
            {"name": "Синий", "quantity": 3, "price": 3200.0},
            {"name": "Зеленый", "quantity": 2, "price": 3200.0}
        ]
    },
    
    # Картриджи
    {
        "category": "Картриджи",
        "name": "Elf Bar Pods",
        "description": "Картриджи для Elf Bar",
        "price": 150.0,
        "has_variants": True,
        "variants": [
            {"name": "Клубника-банан", "quantity": 25, "price": 150.0},
            {"name": "Манго-персик", "quantity": 20, "price": 150.0},
            {"name": "Виноград-лед", "quantity": 18, "price": 150.0},
            {"name": "Кола-лед", "quantity": 22, "price": 150.0},
            {"name": "Мята-ментол", "quantity": 15, "price": 150.0},
            {"name": "Яблоко-лед", "quantity": 19, "price": 150.0}
        ]
    },
    {
        "category": "Картриджи",
        "name": "HQD Pods",
        "description": "Картриджи для HQD",
        "price": 180.0,
        "has_variants": True,
        "variants": [
            {"name": "Клубника-молоко", "quantity": 30, "price": 180.0},
            {"name": "Манго-лед", "quantity": 24, "price": 180.0},
            {"name": "Виноград-лед", "quantity": 21, "price": 180.0},
            {"name": "Кола-лед", "quantity": 26, "price": 180.0},
            {"name": "Мята-лед", "quantity": 17, "price": 180.0},
            {"name": "Яблоко-лед", "quantity": 23, "price": 180.0}
        ]
    },
    
    # Жидкости для заправки
    {
        "category": "Жидкости для заправки",
        "name": "Elf Bar Liquid",
        "description": "Жидкость для заправки картриджей",
        "price": 200.0,
        "has_variants": True,
        "variants": [
            {"name": "Клубника-банан", "quantity": 12, "price": 200.0},
            {"name": "Манго-персик", "quantity": 10, "price": 200.0},
            {"name": "Виноград-лед", "quantity": 8, "price": 200.0},
            {"name": "Кола-лед", "quantity": 15, "price": 200.0},
            {"name": "Мята-ментол", "quantity": 6, "price": 200.0},
            {"name": "Яблоко-лед", "quantity": 11, "price": 200.0}
        ]
    },
    {
        "category": "Жидкости для заправки",
        "name": "HQD Liquid",
        "description": "Жидкость для заправки картриджей",
        "price": 220.0,
        "has_variants": True,
        "variants": [
            {"name": "Клубника-молоко", "quantity": 18, "price": 220.0},
            {"name": "Манго-лед", "quantity": 14, "price": 220.0},
            {"name": "Виноград-лед", "quantity": 12, "price": 220.0},
            {"name": "Кола-лед", "quantity": 16, "price": 220.0},
            {"name": "Мята-лед", "quantity": 9, "price": 220.0},
            {"name": "Яблоко-лед", "quantity": 13, "price": 220.0}
        ]
    }
]

async def create_categories(session: AsyncSession):
    """Создание категорий"""
    print("📁 Создание категорий...")
    
    for cat_data in CATEGORIES_DATA:
        # Проверяем, существует ли категория
        result = await session.execute(
            select(Category).where(Category.name == cat_data["name"])
        )
        category = result.scalar_one_or_none()
        
        if not category:
            category = Category(
                name=cat_data["name"],
                description=cat_data["description"],
                cashback_percent=cat_data["cashback_percent"]
            )
            session.add(category)
            print(f"  ✓ Создана категория: {cat_data['name']}")
        else:
            # Обновляем существующую категорию
            category.description = cat_data["description"]
            category.cashback_percent = cat_data["cashback_percent"]
            print(f"  ✓ Обновлена категория: {cat_data['name']}")
    
    await session.commit()

async def create_products(session: AsyncSession):
    """Создание товаров с вариантами"""
    print("📦 Создание товаров...")
    
    # Получаем все категории
    result = await session.execute(select(Category))
    categories = {cat.name: cat for cat in result.scalars()}
    
    for prod_data in PRODUCTS_DATA:
        category = categories.get(prod_data["category"])
        if not category:
            print(f"  ⚠️ Категория {prod_data['category']} не найдена, пропускаем товар")
            continue
        
        # Проверяем, существует ли товар
        result = await session.execute(
            select(Product).where(Product.name == prod_data["name"])
        )
        product = result.scalar_one_or_none()
        
        if not product:
            product = Product(
                name=prod_data["name"],
                description=prod_data["description"],
                price=prod_data["price"],
                category_id=category.id,
                has_variants=prod_data["has_variants"],
                quantity=0  # Общее количество будет считаться из вариантов
            )
            session.add(product)
            await session.flush()  # Получаем ID товара
            print(f"  ✓ Создан товар: {prod_data['name']}")
        else:
            # Обновляем существующий товар
            product.description = prod_data["description"]
            product.price = prod_data["price"]
            product.has_variants = prod_data["has_variants"]
            print(f"  ✓ Обновлен товар: {prod_data['name']}")
        
        # Создаем/обновляем варианты
        if prod_data["has_variants"] and "variants" in prod_data:
            total_quantity = 0
            
            for variant_data in prod_data["variants"]:
                # Проверяем, существует ли вариант
                result = await session.execute(
                    select(ProductVariant).where(
                        ProductVariant.product_id == product.id,
                        ProductVariant.name == variant_data["name"]
                    )
                )
                variant = result.scalar_one_or_none()
                
                if not variant:
                    variant = ProductVariant(
                        product_id=product.id,
                        name=variant_data["name"],
                        price=variant_data.get("price", product.price),
                        quantity=variant_data["quantity"],
                        is_available=variant_data["quantity"] > 0
                    )
                    session.add(variant)
                    print(f"    ✓ Создан вариант: {variant_data['name']} (остаток: {variant_data['quantity']})")
                else:
                    # Обновляем существующий вариант
                    variant.price = variant_data.get("price", product.price)
                    variant.quantity = variant_data["quantity"]
                    variant.is_available = variant_data["quantity"] > 0
                    print(f"    ✓ Обновлен вариант: {variant_data['name']} (остаток: {variant_data['quantity']})")
                
                total_quantity += variant_data["quantity"]
            
            # Обновляем общее количество товара
            product.quantity = total_quantity
        
        await session.commit()

async def main():
    """Основная функция"""
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("📦 ЗАГРУЗКА ТОВАРОВ ИЗ PDF")
    print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
    print("")
    
    async with get_async_session() as session:
        try:
            await create_categories(session)
            await create_products(session)
            
            print("")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("✅ ТОВАРЫ УСПЕШНО ЗАГРУЖЕНЫ!")
            print("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
            print("")
            print("📊 Статистика:")
            
            # Подсчитываем статистику
            result = await session.execute(select(Category))
            categories_count = len(result.scalars().all())
            
            result = await session.execute(select(Product))
            products_count = len(result.scalars().all())
            
            result = await session.execute(select(ProductVariant))
            variants_count = len(result.scalars().all())
            
            print(f"  📁 Категорий: {categories_count}")
            print(f"  📦 Товаров: {products_count}")
            print(f"  🍓 Вариантов вкусов: {variants_count}")
            print("")
            print("🎉 Готово! Проверьте Mini App в Telegram.")
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            await session.rollback()
            raise

if __name__ == "__main__":
    asyncio.run(main())