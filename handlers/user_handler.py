import logging

from aiogram import F
from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.user_factory import (
    EditMyProfileCallback,
    LanguageSelectionCallback,
)
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils import inline_kb_utils
from services.user_services import get_user_profile, edit_user_profile_value

router = Router()
logger = logging.getLogger(__name__)


@router.callback_query(F.data == 'profile')
@router.callback_query(F.data == 'back_to_my_profile')
async def my_profile(callback: CallbackQuery, session: AsyncSession):
    """Обработчик для отображения профиль пользователя"""
    await callback.answer()
    await get_user_profile(callback, inline_keyboards.my_profile, session)


@router.callback_query(F.data == 'edit_my_profile')
@router.callback_query(F.data == 'back_to_edit_my_profile')
async def edit_my_profile(callback: CallbackQuery, session: AsyncSession):
    """Обработчик для отображения меню редактирования пользователя"""
    await callback.answer()
    keyboard = await inline_kb_utils.get_edit_profile_inline_kb(callback.from_user.id)
    await get_user_profile(
        callback, keyboard, session
    )


@router.callback_query(EditMyProfileCallback.filter(F.action == 'language'))
async def edit_profile_language(
    callback: CallbackQuery, callback_data: EditMyProfileCallback
):
    """Обработчик для изменения языка пользователя"""
    await callback.answer()
    inline_kb = await inline_kb_utils.get_language_select_inline_kb(
        callback_data.user_tg_id
    )

    await  callback.message.edit_text(
        text='Изменение языка\n'
             '<b>Выберите язык</b> 👇',
        reply_markup=inline_kb,
    )


@router.callback_query(LanguageSelectionCallback.filter())
async def process_language_select(
    callback: CallbackQuery,
    callback_data: LanguageSelectionCallback,
    session: AsyncSession,
):
    """Изменение языка пользователя."""
    edit_pet = await edit_user_profile_value(
        callback_data.user_tg_id, 'language', callback_data.language.value, session
    )

    if edit_pet:
        await callback.message.edit_text(
            f"Теперь язык: \"{callback_data.language.value}\".",
            reply_markup=inline_keyboards.back_edit_my_profile,
        )
    else:
        await callback.message.answer(
            'Произошла ошибка при изменении языка!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
