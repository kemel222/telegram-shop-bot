"""
Скрипт для добавления тестовых данных в базу данных
"""
import asyncio
from database.database import async_session_maker
from database.models import Category, Product, PromoCode, PromoCodeType


async def add_test_data():
    """Добавить тестовые данные"""
    async with async_session_maker() as session:
        print("🔄 Добавление тестовых данных...")
        
        # Добавляем категории
        categories_data = [
            {
                "name": "Электроника",
                "description": "Смартфоны, планшеты и другие гаджеты",
                "image_url": None
            },
            {
                "name": "Одежда",
                "description": "Модная одежда для всех",
                "image_url": None
            },
            {
                "name": "Продукты",
                "description": "Свежие продукты и деликатесы",
                "image_url": None
            }
        ]
        
        categories = []
        for cat_data in categories_data:
            category = Category(**cat_data)
            session.add(category)
            categories.append(category)
        
        await session.flush()
        print(f"✅ Добавлено {len(categories)} категорий")
        
        # Добавляем товары
        products_data = [
            # Электроника
            {
                "category_id": categories[0].id,
                "name": "iPhone 15 Pro",
                "description": "Флагманский смартфон от Apple с титановым корпусом",
                "price": 99990,
                "quantity": 10,
                "is_available": True
            },
            {
                "category_id": categories[0].id,
                "name": "Samsung Galaxy S24",
                "description": "Мощный Android-смартфон с AI функциями",
                "price": 79990,
                "quantity": 15,
                "is_available": True
            },
            {
                "category_id": categories[0].id,
                "name": "AirPods Pro 2",
                "description": "Беспроводные наушники с шумоподавлением",
                "price": 24990,
                "quantity": 25,
                "is_available": True
            },
            
            # Одежда
            {
                "category_id": categories[1].id,
                "name": "Футболка Nike",
                "description": "Спортивная футболка из дышащего материала",
                "price": 2990,
                "quantity": 50,
                "is_available": True
            },
            {
                "category_id": categories[1].id,
                "name": "Джинсы Levi's 501",
                "description": "Классические прямые джинсы",
                "price": 7990,
                "quantity": 30,
                "is_available": True
            },
            {
                "category_id": categories[1].id,
                "name": "Кроссовки Adidas",
                "description": "Удобные беговые кроссовки",
                "price": 8990,
                "quantity": 20,
                "is_available": True
            },
            
            # Продукты
            {
                "category_id": categories[2].id,
                "name": "Хлеб бородинский",
                "description": "Свежий хлеб из ржаной муки",
                "price": 85,
                "quantity": 100,
                "is_available": True
            },
            {
                "category_id": categories[2].id,
                "name": "Молоко 3.2%",
                "description": "Натуральное коровье молоко",
                "price": 120,
                "quantity": 80,
                "is_available": True
            },
            {
                "category_id": categories[2].id,
                "name": "Сыр Российский",
                "description": "Твёрдый сыр, 500г",
                "price": 450,
                "quantity": 40,
                "is_available": True
            }
        ]
        
        for prod_data in products_data:
            product = Product(**prod_data)
            session.add(product)
        
        await session.flush()
        print(f"✅ Добавлено {len(products_data)} товаров")
        
        # Добавляем промокоды
        promo_codes_data = [
            {
                "code": "SALE20",
                "type": PromoCodeType.PERCENT,
                "value": 20,
                "is_active": True,
                "usage_limit": None
            },
            {
                "code": "DISCOUNT500",
                "type": PromoCodeType.FIXED,
                "value": 500,
                "is_active": True,
                "usage_limit": 100
            },
            {
                "code": "BONUS1000",
                "type": PromoCodeType.BALANCE,
                "value": 1000,
                "is_active": True,
                "usage_limit": 50
            },
            {
                "code": "WELCOME",
                "type": PromoCodeType.PERCENT,
                "value": 15,
                "is_active": True,
                "usage_limit": None
            },
            {
                "code": "FREEMONEY",
                "type": PromoCodeType.BALANCE,
                "value": 500,
                "is_active": True,
                "usage_limit": None
            }
        ]
        
        for promo_data in promo_codes_data:
            promo = PromoCode(**promo_data)
            session.add(promo)
        
        await session.flush()
        print(f"✅ Добавлено {len(promo_codes_data)} промокодов")
        
        await session.commit()
        
        print("\n🎉 Все тестовые данные успешно добавлены!")
        print("\n📋 Промокоды:")
        for promo_data in promo_codes_data:
            type_name = {
                PromoCodeType.PERCENT: "Процентная скидка",
                PromoCodeType.FIXED: "Фиксированная скидка",
                PromoCodeType.BALANCE: "Пополнение баланса"
            }[promo_data["type"]]
            
            value_str = f"{promo_data['value']}%" if promo_data["type"] == PromoCodeType.PERCENT else f"{promo_data['value']}₽"
            print(f"  • {promo_data['code']} - {type_name}: {value_str}")


async def main():
    """Главная функция"""
    try:
        await add_test_data()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

