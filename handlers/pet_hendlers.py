import logging

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import inline_keyboards

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(F.data.in_({'pets_menu', 'back_to_pets_menu'}))
async def pets_menu(callback: CallbackQuery):
    await callback.answer()
    await  callback.message.edit_text(
        text='Питомцы',
        reply_markup=inline_keyboards.main_menu_pets,
    )


@router.callback_query(F.data == 'add_pet')
async def add_pet(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    await  callback.message.edit_text(
        text='Добавление питомца 🦝',
        reply_markup=inline_keyboards.menu_add_pet,
    )
