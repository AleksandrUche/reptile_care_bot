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
    HistoryPetCallback,
    FeedingHistoryPaginationCallback,
    FeedingHistoryDetailCallback,
    ChoiceDeleteFeeding,
)
from keyboards.inline_keyboards.pet.history_pet_kb import (
    get_menu_history_pet_inline_kb,
    show_feeding_history_inline_kb,
    detail_feeding_inline_kb,
    get_edit_feeding_history_clear_state_inline_kb,
    get_successful_edit_feeding_history_inline_kb,
    get_delete_feeding_inline_kb,
)
from services.pet_services import (
    get_all_pet_feeding,
    get_feeding,
    edit_date_feeding_history,
    edit_description_feeding_history,
    delete_feeding,
)
from services.registration_services import get_user
from services.utils import parse_time, parse_date
from states.pet_states import (
    FeedingHistoryEditDateFSM,
    FeedingHistoryEditDescriptionFSM,
)

logger = logging.getLogger(__name__)
router = Router(name='history_pet')


@router.callback_query(HistoryPetCallback.filter(F.action == 'menu'))
async def menu_history_pet_handler(
    callback: CallbackQuery, callback_data: HistoryPetCallback,
):
    """Главное меню взаимодействия с историями"""
    await callback.answer()
    inline_kb = await get_menu_history_pet_inline_kb(
        callback_data.pet_id, callback_data.company_id, callback_data.group_id
    )
    await callback.message.edit_text(
        text='<b>Показатели питомца</b>\n\n'
             'Здесь вы можете отслеживать все важные параметры:\n'
             '<b>Кормления</b> - график и история кормлений\n'
             '<b>Линька</b> - контроль периодов линьки\n'
             '<b>Измерения</b> - рост и размеры\n'
             '<b>Масса</b> - динамика веса\n\n'
             'ℹ️ В каждом разделе доступны:\n'
             'Просмотр истории изменений\n'
             'Редактирование предыдущих записей\n'
             'Удаление записей\n\n'
             'Выберите категорию:',
        reply_markup=inline_kb,
    )


@router.callback_query(HistoryPetCallback.filter(F.action == 'feeding_pet_history'))
async def history_feeding_pet_handler(
    callback: CallbackQuery,
    callback_data: HistoryPetCallback,
    session: AsyncSession
):
    """Просмотр истории кормлений питомца"""
    await callback.answer()
    try:
        user = await get_user(callback.from_user.id, session)
        feeding_pet_history = await get_all_pet_feeding(callback_data.pet_id, session)

        inline_kb = await show_feeding_history_inline_kb(
            feeding_pet_history,
            user.tz_region,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при вызове истории кормлений питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )
        await callback.answer(
            text='У данного питомца нет истории кормлений',
            show_alert=True,
        )

    else:
        date_last = feeding_pet_history[-1].date_feed.astimezone(
            ZoneInfo(user.tz_region)
        ).strftime('%d.%m.%y, %H:%M')

        await callback.message.edit_text(
            text='История кормлений питомца\n\n'
                 f'Кормлений: {len(feeding_pet_history)}\n'
                 f'Последняя дата кормления: {date_last}\n\n'
                 'Для редактирования нажмите на дату кормления.',
            reply_markup=inline_kb,
        )


@router.callback_query(FeedingHistoryPaginationCallback.filter(F.action == 'next'))
async def next_page_feeding_history_handler(
    callback: CallbackQuery,
    callback_data: FeedingHistoryPaginationCallback,
    session: AsyncSession
):
    """
    Обработчик для кнопки 'Вперед'. Пагинация для просмотра истории кормлений питомца.
    """
    await callback.answer()
    page = callback_data.page + 1

    feeding_pet_history = await get_all_pet_feeding(callback_data.pet_id, session)

    inline_kb = await show_feeding_history_inline_kb(
        feeding_pet_history,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        page,
    )

    date_last = feeding_pet_history[-1].date_feed.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%y, %H:%M')

    await callback.message.edit_text(
        text='История кормлений питомца\n\n'
             f'Кормлений: {len(feeding_pet_history)}\n'
             f'Последняя дата кормления: {date_last}',
        reply_markup=inline_kb,
    )


@router.callback_query(FeedingHistoryPaginationCallback.filter(F.action == 'prev'))
async def prev_page_feeding_history_handler(
    callback: CallbackQuery,
    callback_data: FeedingHistoryPaginationCallback,
    session: AsyncSession
):
    """
    Обработчик для кнопки 'Назад'. Пагинация для просмотра истории кормлений питомца.
    """
    await callback.answer()
    page = callback_data.page - 1

    feeding_pet_history = await get_all_pet_feeding(callback_data.pet_id, session)

    inline_kb = await show_feeding_history_inline_kb(
        feeding_pet_history,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        page,
    )

    date_last = feeding_pet_history[-1].date_feed.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%y, %H:%M')

    await callback.message.edit_text(
        text='История кормлений питомца\n\n'
             f'Кормлений: {len(feeding_pet_history)}\n'
             f'Последняя дата кормления: {date_last}',
        reply_markup=inline_kb,
    )


