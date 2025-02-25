import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from database.models.pets_models import CompanyOrm, PetOrm
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


async def get_company_and_groups(user_id: int, session: AsyncSession):
    """Возвращает компанию и все группы связанные с ней"""
    company = await session.scalar(
        select(CompanyOrm)
        .options(joinedload(CompanyOrm.groups))
        .filter(CompanyOrm.user.has(telegram_id=user_id))
    )
    return company


async def add_pet(user_id: int, pet_name: str, session: AsyncSession):
    """
    Добавляет питомца в компанию пользователя, с группой "По умолчанию".
    """
    user_company = await get_company_and_groups(user_id, session)

    pet = PetOrm(
        name=pet_name,
        company_id=user_company.id,
        group_id=user_company.groups[0].id,
    )
    session.add(pet)
    try:
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при добавлении питомца: {e}', exc_info=True)
        return False
    else:
        return True


async def get_my_companies_and_pets(user_id: int, session: AsyncSession):
    result = await session.scalars(
        select(CompanyOrm)
        .join(UserOrm, CompanyOrm.user_id == UserOrm.id)
        .where(UserOrm.telegram_id == user_id)
        .options(joinedload(CompanyOrm.pets))
    )
    return result.unique().all()
