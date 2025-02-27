import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import (
    PaginationCallbackFactory,
)
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils.inline_kb_utils import (
    show_companies_page_inline_kb,
)
from services.pet_services import (
    get_user_company,
)

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(
    F.data.in_({"company", "back_to_company_menu"}), StateFilter(default_state)
)
async def company_main_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Компании 🏢",
        reply_markup=inline_keyboards.menu_company,
    )


@router.callback_query(F.data == "my_companies", StateFilter(default_state))
async def my_all_companies(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    my_companies = await get_user_company(callback.from_user.id, session)


    inline_kb = await show_companies_page_inline_kb(companies=my_companies, page=0)

    await callback.message.edit_text(
        text="🏢Все компании:\n\n" f"Количество компаний: {len(companies)}",
        reply_markup=inline_kb,
    )
