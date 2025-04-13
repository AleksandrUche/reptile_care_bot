import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards.pet import common_pet_kb
from filters.pet_filters import is_alnum_with_spaces
from services.pet_services import add_pet
from states.pet_states import PetAddFSM

logger = logging.getLogger(__name__)
router = Router(name='add_pet')


@router.callback_query(F.data == 'add_pet', StateFilter(default_state))
async def add_pet_handler(callback: CallbackQuery, state: FSMContext):
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Добавление питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите имя питомца:</b>',
        reply_markup=common_pet_kb.menu_add_pet,
    )
    await state.set_state(PetAddFSM.pet_name)


@router.message(StateFilter(PetAddFSM.pet_name), F.text.func(is_alnum_with_spaces))
async def process_pet_name(message: Message, state: FSMContext, session: AsyncSession):
    """Добавляет питомца (с именем) в компанию со стандартной группой"""
    await state.update_data(pet_name=message.text)
    state_data = await state.get_data()

    added_pet = await add_pet(message.from_user.id, state_data['pet_name'], session)
    if added_pet:
        await message.answer(
            f"Питомец \"{state_data['pet_name']}\" успешно добавлен!",
            reply_markup=common_pet_kb.main_menu_pets,
        )
    else:
        await message.answer(
            'Произошла ошибка при добавлении питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.message(StateFilter(PetAddFSM.pet_name))
async def warning_incorrect_pet_name(message: Message):
    """Сработает при некорректном вводе имени питомца"""
    await message.answer(
        text='То, что Вы отправили не похоже на имя\n'
             'Пожалуйста, введите имя еще раз\n'
             'Имя может состоять из букв и цифр❗'
    )
