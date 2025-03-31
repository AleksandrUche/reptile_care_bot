import logging

from aiogram import Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import PetsCallback
from keyboards.keyboard_utils.inline_kb_utils import get_edit_pet_inline_kb
from services.pet_services import get_pet
from services.utils import edit_date_format

logger = logging.getLogger(__name__)
router = Router(name='detail_pet')


@router.callback_query(PetsCallback.filter())
async def detail_pets_handler(
    callback: CallbackQuery, callback_data: PetsCallback, session: AsyncSession
):
    """Обработчик для детального просмотра питомца"""
    await callback.answer()

    pet = await get_pet(
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        session
    )

    inline_kb = await get_edit_pet_inline_kb(
        pet['pet'].id, pet['pet'].name, pet['pet'].company_id, pet['pet'].group_id
    )

    date_birth = edit_date_format(pet["pet"].date_birth)
    date_purchase = edit_date_format(pet["pet"].date_purchase)
    latest_molting_date = edit_date_format(pet["latest_molting_date"])

    await callback.message.edit_text(
        text=f'Имя питомца: {pet["pet"].name}\n\n'
             f'Морфа: {pet["pet"].morph}\n'
             f'Вид: {pet["pet"].view}\n'
             f'Пол: {pet["pet"].gender.value}\n'
             f'Вес: {pet["latest_weight"]}\n'
             f'Длина: {pet["latest_length"]}\n'
             f'Линька: {latest_molting_date}\n'
             f'Компания: {pet["company_name"]}\n'
             f'Группа: {pet["group_name"]}\n'
             f'Дата рождения: {date_birth}\n'
             f'Дата приобретения: {date_purchase}\n',
        reply_markup=inline_kb
    )
