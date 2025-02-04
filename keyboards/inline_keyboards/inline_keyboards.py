from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

my_profile = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Оформить подписку', callback_data='subscribe'),
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
        [InlineKeyboardButton(text='Питомцы', callback_data='pets')],
        [InlineKeyboardButton(text='Компания', callback_data='company')],
        [InlineKeyboardButton(text='Кормления', callback_data='pets')],
        [InlineKeyboardButton(text='Профиль', callback_data='profile')],
        [InlineKeyboardButton(text='Поддержка', callback_data='supports')],
    ]

)
