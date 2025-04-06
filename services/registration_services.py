import logging

from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.pets_models import CompanyOrm, GroupOrm
from database.models.user_models import UserOrm
from keyboards.inline_keyboards import inline_keyboards

logger = logging.getLogger(__name__)


async def get_user(telegram_id: int, session: AsyncSession) -> UserOrm | None:
    """
    Проверяет, существует ли пользователь с указанным telegram_id.
    Возвращает объект пользователя.
    """
    stmt = select(UserOrm).filter(UserOrm.telegram_id == telegram_id)
    try:
        res = await session.execute(stmt)
        return res.scalar()
    except Exception as e:
        logger.info(
            f'Профиля пользователя c id {telegram_id} - нет: {e}',
            exc_info=True
        )


async def user_registration(message: Message, session: AsyncSession):
    """
    Проверяет на наличие пользователя в системе, если пользователя нет в БД,
    регистрирует его и создает компанию и группу по умолчанию.
    """
    user_exist = await get_user(message.from_user.id, session)
    keyboard = inline_keyboards.main_menu_inline

    language_user = message.from_user.language_code
    language = language_user if language_user else 'en'

    if user_exist:
        await message.answer(
            text=f'Рады вас видеть снова {user_exist.first_name}😊\n'
                 'Напомню, я бот-помощник,  для ухода за вашими питомцами 🦎🐍🦖\n',
            reply_markup=keyboard,
        )
    else:
        user = UserOrm(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            language=language,
        )
        session.add(user)
        await session.flush()

        company = CompanyOrm(
            name='Моя компания',
            description='Первая компания, создается автоматически.',
            user_id=user.id
        )
        session.add(company)
        await session.flush()

        group = GroupOrm(
            name='Мои питомцы',
            description='Данная группа создана автоматически.',
            company_id=company.id
        )
        session.add(group)
        try:
            await session.commit()
        except Exception as e:
            logger.error(f'Ошибка при регистрации пользователя: {e}', exc_info=True)
            await message.answer(
                text='Произошла ошибка при регистрации. Пожалуйста, попробуйте позже.'
            )
        else:
            await message.answer(
                text=f'Здравствуйте, {user.first_name}! Вы успешно зарегистрированы!\n'
                     'Я бот-помощник создан для ухода за вашими питомцами 🦎🐍🦖\n',
                reply_markup=keyboard
            )
