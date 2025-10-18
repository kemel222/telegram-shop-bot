"""
Скрипт для добавления категорий вейп-шопа Hotspot
"""
import asyncio
from database.database import async_session_maker
from database.models import Category


async def init_categories():
    """Добавить категории для вейп-шопа"""
    async with async_session_maker() as session:
        print("🔄 Добавление категорий Hotspot...")
        
        categories_data = [
            {
                "name": "ЖИДКОСТИ",
                "description": "Жидкости для электронных сигарет различных вкусов",
            },
            {
                "name": "HQD / ОДНОРАЗКИ",
                "description": "Одноразовые электронные сигареты HQD и другие",
            },
            {
                "name": "КАРТРИДЖИ / ИСПАРИТЕЛИ",
                "description": "Сменные картриджи и испарители для POD-систем",
            },
            {
                "name": "POD - СИСТЕМЫ",
                "description": "POD-системы и электронные сигареты",
            }
        ]
        
        for cat_data in categories_data:
            # Проверяем, существует ли уже такая категория
            from sqlalchemy import select
            result = await session.execute(
                select(Category).where(Category.name == cat_data["name"])
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"⚠️  Категория '{cat_data['name']}' уже существует, пропускаем")
                continue
            
            category = Category(**cat_data)
            session.add(category)
            print(f"✅ Добавлена категория: {cat_data['name']}")
        
        await session.commit()
        print("\n🎉 Категории успешно добавлены!")
        print("\n📋 Список категорий:")
        print("1. ЖИДКОСТИ")
        print("2. HQD / ОДНОРАЗКИ")
        print("3. КАРТРИДЖИ / ИСПАРИТЕЛИ")
        print("4. POD - СИСТЕМЫ")


async def main():
    """Главная функция"""
    try:
        await init_categories()
    except Exception as e:
        print(f"❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())

