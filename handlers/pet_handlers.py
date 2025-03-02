import logging

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import (
    PaginationCallback,
    PetsCallback,
    EditPetCallback,
    DeletePetCallback,
)
from filters.pet_filters import is_alnum_with_spaces
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils.inline_kb_utils import (
    show_pets_page_inline_kb,
    get_edit_pet_inline_kb,
    get_delete_pet_inline_kb,
)
from services.pet_services import (
    add_pet,
    get_my_companies_and_pets,
    get_pet,
    edit_pet_value,
    delete_pet,
)
from states.pet_states import PetAddFSM, PetEditNameFSM, PetEditMorphFSM

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
            reply_markup=inline_keyboards.main_menu_pets,
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


@router.callback_query(
    F.data.in_({'my_pets_list', 'back_to_all_pets'}), StateFilter(default_state)
)
async def get_all_pets_handler(callback: CallbackQuery, session: AsyncSession):
    """Просмотр всех питомцев"""
    await callback.answer()
    # сделать сохранение питомцев в кеше для исключения повторных запросов при пагинации
    pets_and_company = await get_my_companies_and_pets(callback.from_user.id, session)

    pets = []
    for company in pets_and_company:
        pets.extend(company.pets)
    inline_kb = await show_pets_page_inline_kb(pets=pets, page=0)

    await callback.message.edit_text(
        text='🦎<b>Все питомцы:</b>\n\n'
             f'Количество питомцев: {len(pets)}',
        reply_markup=inline_kb,
    )


@router.callback_query(PaginationCallback.filter(F.action == 'next'))
async def next_page_my_pets_handler(
    callback: CallbackQuery,
    callback_data: PaginationCallback,
    session: AsyncSession
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
        text='🦎<b>Все питомцы:</b>\n\n'
             f'Количество питомцев: {len(pets)}',
        reply_markup=reply_markup,
    )


@router.callback_query(PaginationCallback.filter(F.action == 'prev'))
async def prev_page_my_pets_handler(
    callback: CallbackQuery,
    callback_data: PaginationCallback,
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
        text='🦎<b>Все питомцы:</b>\n\n'
             f'Количество питомцев: {len(pets)}',
        reply_markup=reply_markup,
    )


@router.callback_query(PetsCallback.filter())
async def detail_pets_handler(
    callback: CallbackQuery, callback_data: PetsCallback, session: AsyncSession
):
    """Обработчик для детального просмотра питомца"""
    await callback.answer()

    pet = await get_pet(
        callback_data.id,
        callback_data.company_id,
        callback_data.group_id,
        session
    )

    inline_kb = await get_edit_pet_inline_kb(pet['pet'].id, pet['pet'].name)

    await callback.message.edit_text(
        text=f'Имя питомца: {pet["pet"].name}\n\n'
             f'Морфа: {pet["pet"].morph}\n'
             f'Вид: {pet["pet"].view}\n'
             f'Пол: {pet["pet"].gender.value}\n'
             f'Вес: {pet["latest_weight"]}\n'
             f'Длина: {pet["latest_length"]}\n'
             f'Линька: {pet["latest_molting_date"]}\n'
             f'Компания: {pet["company_name"]}\n'
             f'Группа: {pet["group_name"]}\n'
             f'Дата рождения: {pet["pet"].date_birth}\n'
             f'Дата приобретения: {pet["pet"].date_purchase}\n',
        reply_markup=inline_kb
    )


@router.callback_query(EditPetCallback.filter(F.field == 'name'))
async def edit_pet_name_handler(
    callback: CallbackQuery, callback_data: EditPetCallback, state: FSMContext,
):
    """Обработчик для изменения имени питомца."""
    await callback.answer()
    await callback.message.edit_text(
        text='🦎Изменение имени питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите новое имя питомца:</b>',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.update_data(pet_id=callback_data.pet_id)
    await state.set_state(PetEditNameFSM.pet_name)


@router.message(StateFilter(PetEditNameFSM.pet_name), F.text.func(is_alnum_with_spaces))
async def process_edit_pet_name(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Изменение имени питомца."""
    await state.update_data(pet_name=message.text)
    state_data = await state.get_data()

    edit_pet = await edit_pet_value(
        state_data['pet_id'], 'name', state_data['pet_name'], session
    )
    if edit_pet:
        await message.answer(
            f"Имя питомца изменено на \"{state_data['pet_name']}\".",
            reply_markup=inline_keyboards.main_menu_pets,
        )
    else:
        await message.answer(
            'Произошла ошибка при изменении имени питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.message(StateFilter(PetEditNameFSM.pet_name))
async def warning_incorrect_value(message: Message):
    """Сработает при некорректном редактировании питомца"""
    await message.answer(
        text='То, что Вы отправили не похоже на имя\n'
             'Пожалуйста, введите имя еще раз\n'
             'Имя может состоять из букв и цифр❗'

    )


@router.callback_query(EditPetCallback.filter(F.field == 'morph'))
async def edit_pet_morph_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для изменения морфы питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Изменение морфы питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите морфу питомца:</b>',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.update_data(pet_id=callback_data.pet_id)
    await state.set_state(PetEditMorphFSM.pet_morph)


@router.message(StateFilter(PetEditMorphFSM.pet_morph))
async def process_edit_pet_morph(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Изменение морфы питомца."""
    await state.update_data(pet_morph=message.text)
    state_data = await state.get_data()

    edit_pet = await edit_pet_value(
        state_data['pet_id'], 'morph', state_data['pet_morph'], session
    )
    if edit_pet:
        await message.answer(
            f"Теперь морфа питомца: \"{state_data['pet_morph']}\".",
            reply_markup=inline_keyboards.main_menu_pets,
        )
    else:
        await message.answer(
            'Произошла ошибка при изменении морфы питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.callback_query(DeletePetCallback.filter(F.action == 'menu'))
async def delete_pet_handler(callback: CallbackQuery, callback_data: DeletePetCallback):
    """Обработчик для удаления питомца."""
    await callback.answer()

    inline_kb = await get_delete_pet_inline_kb(callback_data.pet_id, callback_data.pet_name)

    await callback.message.edit_text(
        f"<b>Вы уверены, что хотите удалить питомца \"{callback_data.pet_name}\"?</b>\n",
        reply_markup=inline_kb,
    )


@router.callback_query(DeletePetCallback.filter(F.action == 'delete'))
async def process_delete_confirm_pet(
    callback: CallbackQuery, callback_data: DeletePetCallback, session: AsyncSession
):
    """Подтверждение Удаления питомца."""
    del_pet = await delete_pet(callback_data.pet_id, session)

    if del_pet:
        await callback.message.edit_text(
            f"Питомец \"{callback_data.pet_name}\" был удален ✔",
            reply_markup=inline_keyboards.main_menu_pets,
        )
    else:
        await callback.message.answer(
            'Произошла ошибка при удалении питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )


@router.callback_query(DeletePetCallback.filter(F.action == 'cencel'))
async def process_undo_delete_pet(
    callback: CallbackQuery, callback_data: DeletePetCallback
):
    """Отмена удаления питомца"""
    ...


@router.callback_query(F.data == 'cancel_state', ~StateFilter(default_state))
async def cancel_state_handler(message: Message, state: FSMContext):
    """Выходит из машины состояния"""
    await state.clear()
    await message.answer("Действие отменено.")
