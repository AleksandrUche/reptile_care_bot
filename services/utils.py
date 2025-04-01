import re
from datetime import datetime, time, date

from config_data.config import TIME_ZONE


def edit_date_format(date: datetime) -> str:
    try:
        return date.astimezone(TIME_ZONE).strftime('%d.%m.%Y')
    except AttributeError:
        return '---'


def parse_date(date_str: str) -> datetime:
    """
    Преобразует дату в формате ДД.ММ.ГГ или ДД.ММ.ГГГГ в объект datetime.
    Разделитель может быть ".", ",", "/", "пробел".
    """
    try:
        day, month, year = map(int, re.split(r'[.,/\s]+', date_str))
        if year < 100:
            if year < 50:
                year += 2000  # 21 век (2000-е)
            else:
                year += 1900  # 20 век (1900-е)
        return datetime(year=year, month=month, day=day)
    except (ValueError, IndexError):
        raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГ или ДД.ММ.ГГГГ.")


def parse_time(time_str: str) -> time:
    """
    Преобразует время в формате ЧЧ:ММ в объект time.
    Разделитель может быть ":", ".", ",", "пробел" и "/".
    """
    try:
        hours, minutes = map(int, re.split(r'[:,./\s]+', time_str))
        if hours > 23:
            raise ValueError("Часы должны быть в диапазоне 0-23")
        if minutes > 59:
            raise ValueError("Минуты должны быть в диапазоне 0-59")
        return time(hour=hours, minute=minutes)
    except (ValueError, IndexError):
        raise ValueError("Неверный формат даты. Используйте ДД.ММ.ГГ или ДД.ММ.ГГГГ.")