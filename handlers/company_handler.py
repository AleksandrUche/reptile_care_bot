import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.company_factory import CompanyCallback
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils.inline_kb_utils import (
    show_companies_page_inline_kb,
)
from services.pet_services import (
    get_all_companies_user,
    get_company,
)

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(
    F.data.in_({'company', 'back_to_company_menu'}), StateFilter(default_state)
)
async def company_main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text='Компании 🏢',
        reply_markup=inline_keyboards.menu_company,
    )


@router.callback_query(
    F.data.in_({'my_companies', 'back_to_all_company'}), StateFilter(default_state)
)
async def my_all_companies(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    my_companies = await get_all_companies_user(callback.from_user.id, session)

    inline_kb = await show_companies_page_inline_kb(companies=my_companies, page=0)

    await callback.message.edit_text(
        text='🏢Все компании:\n\n'
             f'Количество компаний: {len(my_companies)}',
        reply_markup=inline_kb,
    )


@router.callback_query(CompanyCallback.filter())
async def detail_company_handler(
    callback: CallbackQuery,
    callback_data: CompanyCallback,
    session: AsyncSession,
):
    """Обработчик для детального просмотра компании"""
    await callback.answer()
    company = await get_company(callback_data.company_id, session)

    await callback.message.edit_text(
        text=f'Название компании: {company.name}\n\n'
             f'Описание: {company.description}\n'
             f'Питомцев в компании: ---\n',
        reply_markup=inline_keyboards.back_to_all_company

    )
