import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import EditPetCallback
from services.pet_services import add_feeding_pet_date
from services.registration_services import get_user

logger = logging.getLogger(__name__)
router = Router(name='feeding_pet')


@router.callback_query(EditPetCallback.filter(F.field == 'add_feeding'))
async def add_pet_feeding_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    session: AsyncSession
):
    """Обработчик для добавления даты кормления питомца."""
    try:
        date_now = datetime.now().replace(tzinfo=timezone.utc)
        user = await get_user(callback.from_user.id, session)
        if not user.tz_region:
            await callback.answer(
                'Не установлен часовой пояс. Установите часовой пояс в профиле'
            )
            return
        date_tz_user = date_now.replace(tzinfo=ZoneInfo(user.tz_region))
        add_feeding = await add_feeding_pet_date(
            callback_data.pet_id,
            date_tz_user,
            session,
        )
    except Exception as e:
        logger.error(f'Не удалось добавить дату кормления: {e}', exc_info=True)
        await callback.answer(
            text='Произошла ошибка при добавлении кормления',
            show_alert=True,
        )
    else:
        if add_feeding:
            await callback.answer(
                text='✅ Питомец покормлен, дата была добавлена в историю.\n'
                     'Дополнительную информацию можно добавить при детальном '
                     'просмотре истории кормлений',
                show_alert=True,
            )
        else:
            await callback.answer(
                text='Произошла ошибка при добавлении кормления питомца!\n'
                     'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏',
                show_alert=True,
            )
