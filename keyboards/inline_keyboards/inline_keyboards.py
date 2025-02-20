from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from keyboards.keyboard_utils.inline_kb_utils import create_inline_kb

my_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='О боте', callback_data='about_bot'),
         InlineKeyboardButton(text='О подписке', callback_data='about_subscription')],
        [InlineKeyboardButton(text='История пополнений',
                              callback_data='payment_history'),
         InlineKeyboardButton(text='Добавить компанию', callback_data='add_company')],
        [InlineKeyboardButton(text='Пользовательское соглашение',
                              callback_data='user_offer')],
    ],
)

main_menu_inline = create_inline_kb(
    2,
    pets_menu='Питомцы',
    company='Компания',
    pets='Кормления',
    profile='Профиль',
    supports='Поддержка',
)

main_menu_pets = create_inline_kb(
    2,
    add_pet='➕ Добавить питомца',
    my_pets='🧾 Мои питомцы',
    back_to_main_menu='⬅ Назад',
)

menu_add_pet = create_inline_kb(
    2, cancel_add_pet='Отмена', back_to_pets_menu='⬅ Назад'
)

menu_company = create_inline_kb(2, my_companies='Мои компании')
