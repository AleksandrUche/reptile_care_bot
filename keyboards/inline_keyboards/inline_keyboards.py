from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

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

main_menu_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Питомцы', callback_data='pets_menu')],
        [InlineKeyboardButton(text='Компания', callback_data='company')],
        [InlineKeyboardButton(text='Кормления', callback_data='pets')],
        [InlineKeyboardButton(text='Профиль', callback_data='profile')],
        [InlineKeyboardButton(text='Поддержка', callback_data='supports')],
    ]
)

main_menu_pets = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='➕ Добавить питомца', callback_data='add_pet')],
        [InlineKeyboardButton(text='🧾 Мои питомцы', callback_data='my_pets')],
        [InlineKeyboardButton(text='⬅ Назад', callback_data='back_to_main_menu')],
    ]
)

menu_add_pet = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Кнопка', callback_data='test')],
        [InlineKeyboardButton(text='⬅ Назад', callback_data='back_to_pets_menu')],
    ]
)
