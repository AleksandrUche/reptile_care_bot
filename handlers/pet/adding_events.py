import logging
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from config_data.config import TIME_ZONE
from factory.callback_factory.pet_factory import EditPetCallback
from keyboards.inline_keyboards.pet import common_pet_kb
from keyboards.inline_keyboards.pet.adding_events_kb import (
    get_return_detail_view_pet_inline_kb,
)
from services.pet_services import (
    add_weight_pet,
    add_length_pet,
    add_molting_pet,
)
from services.registration_services import get_user
from services.utils import parse_date
from states.pet_states import (
    PetEditWeightFSM,
    PetEditLengthFSM,
    PetEditMoltingFSM,
)

logger = logging.getLogger(__name__)
router = Router(name='adding_events')


@router.callback_query(EditPetCallback.filter(F.field == 'weight'))
async def add_pet_weight_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для добавления веса питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='Вес питомца\n'
             '<b>Введите вес питомца:</b>',
        reply_markup=common_pet_kb.menu_add_pet,
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
        date_now = datetime.now().replace(tzinfo=timezone.utc)
        user = await get_user(message.from_user.id, session)
        if not user.tz_region:
            await message.answer(
                'Не установлен часовой пояс. Установите часовой пояс в профиле'
            )
            return
        date_tz_user = date_now.replace(tzinfo=ZoneInfo(user.tz_region))

        add_weight = await add_weight_pet(
            state_data['pet_id'], weight, date_tz_user, session
        )
    except ValueError:
        await message.answer(
            'Масса может состоять из цифр и знаков разделения❗\n'
            'Например: 25,7'
        )
    except Exception as e:
        logger.error(
            f'Ошибка при добавлении массы питомца pet_id: {state_data["pet_id"]}. {e}',
            exc_info=True
        )
    else:
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
        reply_markup=common_pet_kb.menu_add_pet,
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
        date_now = datetime.now().replace(tzinfo=timezone.utc)
        user = await get_user(message.from_user.id, session)
        if not user.tz_region:
            await message.answer(
                'Не установлен часовой пояс. Установите часовой пояс в профиле'
            )
            return
        date_tz_user = date_now.replace(tzinfo=ZoneInfo(user.tz_region))
        add_length = await add_length_pet(
            state_data['pet_id'], length, date_tz_user, session
        )
    except ValueError:
        await message.answer(
            'Длина может состоять из цифр и знаков разделения❗\n'
            'Например: 25,7'
        )
    except Exception as e:
        logger.error(
            f'Ошибка при добавлении длины питомца pet_id: {state_data["pet_id"]}. {e}',
            exc_info=True
        )
    else:
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


@router.callback_query(EditPetCallback.filter(F.field == 'molting'))
async def add_pet_molting_handler(
    callback: CallbackQuery,
    callback_data: EditPetCallback,
    state: FSMContext,
):
    """Обработчик для добавления даты линьки питомца."""
    await callback.answer()
    await  callback.message.edit_text(
        text='Добавление даты линьки питомца\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ</b>\n'
             'Разделитель может быть: ".", ",", "пробел" и "/"',
        reply_markup=common_pet_kb.menu_add_pet,
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
    await state.set_state(PetEditMoltingFSM.pet_molting)


@router.message(StateFilter(PetEditMoltingFSM.pet_molting))
async def process_add_molting_pet(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление даты линьки питомца."""
    try:
        user = await get_user(message.from_user.id, session)
        date = parse_date(message.text)
        user_tz = ZoneInfo(user.tz_region)
        date_molting = date.replace(tzinfo=user_tz)
        await state.update_data(date_molting=date_molting)

        state_data = await state.get_data()
        edit_pet = await add_molting_pet(
            state_data['pet_id'], state_data['date_molting'], session
        )
        inline_back_kb = await get_return_detail_view_pet_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
    except ValueError:
        await message.answer('Неверный формат даты. Введите дату в формате ДД.ММ.ГГГГ.')
    else:
        if edit_pet:
            await message.answer(
                '✅ Добавлена дата линьки питомца: '
                f'"{date_molting.strftime("%d.%m.%y")}".',
                reply_markup=inline_back_kb,
            )
        else:
            await message.answer(
                'Произошла ошибка при добавлении даты линьки питомца!\n'
                'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
            )
        await state.clear()
