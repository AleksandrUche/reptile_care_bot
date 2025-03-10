from enum import Enum


class UserRole(Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    USER = 'user'


class SubscriptionType(Enum):
    ONE_MONTH = 'one month'
    TWO_MONTHS = 'two months'
    SIX_MONTHS = 'six months'
    YEAR = 'year'


class UserRoleCompany(Enum):
    OWNER = 'owner'
    ADMIN = 'admin'
    EDITOR = 'editor'
    VIEWER = 'viewer'


class Language(Enum):
    EN = 'en'
    RU = 'ru'