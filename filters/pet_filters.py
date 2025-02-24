import re

def is_alnum_with_spaces(text: str) -> bool:
    """Проверяет, что текст состоит только из букв, цифр и пробелов."""
    return bool(re.match(r'^[a-zA-Zа-яА-Я0-9\s]+$', text))