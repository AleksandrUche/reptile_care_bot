import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import DeletePetCallback, ChoiceDeletePet
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils.inline_kb_utils import get_delete_pet_inline_kb
from services.pet_services import delete_pet, get_pet

logger = logging.getLogger(__name__)
router = Router(name='del_pet')


@router.callback_query(DeletePetCallback.filter(F.action == 'menu'))
async def delete_pet_handler(
    callback: CallbackQuery, callback_data: DeletePetCallback, session: AsyncSession
):
    """Обработчик для удаления питомца."""
    await callback.answer()
    try:
        pet = await get_pet(
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
            session
        )
        inline_kb = await get_delete_pet_inline_kb(callback_data.pet_id, pet.name)
    except Exception as e:
        logger.error(f'Не удалось найти питомца {e}', exc_info = True)
    else:
        await callback.message.edit_text(
            f"<b>Вы уверены, что хотите удалить питомца \"{pet.name}\"?</b>\n",
            reply_markup=inline_kb,
        )


@router.callback_query(ChoiceDeletePet.filter(F.action == 'delete'))
async def process_delete_confirm_pet(
    callback: CallbackQuery, callback_data: DeletePetCallback, session: AsyncSession
):
    """Подтверждение Удаления питомца."""
    try:
        await delete_pet(callback_data.pet_id, session)

    except Exception as e:
        logger.error(f'Ошибка при удалении питомца: {e}', exc_info=True)
        await callback.message.answer(
            'Произошла ошибка при удалении питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    else:
        await callback.message.edit_text(
            f"Питомец \"{callback_data.pet_name}\" был удален ✅",
            reply_markup=inline_keyboards.main_menu_pets,
        )


@router.callback_query(ChoiceDeletePet.filter(F.action == 'cancel'))
async def process_undo_delete_pet(
    callback: CallbackQuery, callback_data: DeletePetCallback
):
    """Отмена удаления питомца"""
    await callback.message.edit_text(
        f"Удаление питомца \"{callback_data.pet_name}\" отменено.",
        reply_markup=inline_keyboards.main_menu_pets,
    )
