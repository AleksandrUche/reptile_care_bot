import logging
from datetime import datetime, tzinfo

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import (
    EditPetCallback,
    AddSheduleFeedingsCallback,
)
from keyboards.keyboard_utils.inline_kb_utils import (
    get_return_detail_view_pet_inline_kb,
    get_add_shedule_feedings_inline_kb,
    get_select_shedule_feedings_clear_state_inline_kb,
)
from services.pet_services import add_feeding_shedule, time_zone_is_not_set, \
    add_group_feeding_shedule
from services.registration_services import get_user
from services.utils import parse_date, parse_time
from states.pet_states import FeedingSingleFSM, FeedingGroupFSM

logger = logging.getLogger(__name__)
router = Router(name='feeding_shedule_pet')


@router.callback_query(AddSheduleFeedingsCallback.filter(F.action == 'menu'))
async def menu_feeding_schedule_handler(
    callback: CallbackQuery, callback_data: AddSheduleFeedingsCallback,
):
    await callback.answer()

    inline_kb = await get_add_shedule_feedings_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await  callback.message.edit_text(
        text='Добавление графика кормлений\n'
             'Варианты добавления кормлений:\n\n'
             '<b>1 вариант</b> — одиночное добавление, добавляется одно запланированное кормление.\n\n'
             '<b>2 вариант</b> — график, например каждые 4 дня и количество повторений.\n\n'
             '<b>3 вариант</b> — похож на второй вариант, но добавляется описание, например, '
             'чередование: 3 кормления с кальцием, одно с витаминами и т.д.\n\n'
             '<b>4 вариант</b> — каждый день и количество запланированных дней.\n\n',
        reply_markup=inline_kb,
    )


@router.callback_query(AddSheduleFeedingsCallback.filter(F.action == 'single_addition'))
async def add_single_feeding_schedule_handler(
    callback: CallbackQuery, callback_data: EditPetCallback, state: FSMContext,
):
    """Обработчик для добавления одной даты кормления"""
    await callback.answer()
    await state.set_state(FeedingSingleFSM.date)
    inline_kb = await get_select_shedule_feedings_clear_state_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await  callback.message.edit_text(
        text='Добавление одного запланированного дня кормления\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ</b>\n'
             'Разделитель может быть: ".", ",", "пробел" и "/"',
        reply_markup=inline_kb
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )


@router.message(StateFilter(FeedingSingleFSM.date))
async def process_add_single_date_feeding(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление даты кормления."""
    user = await get_user(message.from_user.id, session)
    user_timezone = tzinfo(user.tz_region)

    if not user_timezone:
        await time_zone_is_not_set(message, state)
        return

    try:
        date = parse_date(message.text)
        date_feeding = date.replace(tzinfo=user_timezone).date()
        await state.update_data(date=date_feeding)
    except ValueError:
        await message.answer(
            'Неверный формат даты.\n Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.'
        )
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Введите время в формате ЧЧ:ММ.\n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
                 'Разделитель может быть: ":", ".", ",", "пробел" и "/"',
            reply_markup=inline_back_kb
        )
        await state.set_state(FeedingSingleFSM.time)


@router.message(StateFilter(FeedingSingleFSM.time))
async def process_add_single_time_feeding(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление времени кормления."""
    try:
        time_feeding = parse_time(message.text)
        await state.update_data(time=time_feeding)
    except ValueError:
        await message.answer('Неверный формат времени. Введите время в формате ЧЧ:ММ.')
    else:
        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])

        add_feeding = await add_feeding_shedule(
            state_data['pet_id'], date_time, session,
        )
        inline_back_kb = await get_return_detail_view_pet_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        if add_feeding:
            await message.answer(
                "Запланированное кормление добавлено\n"
                f"\"{date_time.strftime('%d.%m.%Y %H:%M')}\".\n"
                'Вам придет уведомление в указанное время.',
                reply_markup=inline_back_kb,
            )
        else:
            await message.answer(
                'Произошла ошибка при добавлении даты запланированного кормления питомца!\n'
                'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
            )
        await state.clear()
    await state.clear()


