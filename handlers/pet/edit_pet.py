import logging
from datetime import datetime

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import TIME_ZONE
from factory.callback_factory.pet_factory import (
    EditPetCallback,
    GenderSelectionCallback,
)
from filters.pet_filters import is_alnum_with_spaces
from keyboards.inline_keyboards import inline_keyboards
from keyboards.keyboard_utils.inline_kb_utils import (
    get_edit_pet_inline_kb,
    get_gender_select_pet_inline_kb,
    get_return_detail_view_pet_inline_kb,
)
from services.pet_services import edit_pet_value
from states.pet_states import (
    PetEditNameFSM,
    PetEditMorphFSM,
    PetEditViewFSM,
    PetEditBirthFSM,
    PetEditPurchaseFSM,
)

logger = logging.getLogger(__name__)
router = Router(name='edit_pet')


@router.callback_query(EditPetCallback.filter(F.field == 'all_editing_tools'))
async def detailed_editing_pet_handler(
    callback: CallbackQuery, callback_data: EditPetCallback
):
    """Обработчик для детального просмотра питомца"""
    await callback.answer()
    inline_kb = await get_edit_pet_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await callback.message.edit_reply_markup(
        reply_markup=inline_kb,
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
             '<b>Выберите пол питомца</b> 👇',
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
    await callback.message.edit_text(
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
