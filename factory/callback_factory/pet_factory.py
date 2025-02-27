from aiogram.filters.callback_data import CallbackData


class PaginationCallbackFactory(CallbackData, prefix='paginate'):
    action: str  # Действие: 'prev' или 'next'
    page: int


class PetsCallbackFactory(CallbackData, prefix='pet'):
    id: int
    company_id: int
    group_id: int


class EditPetCallback(CallbackData, prefix='edit_pet'):
    field: str  # Поле, которое нужно изменить (например, "name", "morph"...)
    pet_id: int
