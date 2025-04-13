from keyboards.keyboard_utils.inline_kb_utils import create_inline_kb

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
