from typing import Literal

from aiogram.filters.callback_data import CallbackData

from enums.enum_role import Language


class LanguageSelectionCallback(CallbackData, prefix="edit_language"):
    language: Language
    user_tg_id: int


class EditMyProfileCallback(CallbackData, prefix="edit_my_profile"):
    action: Literal["language", "edit_time_zone"]
    user_tg_id: int


class EditTimeZoneSelectCallback(CallbackData, prefix="edit_time_zone"):
    action: Literal["geolocation", "search_city"]
    user_tg_id: int


class ApproveTimeZoneCallback(CallbackData, prefix="approve_time_zone"):
    user_tg_id: int
    time_zone: str
    offset: int
    lng: float
    lat: float
