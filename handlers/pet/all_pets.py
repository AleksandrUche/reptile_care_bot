import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards.pet import common_pet_kb
from factory.callback_factory.pet_factory import AllPetPaginationCallback
from keyboards.inline_keyboards.pet.all_pets_kb import show_pets_page_inline_kb
from services.pet_services import get_my_companies_and_pets

logger = logging.getLogger(__name__)
router = Router(name="all_pets")


@router.callback_query(
    F.data.in_({"pets_menu", "back_to_pets_menu"}), StateFilter(default_state)
)
async def pets_menu(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        text="Питомцы",
        reply_markup=common_pet_kb.main_menu_pets,
    )


@router.callback_query(
    F.data.in_({"my_pets_list", "back_to_all_pets"}), StateFilter(default_state)
)
async def get_all_pets_handler(callback: CallbackQuery, session: AsyncSession):
    """Просмотр всех питомцев"""
    await callback.answer()
    pets_and_company = await get_my_companies_and_pets(callback.from_user.id, session)

    pets = []
    for company in pets_and_company:
        pets.extend(company.pets)
    inline_kb = await show_pets_page_inline_kb(pets=pets, page=0)

    await callback.message.edit_text(
        text=f"🦎<b>Все питомцы:</b>\n\nКоличество питомцев: {len(pets)}",
        reply_markup=inline_kb,
    )


@router.callback_query(AllPetPaginationCallback.filter(F.action == "next"))
async def next_page_my_pets_handler(
    callback: CallbackQuery,
    callback_data: AllPetPaginationCallback,
    session: AsyncSession,
):
    """Обработчик для кнопки 'Вперед'"""
    await callback.answer()
    page = callback_data.page + 1

    pets_and_company = await get_my_companies_and_pets(callback.from_user.id, session)

    pets = []
    for company in pets_and_company:
        pets.extend(company.pets)
    reply_markup = await show_pets_page_inline_kb(pets, page=page)

    await callback.message.edit_text(
        text=f"🦎<b>Все питомцы:</b>\n\nКоличество питомцев: {len(pets)}",
        reply_markup=reply_markup,
    )


@router.callback_query(AllPetPaginationCallback.filter(F.action == "prev"))
async def prev_page_my_pets_handler(
    callback: CallbackQuery,
    callback_data: AllPetPaginationCallback,
    session: AsyncSession,
):
    """Обработчик для кнопки 'Назад'"""
    await callback.answer()
    page = callback_data.page - 1

    pets_and_company = await get_my_companies_and_pets(callback.from_user.id, session)

    pets = []
    for company in pets_and_company:
        pets.extend(company.pets)
    reply_markup = await show_pets_page_inline_kb(pets, page=page)

    await callback.message.edit_text(
        text=f"🦎<b>Все питомцы:</b>\n\nКоличество питомцев: {len(pets)}",
        reply_markup=reply_markup,
    )
