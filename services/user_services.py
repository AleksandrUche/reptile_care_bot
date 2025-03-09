import logging
from sqlalchemy import update
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user_models import UserOrm
from services.registration_services import user_exists

logger = logging.getLogger(__name__)


async def get_user_profile(
    callback: CallbackQuery,
    keyboard,
    session: AsyncSession
):
    try:
        user = await user_exists(callback.from_user.id, session)
    except Exception as e:
        logger.error(
            f'Ошибка при открытии профиля пользователя c id = {callback.from_user.id}: {e}',
            exc_info=True
        )
        await callback.message.answer(
            text='Произошла ошибка, пользователь не найден\n'
                 'Попробуйте еще раз, в случае неудачи обратитесь в поддержку.'
        )
    else:
        await callback.message.edit_text(
            text=f'Ваше имя: {user.first_name}\n'
                 f'Язык: {user.language}\n'
                 f'Часовой пояс: {user.tz_offset}\n',
            reply_markup=keyboard,
        )


async def edit_user_profile_value(
    user_tg_id: int, name_field: str, value: str, session: AsyncSession
):
    """
    Изменяет значения указанного поля.
    :param user_tg_id: ID пользователя в телеграм.
    :param name_field: Имя поля, которое нужно обновить (например, "language").
    :param value: Новое значение для поля.
    :param session: Сессия.
    :return: True, если обновление прошло успешно, иначе False.
    """
    update_data = {name_field: value}
    stmt = update(UserOrm).filter(UserOrm.telegram_id == user_tg_id).values(
        **update_data
    )

    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при изменении \"{name_field}\" пользователя: {e}',
                     exc_info=True)
    else:
        return True
