"""
Скрипт для загрузки реальных товаров магазина электронных сигарет
"""
import asyncio
from database.database import async_session_maker
from database.models import Category, Product, ProductVariant, PromoCode, PromoCodeType


async def load_real_products():
    """Загрузить реальные товары для магазина электронных сигарет"""
    async with async_session_maker() as session:
        print("🔄 Загрузка реальных товаров...")
        
        # Добавляем категории для магазина электронных сигарет
        categories_data = [
            {
                "name": "Электронные сигареты",
                "description": "Одноразовые и многоразовые электронные сигареты",
                "image_url": None,
                "cashback_percent": 2.5
            },
            {
                "name": "Поды",
                "description": "Сменные картриджи и поды для электронных сигарет",
                "image_url": None,
                "cashback_percent": 2.5
            },
            {
                "name": "Жидкости",
                "description": "Жидкости для электронных сигарет различных вкусов",
                "image_url": None,
                "cashback_percent": 3.5
            },
            {
                "name": "Аксессуары",
                "description": "Зарядные устройства, чехлы и другие аксессуары",
                "image_url": None,
                "cashback_percent": 3.5
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
            # Электронные сигареты
            {
                "category_id": 1,  # Будет заменено на реальный ID
                "name": "Elf Bar 600",
                "description": "Одноразовая электронная сигарета с 600 затяжками",
                "price": 450,
                "quantity": 50,
                "is_available": True,
                "has_variants": True
            },
            {
                "category_id": 1,
                "name": "HQD Cuvie Plus",
                "description": "Одноразовая электронная сигарета с 1200 затяжками",
                "price": 650,
                "quantity": 30,
                "is_available": True,
                "has_variants": True
            },
            {
                "category_id": 1,
                "name": "Lost Mary OS5000",
                "description": "Одноразовая электронная сигарета с 5000 затяжками",
                "price": 1200,
                "quantity": 25,
                "is_available": True,
                "has_variants": True
            },
            
            # Поды
            {
                "category_id": 2,
                "name": "JUUL Pods",
                "description": "Сменные картриджи для JUUL",
                "price": 350,
                "quantity": 100,
                "is_available": True,
                "has_variants": True
            },
            {
                "category_id": 2,
                "name": "Vuse Pods",
                "description": "Сменные картриджи для Vuse",
                "price": 320,
                "quantity": 80,
                "is_available": True,
                "has_variants": True
            },
            
            # Жидкости
            {
                "category_id": 3,
                "name": "Salt Liquid 30ml",
                "description": "Солевая жидкость для электронных сигарет, 30мл",
                "price": 800,
                "quantity": 60,
                "is_available": True,
                "has_variants": True
            },
            {
                "category_id": 3,
                "name": "Freebase Liquid 60ml",
                "description": "Обычная жидкость для электронных сигарет, 60мл",
                "price": 1200,
                "quantity": 40,
                "is_available": True,
                "has_variants": True
            },
            
            # Аксессуары
            {
                "category_id": 4,
                "name": "Зарядное устройство USB-C",
                "description": "Универсальное зарядное устройство для электронных сигарет",
                "price": 500,
                "quantity": 20,
                "is_available": True,
                "has_variants": False
            },
            {
                "category_id": 4,
                "name": "Чехол для электронной сигареты",
                "description": "Защитный чехол из силикона",
                "price": 200,
                "quantity": 50,
                "is_available": True,
                "has_variants": False
            }
        ]
        
        products = []
        for prod_data in products_data:
            # Заменяем category_id на реальный ID
            category_index = prod_data["category_id"] - 1
            prod_data["category_id"] = categories[category_index].id
            product = Product(**prod_data)
            session.add(product)
            products.append(product)
        
        await session.flush()
        print(f"✅ Добавлено {len(products)} товаров")
        
        # Добавляем варианты товаров (вкусы)
        variants_data = [
            # Elf Bar 600 вкусы
            {
                "product_id": products[0].id,
                "name": "Мята",
                "price": None,
                "quantity": 10,
                "is_available": True
            },
            {
                "product_id": products[0].id,
                "name": "Клубника",
                "price": None,
                "quantity": 8,
                "is_available": True
            },
            {
                "product_id": products[0].id,
                "name": "Арбуз",
                "price": None,
                "quantity": 12,
                "is_available": True
            },
            {
                "product_id": products[0].id,
                "name": "Манго",
                "price": None,
                "quantity": 5,
                "is_available": True
            },
            
            # HQD Cuvie Plus вкусы
            {
                "product_id": products[1].id,
                "name": "Кола",
                "price": None,
                "quantity": 6,
                "is_available": True
            },
            {
                "product_id": products[1].id,
                "name": "Ледяная мята",
                "price": None,
                "quantity": 8,
                "is_available": True
            },
            {
                "product_id": products[1].id,
                "name": "Киви",
                "price": None,
                "quantity": 4,
                "is_available": True
            },
            
            # Lost Mary OS5000 вкусы
            {
                "product_id": products[2].id,
                "name": "Клубничный чизкейк",
                "price": None,
                "quantity": 3,
                "is_available": True
            },
            {
                "product_id": products[2].id,
                "name": "Мохито",
                "price": None,
                "quantity": 5,
                "is_available": True
            },
            {
                "product_id": products[2].id,
                "name": "Ананас",
                "price": None,
                "quantity": 2,
                "is_available": True
            },
            
            # JUUL Pods вкусы
            {
                "product_id": products[3].id,
                "name": "Табак",
                "price": None,
                "quantity": 20,
                "is_available": True
            },
            {
                "product_id": products[3].id,
                "name": "Мята",
                "price": None,
                "quantity": 15,
                "is_available": True
            },
            {
                "product_id": products[3].id,
                "name": "Манго",
                "price": None,
                "quantity": 10,
                "is_available": True
            },
            
            # Vuse Pods вкусы
            {
                "product_id": products[4].id,
                "name": "Классический табак",
                "price": None,
                "quantity": 18,
                "is_available": True
            },
            {
                "product_id": products[4].id,
                "name": "Ментол",
                "price": None,
                "quantity": 12,
                "is_available": True
            },
            
            # Salt Liquid вкусы
            {
                "product_id": products[5].id,
                "name": "Клубника-банан",
                "price": None,
                "quantity": 15,
                "is_available": True
            },
            {
                "product_id": products[5].id,
                "name": "Ледяная мята",
                "price": None,
                "quantity": 20,
                "is_available": True
            },
            {
                "product_id": products[5].id,
                "name": "Ваниль",
                "price": None,
                "quantity": 10,
                "is_available": True
            },
            
            # Freebase Liquid вкусы
            {
                "product_id": products[6].id,
                "name": "Табак",
                "price": None,
                "quantity": 8,
                "is_available": True
            },
            {
                "product_id": products[6].id,
                "name": "Карамель",
                "price": None,
                "quantity": 12,
                "is_available": True
            },
            {
                "product_id": products[6].id,
                "name": "Кофе",
                "price": None,
                "quantity": 6,
                "is_available": True
            }
        ]
        
        for variant_data in variants_data:
            variant = ProductVariant(**variant_data)
            session.add(variant)
        
        await session.flush()
        print(f"✅ Добавлено {len(variants_data)} вариантов товаров")
        
        # Добавляем промокоды
        promo_codes_data = [
            {
                "code": "WELCOME10",
                "type": PromoCodeType.PERCENT,
                "value": 10,
                "is_active": True,
                "usage_limit": None
            },
            {
                "code": "DISCOUNT200",
                "type": PromoCodeType.FIXED,
                "value": 200,
                "is_active": True,
                "usage_limit": 100
            },
            {
                "code": "BONUS500",
                "type": PromoCodeType.BALANCE,
                "value": 500,
                "is_active": True,
                "usage_limit": 50
            },
            {
                "code": "SALE15",
                "type": PromoCodeType.PERCENT,
                "value": 15,
                "is_active": True,
                "usage_limit": None
            },
            {
                "code": "CASHBACK100",
                "type": PromoCodeType.BALANCE,
                "value": 100,
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
        
        print("\n🎉 Все товары успешно загружены!")
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
        await load_real_products()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
