from aiogram.filters.callback_data import CallbackData

from enums.enum_role import Language


class LanguageSelectionCallback(CallbackData, prefix='edit_language'):
    language: Language
    user_tg_id: int


class EditMyProfileCallback(CallbackData, prefix='edit_my_profile'):
    action: str  # language
    user_tg_id: int
