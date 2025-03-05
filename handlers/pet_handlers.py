import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import TIME_ZONE
from factory.callback_factory.pet_factory import (
    PaginationCallback,
    PetsCallback,
    EditPetCallback,
    DeletePetCallback,
    GenderSelectionCallback,
)
from filters.pet_filters import is_alnum_with_spaces
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils.inline_kb_utils import (
    show_pets_page_inline_kb,
    get_edit_pet_inline_kb,
    get_delete_pet_inline_kb,
    get_gender_select_pet_inline_kb,
    get_return_detail_view_pet_inline_kb,
)
from services.pet_services import (
    add_pet,
    get_my_companies_and_pets,
    get_pet,
    edit_pet_value,
    delete_pet,
    add_weight_pet,
    add_length_pet,
)
from states.pet_states import (
    PetAddFSM,
    PetEditNameFSM,
    PetEditMorphFSM,
    PetEditViewFSM,
    PetEditBirthFSM,
    PetEditPurchaseFSM,
    PetEditWeightFSM,
    PetEditLengthFSM,
)

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
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        session
    )

    inline_kb = await get_edit_pet_inline_kb(
        pet['pet'].id, pet['pet'].name, pet['pet'].company_id, pet['pet'].group_id
    )

    date_birth = edit_date_format(pet["pet"].date_birth)
    date_purchase = edit_date_format(pet["pet"].date_purchase)
    latest_molting_date = edit_date_format(pet["latest_molting_date"])

    await callback.message.edit_text(
        text=f'Имя питомца: {pet["pet"].name}\n\n'
             f'Морфа: {pet["pet"].morph}\n'
             f'Вид: {pet["pet"].view}\n'
             f'Пол: {pet["pet"].gender.value}\n'
             f'Вес: {pet["latest_weight"]}\n'
             f'Длина: {pet["latest_length"]}\n'
             f'Линька: {latest_molting_date}\n'
             f'Компания: {pet["company_name"]}\n'
             f'Группа: {pet["group_name"]}\n'
             f'Дата рождения: {date_birth}\n'
             f'Дата приобретения: {date_purchase}\n',
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
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
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
    inline_back_kb = await get_return_detail_view_pet_inline_kb(
        state_data['pet_id'], state_data['company_id'], state_data['group_id']
    )
    if edit_pet:
        await message.answer(
            f"Имя питомца изменено на \"{state_data['pet_name']}\".",
            reply_markup=inline_back_kb,
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
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
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
    inline_back_kb = await get_return_detail_view_pet_inline_kb(
        state_data['pet_id'], state_data['company_id'], state_data['group_id']
    )
    if edit_pet:
        await message.answer(
            f"Теперь морфа питомца: \"{state_data['pet_morph']}\".",
            reply_markup=inline_back_kb,
        )
    else:
        await message.answer(
            'Произошла ошибка при изменении морфы питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.callback_query(EditPetCallback.filter(F.field == 'view'))
async def edit_pet_view_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для изменения вида питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Изменение вида питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите вид питомца:</b>',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
    await state.set_state(PetEditViewFSM.pet_view)


@router.message(StateFilter(PetEditViewFSM.pet_view))
async def process_edit_pet_view(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Изменение вида питомца."""
    await state.update_data(pet_view=message.text)
    state_data = await state.get_data()

    edit_pet = await edit_pet_value(
        state_data['pet_id'], 'view', state_data['pet_view'], session
    )
    inline_back_kb = await get_return_detail_view_pet_inline_kb(
        state_data['pet_id'], state_data['company_id'], state_data['group_id']
    )
    if edit_pet:
        await message.answer(
            f"Теперь вид питомца: \"{state_data['pet_view']}\".",
            reply_markup=inline_back_kb,
        )
    else:
        await message.answer(
            'Произошла ошибка при изменении вида питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.callback_query(EditPetCallback.filter(F.field == 'gender'))
async def edit_pet_gender_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
):
    """Обработчик для изменения пола питомца."""
    await callback.answer()

    inline_kb = await get_gender_select_pet_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await  callback.message.edit_text(
        text='🦎Изменение пола питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Выберите пол питомца:</b>',
        reply_markup=inline_kb,
    )


@router.callback_query(GenderSelectionCallback.filter())
async def process_edit_pet_gender(
    callback: CallbackQuery,
    callback_data: GenderSelectionCallback,
    session: AsyncSession,
):
    """Изменение пола питомца."""
    edit_pet = await edit_pet_value(
        callback_data.pet_id, 'gender', callback_data.action.name, session
    )
    inline_back_kb = await get_return_detail_view_pet_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    if edit_pet:
        await callback.message.edit_text(
            f"Теперь пол питомца: \"{callback_data.action.value}\".",
            reply_markup=inline_back_kb,
        )
    else:
        await callback.message.answer(
            'Произошла ошибка при изменении пола питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )


@router.callback_query(EditPetCallback.filter(F.field == 'weight'))
async def add_pet_weight_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для добавления веса питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Вес питомца\n'
             '<b>Введите вес питомца:</b>',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
    await state.set_state(PetEditWeightFSM.pet_weight)


@router.message(StateFilter(PetEditWeightFSM.pet_weight), ~F.text.isalpha())
async def process_add_weight(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление веса питомца."""
    await state.update_data(pet_weight=message.text)
    state_data = await state.get_data()
    try:
        weight = float(state_data['pet_weight'].replace(',', '.'))
    except ValueError:
        await message.answer(
            'Масса может состоять из цифр и знаков разделения❗\n'
            'Например: 25,7'
        )

    add_weight = await add_weight_pet(
        state_data['pet_id'], weight, session
    )
    inline_back_kb = await get_return_detail_view_pet_inline_kb(
        state_data['pet_id'], state_data['company_id'], state_data['group_id']
    )
    if add_weight:
        await message.answer(
            f"Масса питомца \"{state_data['pet_weight']}\" добавлена ✅.",
            reply_markup=inline_back_kb,
        )
    else:
        await message.answer(
            'Произошла ошибка при добавлении массы питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.message(StateFilter(PetEditWeightFSM.pet_weight))
async def warning_incorrect_weight(message: Message):
    """Сработает при некорректном вводе массы питомца"""
    await message.answer(
        text='То, что Вы отправили не похоже на массу\n'
             'Пожалуйста, введите массу еще раз\n'
             'Масса может состоять из цифр❗'

    )


@router.callback_query(EditPetCallback.filter(F.field == 'length'))
async def add_pet_length_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для добавления длины питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Длина питомца\n'
             '<b>Введите длину питомца:</b>',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
    await state.set_state(PetEditLengthFSM.pet_length)


@router.message(StateFilter(PetEditLengthFSM.pet_length), ~F.text.isalpha())
async def process_add_length(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление длины питомца."""
    await state.update_data(pet_length=message.text)
    state_data = await state.get_data()
    try:
        length = float(state_data['pet_length'].replace(',', '.'))
    except ValueError:
        await message.answer(
            'Длина может состоять из цифр и знаков разделения❗\n'
            'Например: 25,7'
        )

    add_length = await add_length_pet(
        state_data['pet_id'], length, session
    )
    inline_back_kb = await get_return_detail_view_pet_inline_kb(
        state_data['pet_id'], state_data['company_id'], state_data['group_id']
    )
    if add_length:
        await message.answer(
            f"Длина питомца \"{state_data['pet_length']}\" добавлена ✅.",
            reply_markup=inline_back_kb,
        )
    else:
        await message.answer(
            'Произошла ошибка при добавлении длины питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    await state.clear()


@router.message(StateFilter(PetEditLengthFSM.pet_length))
async def warning_incorrect_length(message: Message):
    """Сработает при некорректном вводе длины питомца"""
    await message.answer(
        text='То, что Вы отправили не похоже на длину\n'
             'Пожалуйста, введите длину еще раз\n'
             'Масса может состоять из цифр❗'
    )


@router.callback_query(EditPetCallback.filter(F.field == 'birth'))
async def edit_pet_birth_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для изменения даты рождения питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Изменение даты рождения питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите дату рождения питомца в формате ДД.ММ.ГГГГ:</b>',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
    await state.set_state(PetEditBirthFSM.pet_birth)


@router.message(StateFilter(PetEditBirthFSM.pet_birth))
async def process_edit_pet_birth(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Изменение даты рождения питомца."""
    try:
        date_birth = datetime.strptime(message.text, '%d.%m.%Y')
        await state.update_data(pet_birth=date_birth)
    except ValueError:
        await message.answer('Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ.')
    else:
        state_data = await state.get_data()

        edit_pet = await edit_pet_value(
            state_data['pet_id'], 'date_birth', state_data['pet_birth'], session
        )
        inline_back_kb = await get_return_detail_view_pet_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )

        if edit_pet:
            await message.answer(
                "Теперь дата рождения питомца: "
                f"\"{date_birth.astimezone(TIME_ZONE).strftime('%d.%m.%Y')}\".",
                reply_markup=inline_back_kb,
            )
        else:
            await message.answer(
                'Произошла ошибка при изменении даты рождения питомца!\n'
                'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
            )
        await state.clear()


@router.callback_query(EditPetCallback.filter(F.field == 'purchase'))
async def edit_pet_purchase_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для изменения даты приобретения питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='🦎Изменение даты приобретения питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите дату приобретения питомца в формате ДД.ММ.ГГГГ:</b>\n',
        reply_markup=inline_keyboards.menu_add_pet,
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
    await state.set_state(PetEditPurchaseFSM.pet_purchase)


@router.message(StateFilter(PetEditPurchaseFSM.pet_purchase))
async def process_edit_purchase_birth(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Изменение даты приобретения питомца."""
    try:
        date_purchase = datetime.strptime(message.text, '%d.%m.%Y')
        await state.update_data(pet_purchase=date_purchase)
    except ValueError:
        await message.answer('Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ.')
    else:
        state_data = await state.get_data()

        edit_pet = await edit_pet_value(
            state_data['pet_id'], 'date_purchase', state_data['pet_purchase'], session
        )
        inline_back_kb = await get_return_detail_view_pet_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )

        if edit_pet:
            await message.answer(
                "Теперь дата приобретения питомца: "
                f"\"{date_purchase.astimezone(TIME_ZONE).strftime('%d.%m.%Y')}\".",
                reply_markup=inline_back_kb,
            )
        else:
            await message.answer(
                'Произошла ошибка при изменении даты приобретения питомца!\n'
                'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
            )
        await state.clear()


@router.callback_query(DeletePetCallback.filter(F.action == 'menu'))
async def delete_pet_handler(callback: CallbackQuery, callback_data: DeletePetCallback):
    """Обработчик для удаления питомца."""
    await callback.answer()

    inline_kb = await get_delete_pet_inline_kb(
        callback_data.pet_id, callback_data.pet_name
    )

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
            f"Питомец \"{callback_data.pet_name}\" был удален ✅",
            reply_markup=inline_keyboards.main_menu_pets,
        )
    else:
        await callback.message.answer(
            'Произошла ошибка при удалении питомца!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )


@router.callback_query(DeletePetCallback.filter(F.action == 'cancel'))
async def process_undo_delete_pet(
    callback: CallbackQuery, callback_data: DeletePetCallback
):
    """Отмена удаления питомца"""
    await callback.message.edit_text(
        f"Удаление питомца \"{callback_data.pet_name}\" отменено.",
        reply_markup=inline_keyboards.main_menu_pets,
    )


@router.callback_query(F.data == 'cancel_state', ~StateFilter(default_state))
async def cancel_state_handler(message: Message, state: FSMContext):
    """Выходит из машины состояния"""
    await state.clear()
    await message.answer("Действие отменено.")
