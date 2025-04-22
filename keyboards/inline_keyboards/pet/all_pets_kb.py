from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.pet_factory import PetsCallback, AllPetPaginationCallback


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
            ).pack(),
        )

    if page > 0:
        builder.button(
            text="⬅️ Назад",
            callback_data=AllPetPaginationCallback(action="prev", page=page).pack(),
        )
    if end_index < len(pets):
        builder.button(
            text="Вперед ➡️",
            callback_data=AllPetPaginationCallback(action="next", page=page).pack(),
        )

    builder.button(text="🔙 Главное меню", callback_data="back_to_main_menu")
    builder.adjust(1)  # Кнопок в строке

    return builder.as_markup()
