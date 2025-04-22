from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.company_factory import CompanyCallback
from factory.callback_factory.pet_factory import AllPetPaginationCallback
from keyboards.keyboard_utils.inline_kb_utils import create_inline_kb

menu_company = create_inline_kb(
    1,
    my_companies='Мои компании',
    back_to_main_menu='⬅ Назад',
)

back_to_all_company = create_inline_kb(1, back_to_all_company='⬅ Назад')


async def show_companies_page_inline_kb(
    companies: list, page: int = 0, per_page: int = 6
):
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
            callback_data=CompanyCallback(
                company_id=company.id, user_id=company.user_id
            ).pack(),
        )

    if page > 0:
        builder.button(
            text='⬅️ Назад',
            callback_data=AllPetPaginationCallback(action='prev', page=page).pack(),
        )
    if end_index < len(companies):
        builder.button(
            text='Вперед ➡️',
            callback_data=AllPetPaginationCallback(action='next', page=page).pack(),
        )

    builder.button(text='🔙 Меню', callback_data='back_to_company_menu')
    builder.adjust(1)

    return builder.as_markup()
