import logging

from aiogram import F
from aiogram import Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.user_factory import (
    EditMyProfileCallback,
    LanguageSelectionCallback,
    EditTimeZoneSelectCallback,
    ApproveTimeZoneCallback,
)
from integrations.timezone_service import GeoAPIClient
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils import inline_kb_utils
from keyboards.keyboard_utils.inline_kb_utils import (
    get_approve_tz_by_city_inline_kb,
    get_back_select_time_zone_inline_kb,
    get_approve_tz_by_location_inline_kb,
)
from services.user_services import (
    get_user_profile,
    edit_user_profile_value,
    edit_user_time_zone,
)
from states.user_states import SearchTimeZoneByCityFSM, SearchTimeZoneByGeoPositionFSM

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


@router.callback_query(EditMyProfileCallback.filter(F.action == 'edit_time_zone'))
async def edit_profile_timezone(
    callback: CallbackQuery, callback_data: EditMyProfileCallback
):
    """Обработчик для изменения таймзоны пользователя"""
    await callback.answer()
    inline_kb = await inline_kb_utils.get_timezone_select_inline_kb(
        callback_data.user_tg_id
    )

    await  callback.message.edit_text(
        text='🕛 Часовой пояс\n'
             '<b>Выберите способ добавления</b> 👇',
        reply_markup=inline_kb,
    )


@router.callback_query(EditTimeZoneSelectCallback.filter(F.action == 'search_city'))
async def process_edit_time_zone_by_search_city(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Изменение часового пояса по городу."""
    await  callback.answer()

    inline_back_kb = await get_back_select_time_zone_inline_kb(
        callback.message.from_user.id
    )

    await callback.message.edit_text(
        'Поиск часового пояса по вашему городу\n'
        '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
        'Город можно ввести с уточнением области\n'
        '<b>Введите город:</b>\n',
        reply_markup=inline_back_kb,
    )
    await state.set_state(SearchTimeZoneByCityFSM.city)


@router.message(StateFilter(SearchTimeZoneByCityFSM.city))
async def process_edit_time_zone_by_city(message: Message, state: FSMContext):
    """Изменение часового пояса по поиску города пользователя."""
    await state.update_data(city=message.text)
    city = await state.get_value('city')

    api_client = GeoAPIClient()
    timezone = await api_client.get_search_time_zone_by_city(city)
    if not timezone:
        await message.answer('Возможно, Вы допустили ошибку, повторите еще раз.')
    inline_approve_kb = await get_approve_tz_by_city_inline_kb(
        message.from_user.id,
        timezone['time_zone'],
        timezone['offset'],
        timezone['lng'],
        timezone['lat'],
    )
    gmt = '+' if timezone['offset'] > 0 else ''

    if timezone:
        await message.answer(
            f"Ваш часовой пояс \"GMT {gmt}{timezone['offset']}\"?\n"
            f"{timezone['time_zone']}",
            reply_markup=inline_approve_kb,
        )
    else:
        await message.answer(
            'Произошла ошибка при поиске часового пояса!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.callback_query(ApproveTimeZoneCallback.filter())
async def process_approve_edit_time_zone_by_city(
    callback: CallbackQuery,
    callback_data: ApproveTimeZoneCallback,
    session: AsyncSession,
):
    """Добавление часового пояса в БД."""

    add_time_zone = await edit_user_time_zone(
        callback_data.user_tg_id,
        callback_data.time_zone,
        callback_data.offset,
        callback_data.lng,
        callback_data.lat,
        session
    )

    if add_time_zone:
        await callback.message.answer(
            f"Часовой пояс \"{callback_data.time_zone}\" добавлен",
            reply_markup=inline_keyboards.back_edit_my_profile,
        )
    else:
        await callback.message.answer(
            'Произошла ошибка при добавлении часового пояса!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )


@router.callback_query(EditTimeZoneSelectCallback.filter(F.action == 'geolocation'))
async def process_edit_time_zone_by_geolocation(
    callback: CallbackQuery,
    state: FSMContext,
):
    """Изменение часового пояса по геопозиции."""
    await  callback.answer()

    inline_back_kb = await get_back_select_time_zone_inline_kb(
        callback.message.from_user.id
    )

    await callback.message.edit_text(
        'Поиск часового пояса по вашей геопозиции\n'
        '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
        '<b>Поделитесь геопозицией</b>\n',
        reply_markup=inline_back_kb,
    )
    await state.set_state(SearchTimeZoneByGeoPositionFSM.location)


@router.message(StateFilter(SearchTimeZoneByGeoPositionFSM.location), F.location)
async def process_edit_time_zone_by_location(message: Message, state: FSMContext):
    """Изменение часового пояса по геопозиции пользователя."""

    api_client = GeoAPIClient()
    coords = {'lng': message.location.longitude, 'lat': message.location.latitude}
    timezone = await api_client.get_time_zone_by_coord(coords)

    inline_approve_kb = await get_approve_tz_by_location_inline_kb(
        message.from_user.id,
        timezone['time_zone'],
        timezone['offset'],
        coords['lng'],
        coords['lat'],
    )
    gmt = '+' if timezone['offset'] > 0 else ''

    if timezone:
        await message.answer(
            f"Ваш часовой пояс \"GMT {gmt}{timezone['offset']}\"?\n"
            f"{timezone['time_zone']}",
            reply_markup=inline_approve_kb,
        )
    else:
        await message.answer(
            'Произошла ошибка при поиске часового пояса!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.message(StateFilter(SearchTimeZoneByGeoPositionFSM.location))
async def warning_incorrect_geo_location(message: Message):
    """Сработает при некорректной отправки геопозиции"""
    await message.answer(
        text='То, что Вы отправили не похоже на вашу геопозицию 🚩\n'
             'Пожалуйста, отправьте геопозицию еще раз\n'
    )
