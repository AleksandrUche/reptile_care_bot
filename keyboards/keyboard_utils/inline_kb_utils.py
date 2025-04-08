from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from enums.enum_role import Language
from enums.pets_enum import GenderRole
from factory.callback_factory.company_factory import CompanyCallback
from factory.callback_factory.pet_factory import (
    PaginationCallback,
    PetsCallback,
    EditPetCallback,
    DeletePetCallback,
    GenderSelectionCallback,
    AddSheduleFeedingsCallback,
    ConfirmFeedingEventsCallback,
)
from factory.callback_factory.user_factory import (
    EditMyProfileCallback,
    LanguageSelectionCallback,
    EditTimeZoneSelectCallback,
    ApproveTimeZoneCallback,
)
from lexicon.lexicon import LEXICON_RU


def create_inline_kb(width: int, *args: str, **kwargs: str) -> InlineKeyboardMarkup:
    """
    Функция для формирования инлайн-клавиатуры.
    :param width: Количество кнопок по ширине.
    :param args: Позиционные аргументы для [LEXICON].
    :param kwargs: Именованные value_button='text button'.
    """
    kb_builder = InlineKeyboardBuilder()
    buttons: list[InlineKeyboardButton] = []

    # Заполняем список кнопками из аргументов args и kwargs
    if args:
        for button in args:
            buttons.append(InlineKeyboardButton(
                text=LEXICON_RU[button] if button in LEXICON_RU else button,
                callback_data=button))
    if kwargs:
        for button, text in kwargs.items():
            buttons.append(InlineKeyboardButton(
                text=text,
                callback_data=button))

    # Распаковываем список с кнопками в билдер методом row c параметром width
    kb_builder.row(*buttons, width=width)
    return kb_builder.as_markup()


async def show_pets_page_inline_kb(pets: list, page: int = 0, pets_per_page: int = 6):
    """
    Отображает питомцев на странице с пагинацией.
    :param pets: Список всех питомцев.
    :param page: Номер текущей страницы.
    :param pets_per_page: Количество питомцев на одной странице.
    :return: Инлайн клавиатура.
    """
    # Вычисляем начальный и конечный индекс для текущей страницы
    start_index = page * pets_per_page
    end_index = start_index + pets_per_page
    pets_page = pets[start_index:end_index]

    builder = InlineKeyboardBuilder()

    for pet in pets_page:
        builder.button(
            text=pet.name,
            callback_data=PetsCallback(
                pet_id=pet.id, company_id=pet.company_id, group_id=pet.group_id
            )
        )

    if page > 0:
        builder.button(
            text='⬅️ Назад',
            callback_data=PaginationCallback(action='prev', page=page).pack()
        )
    if end_index < len(pets):
        builder.button(
            text='Вперед ➡️',
            callback_data=PaginationCallback(action='next', page=page).pack()
        )

    builder.button(text='🔙 Главное меню', callback_data='back_to_main_menu')
    builder.adjust(1)  # Кнопок в строке

    return builder.as_markup()


async def show_companies_page_inline_kb(
    companies: list, page: int = 0, per_page: int = 6
):
    """
    Отображает компании на странице с пагинацией.
    :param company: Список всех компаний.
    :param page: Номер текущей страницы.
    :param pets_per_page: Количество компаний на одной странице.
    :return: Инлайн клавиатура.
    """
    # Вычисляем начальный и конечный индекс для текущей страницы
    start_index = page * per_page
    end_index = start_index + per_page
    companies_page = companies[start_index:end_index]

    builder = InlineKeyboardBuilder()

    for company in companies_page:
        builder.button(
            text=company.name,
            callback_data=CompanyCallback(
                company_id=company.id, user_id=company.user_id
            )
        )

    if page > 0:
        builder.button(
            text='⬅️ Назад',
            callback_data=PaginationCallback(action='prev', page=page).pack()
        )
    if end_index < len(companies):
        builder.button(
            text='Вперед ➡️',
            callback_data=PaginationCallback(action='next', page=page).pack()
        )

    builder.button(text='🔙 Меню', callback_data='back_to_company_menu')
    builder.adjust(1)

    return builder.as_markup()


