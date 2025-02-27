from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.pet_factory import (
    PaginationCallbackFactory,
    PetsCallbackFactory,
)
from factory.callback_factory.company_factory import CompanyCallbackFactory
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
            callback_data=PetsCallbackFactory(
                id=pet.id, company_id=pet.company_id, group_id=pet.group_id
            )
        )

    if page > 0:
        builder.button(
            text='⬅️ Назад',
            callback_data=PaginationCallbackFactory(action='prev', page=page).pack()
        )
    if end_index < len(pets):
        builder.button(
            text='Вперед ➡️',
            callback_data=PaginationCallbackFactory(action='next', page=page).pack()
        )

    builder.button(text='🔙 Главное меню', callback_data='back_to_main_menu')
    builder.adjust(1)  # Кнопок в строке

    return builder.as_markup()


async def show_companies_page_inline_kb(companies: list, page: int = 0, per_page: int = 6):
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
            callback_data=CompanyCallbackFactory(
                company_id=company.id, user_id=company.user_id
            )
        )

    if page > 0:
        builder.button(
            text='⬅️ Назад',
            callback_data=PaginationCallbackFactory(action='prev', page=page).pack()
        )
    if end_index < len(companies):
        builder.button(
            text='Вперед ➡️',
            callback_data=PaginationCallbackFactory(action='next', page=page).pack()
        )

    builder.button(text='🔙 Меню', callback_data='back_to_company_menu')
    builder.adjust(1)

    return builder.as_markup()
