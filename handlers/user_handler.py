from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user_models import UserOrm
from keyboards.inline_keyboards import inline_keyboards

router = Router()


@router.message(F.text == 'Профиль')
async def my_profile(message: Message, session: AsyncSession):
    user = await session.scalar(
        select(UserOrm).filter(UserOrm.telegram_id == message.from_user.id)
    )

    if not user:
        await message.answer(text='Произошла ошибка, пользователь не найден')

    await message.answer(
        text=f'Ваше имя: {user.first_name}\n',
        reply_markup=inline_keyboards.my_profile,
    )


@router.callback_query(F.data == 'about_subscription')
async def process_buttons_press(callback: CallbackQuery):
    await callback.message.answer(
        text='📋Подписка позволяет вам добавлять больше двух питомцев, '
             'создавать компании/группы, делится ими с другими '
             'пользователями для администрирования и работы. Выдавать определенную роль '
             'в компании это может быть как рабочий так и администратор.\n'
             '🙂 Без подписки вы можете пользоваться ботом, но добавлять больше двух '
             'питомцев нельзя а так же нельзя создавать дополнительные компании и '
             'группы животных.\n\n'
             '⭐Стоимость полного доступа:\n'
             '...₽ - 30 дней\n'
             '...₽ - 60 дней\n'
             '...₽ - 90 дней\n'
             '...₽ - 183 дня\n'
             '...₽ - 365 дней\n'
    )
    await callback.answer()
