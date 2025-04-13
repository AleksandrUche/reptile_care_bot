from zoneinfo import ZoneInfo

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.pet_factory import (
    SheduleFeedingsCallback,
    PetsCallback,
    FeedingSheduleDetailCallback,
    FeedingShedulePaginationCallback,
    ChoiceDeleteFeedingShedule, ConfirmFeedingEventsCallback,
)
from factory.callback_factory.user_factory import EditMyProfileCallback


async def get_menu_shedule_feedings_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Меню графика кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='Добавить график',
        callback_data=SheduleFeedingsCallback(action='add_shedule', **data).pack()
    )
    builder.button(
        text='Запланированные',
        callback_data=SheduleFeedingsCallback(action='planned_shedule', **data).pack()
    )
    builder.button(
        text='⬅ Вернуться к питомцу',
        callback_data=PetsCallback(**data).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


async def get_add_shedule_feedings_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Клавиатура для выбора режима добавления графика кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='1 вариант',
        callback_data=SheduleFeedingsCallback(
            action='single_addition', **data
        ).pack()
    )
    builder.button(
        text='2 вариант',
        callback_data=SheduleFeedingsCallback(action='group_addition', **data).pack()
    )
    builder.button(
        text='3 вариант',
        callback_data=SheduleFeedingsCallback(
            action='group_addition_and_description', **data).pack()
    )
    builder.button(
        text='4 вариант',
        callback_data=SheduleFeedingsCallback(action='every_day', **data).pack()
    )
    builder.button(
        text='⬅ Назад',
        callback_data=SheduleFeedingsCallback(action='menu', **data).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_select_shedule_feedings_clear_state_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Возврат к меню выбора добавления графиков кормления с очисткой машины состояний"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='Отмена',
        callback_data='cancel_state'
    )
    builder.button(
        text='⬅ Назад',
        callback_data=SheduleFeedingsCallback(action='menu', **data).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_select_shedule_feedings_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Возврат к меню выбора добавления графиков кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='⬅ Назад',
        callback_data=SheduleFeedingsCallback(action='menu', **data).pack()
    )
    builder.adjust(1)
    return builder.as_markup()


