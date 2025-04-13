import itertools
import logging
from datetime import datetime, timezone, timedelta

from aiogram.types import CallbackQuery
from sqlalchemy import DateTime
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
    FeedingPetOrm,
    FeedingScheduleOrm,
)
from database.models.user_models import UserOrm
from factory.callback_factory.pet_factory import SheduleFeedingsCallback
from keyboards.keyboard_utils.inline_kb_utils import no_time_zone_inline_kb

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
    try:
        stmt = delete(PetOrm).filter(PetOrm.id == pet_id)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при удалении питомца с ID-{pet_id}: {e}', exc_info=True)
        raise


async def get_my_companies_and_pets(user_id: int, session: AsyncSession):
    result = await session.scalars(
        select(CompanyOrm)
        .join(UserOrm, CompanyOrm.user_id == UserOrm.id)
        .where(UserOrm.telegram_id == user_id)
        .options(joinedload(CompanyOrm.pets))
    )
    return result.unique().all()


async def get_pet(pet_id: int, company_id: int, group_id: int, session: AsyncSession):
    return await session.scalar(
        select(PetOrm)
        .filter(
            PetOrm.id == pet_id,
            PetOrm.company_id == company_id,
            PetOrm.group_id == group_id,
        )
    )


async def get_pet_all_information(pet_id: int, company_id: int, group_id: int,
                                  session: AsyncSession):
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


async def add_weight_pet(pet_id: int, weight: float, session: AsyncSession):
    """
    Добавляет вес для определенного питомца.
    """
    current_date = datetime.now().replace(tzinfo=timezone.utc)
    stmt = WeightPetOrm(
        weight=weight,
        pet_id=pet_id,
        date_measure=current_date,
    )
    session.add(stmt)
    try:
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при добавлении веса: {e}', exc_info=True)
        return False
    else:
        return True


async def add_length_pet(pet_id: int, length: float, session: AsyncSession):
    """
    Добавляет длину для определенного питомца.
    """
    current_date = datetime.now().replace(tzinfo=timezone.utc)
    stmt = LengthPetOrm(
        length=length,
        pet_id=pet_id,
        date_measure=current_date,
    )
    session.add(stmt)
    try:
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при добавлении длины: {e}', exc_info=True)
        return False
    else:
        return True


async def add_molting_pet(pet_id: int, date_molting: DateTime, session: AsyncSession):
    """
    Добавляет дату линьку для определенного питомца.
    """
    stmt = MoltingPetOrm(
        pet_id=pet_id,
        date_measure=date_molting,
    )
    session.add(stmt)
    try:
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при добавлении даты линьки: {e}', exc_info=True)
        return False
    else:
        return True


