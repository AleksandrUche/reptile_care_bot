import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards import inline_keyboards
from services.pet_services import get_user_company, get_company_and_groups, add_pet
from states.pet_states import AddPetFSM

logger = logging.getLogger(__name__)
router = Router()


@router.callback_query(
    F.data.in_({'pets_menu', 'back_to_pets_menu'}), StateFilter(default_state)
)
async def pets_menu(callback: CallbackQuery):
    await callback.answer()
    await  callback.message.edit_text(
        text='Питомцы',
        reply_markup=inline_keyboards.main_menu_pets,
    )


@router.callback_query(F.data == 'add_pet', StateFilter(default_state))
async def add_pet_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Добавление питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите имя питомца:</b>',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.set_state(AddPetFSM.pet_name)


@router.message(StateFilter(AddPetFSM.pet_name), F.text.func(is_alnum_with_spaces))
async def process_pet_name(message: Message, state: FSMContext, session: AsyncSession):
    """Добавляет питомца (с именем) в компанию со стандартной группой"""
    await state.update_data(pet_name=message.text)
    state_data = await state.get_data()

    added_pet = await add_pet(message.from_user.id, state_data['pet_name'], session)
    if added_pet:
        await message.answer(
            f"Питомец '{state_data['pet_name']}' успешно добавлен!",
            reply_markup=inline_keyboards.main_menu_pets,
        )
    else:
        await message.answer(
            'Произошла ошибка при добавлении питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.callback_query(F.data == 'cancel_add_pet', ~StateFilter(default_state))
async def cancel_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Действие отменено.")


@router.callback_query(
    F.data.in_({'company', 'back_to_company_menu'}), StateFilter(default_state)
)
async def company_main_menu(callback: CallbackQuery):
    await callback.answer()
    await  callback.message.edit_text(
        text='Компании 🏙',
        reply_markup=inline_keyboards.menu_company,
    )

@router.callback_query(
    F.data == 'my_companies', StateFilter(default_state)
)
async def my_company(callback: CallbackQuery, session: AsyncSession):
    await callback.answer()
    my_company = await get_user_company(callback.from_user.id, session)
    companies = ['Все компании: 🏙']

    for company in my_company:
        companies.append(company.name)

    await  callback.message.edit_text(
        text= '\n'.join(companies),
    )
