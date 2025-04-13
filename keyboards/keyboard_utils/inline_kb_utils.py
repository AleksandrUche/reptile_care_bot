from aiogram.types import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

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
