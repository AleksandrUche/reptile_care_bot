import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import (
    AddSheduleFeedingsCallback,
    ConfirmFeedingEventsCallback,
)
from keyboards.keyboard_utils.inline_kb_utils import (
    get_add_shedule_feedings_inline_kb,
    get_select_shedule_feedings_clear_state_inline_kb,
    get_select_shedule_feedings_inline_kb,
)
from services.pet_services import (
    add_feeding_shedule,
    time_zone_is_not_set,
    add_group_feeding_shedule,
    add_group_feeding_and_description_shedule,
    add_feeding_pet_date,
    change_reminder_feeding_shedule,
    get_feeding_shedule,
)
from services.registration_services import get_user
from services.utils import parse_date, parse_time
from states.pet_states import (
    FeedingSingleFSM,
    FeedingGroupFSM,
    FeedingGroupAndDescriptionFSM,
)

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
    callback: CallbackQuery,
    callback_data: AddSheduleFeedingsCallback,
    state: FSMContext,
    session: AsyncSession,
):
    """Обработчик для добавления одной даты кормления"""
    await callback.answer()
    # Проверка тайм зоны пользователя
    user = await get_user(callback.from_user.id, session)
    if not user.tz_region:
        await time_zone_is_not_set(callback, callback_data)
        return
    user_timezone = ZoneInfo(user.tz_region)

    await state.set_state(FeedingSingleFSM.date)
    inline_kb = await get_select_shedule_feedings_clear_state_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await callback.message.edit_text(
        text='Добавление одного запланированного дня кормления\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ</b>\n'
             'Разделитель может быть: ".", ",", "пробел" и "/"',
        reply_markup=inline_kb
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        user_timezone=user_timezone,
    )


@router.message(StateFilter(FeedingSingleFSM.date))
async def process_add_single_date_feeding(message: Message, state: FSMContext):
    """Добавление даты кормления."""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)
        date_feeding = date.replace(tzinfo=state_data['user_timezone']).date()
        await state.update_data(date=date_feeding)
    except ValueError:
        await message.answer(
            'Неверный формат даты.\n Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.'
        )
    else:
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
        inline_back_kb = await get_select_shedule_feedings_inline_kb(
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
    callback: CallbackQuery,
    callback_data: AddSheduleFeedingsCallback,
    state: FSMContext,
    session: AsyncSession,
):
    """
    Обработчик для добавления группы дат кормлений
    Принимает date, time, offset, repeat
    """
    await callback.answer()
    # Проверка тайм зоны пользователя
    user = await get_user(callback.from_user.id, session)
    if not user.tz_region:
        await time_zone_is_not_set(callback, callback_data)
        return
    user_timezone = ZoneInfo(user.tz_region)

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
        group_id=callback_data.group_id,
        user_timezone=user_timezone,
    )
    await state.set_state(FeedingGroupFSM.date)


