from keyboards.keyboard_utils.inline_kb_utils import create_inline_kb

main_menu_inline = create_inline_kb(
    2,
    pets_menu="Питомцы",
    company="Компания",
    pets="Кормления",
    profile="Профиль",
    supports="Поддержка",
    about_bot="О боте",
    user_offer="Пользовательское соглашение",
)

back_to_main_menu = create_inline_kb(1, back_to_main_menu="⬅ Назад")
