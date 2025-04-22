from typing import Literal

from aiogram.filters.callback_data import CallbackData

from enums.pets_enum import GenderRole


# TODO: КОММЕНТЫ ОПИСАНИЯ МОДЕЛИ НЕ ВЕЗДЕ УКАЗАНЫ, УНИФИЦИРУЙ К ОДНОМУ ВИДУ


class AllPetPaginationCallback(CallbackData, prefix="pet_all_paginate"):
    action: Literal["prev", "next"]
    page: int


class PetsCallback(CallbackData, prefix="pet"):
    pet_id: int
    company_id: int
    group_id: int


class EditPetCallback(CallbackData, prefix="edit_pet"):
    field: str  # Поле, которое нужно изменить (например, "name", "morph"...)
    pet_id: int
    company_id: int  # для возврата к детальному просмотру питомца
    group_id: int


class DeletePetCallback(CallbackData, prefix="delete_pet"):
    """Для удаления питомца"""

    action: str  # menu
    pet_id: int
    company_id: int  # для возврата к детальному просмотру питомца
    group_id: int


class ChoiceDeletePet(CallbackData, prefix="choice_delete_pet"):
    """Для подтверждения удаления питомца"""

    action: Literal["delete", "cancel"]
    pet_id: int
    pet_name: str


class GenderSelectionCallback(CallbackData, prefix="gender_pet"):
    action: GenderRole
    pet_id: int
    company_id: int  # для возврата к детальному просмотру питомца
    group_id: int


class ScheduleFeedingsCallback(CallbackData, prefix="schedule_feeding"):
    """
    Фабрика для добавления графика кормлений
    action:
    menu, planned_schedule
    add_schedule, single_addition, group_addition, group_addition_and_description, every_day,
    """

    action: str
    pet_id: int
    company_id: int  # для возврата к детальному просмотру питомца
    group_id: int


class ConfirmFeedingEventsCallback(CallbackData, prefix="confirm_feeding_events"):
    """
    Фабрика для обработки напоминаний кормления (для подтверждения, отмены или
    повторного напоминания уведомления.)
    action: approve, cancel, remind
    """

    action: str
    event_feeding_id: int
    pet_id: int
    pet_name: str


class FeedingSchedulePaginationCallback(CallbackData, prefix="schedule_paginate"):
    action: Literal["prev", "next"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int


class FeedingScheduleDetailCallback(CallbackData, prefix="schedule_detail"):
    action: Literal["detail", "delete", "edit"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    schedule_id: int


class ChoiceDeleteFeedingSchedule(
    CallbackData, prefix="choice_delete_feeding_schedule"
):
    """Для подтверждения удаления запланированного кормления."""

    action: str  # delete, cancel
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    schedule_id: int


class HistoryPetCallback(CallbackData, prefix="history_pet"):
    """Фабрика для истории событий питомца."""

    action: Literal["menu", "feeding_pet_history", "molting_history"]
    pet_id: int
    company_id: int
    group_id: int


class FeedingHistoryPaginationCallback(CallbackData, prefix="feeding_paginate"):
    action: str  # Действие: prev или next
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int


class FeedingHistoryDetailCallback(CallbackData, prefix="feeding_detail"):
    """Для взаимодействия с событиями кормления"""

    action: Literal["detail", "edit_date", "edit_description", "delete"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    feeding_id: int


class ChoiceDeleteFeeding(CallbackData, prefix="choice_delete_feeding"):
    """Для подтверждения удаления кормления"""

    action: Literal["delete", "cancel"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    feeding_id: int


class MoltingHistoryPaginationCallback(CallbackData, prefix="molting_paginate"):
    action: Literal["prev", "next"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int


class MoltingHistoryDetailCallback(CallbackData, prefix="molting_detail"):
    """Для взаимодействия с событиями линьки"""

    action: Literal["detail", "edit_date", "edit_description", "delete"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    molting_id: int


class ChoiceDeleteMoltingCallback(CallbackData, prefix="choice_delete_molting"):
    """Для подтверждения удаления линьки"""

    action: Literal["cancel", "delete"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    molting_id: int


class WeightHistoryPaginationCallback(CallbackData, prefix="weight_paginate"):
    action: Literal["prev", "next"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int


class WeightHistoryDetailCallback(CallbackData, prefix="weight_detail"):
    """Для взаимодействия с событиями измерения веса"""

    action: Literal["detail", "edit_date", "edit_description", "delete"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    weight_id: int


class ChoiceDeleteWeightCallback(CallbackData, prefix="choice_delete_weight"):
    """Для подтверждения удаления веса питомца"""

    action: Literal["delete", "cancel"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    weight_id: int


class LengthHistoryPaginationCallback(CallbackData, prefix="length_paginate"):
    """Для просмотра событий измерения длины"""

    action: Literal["prev", "next"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int


class LengthHistoryDetailCallback(CallbackData, prefix="length_detail"):
    """Для взаимодействия с событиями измерения длины"""

    action: Literal["detail", "edit_date", "edit_description", "delete"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    length_id: int


class ChoiceDeleteLengthCallback(CallbackData, prefix="choice_delete_length"):
    """Для подтверждения удаления измерения длины питомца"""

    action: Literal["delete", "cancel"]
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    length_id: int
