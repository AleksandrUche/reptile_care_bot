import logging

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import inline_keyboards
from services.registration.registration_services import user_exists

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'profile')
async def my_profile(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    try:
        user = await user_exists(callback.from_user.id, session)
    except Exception as e:
        logger.error(
            f'Ошибка при открытии профиля пользователя c id = {callback.from_user.id}: {e}',
            exc_info=True
        )
        await callback.message.answer(text='Произошла ошибка, пользователь не найден')
    else:
        await callback.message.answer(
            text=f'Ваше имя: {user.first_name}\n',
            reply_markup=inline_keyboards.my_profile,
        )
    await callback.answer()
