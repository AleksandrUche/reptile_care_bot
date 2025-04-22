import logging

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import EditPetCallback
from services.pet_services import add_feeding_pet_date

logger = logging.getLogger(__name__)
router = Router(name="feeding_pet")


@router.callback_query(EditPetCallback.filter(F.field == "add_feeding"))
async def add_pet_feeding_handler(
    callback: CallbackQuery, callback_data: EditPetCallback, session: AsyncSession
):
    """Обработчик для добавления даты кормления питомца."""
    await callback.answer()
    try:
        await add_feeding_pet_date(callback_data.pet_id, session)
    except Exception as e:
        logger.error(f"Не удалось добавить дату кормления: {e}", exc_info=True)
        await callback.message.answer("Произошла ошибка при добавлении кормления")
    else:
        await callback.message.answer(
            text="🦎 Питомец покормлен, дата была добавлена в историю.\n"
            "Дополнительную информацию можно добавить при детальном "
            "просмотре истории кормлений",
        )
