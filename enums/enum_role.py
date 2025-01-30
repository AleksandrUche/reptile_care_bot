from enum import Enum


class UserRole(Enum):
    OWNER = "owner"
    ADMIN = "admin"
    BASE = "base"


class SubscriptionType(Enum):
    ONE_MONTH = "one month"
    TWO_MONTHS = "two months"
    SIX_MONTHS = "six months"
    YEAR = 'year'
