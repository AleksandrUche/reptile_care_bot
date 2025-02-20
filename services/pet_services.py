import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models.pets_models import CompanyOrm
from database.models.user_models import UserOrm

logger = logging.getLogger(__name__)


async def get_user_company(user_id: int, session: AsyncSession):
    """Возвращает все компании пользователя"""
    company = await session.scalar(
        select(UserOrm)
        .options(joinedload(UserOrm.companies))
        .filter(UserOrm.telegram_id == user_id)
    )
    return company.companies


async def get_groups_in_company(user_id: int, session: AsyncSession):
    """Возвращает все группы связанные с компанией пользователя"""
    ...


async def add_pet(user_id: int, pet_name: str, session: AsyncSession):
    """
    Добавляет питомца в компанию пользователя.
    """
    ...
