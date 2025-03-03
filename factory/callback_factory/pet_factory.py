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
    action: str # menu, delete, cancel
    pet_id: int
    pet_name: str


class GenderSelectionCallback(CallbackData, prefix='gender_pet'):
    action: GenderRole
    pet_id: int
    company_id: int # для возврата к детальному просмотру питомца
    group_id: int