async def show_shedule_feedings_inline_kb(
    shedules: list,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
    per_page: int = 6
):
    """
    Отображает запланированные кормления с пагинацией.
    :param shedules: Список всех дат графиков.
    :param user_timezone: Таймзона пользователя из БД
    :param pet_id: ID питомца
    :param company_id: ID компании
    :param group_id: ID группы питомца
    :param page: Номер текущей страницы.
    :param per_page: Количество запланированных дат на одной странице.
    :return: Инлайн клавиатура.
    """
    # Вычисляем начальный и конечный индекс для текущей страницы
    start_index = page * per_page
    end_index = start_index + per_page
    shedule_page = shedules[start_index:end_index]

    builder = InlineKeyboardBuilder()
    # для возврата в меню
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    for shedule in shedule_page:
        date_time = shedule.scheduled_time
        shedule_time = date_time.astimezone(
            ZoneInfo(user_timezone)
        ).strftime('%d.%m.%Y, %H:%M')

        builder.row(
            InlineKeyboardButton(
                text=f'Дата: {shedule_time}',
                callback_data=FeedingSheduleDetailCallback(
                    action='detail',
                    page=page,
                    user_tz=user_timezone,
                    shedule_id=shedule.id,
                    **data
                ).pack()
            )
        )
        builder.row(
            InlineKeyboardButton(
                text='✏ Редактировать',
                callback_data=FeedingSheduleDetailCallback(
                    action='edit',
                    page=page,
                    user_tz=user_timezone,
                    shedule_id=shedule.id,
                    **data
                ).pack()
            ),
            InlineKeyboardButton(
                text='🗑 Удалить',
                callback_data=FeedingSheduleDetailCallback(
                    action='delete',
                    page=page,
                    user_tz=user_timezone,
                    shedule_id=shedule.id,
                    **data
                ).pack()
            ),
            width=2,
        )

    pagination_buttons = []
    if page > 0:
        pagination_buttons.append(
            InlineKeyboardButton(
                text='⬅️ Назад',
                callback_data=FeedingShedulePaginationCallback(
                    action='prev', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )
    if end_index < len(shedules):
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед ➡️',
                callback_data=FeedingShedulePaginationCallback(
                    action='next', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text='⬅ Меню',
            callback_data=SheduleFeedingsCallback(action='menu', **data).pack()
        )
    )
    return builder.as_markup()


async def detail_shedule_feedings_inline_kb(
    shedule_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается в детальном просмотре запланированного кормления"""
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='✏ Редактировать',
            callback_data=FeedingSheduleDetailCallback(
                action='edit',
                page=page,
                user_tz=user_timezone,
                shedule_id=shedule_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='🗑 Удалить',
            callback_data=FeedingSheduleDetailCallback(
                action='delete',
                page=page,
                user_tz=user_timezone,
                shedule_id=shedule_id,
                **data
            ).pack()
        )
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад',
            callback_data=FeedingShedulePaginationCallback(
                # page -1 т.к. использую обработчик для next
                action='next', page=page - 1, user_tz=user_timezone, **data
            ).pack()
        )
    )
    return builder.as_markup()


async def get_edit_shedule_feedings_clear_state_inline_kb(
    shedule_id: int,
    user_timezone,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при редактировании запланированного кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='Отмена',
        callback_data='cancel_state'
    )
    builder.button(
        text='⬅ Назад',
        callback_data=FeedingSheduleDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            shedule_id=shedule_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_successful_edit_shedule_feedings_inline_kb(
    shedule_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при успешном редактировании запланированного кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='⬅ Детальный просмотр',
        callback_data=FeedingSheduleDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            shedule_id=shedule_id,
            **data
        ).pack()
    )
    return builder.as_markup()


async def get_delete_feeding_shedule_inline_kb(
    shedule_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Подтверждение удаления запланированного кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='✅ ДА',
        callback_data=ChoiceDeleteFeedingShedule(
            action='delete',
            page=page,
            user_tz=user_timezone,
            shedule_id=shedule_id,
            **data
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=ChoiceDeleteFeedingShedule(
            action='cancel',
            page=page,
            user_tz=user_timezone,
            shedule_id=shedule_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_shedule_feeding_approve_inline_kb(
    event_feeding_id: int, pet_id: int, pet_name: str
):
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Покормил(а) ✅',
        callback_data=ConfirmFeedingEventsCallback(
            action='approve',
            event_feeding_id=event_feeding_id,
            pet_id=pet_id,
            pet_name=pet_name,
        ).pack()
    )
    builder.button(
        text='Напомнить ⏱',
        callback_data=ConfirmFeedingEventsCallback(
            action='remind',
            event_feeding_id=event_feeding_id,
            pet_id=pet_id,
            pet_name=pet_name,
        ).pack()
    )
    builder.button(
        text='Не напоминать ❌',
        callback_data=ConfirmFeedingEventsCallback(
            action='cancel',
            event_feeding_id=event_feeding_id,
            pet_id=pet_id,
            pet_name=pet_name,
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def no_time_zone_inline_kb(
    user_tg_id: int, pet_id: int, company_id: int, group_id: int
):
    """
    Клавиатура возникающая в процессе добавлений графиков кормлений если у
    пользователя не определена таймзона
    """
    builder = InlineKeyboardBuilder()
    builder.button(
        text='Указать таймзону',
        callback_data=EditMyProfileCallback(
            action='edit_time_zone',
            user_tg_id=user_tg_id).pack()
    )
    builder.button(
        text='Назад',
        callback_data=SheduleFeedingsCallback(
            action='menu',
            pet_id=pet_id,
            company_id=company_id,
            group_id=group_id,
        ).pack()
    )
    builder.adjust(1)
    return builder.as_markup()
