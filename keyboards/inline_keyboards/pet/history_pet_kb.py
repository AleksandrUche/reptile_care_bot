from zoneinfo import ZoneInfo

from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from factory.callback_factory.pet_factory import (
    HistoryPetCallback,
    PetsCallback,
    FeedingHistoryPaginationCallback,
    FeedingHistoryDetailCallback,
    ChoiceDeleteFeeding,
    MoltingHistoryDetailCallback,
    MoltingHistoryPaginationCallback,
    ChoiceDeleteMoltingCallback,
    WeightHistoryDetailCallback,
    WeightHistoryPaginationCallback,
    ChoiceDeleteWeightCallback,
    LengthHistoryDetailCallback,
    LengthHistoryPaginationCallback,
    ChoiceDeleteLengthCallback,
)


async def get_menu_history_pet_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Меню истории событий питомца"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='🍽 Кормления',
        callback_data=HistoryPetCallback(action='feeding_pet_history', **data).pack()
    )
    builder.button(
        text='🐍 Линьки',
        callback_data=HistoryPetCallback(action='molting_history', **data).pack()
    )
    builder.button(
        text='📐 Измерения',
        callback_data=HistoryPetCallback(action='length_history', **data).pack()
    )
    builder.button(
        text='⚖️ Масса',
        callback_data=HistoryPetCallback(action='weight_history', **data).pack()
    )
    builder.button(
        text='⬅ Вернуться к питомцу',
        callback_data=PetsCallback(**data).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_back_main_history_menu_inline_kb(
    pet_id: int, company_id: int, group_id: int
):
    """Возврат в главное меню истории событий питомца"""
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder = InlineKeyboardBuilder()
    builder.button(
        text='⬅ Назад в меню',
        callback_data=HistoryPetCallback(action='menu', **data).pack()
    )
    return builder.as_markup()


async def show_feeding_history_inline_kb(
    feeding_history: list,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
    per_page: int = 6
):
    """
    Отображает кормления с пагинацией.
    :param feeding_history: Список всех кормлений.
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
    feeding_page = feeding_history[start_index:end_index]

    builder = InlineKeyboardBuilder()
    # для возврата в меню
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    for feeding in feeding_page:
        date_time = feeding.date_feed
        shedule_time = date_time.astimezone(
            ZoneInfo(user_timezone)
        ).strftime('%d.%m.%y, %H:%M')

        builder.row(
            InlineKeyboardButton(
                text=f'{shedule_time}',
                callback_data=FeedingHistoryDetailCallback(
                    action='detail',
                    page=page,
                    user_tz=user_timezone,
                    feeding_id=feeding.id,
                    **data
                ).pack()
            ),
            InlineKeyboardButton(
                text='🗑 Удалить',
                callback_data=FeedingHistoryDetailCallback(
                    action='delete',
                    page=page,
                    user_tz=user_timezone,
                    feeding_id=feeding.id,
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
                callback_data=FeedingHistoryPaginationCallback(
                    action='prev', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )
    if end_index < len(feeding_history):
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед ➡️',
                callback_data=FeedingHistoryPaginationCallback(
                    action='next', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад в меню',
            callback_data=HistoryPetCallback(action='menu', **data).pack()
        )
    )
    return builder.as_markup()


async def detail_feeding_inline_kb(
    shedule_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается в детальном просмотре кормления"""
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='✏ Дату',
            callback_data=FeedingHistoryDetailCallback(
                action='edit_date',
                page=page,
                user_tz=user_timezone,
                feeding_id=shedule_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='✏ Описание',
            callback_data=FeedingHistoryDetailCallback(
                action='edit_description',
                page=page,
                user_tz=user_timezone,
                feeding_id=shedule_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='🗑 Удалить',
            callback_data=FeedingHistoryDetailCallback(
                action='delete',
                page=page,
                user_tz=user_timezone,
                feeding_id=shedule_id,
                **data
            ).pack()
        ),
        width=1
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад',
            callback_data=FeedingHistoryPaginationCallback(
                # page -1 т.к. использую обработчик для next
                action='next', page=page - 1, user_tz=user_timezone, **data
            ).pack()
        )
    )
    return builder.as_markup()