@router.callback_query(
    FeedingHistoryDetailCallback.filter(F.action == 'detail'),
    StateFilter(default_state)
)
async def detail_feeding_handler(
    callback: CallbackQuery,
    callback_data: FeedingHistoryDetailCallback,
    session: AsyncSession
):
    """Детальный просмотр кормления питомца"""
    await callback.answer()
    feeding_event = await get_feeding(callback_data.feeding_id, session)

    inline_kb = await detail_feeding_inline_kb(
        feeding_event.id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page
    )

    date_event = feeding_event.date_feed.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%y, %H:%M')

    await callback.message.edit_text(
        text='Детальный просмотр кормления питомца\n\n'
             f'Дата кормления: {date_event}\n'
             f'Описание: {feeding_event.description}\n',
        reply_markup=inline_kb,
    )


@router.callback_query(FeedingHistoryDetailCallback.filter(F.action == 'edit_date'))
async def edit_feeding_history_date_handler(
    callback: CallbackQuery,
    callback_data: FeedingHistoryDetailCallback,
    state: FSMContext,
):
    """Редактирование даты и времени кормления"""
    await callback.answer()

    await state.set_state(FeedingHistoryEditDateFSM.date)
    inline_kb = await get_edit_feeding_history_clear_state_inline_kb(
        callback_data.feeding_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Редактирование даты кормления\n'
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
        shedule_id=callback_data.feeding_id,
    )


@router.message(StateFilter(FeedingHistoryEditDateFSM.date))
async def process_edit_date_feeding_history(message: Message, state: FSMContext):
    """Ввод новой даты кормления (редактирование). FSM"""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)

        user_tz = ZoneInfo(state_data['user_tz'])
        date_feeding = date.replace(tzinfo=user_tz).date()
        await state.update_data(date=date_feeding)

        inline_back_kb = await get_edit_feeding_history_clear_state_inline_kb(
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
        await state.set_state(FeedingHistoryEditDateFSM.time)


@router.message(StateFilter(FeedingHistoryEditDateFSM.time))
async def process_edit_time_feeding_history(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Ввод нового времени кормления (редактирование). FSM"""
    try:
        time_feeding = parse_time(message.text)
        await state.update_data(time=time_feeding)

        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])

        await edit_date_feeding_history(state_data['shedule_id'], date_time, session)

    except ValueError:
        await message.answer('Неверный формат времени. Введите время в формате ЧЧ:ММ.')
    else:
        inline_back_kb = await get_successful_edit_feeding_history_inline_kb(
            state_data['shedule_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
        await message.answer(
            "Дата кормления отредактирована ✅\n",
            reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(
    FeedingHistoryDetailCallback.filter(F.action == 'edit_description')
)
async def edit_feeding_history_description_handler(
    callback: CallbackQuery,
    callback_data: FeedingHistoryDetailCallback,
    state: FSMContext,
):
    """Редактирование описания кормления"""
    await callback.answer()

    await state.set_state(FeedingHistoryEditDescriptionFSM.description)
    inline_kb = await get_edit_feeding_history_clear_state_inline_kb(
        callback_data.feeding_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Введите новое описание кормления\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n',
        reply_markup=inline_kb
    )
    await state.update_data(
        page=callback_data.page,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        shedule_id=callback_data.feeding_id,
    )


@router.message(StateFilter(FeedingHistoryEditDescriptionFSM.description))
async def process_edit_description_feeding_history(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Ввод нового описания при редактировании запланированного кормления и сохранение в БД."""
    try:
        await state.update_data(description=message.text)
        state_data = await state.get_data()
        await edit_description_feeding_history(
            state_data['shedule_id'],
            state_data['description'],
            session,
        )
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        inline_back_kb = await get_successful_edit_feeding_history_inline_kb(
            state_data['shedule_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
        await message.answer(
            "Описание кормления отредактировано ✅\n",
            reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(FeedingHistoryDetailCallback.filter(F.action == 'delete'))
async def delete_feeding_handler(
    callback: CallbackQuery, callback_data: FeedingHistoryDetailCallback
):
    """Удаление кормления"""
    await callback.answer()
    inline_kb = await get_delete_feeding_inline_kb(
        callback_data.feeding_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Удаление кормления\n'
             'Вы уверены, что хотите удалить кормление из истории?\n',
        reply_markup=inline_kb
    )


@router.callback_query(ChoiceDeleteFeeding.filter(F.action == 'delete'))
async def process_delete_feeding(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteFeeding,
    session: AsyncSession
):
    """Подтверждение удаления кормления. FSM"""
    await callback.answer()
    try:
        await delete_feeding(callback_data.feeding_id, session)

    except Exception as e:
        logger.error(f'Ошибка при удалении кормления: {e}', exc_info=True)
        await callback.message.answer(
            'Произошла ошибка при удалении кормления!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    else:
        await callback.answer(
            'Кормление удалено ✅',
            show_alert=True,
        )
        detail_callback_data = FeedingHistoryPaginationCallback(
            action='next',
            page=callback_data.page - 1,  # page -1 т.к. использую обработчик для next
            user_tz=callback_data.user_tz,
            pet_id=callback_data.pet_id,
            company_id=callback_data.company_id,
            group_id=callback_data.group_id,
        )
        await next_page_feeding_history_handler(callback, detail_callback_data, session)


@router.callback_query(ChoiceDeleteFeeding.filter(F.action == 'cancel'))
async def process_undo_delete_feeding(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteFeeding,
    session: AsyncSession
):
    """Отмена удаления кормления"""
    await callback.answer(
        "Удаление кормления отменено.",
        show_alert=True
    )

    detail_callback_data = FeedingHistoryDetailCallback(
        action='detail',
        feeding_id=callback_data.feeding_id,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        page=callback_data.page
    )

    await detail_feeding_handler(callback, detail_callback_data, session)
