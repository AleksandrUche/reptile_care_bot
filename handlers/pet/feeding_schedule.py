import logging
from datetime import datetime
from zoneinfo import ZoneInfo

from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from factory.callback_factory.pet_factory import (
    SheduleFeedingsCallback,
    ConfirmFeedingEventsCallback,
    FeedingShedulePaginationCallback,
    FeedingSheduleDetailCallback,
    ChoiceDeleteFeedingShedule,
)
from keyboards.inline_keyboards.pet.feeding_schedule_kb import (
    get_menu_shedule_feedings_inline_kb,
    get_add_shedule_feedings_inline_kb,
    get_select_shedule_feedings_clear_state_inline_kb,
    get_select_shedule_feedings_inline_kb,
    show_shedule_feedings_inline_kb,
    detail_shedule_feedings_inline_kb,
    get_edit_shedule_feedings_clear_state_inline_kb,
    get_successful_edit_shedule_feedings_inline_kb,
    get_delete_feeding_shedule_inline_kb,
    no_time_zone_inline_kb,
)
from services.pet_services import (
    add_feeding_shedule,
    add_group_feeding_shedule,
    add_group_feeding_and_description_shedule,
    add_feeding_pet_date,
    change_reminder_feeding_shedule,
    get_feeding_shedule,
    get_planned_pet_feeding_schedule,
    edit_feeding_shedule,
    delete_feeding_shedule,
)
from services.registration_services import get_user
from services.utils import parse_date, parse_time
from states.pet_states import (
    FeedingSingleFSM,
    FeedingGroupFSM,
    FeedingGroupAndDescriptionFSM,
    FeedingEveryDayFSM,
    FeedingEditEventFSM,
)

logger = logging.getLogger(__name__)
router = Router(name='feeding_shedule_pet')


@router.callback_query(SheduleFeedingsCallback.filter(F.action == 'menu'))
async def menu_feeding_schedule_handler(
    callback: CallbackQuery, callback_data: SheduleFeedingsCallback,
):
    """Главное меню взаимодействия с графиками"""
    await callback.answer()
    inline_kb = await get_menu_shedule_feedings_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await callback.message.edit_text(
        text='Меню взаимодействия с графиками кормлений\n',
        reply_markup=inline_kb,
    )


async def time_zone_is_not_set(
    callback: CallbackQuery, callback_data: SheduleFeedingsCallback
):
    """Отправляет в чат сообщение с инлайн клавой для установки таймзоны"""
    inline_kb = await no_time_zone_inline_kb(
        callback.from_user.id,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
    )
    await callback.message.answer(
        text='Временная зона не установлена.\n'
             'Пожалуйста, укажите её в настройках профиля.',
        reply_markup=inline_kb,
    )


@router.callback_query(SheduleFeedingsCallback.filter(F.action == 'add_shedule'))
async def choice_feeding_schedule_handler(
    callback: CallbackQuery, callback_data: SheduleFeedingsCallback,
):
    """Выбор вариантов добавления графика"""
    await callback.answer()
    inline_kb = await get_add_shedule_feedings_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await callback.message.edit_text(
        text='Добавление графика кормлений\n'
             'Варианты добавления кормлений:\n\n'
             '<b>1 вариант</b> — одиночное добавление, добавляется одно запланированное кормление.\n\n'
             '<b>2 вариант</b> — график, например каждые 4 дня и количество повторений.\n\n'
             '<b>3 вариант</b> — похож на второй вариант, но добавляется описание, например, '
             'чередование: 3 кормления с кальцием, одно с витаминами и т.д.\n\n'
             '<b>4 вариант</b> — каждый день и количество запланированных дней.\n\n',
        reply_markup=inline_kb,
    )


@router.callback_query(SheduleFeedingsCallback.filter(F.action == 'single_addition'))
async def add_single_feeding_schedule_handler(
    callback: CallbackQuery,
    callback_data: SheduleFeedingsCallback,
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
async def process_add_date_single_feeding(message: Message, state: FSMContext):
    """Добавление даты кормления."""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)
        date_feeding = date.replace(tzinfo=state_data['user_timezone']).date()
        await state.update_data(date=date_feeding)

        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
    except ValueError:
        await message.answer(
            'Неверный формат даты.\n Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.'
        )
    else:
        await message.answer(
            text='Введите время в формате ЧЧ:ММ.\n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
                 'Разделитель может быть: ":", ".", ",", "пробел" и "/"',
            reply_markup=inline_back_kb
        )
        await state.set_state(FeedingSingleFSM.time)