async def add_feeding_pet_date(
    pet_id: int, session: AsyncSession, description: str = None
):
    """
    Добавляет дату кормления питомца.
    """
    try:
        current_date = datetime.now().replace(tzinfo=timezone.utc)
        stmt = FeedingPetOrm(
            pet_id=pet_id,
            date_feed=current_date,
            description=description,
        )
        session.add(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при добавлении кормления: {e}', exc_info=True)
        raise


async def add_feeding_shedule(
    pet_id: int, date: datetime, session: AsyncSession, description: str = None
):
    """
    Добавляет дату запланированного кормления питомца.
    """
    try:
        stmt = FeedingScheduleOrm(
            pet_id=pet_id,
            description=description,
            scheduled_time=date.astimezone(timezone.utc),
        )
        session.add(stmt)
        await session.commit()
    except Exception as e:
        logger.error(f'Ошибка при добавлении даты запланированного кормления: {e}',
                     exc_info=True)
        raise


async def add_group_feeding_shedule(
    pet_id: int, date: datetime, offset: int, repeat: int, session: AsyncSession,
):
    """
    Добавляет график кормления питомца.
    """
    schedules = []
    date_insertion = date.astimezone(timezone.utc)
    for _ in range(repeat):
        stmt = FeedingScheduleOrm(
            pet_id=pet_id,
            scheduled_time=date_insertion,
        )
        schedules.append(stmt)
        date_insertion += timedelta(days=offset)
    try:
        session.add_all(schedules)
        await session.commit()
    except Exception as e:
        logger.error(
            f'Ошибка при добавлении группы запланированных кормлений: {e}',
            exc_info=True
        )


async def add_group_feeding_and_description_shedule(
    pet_id: int,
    date: datetime,
    offset: int,
    repeat: int,
    description_1: str,
    repeat_description_1: int,
    description_2: str,
    repeat_description_2: int,
    session: AsyncSession,
):
    """
    Добавляет график кормления питомца и описание к напоминанию.
    """
    description_schema = []
    for _ in range(repeat_description_1):
        description_schema.append(description_1)
    for _ in range(repeat_description_2):
        description_schema.append(description_2)
    description = itertools.cycle(description_schema)

    schedules = []
    date_insertion = date.astimezone(timezone.utc)
    for _ in range(repeat):
        stmt = FeedingScheduleOrm(
            pet_id=pet_id,
            description=next(description),
            scheduled_time=date_insertion,
        )
        schedules.append(stmt)
        date_insertion += timedelta(days=offset)
    try:
        session.add_all(schedules)
        await session.commit()
    except Exception as e:
        logger.error(
            f'Ошибка при добавлении группы запланированных кормлений c описаниями: {e}',
            exc_info=True
        )


async def time_zone_is_not_set(
    callback: CallbackQuery, callback_data: SheduleFeedingsCallback
):
    """Отправляет в чат сообщение с инлайн клавой для установки таймзоны"""
    inline_kb = await no_time_zone_inline_kb(
        callback.from_user.id,
        callback_data.pet_id,
        callback_data.company_id,
        callback_data.group_id,
    )
    await callback.message.answer(
        text='Временная зона не установлена.\n'
             'Пожалуйста, укажите её в настройках профиля.',
        reply_markup=inline_kb,
    )


async def change_reminder_feeding_shedule(
    event_feeding_id: int, pet_id: int, remind: bool, session: AsyncSession
):
    """Отменяет повторное уведомление кормления питомца"""
    try:
        stmt = update(FeedingScheduleOrm).filter(
            FeedingScheduleOrm.id == event_feeding_id,
            FeedingScheduleOrm.pet_id == pet_id,
        ).values(remind=remind)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(
            f'Ошибка при изменении статуса "напоминания" кормления питомца: {e}',
            exc_info=True
        )
        raise


async def get_feeding_shedule(feeding_id: int, session: AsyncSession):
    """Возвращает информацию о запланированном кормлении по id"""
    return await session.scalar(
        select(FeedingScheduleOrm)
        .filter(FeedingScheduleOrm.id == feeding_id)
    )


async def edit_feeding_shedule(
    shedule_id: int, date: datetime, description: str, session: AsyncSession
):
    """Изменяет значения указанного поля."""
    try:
        stmt = update(FeedingScheduleOrm).filter(
            FeedingScheduleOrm.id == shedule_id
        ).values(scheduled_time=date.astimezone(timezone.utc), description=description)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(
            f'Ошибка при редактировании события кормления: {e}', exc_info=True
        )
        raise


async def get_planned_pet_feeding_schedule(pet_id: int, session: AsyncSession):
    """Возвращает все запланированные кормления питомца"""
    try:
        result = await session.scalars(
            select(FeedingScheduleOrm)
            .filter(
                FeedingScheduleOrm.pet_id == pet_id,
                FeedingScheduleOrm.is_active == True,
            ).order_by(FeedingScheduleOrm.scheduled_time)
        )
        return result.all()
    except Exception as e:
        logger.info(
            f'У питомца c id {pet_id} нет запланированного графика кормлений. \n'
            f'Ошибка: {e}', exc_info=True
        )
        raise


async def delete_feeding_shedule(shedule_id: int, session: AsyncSession):
    """Удаление запланированного кормления по id"""
    try:
        stmt = delete(FeedingScheduleOrm).filter(FeedingScheduleOrm.id == shedule_id)
        await session.execute(stmt)
        await session.commit()
    except Exception as e:
        logger.error(
            f'Ошибка при удалении запланированного кормления с ID-{shedule_id}: {e}',
            exc_info=True)
        raise
