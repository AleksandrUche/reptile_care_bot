from aiogram.filters.callback_data import CallbackData

from enums.pets_enum import GenderRole


class PaginationCallback(CallbackData, prefix='paginate'):
    action: str  # Действие: 'prev' или 'next'
    page: int


class PetsCallback(CallbackData, prefix='pet'):
    pet_id: int
    company_id: int
    group_id: int


class EditPetCallback(CallbackData, prefix='edit_pet'):
    field: str  # Поле, которое нужно изменить (например, "name", "morph"...)
    pet_id: int
    company_id: int  # для возврата к детальному просмотру питомца
    group_id: int


class DeletePetCallback(CallbackData, prefix='delete_pet'):
    """Для удаления питомца"""
    action: str # menu,
    pet_id: int


class ChoiceDeletePet(CallbackData, prefix='choice_delete_pet'):
    """Для подтверждения удаления питомца"""
    action: str  # delete, cancel
    pet_id: int
    pet_name: str


class GenderSelectionCallback(CallbackData, prefix='gender_pet'):
    action: GenderRole
    pet_id: int
    company_id: int # для возврата к детальному просмотру питомца
    group_id: int


class SheduleFeedingsCallback(CallbackData, prefix='shedule_feeding'):
    """
    Фабрика для добавления графика кормлений
    action:
    menu, planned_shedule
    add_shedule, single_addition, group_addition, group_addition_and_description, every_day,
    """
    action: str
    pet_id: int
    company_id: int # для возврата к детальному просмотру питомца
    group_id: int


class ConfirmFeedingEventsCallback(CallbackData, prefix='confirm_feeding_events'):
    """
    Фабрика для обработки напоминаний кормления (для подтверждения, отмены или
    повторного напоминания уведомления.)
    action: approve, cancel, remind
    """
    action: str
    event_feeding_id: int
    pet_id: int
    pet_name: str


class FeedingShedulePaginationCallback(CallbackData, prefix='shedule_paginate'):
    action: str  # Действие: prev или next
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int


class FeedingSheduleDetailCallback(CallbackData, prefix='shedule_detail'):
    action: str  # Действия: detail, edit, delete
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    shedule_id: int


class ChoiceDeleteFeedingShedule(CallbackData, prefix='choice_delete_feeding_shedule'):
    """Для подтверждения удаления запланированного кормления"""
    action: str  # delete, cancel
    page: int
    user_tz: str
    pet_id: int
    company_id: int
    group_id: int
    shedule_id: int
