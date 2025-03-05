from datetime import datetime
from config_data.config import TIME_ZONE


def edit_date_format(date: datetime) -> str:
    try:
        return date.astimezone(TIME_ZONE).strftime('%d.%m.%Y')
    except AttributeError:
        return '---'