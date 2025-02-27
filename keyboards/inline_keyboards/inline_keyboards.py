from keyboards.keyboard_utils.inline_kb_utils import create_inline_kb

my_profile = create_inline_kb(
    1,
    about_subscription='Подписка',
    payment_history='История пополнений',
    back_to_main_menu='⬅ Назад',
)

main_menu_inline = create_inline_kb(
    2,
    pets_menu='Питомцы',
    company='Компания',
    pets='Кормления',
    profile='Профиль',
    supports='Поддержка',
    about_bot='О боте',
    user_offer='Пользовательское соглашение',
)

main_menu_pets = create_inline_kb(
    2,
    add_pet='➕ Добавить питомца',
    my_pets_list='🧾 Все питомцы',
    back_to_main_menu='⬅ Назад',
)

menu_add_pet = create_inline_kb(
    2,
    cancel_state='Отмена',
    back_to_pets_menu='⬅ Назад'
)

back_to_all_pets = create_inline_kb(
    1, back_to_all_pets='⬅ Назад'
)

back_to_main_menu = create_inline_kb(
    1, back_to_main_menu='⬅ Назад'
)

menu_company = create_inline_kb(
    1,
    my_companies='Мои компании',
    back_to_main_menu='⬅ Назад',
)

back_to_all_company = create_inline_kb(
    1, back_to_all_company='⬅ Назад'
)
