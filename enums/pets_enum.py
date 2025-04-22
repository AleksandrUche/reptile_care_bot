from enum import Enum


class GenderRole(Enum):
    BOY = "мальчик"
    GIRL = "девочка"
    NOT_DEFINED = "не определен"


class MeasureUnitFood(Enum):
    GRAM = "г"
    KILOGRAM = "кг"
    QUANTITY = "шт."
    MISS = ""
