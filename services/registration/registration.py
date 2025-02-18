from aiogram.types import Message
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.pets_models import CompanyOrm, GroupOrm
from database.models.user_models import UserOrm
from keyboards.inline_keyboards import inline_keyboards
from keyboards.reply_keyboards import reply_keyboards
from main import logger


async def user_exists(telegram_id: int, session: AsyncSession) -> UserOrm | None:
    """
    Проверяет, существует ли пользователь с указанным telegram_id.
    Возвращает True, если пользователь найден, иначе False.
    """
    stmt = select(UserOrm).filter(UserOrm.telegram_id == telegram_id)
    res = await session.execute(stmt)
    return res.scalar()


async def user_registration(message: Message, session: AsyncSession):
    """
    Проверяет на наличие пользователя в системе, если пользователя нет в БД,
    регистрирует его и создает компанию и группу по умолчанию.
    """
    user_exist = await user_exists(message.from_user.id, session)
    if user_exist:
        await message.answer(
            text=f'Рады вас видеть снова {user_exist.first_name}😊\n'
                 'Напомню, я бот-помощник,  для ухода за вашими питомцами 🦎🐍🦖\n',
            reply_markup=inline_keyboards.my_profile,
        )
    else:
        user = UserOrm(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
        )
        session.add(user)
        await session.flush()

        company = CompanyOrm(name='По умолчанию', user_id=user.id)
        session.add(company)
        await session.flush()

        group = GroupOrm(name='По умолчанию', company_id=company.id)
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
                reply_markup=reply_keyboards.main_menu
            )