async def get_interaction_pet_inline_kb(
    pet_id: int, pet_name: str, company_id: int, group_id: int
):
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='⚖️ Добавить вес',
        callback_data=EditPetCallback(field='weight', **data).pack()
    )
    builder.button(
        text='📐 Добавить длину',
        callback_data=EditPetCallback(field='length', **data).pack()
    )
    builder.button(
        text='🐍 Добавить линьку',
        callback_data=EditPetCallback(field='molting', **data).pack()
    )
    builder.button(
        text='✏ Редактировать',
        callback_data=EditPetCallback(field='all_editing_tools')
    )
    builder.button(
        text='🥗 График кормлений',
        callback_data=AddSheduleFeedingsCallback(action='menu', **data).pack()
    )
    builder.button(
        text='🥗 Покормить',
        callback_data=EditPetCallback(field='add_feeding', **data).pack()
    )
    builder.button(
        text='❌ Удалить питомца ',
        callback_data=DeletePetCallback(
            action='menu', pet_id=pet_id, pet_name=pet_name
        ).pack()
    )
    builder.button(
        text='⬅ Назад',
        callback_data='back_to_all_pets'
    )
    builder.adjust(2)  # По 2 кнопки в строке
    return builder.as_markup()


async def get_edit_pet_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Клавиатура для отображения инлайн меню редактирования питомца"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='✏ Имя',
        callback_data=EditPetCallback(field='name', **data).pack()
    )
    builder.button(
        text='✏ Морфу',
        callback_data=EditPetCallback(field='morph', **data).pack()
    )
    builder.button(
        text='✏ Вид',
        callback_data=EditPetCallback(field='view', **data).pack()
    )
    builder.button(
        text='✏ Пол',
        callback_data=EditPetCallback(field='gender', **data).pack()
    )
    builder.button(
        text='✏ Дата рождения',
        callback_data=EditPetCallback(field='birth', **data).pack()
    )
    builder.button(
        text='✏ Дата приобретения',
        callback_data=EditPetCallback(field='purchase', **data).pack()
    )
    builder.button(
        text='⬅ Назад',
        callback_data=PetsCallback(**data).pack()
    )
    builder.adjust(2)  # По 2 кнопки в строке
    return builder.as_markup()


