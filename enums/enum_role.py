from enum import StrEnum


class UserRole(StrEnum):
    OWNER = 'owner'
    ADMIN = 'admin'
    USER = 'user'


class SubscriptionType(StrEnum):
    ONE_MONTH = 'one month'
    TWO_MONTHS = 'two months'
    SIX_MONTHS = 'six months'
    YEAR = 'year'


class UserRoleCompany(StrEnum):
    OWNER = 'owner'
    ADMIN = 'admin'
    EDITOR = 'editor'
    VIEWER = 'viewer'


class Language(StrEnum):
    EN = 'en'
    RU = 'ru'