@router.message(StateFilter(FeedingGroupFSM.date))
async def process_add_group_feeding_start_date(message: Message, state: FSMContext):
    """Добавление даты кормлений для добавления группы кормлений."""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)
        date_feeding = date.replace(tzinfo=state_data['user_timezone']).date()
        await state.update_data(date=date_feeding)
    except ValueError:
        await message.answer(
            'Неверный формат даты.\n Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.'
        )
    else:
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
        inline_back_kb = await get_select_shedule_feedings_inline_kb(
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


@router.callback_query(AddSheduleFeedingsCallback.filter(
    F.action == 'group_addition_and_description')
)
async def add_group_feedings_schedule_with_description_handler(
    callback: CallbackQuery,
    callback_data: AddSheduleFeedingsCallback,
    state: FSMContext,
    session: AsyncSession,
):
    """
    Обработчик для добавления группы дат кормлений
    Принимает date, time, offset, repeat,
    """
    # Проверка тайм зоны пользователя
    user = await get_user(callback.from_user.id, session)
    if not user.tz_region:
        await time_zone_is_not_set(callback, callback_data)
        return
    user_timezone = ZoneInfo(user.tz_region)

    await callback.answer()
    inline_kb = await get_select_shedule_feedings_clear_state_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await  callback.message.edit_text(
        text='Добавление графика кормлений с описаниям.\n\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n'
             '<b>Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.</b>\n'
             'Разделитель может быть: ".", ",", "пробел" и "/".\n',
        reply_markup=inline_kb
    )
    await state.update_data(
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        user_timezone=user_timezone,
    )
    await state.set_state(FeedingGroupAndDescriptionFSM.date)


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.date))
async def process_add_start_date_group_feeding_with_description(
    message: Message, state: FSMContext
):
    """Добавление даты кормлений для добавления группы кормлений с описаниями."""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)
        date_feeding = date.replace(tzinfo=state_data['user_timezone']).date()
        await state.update_data(date=date_feeding)
    except ValueError:
        await message.answer(
            'Неверный формат даты.\n Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.'
        )
    else:
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Введите время в формате ЧЧ:ММ.\n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
                 'Разделитель может быть: ":", ".", ",", "пробел" и "/".',
            reply_markup=inline_back_kb
        )
        await state.set_state(FeedingGroupAndDescriptionFSM.time)


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.time))
async def process_add_time_group_feeding_with_description(
    message: Message, state: FSMContext
):
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
        await state.set_state(FeedingGroupAndDescriptionFSM.offset)


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.offset), F.text.isdigit())
async def process_add_offset_group_feeding_with_description(
    message: Message, state: FSMContext
):
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
        await state.set_state(FeedingGroupAndDescriptionFSM.repeat)


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.offset))
async def warning_incorrect_offset_group_feeding_with_description(message: Message):
    """Сработает при некорректном вводе интервала кормления"""
    await message.answer(
        text='То, что Вы отправили не похоже на интервал кормлений.\n'
             'Пожалуйста, введите интервал еще раз, он может состоять только из цифр❗'
    )


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.repeat), F.text.isdigit())
async def process_add_repeat_group_feeding_with_description(
    message: Message, state: FSMContext
):
    """Добавление повторения кормлений при групповом добавлении."""
    try:
        await state.update_data(repeat=message.text)
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Напишите первое описание для кормлений, на следующем шаге Вы укажете '
                 'количество повторений данного описания.\n\n'
                 'Например, Вам необходимо придерживаться графика кормлений: три раза '
                 'подряд с добавкой «кальций» и, например, один с «витаминами» и т.д. '
                 'на данном шаге указываем «с кальцием»\n\n'
                 'Добавление второго описания и его повторение будет через один шаг\n',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingGroupAndDescriptionFSM.description_1)


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.repeat))
async def warning_incorrect_repeat_group_feeding_with_description(message: Message):
    """Сработает при некорректном вводе повторений кормлений"""
    await message.answer(
        text='То, что Вы отправили не похоже на количество повторений кормления.\n'
             'Пожалуйста, повторите еще раз, допускаются только цифры❗'
    )


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.description_1))
async def process_add_description_1_group_feeding_with_description(
    message: Message, state: FSMContext
):
    """Добавление первого описания кормлений при групповом добавлении с описанием."""
    try:
        await state.update_data(description_1=message.text)
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Укажите количество повторений первого описания.',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingGroupAndDescriptionFSM.repeat_description_1)


@router.message(
    StateFilter(FeedingGroupAndDescriptionFSM.repeat_description_1),
    F.text.isdigit()
)
async def process_add_repeat_description_1_group_feeding_with_description(
    message: Message, state: FSMContext
):
    """Добавление повторений первого описания при групповом добавлении с описанием."""
    try:
        await state.update_data(repeat_description_1=message.text)
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Напишите второе описание для кормлений, на следующем шаге Вы укажете '
                 'количество повторений данного описания.\n\n'
                 'Например, Вам необходимо придерживаться графика кормлений: три раза '
                 'подряд с добавкой «кальций» и, например, один с «витаминами» и т.д. '
                 'на данном шаге указываем «с витаминами»\n\n',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingGroupAndDescriptionFSM.description_2)


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.repeat_description_1))
async def warning_incorrect_repeat_description_1_group_feeding_with_description(
    message: Message
):
    """Сработает при некорректном вводе повторений первого описания"""
    await message.answer(
        text='То, что Вы отправили не похоже на количество повторений первого описания.\n'
             'Пожалуйста, повторите еще раз, допускаются только цифры❗'
    )


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.description_2))
async def process_add_description_2_group_feeding_with_description(
    message: Message, state: FSMContext
):
    """Добавление второго описания кормлений при групповом добавлении с описанием."""
    try:
        await state.update_data(description_2=message.text)
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='Укажите количество повторений второго описания.',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingGroupAndDescriptionFSM.repeat_description_2)


