from aiogram.utils.keyboard import InlineKeyboardBuilder

from enums.enum_role import Language
from factory.callback_factory.user_factory import (
    EditMyProfileCallback,
    LanguageSelectionCallback,
    ApproveTimeZoneCallback,
    EditTimeZoneSelectCallback,
)
from keyboards.keyboard_utils.inline_kb_utils import create_inline_kb

my_profile = create_inline_kb(
    1,
    about_subscription='Подписка',
    payment_history='История пополнений',
    edit_my_profile='✏ Редактировать',
    back_to_main_menu='⬅ Назад',
)

back_edit_my_profile = create_inline_kb(
    1,
    back_to_edit_my_profile='⬅ Вернуться к редактированию',
)


async def get_edit_profile_inline_kb(user_tg_id: int):
    """Редактирование пользователя."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text='✏ Язык',
        callback_data=EditMyProfileCallback(
            action='language', user_tg_id=user_tg_id
        ).pack(),
    )
    builder.button(
        text='✏ Часовой пояс',
        callback_data=EditMyProfileCallback(
            action='edit_time_zone', user_tg_id=user_tg_id
        ).pack(),
    )
    builder.button(text='⬅ Назад', callback_data='back_to_my_profile')
    builder.adjust(1)
    return builder.as_markup()


async def get_language_select_inline_kb(user_tg_id: int):
    """Выбор языка пользователя."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Русский',
        callback_data=LanguageSelectionCallback(
            language=Language.RU, user_tg_id=user_tg_id
        ).pack(),
    )
    builder.button(
        text='English',
        callback_data=LanguageSelectionCallback(
            language=Language.EN, user_tg_id=user_tg_id
        ).pack(),
    )
    builder.button(text='Назад', callback_data='back_to_edit_my_profile')
    builder.adjust(1)
    return builder.as_markup()


async def get_approve_tz_by_city_inline_kb(
    user_tg_id: int,
    time_zone: str,
    offset: int,
    lng: float,
    lat: float,
):
    """Подтверждение тайм зоны по городу"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='✅ ДА',
        callback_data=ApproveTimeZoneCallback(
            user_tg_id=user_tg_id,
            time_zone=time_zone,
            offset=offset,
            lng=lng,
            lat=lat,
        ).pack(),
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=EditTimeZoneSelectCallback(
            action='search_city', user_tg_id=user_tg_id
        ).pack(),
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_approve_tz_by_location_inline_kb(
    user_tg_id: int,
    time_zone: str,
    offset: int,
    lng: float,
    lat: float,
):
    """Подтверждение тайм зоны по геопозиции"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='✅ ДА',
        callback_data=ApproveTimeZoneCallback(
            user_tg_id=user_tg_id,
            time_zone=time_zone,
            offset=offset,
            lng=lng,
            lat=lat,
        ).pack(),
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=EditTimeZoneSelectCallback(
            action='geolocation', user_tg_id=user_tg_id
        ).pack(),
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_back_select_time_zone_inline_kb(user_tg_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text='Отмена', callback_data='cancel_state')
    builder.button(
        text='⬅ Назад',
        callback_data=EditMyProfileCallback(
            action='edit_time_zone', user_tg_id=user_tg_id
        ).pack(),
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_timezone_select_inline_kb(user_tg_id: int):
    """Редактирование тайм зоны"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Ввести свой город',
        callback_data=EditTimeZoneSelectCallback(
            action='search_city', user_tg_id=user_tg_id
        ).pack(),
    )
    builder.button(
        text='Геопозиция',
        callback_data=EditTimeZoneSelectCallback(
            action='geolocation', user_tg_id=user_tg_id
        ).pack(),
    )
    builder.button(text='⬅ Назад', callback_data='back_to_edit_my_profile')
    builder.adjust(1)
    return builder.as_markup()
