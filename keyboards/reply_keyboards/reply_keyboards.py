from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Мои питомцы'), KeyboardButton(text='Добавить питомца')],
        [KeyboardButton(text='Кормление'), KeyboardButton(text='Группы')],
        [KeyboardButton(text='Профиль'), KeyboardButton(text='Поддержка')],
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню...'
)
