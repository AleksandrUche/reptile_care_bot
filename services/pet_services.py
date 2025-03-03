import logging

from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, aliased, selectinload

from database.models.pets_models import (
    CompanyOrm,
    PetOrm,
    WeightPetOrm,
    LengthPetOrm,
    MoltingPetOrm,
    GroupOrm,
)
from database.models.user_models import UserOrm

logger = logging.getLogger(__name__)


async def get_all_companies_user(user_id: int, session: AsyncSession):
    """Возвращает все компании пользователя"""
    result = await session.scalars(
        select(CompanyOrm)
        .join(UserOrm)
        .options(joinedload(CompanyOrm.user).load_only(UserOrm.telegram_id))
        .filter(UserOrm.telegram_id == user_id)
    )
    return result.unique().all()


async def get_company(company_id: int, session: AsyncSession):
    """Возвращает компанию по id"""
    return await session.scalar(
        select(CompanyOrm)
        .filter(CompanyOrm.id == company_id)
    )


async def get_company_and_groups(user_id: int, session: AsyncSession):
    """Возвращает компанию и все группы связанные с ней"""
    return await session.scalar(
        select(CompanyOrm)
        .options(joinedload(CompanyOrm.groups))
        .filter(CompanyOrm.user.has(telegram_id=user_id))
    )


async def add_pet(user_id: int, pet_name: str, session: AsyncSession):
    """
    Добавляет питомца в компанию пользователя, с группой 'По умолчанию'.
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


async def edit_pet_value(
    pet_id: int, name_field: str, value: str, session: AsyncSession
):
    """
    Изменяет значения указанного поля.
    :param pet_id: ID питомца.
    :param name_field: Имя поля, которое нужно обновить (например, "name").
    :param value: Новое значение для поля.
    :param session: Сессия.
    :return: True, если обновление прошло успешно, иначе False.
    """
    update_data = {name_field: value}
    stmt = update(PetOrm).filter(PetOrm.id == pet_id).values(**update_data)

    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при изменении \"{name_field}\" питомца: {e}',
                     exc_info=True)
    else:
        return True


async def delete_pet(pet_id: int, session: AsyncSession):
    """Удаление питомца по id"""
    stmt = delete(PetOrm).filter(PetOrm.id == pet_id)

    try:
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при удалении питомца с ID-{pet_id}: {e}', exc_info=True)
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


async def get_pet(pet_id: int, company_id: int, group_id: int, session: AsyncSession):
    """
    Возвращает объект питомца, название компании и группы, а также последние
    измерения длины, веса и последнюю дату линьки.
    :return: dict{pet_obj, company_name, group_name, latest_weight, latest_length, latest_molting_date}
    """
    latest_weight_subquery = (
        select(WeightPetOrm)
        .filter(WeightPetOrm.pet_id == pet_id)
        .order_by(WeightPetOrm.date_measure.desc())
        .limit(1)
        .subquery()
    )
    latest_weight_alias = aliased(WeightPetOrm, latest_weight_subquery)

    latest_length_subquery = (
        select(LengthPetOrm)
        .filter(LengthPetOrm.pet_id == pet_id)
        .order_by(LengthPetOrm.date_measure.desc())
        .limit(1)
        .subquery()
    )
    latest_length_alias = aliased(LengthPetOrm, latest_length_subquery)

    latest_molting_subquery = (
        select(MoltingPetOrm)
        .filter(MoltingPetOrm.pet_id == pet_id)
        .order_by(MoltingPetOrm.date_measure.desc())
        .limit(1)
        .subquery()
    )
    latest_molting_alias = aliased(MoltingPetOrm, latest_molting_subquery)

    stmt = (
        select(PetOrm)
        .outerjoin(latest_weight_alias, PetOrm.id == latest_weight_alias.pet_id)
        .outerjoin(latest_length_alias, PetOrm.id == latest_length_alias.pet_id)
        .outerjoin(latest_molting_alias, PetOrm.id == latest_molting_alias.pet_id)
        .options(
            selectinload(PetOrm.company).load_only(CompanyOrm.name),
            selectinload(PetOrm.group).load_only(GroupOrm.name),
        )
        .filter(
            PetOrm.id == pet_id,
            PetOrm.company_id == company_id,
            PetOrm.group_id == group_id,
        )
        .add_columns(
            CompanyOrm.name.label('company_name'),
            GroupOrm.name.label('group_name'),
            latest_weight_alias.weight.label('latest_weight'),
            latest_length_alias.length.label('latest_length'),
            latest_molting_alias.date_measure.label('latest_molting_date'),
        )
    )

    result = await session.execute(stmt)
    row = result.first()

    return {
        'pet': row.PetOrm,
        'company_name': row.company_name,
        'group_name': row.group_name,
        'latest_weight': row.latest_weight,
        'latest_length': row.latest_length,
        'latest_molting_date': row.latest_molting_date,
    }