@router.callback_query(AddSheduleFeedingsCallback.filter(F.action == 'group_addition'))
async def add_group_feedings_schedule_handler(
    callback: CallbackQuery, callback_data: EditPetCallback, state: FSMContext,
):
    """
    Обработчик для добавления группы дат кормлений
    Принимает date, time, offset, repeat
    """
    await callback.answer()
    inline_kb = await get_select_shedule_feedings_clear_state_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await  callback.message.edit_text(
        text='Добавление графика кормлений.\n\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n'
             '<b>Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.</b>\n'
             'Разделитель может быть: ".", ",", "пробел" и "/".\n',
        reply_markup=inline_kb
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id
    )
    await state.set_state(FeedingGroupFSM.date)


@router.message(StateFilter(FeedingGroupFSM.date))
async def process_add_group_feeding_start_date(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление даты кормлений для добавления группы кормлений."""
    user = await get_user(message.from_user.id, session)
    user_timezone = tzinfo(user.tz_region)

    if not user_timezone:
        await time_zone_is_not_set(message, state)
        return

    try:
        date = parse_date(message.text)
        date_feeding = date.replace(tzinfo=user_timezone).date()
        await state.update_data(date=date_feeding)
    except ValueError:
        await message.answer(
            'Неверный формат даты.\n Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.'
        )
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Введите время в формате ЧЧ:ММ.\n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
                 'Разделитель может быть: ":", ".", ",", "пробел" и "/".',
            reply_markup=inline_back_kb
        )
        await state.set_state(FeedingGroupFSM.time)


@router.message(StateFilter(FeedingGroupFSM.time))
async def process_add_group_time_feeding(message: Message, state: FSMContext):
    """Добавление времени кормления."""
    try:
        time_feeding = parse_time(message.text)
        await state.update_data(time=time_feeding)
    except ValueError:
        await message.answer('Неверный формат времени. Введите время в формате ЧЧ:ММ.')
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Введите, через сколько дней будет повторное кормление.\n\n'
                 'Например: если начало графика 01.04.25, задаем повторное кормление '
                 'на 4-й день, значит, повторное кормление будет 05.04.25 (кормление '
                 'на 4-й день, значит, три дня голодовки).\n\n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingGroupFSM.offset)


@router.message(StateFilter(FeedingGroupFSM.offset), F.text.isdigit())
async def process_add_group_feeding_offset(message: Message, state: FSMContext):
    """Добавление интервала кормлений при групповом добавлении."""
    try:
        await state.update_data(offset=message.text)
    except ValueError:
        await message.answer('Произошла ошибка, повторите еще раз.')
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Введите количество повторений.\n\n'
                 'В расписание будет внесено указанное количество дат '
                 'c ранее указанным интервалом.\n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingGroupFSM.repeat)


@router.message(StateFilter(FeedingGroupFSM.offset))
async def warning_incorrect_group_offset_feeding(message: Message):
    """Сработает при некорректном вводе интервала кормления"""
    await message.answer(
        text='То, что Вы отправили не похоже на интервал кормлений.\n'
             'Пожалуйста, введите интервал еще раз, он может состоять только из цифр❗'
    )


@router.message(StateFilter(FeedingGroupFSM.repeat), F.text.isdigit())
async def process_add_group_feeding_repeat(
    message: Message, state: FSMContext, session: AsyncSession):
    """Добавление повторения кормлений при групповом добавлении."""
    try:
        await state.update_data(repeat=message.text)
        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])
        await add_group_feeding_shedule(
            state_data['pet_id'],
            date_time,
            int(state_data['offset']),
            int(state_data['repeat']),
            session,
        )
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='График кормлений успешно добавлен ✅',
            reply_markup=inline_back_kb,
        )
        await state.clear()


@router.message(StateFilter(FeedingGroupFSM.repeat))
async def warning_incorrect_group_repeat_feeding(message: Message):
    """Сработает при некорректном вводе повторений кормлений"""
    await message.answer(
        text='То, что Вы отправили не похоже на количество повторений кормления.\n'
             'Пожалуйста, повторите еще раз, допускаются только цифры❗'
    )