async def get_add_shedule_feedings_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Клавиатура для выбора режима добавления графика кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='1 вариант',
        callback_data=AddSheduleFeedingsCallback(
            action='single_addition', **data
        ).pack()
    )
    builder.button(
        text='2 вариант',
        callback_data=AddSheduleFeedingsCallback(action='group_addition', **data).pack()
    )
    builder.button(
        text='3 вариант',
        callback_data=AddSheduleFeedingsCallback(
            action='group_addition_and_description', **data).pack()
    )
    builder.button(
        text='4 вариант',
        callback_data=AddSheduleFeedingsCallback(action='every_day', **data).pack()
    )
    builder.button(
        text='⬅ Вернуться к питомцу',
        callback_data=PetsCallback(**data).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_select_shedule_feedings_clear_state_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Возврат к меню выбора добавления графиков кормления с очисткой машины состояний"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='Отмена',
        callback_data='cancel_state'
    )
    builder.button(
        text='⬅ Назад',
        callback_data=AddSheduleFeedingsCallback(action='menu', **data).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_select_shedule_feedings_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Возврат к меню выбора добавления графиков кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='⬅ Назад',
        callback_data=AddSheduleFeedingsCallback(action='menu', **data).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_delete_pet_inline_kb(pet_id: int, pet_name: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='✅ ДА',
        callback_data=DeletePetCallback(
            action='delete', pet_id=pet_id, pet_name=pet_name
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=DeletePetCallback(
            action='cancel', pet_id=pet_id, pet_name=pet_name
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_gender_select_pet_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='♂ Мальчик',
        callback_data=GenderSelectionCallback(action=GenderRole.BOY, **data).pack()
    )
    builder.button(
        text='♀ Девочка',
        callback_data=GenderSelectionCallback(
            action=GenderRole.GIRL, **data
        ).pack()
    )
    builder.button(
        text='🤷‍♂️ Не определен',
        callback_data=GenderSelectionCallback(
            action=GenderRole.NOT_DEFINED, **data
        ).pack()
    )
    builder.button(
        text='Назад', callback_data=PetsCallback(**data).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_return_detail_view_pet_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⬅ Вернуться к питомцу',
        callback_data=PetsCallback(
            pet_id=pet_id, company_id=company_id, group_id=group_id
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_edit_profile_inline_kb(user_tg_id: int):
    """Редактирование пользователя."""
    builder = InlineKeyboardBuilder()

    builder.button(
        text='✏ Язык',
        callback_data=EditMyProfileCallback(
            action='language', user_tg_id=user_tg_id
        ).pack()
    )
    builder.button(
        text='✏ Часовой пояс',
        callback_data=EditMyProfileCallback(
            action='edit_time_zone', user_tg_id=user_tg_id
        ).pack()
    )
    builder.button(
        text='⬅ Назад', callback_data='back_to_my_profile'
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_language_select_inline_kb(user_tg_id: int):
    """Выбор языка пользователя."""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Русский',
        callback_data=LanguageSelectionCallback(
            language=Language.RU, user_tg_id=user_tg_id
        ).pack()
    )
    builder.button(
        text='English',
        callback_data=LanguageSelectionCallback(
            language=Language.EN, user_tg_id=user_tg_id
        ).pack()
    )
    builder.button(
        text='Назад', callback_data='back_to_edit_my_profile'
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_timezone_select_inline_kb(user_tg_id: int):
    """Редактирование тайм зоны"""
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Ввести свой город',
        callback_data=EditTimeZoneSelectCallback(
            action='search_city', user_tg_id=user_tg_id
        ).pack()
    )
    builder.button(
        text='Геопозиция',
        callback_data=EditTimeZoneSelectCallback(
            action='geolocation', user_tg_id=user_tg_id
        ).pack()
    )
    builder.button(
        text='⬅ Назад', callback_data='back_to_edit_my_profile'
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_approve_tz_by_city_inline_kb(
    user_tg_id: int, time_zone: str, offset: int, lng: float, lat: float,
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
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=EditTimeZoneSelectCallback(
            action='search_city', user_tg_id=user_tg_id
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_approve_tz_by_location_inline_kb(
    user_tg_id: int, time_zone: str, offset: int, lng: float, lat: float,
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
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=EditTimeZoneSelectCallback(
            action='geolocation', user_tg_id=user_tg_id
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_back_select_time_zone_inline_kb(user_tg_id: int):
    builder = InlineKeyboardBuilder()
    builder.button(text='Отмена', callback_data='cancel_state')
    builder.button(
        text='⬅ Назад',
        callback_data=EditMyProfileCallback(
            action='edit_time_zone',
            user_tg_id=user_tg_id
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def no_time_zone_inline_kb(
    user_tg_id: int, pet_id: int, company_id: int, group_id: int
):
    """
    Клавиатура возникающая в процессе добавлений графиков кормлений если у
    пользователя не определена таймзона
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Указать таймзону',
        callback_data=EditMyProfileCallback(
            action='edit_time_zone',
            user_tg_id=user_tg_id).pack()
    )
    builder.button(
        text='Назад',
        callback_data=AddSheduleFeedingsCallback(
            action='menu',
            pet_id=pet_id,
            company_id=company_id,
            group_id=group_id,
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_shedule_feeding_approve_inline_kb(
    event_feeding_id: int, pet_id: int, pet_name: str
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Покормил(а) ✅',
        callback_data=ConfirmFeedingEventsCallback(
            action='approve',
            event_feeding_id=event_feeding_id,
            pet_id=pet_id,
            pet_name=pet_name,
        ).pack()
    )
    builder.button(
        text='Напомнить ⏱',
        callback_data=ConfirmFeedingEventsCallback(
            action='remind',
            event_feeding_id=event_feeding_id,
            pet_id=pet_id,
            pet_name=pet_name,
        ).pack()
    )
    builder.button(
        text='Не напоминать ❌',
        callback_data=ConfirmFeedingEventsCallback(
            action='cancel',
            event_feeding_id=event_feeding_id,
            pet_id=pet_id,
            pet_name=pet_name,
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()
