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
    MoltingHistoryPaginationCallback,
    MoltingHistoryDetailCallback,
    ChoiceDeleteMoltingCallback,
    WeightHistoryPaginationCallback,
    WeightHistoryDetailCallback,
    ChoiceDeleteWeightCallback,
)
from keyboards.inline_keyboards.pet.history_pet_kb import (
    get_menu_history_pet_inline_kb,
    show_feeding_history_inline_kb,
    detail_feeding_inline_kb,
    get_edit_feeding_history_clear_state_inline_kb,
    get_successful_edit_feeding_history_inline_kb,
    get_delete_feeding_inline_kb,
    show_molting_history_inline_kb,
    detail_molting_inline_kb,
    get_edit_molting_history_clear_state_inline_kb,
    get_successful_edit_molting_history_inline_kb,
    get_delete_molting_inline_kb,
    show_weight_history_inline_kb,
    detail_weight_inline_kb,
    get_edit_weight_history_clear_state_inline_kb,
    get_successful_edit_weight_history_inline_kb,
    get_delete_weight_inline_kb,
)
from services.pet_services import (
    get_all_pet_feeding,
    get_feeding,
    edit_date_feeding_history,
    edit_description_feeding_history,
    delete_feeding,
    get_all_pet_molting,
    get_molting,
    edit_date_molting,
    edit_description_molting,
    delete_molting,
    get_all_pet_weight,
    get_weight,
    edit_date_weight,
    edit_description_weight,
    delete_weight,
)
from services.registration_services import get_user
from services.utils import parse_time, parse_date
from states.pet_states import (
    FeedingHistoryEditDateFSM,
    FeedingHistoryEditDescriptionFSM,
    MoltingHistoryEditDateFSM,
    MoltingHistoryEditDescriptionFSM,
    WeightHistoryEditDateFSM,
    WeightHistoryEditDescriptionFSM,
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
    try:
        user = await get_user(callback.from_user.id, session)
        feeding_pet_history = await get_all_pet_feeding(callback_data.pet_id, session)
        if not feeding_pet_history:
            await callback.answer(
                text='У данного питомца нет истории кормлений.', show_alert=True
            )
            return
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
    try:
        page = callback_data.page + 1

        feeding_pet_history = await get_all_pet_feeding(callback_data.pet_id, session)
        if not feeding_pet_history:
            await callback.message.answer(
                text='У данного питомца нет истории кормлений.'
            )
            return
        inline_kb = await show_feeding_history_inline_kb(
            feeding_pet_history,
            callback_data.user_tz,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
            page,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при вызове истории кормлений питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )

    else:
        # Для обработки пустого списка при удалении всех событий
        if not feeding_pet_history:
            await callback.message.answer(
                text='У данного питомца не найдена история кормлений.',
                reply_markup=inline_kb,
            )
            return
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


@router.callback_query(HistoryPetCallback.filter(F.action == 'molting_history'))
async def history_molting_pet_handler(
    callback: CallbackQuery,
    callback_data: HistoryPetCallback,
    session: AsyncSession
):
    """Просмотр истории линек питомца"""
    try:
        user = await get_user(callback.from_user.id, session)
        molting_history = await get_all_pet_molting(callback_data.pet_id, session)

        if not molting_history:
            await callback.answer(
                text='У данного питомца нет истории линек', show_alert=True
            )
            return

        inline_kb = await show_molting_history_inline_kb(
            molting_history,
            user.tz_region,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при поиске истории линек питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )

    else:
        date_last = molting_history[0].date_measure.astimezone(
            ZoneInfo(user.tz_region)
        ).strftime('%d.%m.%y, %H:%M')

        await callback.message.edit_text(
            text='История линек питомца\n\n'
                 f'Линек: {len(molting_history)}\n'
                 f'Последняя дата линьки: {date_last}\n\n'
                 'Для редактирования нажмите на дату линьки.',
            reply_markup=inline_kb,
        )


@router.callback_query(MoltingHistoryPaginationCallback.filter(F.action == 'next'))
async def next_page_molting_history_handler(
    callback: CallbackQuery,
    callback_data: MoltingHistoryPaginationCallback,
    session: AsyncSession
):
    """
    Обработчик для кнопки 'Вперед'. Пагинация для просмотра истории линек питомца.
    """
    await callback.answer()
    try:
        page = callback_data.page + 1
        molting_history = await get_all_pet_molting(callback_data.pet_id, session)

        inline_kb = await show_molting_history_inline_kb(
            molting_history,
            callback_data.user_tz,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
            page,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при поиске истории линек питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )

    else:
        # Для обработки пустого списка при удалении всех событий
        if not molting_history:
            await callback.message.answer(
                text='У данного питомца не найдена история линек.',
                reply_markup=inline_kb,
            )
            return

        date_last = molting_history[0].date_measure.astimezone(
            ZoneInfo(callback_data.user_tz)
        ).strftime('%d.%m.%y, %H:%M')
        await callback.message.edit_text(
            text='История линек питомца\n\n'
                 f'Линек: {len(molting_history)}\n'
                 f'Последняя дата линьки: {date_last}\n\n'
                 'Для редактирования нажмите на дату линьки.',
            reply_markup=inline_kb,
        )


@router.callback_query(MoltingHistoryPaginationCallback.filter(F.action == 'prev'))
async def prev_page_molting_history_handler(
    callback: CallbackQuery,
    callback_data: MoltingHistoryPaginationCallback,
    session: AsyncSession
):
    """
    Обработчик для кнопки 'Назад'. Пагинация для просмотра истории линек питомца.
    """
    await callback.answer()
    try:
        page = callback_data.page - 1

        molting_history = await get_all_pet_molting(callback_data.pet_id, session)

        inline_kb = await show_molting_history_inline_kb(
            molting_history,
            callback_data.user_tz,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
            page,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при поиске истории линек питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )
        await callback.answer(
            text='У данного питомца нет истории линек', show_alert=True,
        )
    else:
        date_last = molting_history[0].date_measure.astimezone(
            ZoneInfo(callback_data.user_tz)
        ).strftime('%d.%m.%y, %H:%M')

        await callback.message.edit_text(
            text='История линек питомца\n\n'
                 f'Линек: {len(molting_history)}\n'
                 f'Последняя дата линьки: {date_last}\n\n'
                 'Для редактирования нажмите на дату линьки.',
            reply_markup=inline_kb,
        )


@router.callback_query(
    MoltingHistoryDetailCallback.filter(F.action == 'detail'),
    StateFilter(default_state)
)
async def detail_molting_handler(
    callback: CallbackQuery,
    callback_data: MoltingHistoryDetailCallback,
    session: AsyncSession
):
    """Детальный просмотр линьки питомца"""
    await callback.answer()
    molting_event = await get_molting(callback_data.molting_id, session)

    inline_kb = await detail_molting_inline_kb(
        molting_event.id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page
    )

    date_event = molting_event.date_measure.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%y, %H:%M')

    await callback.message.edit_text(
        text='Детальный просмотр линьки питомца\n\n'
             f'Дата линьки: {date_event}\n'
             f'Описание: {molting_event.description}\n',
        reply_markup=inline_kb,
    )


@router.callback_query(MoltingHistoryDetailCallback.filter(F.action == 'edit_date'))
async def edit_molting_history_date_handler(
    callback: CallbackQuery,
    callback_data: MoltingHistoryDetailCallback,
    state: FSMContext,
):
    """Редактирование даты и времени линьки"""
    await callback.answer()

    await state.set_state(MoltingHistoryEditDateFSM.date)
    inline_kb = await get_edit_molting_history_clear_state_inline_kb(
        callback_data.molting_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Редактирование даты линьки\n'
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
        molting_id=callback_data.molting_id,
    )


@router.message(StateFilter(MoltingHistoryEditDateFSM.date))
async def process_edit_date_molting_history(message: Message, state: FSMContext):
    """Ввод новой даты линьки (редактирование). FSM"""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)

        user_tz = ZoneInfo(state_data['user_tz'])
        date_molting = date.replace(tzinfo=user_tz).date()
        await state.update_data(date=date_molting)

        inline_back_kb = await get_edit_molting_history_clear_state_inline_kb(
            state_data['molting_id'],
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
        await state.set_state(MoltingHistoryEditDateFSM.time)


@router.message(StateFilter(MoltingHistoryEditDateFSM.time))
async def process_edit_time_molting_history(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Ввод нового времени линьки (редактирование). FSM"""
    try:
        time_molting = parse_time(message.text)
        await state.update_data(time=time_molting)

        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])

        await edit_date_molting(state_data['molting_id'], date_time, session)

    except ValueError:
        await message.answer('Неверный формат времени. Введите время в формате ЧЧ:ММ.')
    else:
        inline_back_kb = await get_successful_edit_molting_history_inline_kb(
            state_data['molting_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
        await message.answer(
            "Дата линьки изменена ✅\n", reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(
    MoltingHistoryDetailCallback.filter(F.action == 'edit_description')
)
async def edit_molting_history_description_handler(
    callback: CallbackQuery,
    callback_data: MoltingHistoryDetailCallback,
    state: FSMContext,
):
    """Редактирование описания линьки"""
    await callback.answer()

    await state.set_state(MoltingHistoryEditDescriptionFSM.description)
    inline_kb = await get_edit_feeding_history_clear_state_inline_kb(
        callback_data.molting_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Введите новое описание линьки\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n',
        reply_markup=inline_kb
    )
    await state.update_data(
        page=callback_data.page,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        molting_id=callback_data.molting_id,
    )


@router.message(StateFilter(MoltingHistoryEditDescriptionFSM.description))
async def process_edit_description_molting_history(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Ввод нового описания при редактировании линьки и сохранение в БД."""
    try:
        await state.update_data(description=message.text)
        state_data = await state.get_data()
        await edit_description_molting(
            state_data['molting_id'], state_data['description'], session
        )
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        inline_back_kb = await get_successful_edit_molting_history_inline_kb(
            state_data['molting_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
        await message.answer(
            "Описание линьки изменено ✅\n", reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(MoltingHistoryDetailCallback.filter(F.action == 'delete'))
async def delete_molting_handler(
    callback: CallbackQuery, callback_data: MoltingHistoryDetailCallback
):
    """Удаление линьки"""
    await callback.answer()
    inline_kb = await get_delete_molting_inline_kb(
        callback_data.molting_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Удаление линьки\n'
             'Вы уверены, что хотите удалить линьку из истории?\n',
        reply_markup=inline_kb
    )


@router.callback_query(ChoiceDeleteMoltingCallback.filter(F.action == 'delete'))
async def process_delete_molting(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteMoltingCallback,
    session: AsyncSession
):
    """Подтверждение удаления линьки. FSM"""
    try:
        await delete_molting(callback_data.molting_id, session)

    except Exception as e:
        logger.error(f'Ошибка при удалении линьки: {e}', exc_info=True)
        await callback.message.answer(
            'Произошла ошибка при удалении линьки!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    else:
        await callback.answer('Линька удалена ✅', show_alert=True)

        detail_callback_data = MoltingHistoryPaginationCallback(
            action='next',
            page=callback_data.page - 1,  # page -1 т.к. использую обработчик для next
            user_tz=callback_data.user_tz,
            pet_id=callback_data.pet_id,
            company_id=callback_data.company_id,
            group_id=callback_data.group_id,
        )
        await next_page_molting_history_handler(callback, detail_callback_data, session)


@router.callback_query(ChoiceDeleteMoltingCallback.filter(F.action == 'cancel'))
async def process_undo_delete_molting(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteMoltingCallback,
    session: AsyncSession
):
    """Отмена удаления линьки"""
    await callback.answer("Удаление линьки отменено.", show_alert=True)

    detail_callback_data = MoltingHistoryDetailCallback(
        action='detail',
        molting_id=callback_data.molting_id,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        page=callback_data.page
    )

    await detail_molting_handler(callback, detail_callback_data, session)


@router.callback_query(HistoryPetCallback.filter(F.action == 'weight_history'))
async def history_weight_pet_handler(
    callback: CallbackQuery,
    callback_data: HistoryPetCallback,
    session: AsyncSession
):
    """Просмотр истории взвешиваний питомца"""
    try:
        user = await get_user(callback.from_user.id, session)
        weight_history = await get_all_pet_weight(callback_data.pet_id, session)

        if not weight_history:
            await callback.answer(
                text='У данного питомца нет истории взвешиваний', show_alert=True
            )
            return

        inline_kb = await show_weight_history_inline_kb(
            weight_history,
            user.tz_region,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при поиске истории взвешиваний питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )

    else:
        date_last = weight_history[0].date_measure.astimezone(
            ZoneInfo(user.tz_region)
        ).strftime('%d.%m.%y, %H:%M')

        await callback.message.edit_text(
            text='История веса питомца\n\n'
                 f'Взвешиваний: {len(weight_history)}\n'
                 f'Последняя дата измерения: {date_last}\n\n'
                 'Для редактирования нажмите на дату измерения веса.',
            reply_markup=inline_kb,
        )


@router.callback_query(WeightHistoryPaginationCallback.filter(F.action == 'next'))
async def next_page_weight_history_handler(
    callback: CallbackQuery,
    callback_data: WeightHistoryPaginationCallback,
    session: AsyncSession
):
    """
    Обработчик для кнопки 'Вперед'. Пагинация для просмотра истории взвешиваний питомца.
    """
    await callback.answer()
    try:
        page = callback_data.page + 1
        weight_history = await get_all_pet_weight(callback_data.pet_id, session)

        inline_kb = await show_weight_history_inline_kb(
            weight_history,
            callback_data.user_tz,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
            page,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при поиске истории взвешиваний питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )

    else:
        # Для обработки пустого списка при удалении всех событий
        if not weight_history:
            await callback.message.answer(
                text='У данного питомца не найдена история взвешиваний.',
                reply_markup=inline_kb,
            )
            return

        date_last = weight_history[0].date_measure.astimezone(
            ZoneInfo(callback_data.user_tz)
        ).strftime('%d.%m.%y, %H:%M')
        await callback.message.edit_text(
            text='История веса питомца\n\n'
                 f'Взвешиваний: {len(weight_history)}\n'
                 f'Последняя дата измерения: {date_last}\n\n'
                 'Для редактирования нажмите на дату измерения веса.',
            reply_markup=inline_kb,
        )


@router.callback_query(WeightHistoryPaginationCallback.filter(F.action == 'prev'))
async def prev_page_weight_history_handler(
    callback: CallbackQuery,
    callback_data: WeightHistoryPaginationCallback,
    session: AsyncSession
):
    """
    Обработчик для кнопки 'Назад'. Пагинация для просмотра истории взвешиваний питомца.
    """
    await callback.answer()
    try:
        page = callback_data.page - 1

        weight_history = await get_all_pet_weight(callback_data.pet_id, session)

        inline_kb = await show_weight_history_inline_kb(
            weight_history,
            callback_data.user_tz,
            callback_data.pet_id,
            callback_data.company_id,
            callback_data.group_id,
            page,
        )
    except Exception as e:
        logger.info(
            'Произошла ошибка при поиске истории взвешиваний питомца pet id:'
            f'{callback_data.pet_id}, user id: {callback.from_user.id}. {e}',
            exc_info=True
        )
        await callback.answer(
            text='У данного питомца нет истории взвешиваний', show_alert=True,
        )
    else:
        date_last = weight_history[0].date_measure.astimezone(
            ZoneInfo(callback_data.user_tz)
        ).strftime('%d.%m.%y, %H:%M')

        await callback.message.edit_text(
            text='История веса питомца\n\n'
                 f'Взвешиваний: {len(weight_history)}\n'
                 f'Последняя дата измерения: {date_last}\n\n'
                 'Для редактирования нажмите на дату измерения веса.',
            reply_markup=inline_kb,
        )


@router.callback_query(
    WeightHistoryDetailCallback.filter(F.action == 'detail'),
    StateFilter(default_state)
)
async def detail_weight_handler(
    callback: CallbackQuery,
    callback_data: WeightHistoryDetailCallback,
    session: AsyncSession
):
    """Детальный просмотр измерения веса питомца"""
    await callback.answer()
    weight_event = await get_weight(callback_data.weight_id, session)

    inline_kb = await detail_weight_inline_kb(
        weight_event.id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page
    )

    date_event = weight_event.date_measure.astimezone(
        ZoneInfo(callback_data.user_tz)
    ).strftime('%d.%m.%y, %H:%M')

    await callback.message.edit_text(
        text='Детальный просмотр взвешивания питомца\n\n'
             f'Дата измерения: {date_event}\n'
             f'Описание: {weight_event.description}\n',
        reply_markup=inline_kb,
    )


@router.callback_query(WeightHistoryDetailCallback.filter(F.action == 'edit_date'))
async def edit_weight_history_date_handler(
    callback: CallbackQuery,
    callback_data: WeightHistoryDetailCallback,
    state: FSMContext,
):
    """Редактирование даты и времени взвешивания"""
    await callback.answer()

    await state.set_state(WeightHistoryEditDateFSM.date)
    inline_kb = await get_edit_weight_history_clear_state_inline_kb(
        callback_data.weight_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Редактирование даты измерения веса\n'
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
        weight_id=callback_data.weight_id,
    )


@router.message(StateFilter(WeightHistoryEditDateFSM.date))
async def process_edit_date_weight_history(message: Message, state: FSMContext):
    """Ввод новой даты измерения веса (редактирование). FSM"""
    try:
        state_data = await state.get_data()
        date = parse_date(message.text)

        user_tz = ZoneInfo(state_data['user_tz'])
        date_weight = date.replace(tzinfo=user_tz).date()
        await state.update_data(date=date_weight)

        inline_back_kb = await get_edit_weight_history_clear_state_inline_kb(
            state_data['weight_id'],
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
        await state.set_state(WeightHistoryEditDateFSM.time)


@router.message(StateFilter(WeightHistoryEditDateFSM.time))
async def process_edit_time_weight_history(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Ввод нового времени измерения веса (редактирование). FSM"""
    try:
        time_weight = parse_time(message.text)
        await state.update_data(time=time_weight)

        state_data = await state.get_data()
        date_time = datetime.combine(state_data['date'], state_data['time'])

        await edit_date_weight(state_data['weight_id'], date_time, session)

    except ValueError:
        await message.answer('Неверный формат времени. Введите время в формате ЧЧ:ММ.')
    else:
        inline_back_kb = await get_successful_edit_weight_history_inline_kb(
            state_data['weight_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
        await message.answer(
            "Дата взвешивания изменена ✅\n", reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(
    WeightHistoryDetailCallback.filter(F.action == 'edit_description')
)
async def edit_weight_history_description_handler(
    callback: CallbackQuery,
    callback_data: WeightHistoryDetailCallback,
    state: FSMContext,
):
    """Редактирование описания взвешивания"""
    await callback.answer()

    await state.set_state(WeightHistoryEditDescriptionFSM.description)
    inline_kb = await get_edit_feeding_history_clear_state_inline_kb(
        callback_data.weight_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Введите новое описание\n'
             '🔙Для возврата нажмите «Отмена», затем «Назад».\n',
        reply_markup=inline_kb
    )
    await state.update_data(
        page=callback_data.page,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        weight_id=callback_data.weight_id,
    )


@router.message(StateFilter(WeightHistoryEditDescriptionFSM.description))
async def process_edit_description_weight_history(
    message: Message, state: FSMContext, session: AsyncSession
):
    """Ввод нового описания при редактировании взвешивания и сохранение в БД."""
    try:
        await state.update_data(description=message.text)
        state_data = await state.get_data()
        await edit_description_weight(
            state_data['weight_id'], state_data['description'], session
        )
    except ValueError:
        await message.answer('Произошла ошибка, пожалуйста, повторите еще раз.')
    else:
        inline_back_kb = await get_successful_edit_weight_history_inline_kb(
            state_data['weight_id'],
            state_data['user_tz'],
            state_data['pet_id'],
            state_data['company_id'],
            state_data['group_id'],
            state_data['page'],
        )
        await message.answer(
            "Описание взвешивания изменено ✅\n", reply_markup=inline_back_kb,
        )
        await state.clear()


@router.callback_query(WeightHistoryDetailCallback.filter(F.action == 'delete'))
async def delete_weight_handler(
    callback: CallbackQuery, callback_data: WeightHistoryDetailCallback
):
    """Удаление измерения веса"""
    await callback.answer()
    inline_kb = await get_delete_weight_inline_kb(
        callback_data.weight_id,
        callback_data.user_tz,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
        callback_data.page,
    )

    await callback.message.edit_text(
        text='Удаление взвешивания\n'
             'Вы уверены, что хотите удалить линьку из истории?\n',
        reply_markup=inline_kb
    )


@router.callback_query(ChoiceDeleteWeightCallback.filter(F.action == 'delete'))
async def process_delete_weight(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteWeightCallback,
    session: AsyncSession
):
    """Подтверждение удаления измерения веса. FSM"""
    try:
        await delete_weight(callback_data.weight_id, session)

    except Exception as e:
        logger.error(f'Ошибка при удалении измерения веса: {e}', exc_info=True)
        await callback.message.answer(
            'Произошла ошибка при удалении взвешивания!\n'
            'Попробуйте еще раз 😉, если что, обратитесь в поддержку 😏'
        )
    else:
        await callback.answer('Взвешивание удалено ✅', show_alert=True)

        detail_callback_data = WeightHistoryPaginationCallback(
            action='next',
            page=callback_data.page - 1,  # page -1 т.к. использую обработчик для next
            user_tz=callback_data.user_tz,
            pet_id=callback_data.pet_id,
            company_id=callback_data.company_id,
            group_id=callback_data.group_id,
        )
        await next_page_weight_history_handler(callback, detail_callback_data, session)


@router.callback_query(ChoiceDeleteWeightCallback.filter(F.action == 'cancel'))
async def process_undo_delete_weight(
    callback: CallbackQuery,
    callback_data: ChoiceDeleteWeightCallback,
    session: AsyncSession
):
    """Отмена удаления измерения веса"""
    await callback.answer("Удаление взвешивания отменено.", show_alert=True)

    detail_callback_data = WeightHistoryDetailCallback(
        action='detail',
        weight_id=callback_data.weight_id,
        user_tz=callback_data.user_tz,
        pet_id=callback_data.pet_id,
        company_id=callback_data.company_id,
        group_id=callback_data.group_id,
        page=callback_data.page
    )

    await detail_weight_handler(callback, detail_callback_data, session)
