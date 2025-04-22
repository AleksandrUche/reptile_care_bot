import logging

from aiogram.types import CallbackQuery
from sqlalchemy import update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user_models import UserOrm
from services.registration_services import get_user

logger = logging.getLogger(__name__)


async def get_user_profile(callback: CallbackQuery, keyboard, session: AsyncSession):
    try:
        user = await get_user(callback.from_user.id, session)
    except Exception as e:
        logger.error(
            f"Ошибка при открытии профиля пользователя c id = {callback.from_user.id}: {e}",
            exc_info=True,
        )
        await callback.message.answer(
            text="Произошла ошибка, пользователь не найден\n"
            "Попробуйте еще раз, в случае неудачи обратитесь в поддержку."
        )
    else:
        if user.tz_region:
            gmt = "+" if user.tz_offset > 0 else ""
            user_tz = f'GMT "{gmt}{user.tz_offset}"'
        else:
            user_tz = "Не указан"

        await callback.message.edit_text(
            text=f"Ваше имя: {user.first_name}\n"
            f"Язык: {user.language}\n"
            f"Часовой пояс: {user_tz}",
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
    stmt = (
        update(UserOrm).filter(UserOrm.telegram_id == user_tg_id).values(**update_data)
    )

    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(
            f'Ошибка при изменении "{name_field}" пользователя: {e}', exc_info=True
        )
    else:
        return True


async def edit_user_time_zone(
    user_tg_id: int,
    tz_region: str,
    tz_offset: int,
    longitude: float,
    latitude: float,
    session: AsyncSession,
):
    """
    Изменяет данные связанные с таймзоной пользователя
    :param user_tg_id: ID пользователя в телеграм.
    :param tz_region: Регион пользователя ("Europe/Moscow")
    :param tz_offset: Смещение пояса от UTC.
    :param longitude: Долгота.
    :param latitude: Широта.
    :param session: Сессия.
    :return: True, если обновление прошло успешно, иначе False.
    """

    stmt = (
        update(UserOrm)
        .filter(UserOrm.telegram_id == user_tg_id)
        .values(
            tz_region=tz_region,
            tz_offset=tz_offset,
            longitude=longitude,
            latitude=latitude,
        )
    )

    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(
            f'Ошибка при изменении таймзоны пользователя с id "{user_tg_id}": {e}',
            exc_info=True,
        )
    else:
        return True