@router.message(StateFilter(FeedingSingleFSM.time))
async def process_add_time_single_feeding(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление времени кормления."""
    try:
        time_feeding = parse_time(message.text)
        await state.update_data(time=time_feeding)

        state_data = await state.get_data()
        inline_back_kb = await get_select_shedule_feedings_clear_state_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
    except ValueError:
        await message.answer('Неверный формат времени. Введите время в формате ЧЧ:ММ.')
    else:
        await message.answer(
            'Заполните описание\n\n'
            'Если в этом нет необходимости, можно пропустить этот шаг, отправив любой '
            'символ.',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingSingleFSM.description)


@router.message(StateFilter(FeedingSingleFSM.description))
async def process_add_description_single_feeding(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Добавление описания кормления при одиночном добавлении."""
    try:
        await state.update_data(description=message.text)
        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])
        await add_feeding_shedule(
            state_data['pet_id'], date_time, session, state_data['description']
        )
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        inline_back_kb = await get_select_shedule_feedings_inline_kb(
            state_data['pet_id'], state_data['company_id'], state_data['group_id']
        )
        await message.answer(
            "Запланированное кормление добавлено ✅\n"
            f"\"{date_time.strftime('%d.%m.%Y %H:%M')}\".\n"
            'Вам придет уведомление в указанное время.',
            reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(SheduleFeedingsCallback.filter(F.action == 'group_addition'))
async def add_group_feedings_schedule_handler(
    callback: CallbackQuery,
    callback_data: SheduleFeedingsCallback,
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
async def process_add_offset_group_feeding(message: Message, state: FSMContext):
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
async def warning_incorrect_offset_group_feeding(message: Message):
    """Сработает при некорректном вводе интервала кормления"""
    await message.answer(
        text='То, что Вы отправили не похоже на интервал кормлений.\n'
             'Пожалуйста, введите интервал еще раз, он может состоять только из цифр❗'
    )


@router.message(StateFilter(FeedingGroupFSM.repeat), F.text.isdigit())
async def process_add_repeat_group_feeding(
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
async def warning_incorrect_repeat_group_feeding(message: Message):
    """Сработает при некорректном вводе повторений кормлений"""
    await message.answer(
        text='То, что Вы отправили не похоже на количество повторений кормления.\n'
             'Пожалуйста, повторите еще раз, допускаются только цифры❗'
    )


@router.callback_query(SheduleFeedingsCallback.filter(
    F.action == 'group_addition_and_description')
)
async def add_group_feedings_schedule_with_description_handler(
    callback: CallbackQuery,
    callback_data: SheduleFeedingsCallback,
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


@router.callback_query(SheduleFeedingsCallback.filter(F.action == 'every_day'))
async def add_group_feedings_every_day_schedule_handler(
    callback: CallbackQuery,
    callback_data: SheduleFeedingsCallback,
    state: FSMContext,
    session: AsyncSession,
):
    """
    Обработчик для добавления графика кормлений на каждый день
    Принимает date, time, repeat
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
    await state.set_state(FeedingEveryDayFSM.date)


@router.message(StateFilter(FeedingEveryDayFSM.date))
async def process_add_start_date_group_feeding_every_day(message: Message,
                                                         state: FSMContext):
    """Добавление начальной даты кормлений для добавления кормлений на каждый день."""
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
        await state.set_state(FeedingEveryDayFSM.time)


@router.message(StateFilter(FeedingEveryDayFSM.time))
async def process_add_time_group_feeding_every_day(message: Message, state: FSMContext):
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
            text='Введите количество повторений.\n\n'
                 'В расписание будет внесено указанное количество дат \n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingEveryDayFSM.repeat)


@router.message(StateFilter(FeedingEveryDayFSM.repeat), F.text.isdigit())
async def process_add_repeat_group_feeding_every_day(
    message: Message, state: FSMContext, session: AsyncSession):
    """Добавление повторения кормлений для кормлений на каждый день."""
    try:
        await state.update_data(repeat=message.text)
        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])
        await add_group_feeding_shedule(
            state_data['pet_id'],
            date_time,
            1,
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


@router.message(StateFilter(FeedingEveryDayFSM.repeat))
async def warning_incorrect_repeat_feeding_every_day(message: Message):
    """Сработает при некорректном вводе повторений"""
    await message.answer(
        text='То, что Вы отправили не похоже на количество повторений кормления.\n'
             'Пожалуйста, повторите еще раз, допускаются только цифры❗',
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


@router.callback_query(SheduleFeedingsCallback.filter(F.action == 'planned_shedule'))
async def planned_feeding_shedule_handler(
    callback: CallbackQuery,
    callback_data: SheduleFeedingsCallback,
    session: AsyncSession
):
    """Посмотреть запланированный график кормлений питомца"""
    await callback.answer()
    try:
        user = await get_user(callback.from_user.id, session)
        feeding_shedules = await get_planned_pet_feeding_schedule(
            callback_data.pet_id, session
        )
        inline_kb = await show_shedule_feedings_inline_kb(
            feeding_shedules,
            user.tz_region,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
        )
    except Exception as e:
        logger.info(
            f'У пользователя c id {callback.from_user.id} нет запланированного '
            f'графика кормлений.\n Ошибка: {e}', exc_info=True
        )
        await callback.answer(
            text='У Вас нет запланированных кормлений',
            show_alert=True,
        )

    else:
        date_next = feeding_shedules[0].scheduled_time.astimezone(
            ZoneInfo(user.tz_region)
        ).strftime('%d.%m.%Y, %H:%M')

        date_last = feeding_shedules[-1].scheduled_time.astimezone(
            ZoneInfo(user.tz_region)
        ).strftime('%d.%m.%Y, %H:%M')

        await callback.message.edit_text(
            text='График кормления питомца\n\n'
                 f'Запланировано кормлений: {len(feeding_shedules)}\n'
                 f'Следующая дата: {date_next}\n'
                 f'Последняя дата: {date_last}',
            reply_markup=inline_kb,
        )


@router.callback_query(FeedingShedulePaginationCallback.filter(F.action == 'next'))
async def next_page_feeding_shedule_handler(
    callback: CallbackQuery,
    callback_data: FeedingShedulePaginationCallback,
    session: AsyncSession
):
    """Обработчик для кнопки 'Вперед'. Пагинация для просмотра запланированного графика"""
    await callback.answer()
    page = callback_data.page + 1

    feeding_shedules = await get_planned_pet_feeding_schedule(
        callback_data.pet_id, session
    )

    inline_kb = await show_shedule_feedings_inline_kb(
        feeding_shedules,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        page,
    )

    date_next = feeding_shedules[0].scheduled_time.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%Y, %H:%M')

    date_last = feeding_shedules[-1].scheduled_time.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%Y, %H:%M')

    await callback.message.edit_text(
        text='График кормления питомца\n\n'
             f'Запланировано кормлений: {len(feeding_shedules)}\n'
             f'Следующая дата: {date_next}\n'
             f'Последняя дата: {date_last}',
        reply_markup=inline_kb,
    )


@router.callback_query(FeedingShedulePaginationCallback.filter(F.action == 'prev'))
async def prev_page_my_pets_handler(
    callback: CallbackQuery,
    callback_data: FeedingShedulePaginationCallback,
    session: AsyncSession
):
    """Обработчик для кнопки 'Назад'. Пагинация для просмотра запланированного графика"""
    await callback.answer()
    page = callback_data.page - 1

    feeding_shedules = await get_planned_pet_feeding_schedule(
        callback_data.pet_id, session
    )

    inline_kb = await show_shedule_feedings_inline_kb(
        feeding_shedules,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        page,
    )
    date_next = feeding_shedules[0].scheduled_time.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%Y, %H:%M')

    date_last = feeding_shedules[-1].scheduled_time.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%Y, %H:%M')

    await callback.message.edit_text(
        text='График кормления питомца\n\n'
             f'Запланировано кормлений: {len(feeding_shedules)}\n'
             f'Следующая дата: {date_next}\n'
             f'Последняя дата: {date_last}',
        reply_markup=inline_kb,
    )


@router.callback_query(
    FeedingSheduleDetailCallback.filter(F.action == 'detail'),
    StateFilter(default_state)
)
async def detail_feeding_shedule_handler(
    callback: CallbackQuery,
    callback_data: FeedingSheduleDetailCallback,
    session: AsyncSession
):
    """Детальный просмотр даты из графика кормлений питомца"""
    await callback.answer()
    feeding_event = await get_feeding_shedule(callback_data.shedule_id, session)

    inline_kb = await detail_shedule_feedings_inline_kb(
        feeding_event.id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page
    )

    date_event = feeding_event.scheduled_time.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%Y, %H:%M')

    await callback.message.edit_text(
        text='Детальный просмотр кормления питомца\n\n'
             f'Дата кормления: {date_event}\n'
             f'Описание: {feeding_event.description}\n',
        reply_markup=inline_kb,
    )


@router.callback_query(FeedingSheduleDetailCallback.filter(F.action == 'edit'))
async def edit_feeding_shedule_handler(
    callback: CallbackQuery,
    callback_data: FeedingSheduleDetailCallback,
    state: FSMContext,
):
    """Редактирование запланированного кормления"""
    await callback.answer()

    await state.set_state(FeedingEditEventFSM.date)
    inline_kb = await get_edit_shedule_feedings_clear_state_inline_kb(
        callback_data.shedule_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Редактирование запланированного дня кормления\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
             '<b>Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ</b>\n'
             'Разделитель может быть: ".", ",", "пробел" и "/"',
        reply_markup=inline_kb
    )
    await state.update_data(
        page=callback_data.page,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        shedule_id=callback_data.shedule_id,
    )


@router.message(StateFilter(FeedingEditEventFSM.date))
async def process_edit_date_feeding_shedule(message: Message, state: FSMContext):
    """Редактирование даты кормления."""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)

        user_tz = ZoneInfo(state_data['user_tz'])
        date_feeding = date.replace(tzinfo=user_tz).date()
        await state.update_data(date=date_feeding)

        inline_back_kb = await get_edit_shedule_feedings_clear_state_inline_kb(
            state_data['shedule_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )

    except ValueError:
        await message.answer(
            'Неверный формат даты.\n Введите дату в формате ДД.ММ.ГГГГ или ДД.ММ.ГГ.'
        )
    else:
        await message.answer(
            text='Введите новое время в формате ЧЧ:ММ.\n'
                 '🔙Для возврата нажмите «Отмена», затем «Назад».\n\n'
                 'Разделитель может быть: ":", ".", ",", "пробел" и "/"',
            reply_markup=inline_back_kb
        )
        await state.set_state(FeedingEditEventFSM.time)


@router.message(StateFilter(FeedingEditEventFSM.time))
async def process_edit_time_feeding_shedule(message: Message, state: FSMContext):
    """Добавление времени кормления."""
    try:
        time_feeding = parse_time(message.text)
        await state.update_data(time=time_feeding)

        state_data = await state.get_data()
        inline_back_kb = await get_edit_shedule_feedings_clear_state_inline_kb(
            state_data['shedule_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
    except ValueError:
        await message.answer('Неверный формат времени. Введите время в формате ЧЧ:ММ.')
    else:
        await message.answer(
            'Введите новое описание\n\n'
            'Если в этом нет необходимости, можно пропустить этот шаг, отправив любой '
            'символ.',
            reply_markup=inline_back_kb,
        )
        await state.set_state(FeedingEditEventFSM.description)


@router.message(StateFilter(FeedingEditEventFSM.description))
async def process_edit_description_feeding_shedule(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Ввод нового описания при редактировании запланированного кормления и сохранение в БД."""
    try:
        await state.update_data(description=message.text)
        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])
        await edit_feeding_shedule(
            state_data['shedule_id'],
            date_time,
            state_data['description'],
            session,
        )
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        inline_back_kb = await get_successful_edit_shedule_feedings_inline_kb(
            state_data['shedule_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
        await message.answer(
            "Запланированное кормление отредактировано ✅\n",
            reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(FeedingSheduleDetailCallback.filter(F.action == 'delete'))
async def delete_feeding_shedule_handler(
    callback: CallbackQuery, callback_data: FeedingSheduleDetailCallback
):
    """Удаление запланированного кормления в детальном просмотре события"""
    await callback.answer()
    inline_kb = await get_delete_feeding_shedule_inline_kb(
        callback_data.shedule_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Удаление запланированного кормления',
        reply_markup=inline_kb
    )


@router.callback_query(ChoiceDeleteFeedingShedule.filter(F.action == 'delete'))
async def process_delete_feeding_shedule(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteFeedingShedule,
    session: AsyncSession
):
    """Подтверждение Удаления питомца."""
    await callback.answer()
    try:
        await delete_feeding_shedule(callback_data.shedule_id, session)

    except Exception as e:
        logger.error(
            f'Ошибка при удалении запланированного кормления: {e}',
                     exc_info=True
        )
        await callback.message.answer(
            'Произошла ошибка при удалении запланированного кормления !\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    else:
        await callback.answer(
            "Запланированное кормление\n было удалено ✅",
            show_alert=True,
        )
        detail_callback_data = FeedingShedulePaginationCallback(
            action='next',
            page=callback_data.page - 1,  # page -1 т.к. использую обработчик для next
            user_tz=callback_data.user_tz,
            pet_id=callback_data.pet_id,
            company_id=callback_data.company_id,
            group_id=callback_data.group_id,
        )
        await next_page_feeding_shedule_handler(callback, detail_callback_data, session)


@router.callback_query(ChoiceDeleteFeedingShedule.filter(F.action == 'cancel'))
async def process_undo_feeding_shedule(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteFeedingShedule,
    session: AsyncSession
):
    """Отмена удаления запланированного кормления"""
    await callback.answer(
        "Удаление запланированного кормления отменено.",
        show_alert=True
    )

    detail_callback_data = FeedingSheduleDetailCallback(
        action='detail',
        shedule_id=callback_data.shedule_id,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        page=callback_data.page
    )

    await detail_feeding_shedule_handler(callback, detail_callback_data, session)