@router.message(
    StateFilter(FeedingGroupAndDescriptionFSM.repeat_description_2),
    F.text.isdigit()
)
async def process_add_repeat_description_2_group_feeding_with_description(
    message: Message, state: FSMContext, session: AsyncSession
):
    """
    Добавление повторений второго описания при групповом добавлении с описанием и
    финишная работа со всеми данными.
    """
    try:
        await state.update_data(repeat_description_2=message.text)
        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])
        await add_group_feeding_and_description_shedule(
            state_data['pet_id'],
            date_time,
            int(state_data['offset']),
            int(state_data['repeat']),
            state_data['description_1'],
            int(state_data['repeat_description_1']),
            state_data['description_2'],
            int(state_data['repeat_description_2']),
            session,
        )
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            text='График кормлений с описаниями успешно добавлен ✅',
            reply_markup=inline_back_kb,
        )
        await state.clear()


@router.message(StateFilter(FeedingGroupAndDescriptionFSM.repeat_description_2))
async def warning_incorrect_repeat_description_2_group_feeding_with_description(
    message: Message
):
    """Сработает при некорректном вводе повторений второго описания"""
    await message.answer(
        text='То, что Вы отправили не похоже на количество повторений второго описания.\n'
             'Пожалуйста, повторите еще раз, допускаются только цифры❗'
    )


@router.callback_query(ConfirmFeedingEventsCallback.filter(F.action == 'approve'))
async def confirmation_feeding_event_handler(
    callback: CallbackQuery,
    callback_data: ConfirmFeedingEventsCallback,
    session: AsyncSession,
):
    """
    Обработчик для подтверждения кормления по графику из уведомления
    """
    try:
        feeding_event = await get_feeding_shedule(
            callback_data.event_feeding_id, session
        )
        await add_feeding_pet_date(
            callback_data.pet_id, session, feeding_event.description)
        await change_reminder_feeding_shedule(
            callback_data.event_feeding_id, callback_data.pet_id, False, session,
        )
    except Exception as e:
        logger.error(f'Не удалось подтвердить кормление из уведомления: {e}',
                     exc_info=True)
        await callback.answer(
            text=f'Не удалось подтвердить кормление «{callback_data.pet_name}»❗\n'
                 f'Попробуйте еще раз.',
            show_alert=True,
        )
    else:
        await callback.answer(
            text=f'Питомец «{callback_data.pet_name}» покормлен ✅\n'
                 'Кормление добавлено в историю',
            show_alert=True,
        )


@router.callback_query(ConfirmFeedingEventsCallback.filter(F.action == 'remind'))
async def remind_feeding_event_handler(
    callback: CallbackQuery,
    callback_data: ConfirmFeedingEventsCallback,
    session: AsyncSession
):
    """
    Обработчик для подтверждения "повторного" напоминания кормления из графика
    """
    try:
        await change_reminder_feeding_shedule(
            callback_data.event_feeding_id, callback_data.pet_id, True, session,
        )
    except Exception as e:
        logger.error(f'Не удалось запланировать повторное уведомление кормления: {e}',
                     exc_info=True)
        await callback.answer(
            text=f'Не удалось запланировать повторное уведомление кормления для «{callback_data.pet_name}»❗\n'
                 f'Попробуйте еще раз.',
            show_alert=True,
        )
    else:
        await callback.answer(
            text='Запланировано повторное напоминание о кормлении '
                 f'«{callback_data.pet_name}», уведомление придет через 1 час ✅',
            show_alert=True,
        )


@router.callback_query(ConfirmFeedingEventsCallback.filter(F.action == 'cancel'))
async def cancel_remind_feeding_event_handler(
    callback: CallbackQuery,
    callback_data: ConfirmFeedingEventsCallback,
    session: AsyncSession,
):
    """
    Обработчик для отмены повторного уведомления о кормлении bp
    """
    try:
        await change_reminder_feeding_shedule(
            callback_data.event_feeding_id, callback_data.pet_id, False, session,
        )
    except Exception as e:
        logger.error(f'Не удалось отменить повторное уведомление: {e}', exc_info=True)
        await callback.answer(
            text='Не удалось отменить повторное напоминание о '
                 f'кормлении «{callback_data.pet_name}»!',
            show_alert=True,
        )
    else:
        await callback.answer(
            text=f'Повторное напоминание для «{callback_data.pet_name}» отменено❗',
            show_alert=True,
        )