async def get_edit_feeding_history_clear_state_inline_kb(
    shedule_id: int,
    user_timezone,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при редактировании кормления в истории"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='Отмена',
        callback_data='cancel_state'
    )
    builder.button(
        text='⬅ Назад',
        callback_data=FeedingHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            feeding_id=shedule_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_successful_edit_feeding_history_inline_kb(
    shedule_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при успешном редактировании кормления в истории"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='⬅ Детальный просмотр',
        callback_data=FeedingHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            feeding_id=shedule_id,
            **data
        ).pack()
    )
    return builder.as_markup()


async def get_delete_feeding_inline_kb(
    feeding_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Подтверждение удаления кормления"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='✅ ДА',
        callback_data=ChoiceDeleteFeeding(
            action='delete',
            page=page,
            user_tz=user_timezone,
            feeding_id=feeding_id,
            **data
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=ChoiceDeleteFeeding(
            action='cancel',
            page=page,
            user_tz=user_timezone,
            feeding_id=feeding_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def show_molting_history_inline_kb(
    molting_history: list,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
    per_page: int = 6
):
    """
    Отображает линьки с пагинацией.
    :param molting_history: Список всех линек питомца.
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
    molting_page = molting_history[start_index:end_index]

    builder = InlineKeyboardBuilder()
    # для возврата в меню
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    for molting in molting_page:
        date_time = molting.date_measure
        shedule_time = date_time.astimezone(
            ZoneInfo(user_timezone)
        ).strftime('%d.%m.%y, %H:%M')

        builder.row(
            InlineKeyboardButton(
                text=f'{shedule_time}',
                callback_data=MoltingHistoryDetailCallback(
                    action='detail',
                    page=page,
                    user_tz=user_timezone,
                    molting_id=molting.id,
                    **data
                ).pack()
            ),
            InlineKeyboardButton(
                text='🗑 Удалить',
                callback_data=MoltingHistoryDetailCallback(
                    action='delete',
                    page=page,
                    user_tz=user_timezone,
                    molting_id=molting.id,
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
                callback_data=MoltingHistoryPaginationCallback(
                    action='prev', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )
    if end_index < len(molting_history):
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед ➡️',
                callback_data=MoltingHistoryPaginationCallback(
                    action='next', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад в меню',
            callback_data=HistoryPetCallback(action='menu', **data).pack()
        )
    )
    return builder.as_markup()


async def detail_molting_inline_kb(
    molting_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается в детальном просмотре линьки"""
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='✏ Дату',
            callback_data=MoltingHistoryDetailCallback(
                action='edit_date',
                page=page,
                user_tz=user_timezone,
                molting_id=molting_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='✏ Описание',
            callback_data=MoltingHistoryDetailCallback(
                action='edit_description',
                page=page,
                user_tz=user_timezone,
                molting_id=molting_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='🗑 Удалить',
            callback_data=MoltingHistoryDetailCallback(
                action='delete',
                page=page,
                user_tz=user_timezone,
                molting_id=molting_id,
                **data
            ).pack()
        ),
        width=1
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад',
            callback_data=MoltingHistoryPaginationCallback(
                # page -1 т.к. использую обработчик для next
                action='next', page=page - 1, user_tz=user_timezone, **data
            ).pack()
        )
    )
    return builder.as_markup()


async def get_edit_molting_history_clear_state_inline_kb(
    molting_id: int,
    user_timezone,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при редактировании линьки в истории"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='Отмена',
        callback_data='cancel_state'
    )
    builder.button(
        text='⬅ Назад',
        callback_data=MoltingHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            molting_id=molting_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_successful_edit_molting_history_inline_kb(
    molting_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при успешном редактировании линьки в истории"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='⬅ Детальный просмотр',
        callback_data=MoltingHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            molting_id=molting_id,
            **data
        ).pack()
    )
    return builder.as_markup()


async def get_delete_molting_inline_kb(
    molting_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Подтверждение удаления линьки"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='✅ ДА',
        callback_data=ChoiceDeleteMoltingCallback(
            action='delete',
            page=page,
            user_tz=user_timezone,
            molting_id=molting_id,
            **data
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=ChoiceDeleteMoltingCallback(
            action='cancel',
            page=page,
            user_tz=user_timezone,
            molting_id=molting_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def show_weight_history_inline_kb(
    weight_history: list,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
    per_page: int = 6
):
    """
    Отображает историю веса с пагинацией.
    :param weight_history: Список всех измерений веса питомца.
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
    weight_page = weight_history[start_index:end_index]

    builder = InlineKeyboardBuilder()
    # для возврата в меню
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    for weight in weight_page:
        date_time = weight.date_measure
        shedule_time = date_time.astimezone(
            ZoneInfo(user_timezone)
        ).strftime('%d.%m.%y, %H:%M')

        builder.row(
            InlineKeyboardButton(
                text=f'{shedule_time}',
                callback_data=WeightHistoryDetailCallback(
                    action='detail',
                    page=page,
                    user_tz=user_timezone,
                    weight_id=weight.id,
                    **data
                ).pack()
            ),
            InlineKeyboardButton(
                text='🗑 Удалить',
                callback_data=WeightHistoryDetailCallback(
                    action='delete',
                    page=page,
                    user_tz=user_timezone,
                    weight_id=weight.id,
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
                callback_data=WeightHistoryPaginationCallback(
                    action='prev', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )
    if end_index < len(weight_history):
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед ➡️',
                callback_data=WeightHistoryPaginationCallback(
                    action='next', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад в меню',
            callback_data=HistoryPetCallback(action='menu', **data).pack()
        )
    )
    return builder.as_markup()


async def detail_weight_inline_kb(
    weight_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается в детальном просмотре истории веса"""
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='✏ Дату',
            callback_data=WeightHistoryDetailCallback(
                action='edit_date',
                page=page,
                user_tz=user_timezone,
                weight_id=weight_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='✏ Описание',
            callback_data=WeightHistoryDetailCallback(
                action='edit_description',
                page=page,
                user_tz=user_timezone,
                weight_id=weight_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='🗑 Удалить',
            callback_data=WeightHistoryDetailCallback(
                action='delete',
                page=page,
                user_tz=user_timezone,
                weight_id=weight_id,
                **data
            ).pack()
        ),
        width=1
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад',
            callback_data=WeightHistoryPaginationCallback(
                # page -1 т.к. использую обработчик для next
                action='next', page=page - 1, user_tz=user_timezone, **data
            ).pack()
        )
    )
    return builder.as_markup()


async def get_edit_weight_history_clear_state_inline_kb(
    weight_id: int,
    user_timezone,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при редактировании истории веса (в истории)"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='Отмена',
        callback_data='cancel_state'
    )
    builder.button(
        text='⬅ Назад',
        callback_data=WeightHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            weight_id=weight_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_successful_edit_weight_history_inline_kb(
    weight_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при успешном редактировании веса (в истории)"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='⬅ Детальный просмотр',
        callback_data=WeightHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            weight_id=weight_id,
            **data
        ).pack()
    )
    return builder.as_markup()


async def get_delete_weight_inline_kb(
    weight_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Подтверждение удаления веса питомца (в истории)"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='✅ ДА',
        callback_data=ChoiceDeleteWeightCallback(
            action='delete',
            page=page,
            user_tz=user_timezone,
            weight_id=weight_id,
            **data
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=ChoiceDeleteWeightCallback(
            action='cancel',
            page=page,
            user_tz=user_timezone,
            weight_id=weight_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def show_length_history_inline_kb(
    length_history: list,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
    per_page: int = 6
):
    """
    Отображается в просмотре истории длины с пагинацией.
    :param length_history: Список всех измерений длины питомца.
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
    length_page = length_history[start_index:end_index]

    builder = InlineKeyboardBuilder()
    # для возврата в меню
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    for length in length_page:
        date_time = length.date_measure
        shedule_time = date_time.astimezone(
            ZoneInfo(user_timezone)
        ).strftime('%d.%m.%y, %H:%M')

        builder.row(
            InlineKeyboardButton(
                text=f'{shedule_time}',
                callback_data=LengthHistoryDetailCallback(
                    action='detail',
                    page=page,
                    user_tz=user_timezone,
                    length_id=length.id,
                    **data
                ).pack()
            ),
            InlineKeyboardButton(
                text='🗑 Удалить',
                callback_data=LengthHistoryDetailCallback(
                    action='delete',
                    page=page,
                    user_tz=user_timezone,
                    length_id=length.id,
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
                callback_data=LengthHistoryPaginationCallback(
                    action='prev', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )
    if end_index < len(length_history):
        pagination_buttons.append(
            InlineKeyboardButton(
                text='Вперед ➡️',
                callback_data=LengthHistoryPaginationCallback(
                    action='next', page=page, user_tz=user_timezone, **data
                ).pack()
            )
        )

    if pagination_buttons:
        builder.row(*pagination_buttons)

    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад в меню',
            callback_data=HistoryPetCallback(action='menu', **data).pack()
        )
    )
    return builder.as_markup()


async def detail_length_inline_kb(
    length_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается в детальном просмотре истории длины"""
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text='✏ Дату',
            callback_data=LengthHistoryDetailCallback(
                action='edit_date',
                page=page,
                user_tz=user_timezone,
                length_id=length_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='✏ Описание',
            callback_data=LengthHistoryDetailCallback(
                action='edit_description',
                page=page,
                user_tz=user_timezone,
                length_id=length_id,
                **data
            ).pack()
        ),
        InlineKeyboardButton(
            text='🗑 Удалить',
            callback_data=LengthHistoryDetailCallback(
                action='delete',
                page=page,
                user_tz=user_timezone,
                length_id=length_id,
                **data
            ).pack()
        ),
        width=1
    )
    builder.row(
        InlineKeyboardButton(
            text='⬅ Назад',
            callback_data=LengthHistoryPaginationCallback(
                # page -1 т.к. использую обработчик для next
                action='next', page=page - 1, user_tz=user_timezone, **data
            ).pack()
        )
    )
    return builder.as_markup()


async def get_edit_length_history_clear_state_inline_kb(
    length_id: int,
    user_timezone,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при редактировании истории длины (в истории)"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}

    builder.button(
        text='Отмена',
        callback_data='cancel_state'
    )
    builder.button(
        text='⬅ Назад',
        callback_data=LengthHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            length_id=length_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()


async def get_successful_edit_length_history_inline_kb(
    length_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Отображается при успешном редактировании длины (в истории)"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='⬅ Детальный просмотр',
        callback_data=LengthHistoryDetailCallback(
            action='detail',
            page=page,
            user_tz=user_timezone,
            length_id=length_id,
            **data
        ).pack()
    )
    return builder.as_markup()


async def get_delete_length_inline_kb(
    length_id: int,
    user_timezone: str,
    pet_id: int,
    company_id: int,
    group_id: int,
    page: int = 0,
):
    """Подтверждение удаления длины питомца (в истории)"""
    builder = InlineKeyboardBuilder()
    data = {'pet_id': pet_id, 'company_id': company_id, 'group_id': group_id}
    builder.button(
        text='✅ ДА',
        callback_data=ChoiceDeleteLengthCallback(
            action='delete',
            page=page,
            user_tz=user_timezone,
            length_id=length_id,
            **data
        ).pack()
    )
    builder.button(
        text='❌ НЕТ',
        callback_data=ChoiceDeleteLengthCallback(
            action='cancel',
            page=page,
            user_tz=user_timezone,
            length_id=length_id,
            **data
        ).pack()
    )
    builder.adjust(2)
    return builder.as_markup()
