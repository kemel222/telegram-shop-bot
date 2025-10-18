from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from services.user_service import UserService
from services.promo_service import PromoService
from database.database import async_session_maker

router = Router()


class PromoStates(StatesGroup):
    waiting_for_promo = State()


@router.message(F.text.startswith("Промокод:") | F.text.startswith("промокод:"))
async def activate_promo_from_message(message: Message):
    """Активировать промокод из сообщения"""
    # Извлекаем промокод из текста
    promo_code = message.text.split(":", 1)[1].strip()
    
    async with async_session_maker() as session:
        user = await UserService.get_user_by_telegram_id(session, message.from_user.id)
        
        if not user:
            await message.answer("❌ Пользователь не найден. Используйте /start")
            return
        
        # Проверяем промокод
        is_valid, error_msg, promo = await PromoService.validate_promo_code(session, promo_code)
        
        if not is_valid:
            await message.answer(f"❌ {error_msg}")
            return
        
        from database.models import PromoCodeType
        
        if promo.type == PromoCodeType.BALANCE:
            # Применяем промокод на пополнение баланса
            success, msg, _ = await PromoService.apply_promo_code(session, user.id, promo_code, 0)
            
            if success:
                # Обновляем пользователя
                user = await UserService.get_user_by_id(session, user.id)
                await message.answer(f"✅ {msg}\n💰 Ваш новый баланс: {user.balance}₽")
            else:
                await message.answer(f"❌ {msg}")
        else:
            await message.answer(
                f"✅ Промокод действителен!\n"
                f"Используйте его при оформлении заказа для получения скидки."
            )

