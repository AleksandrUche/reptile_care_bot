from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.user_models import UserOrm
from keyboards.reply_keyboards import reply_keyboards
from lexicon.lexicon import LEXICON_RU

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    user = UserOrm(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    session.add(user)
    try:
        await session.commit()
        await message.answer(
            text=f'Здравствуйте, {user.first_name}! Вы успешно зарегистрированы!\n'
                 'Я бот-помощник создан для ухода за вашими питомцами 🦎🐍🦖\n',
            reply_markup=reply_keyboards.main_menu
        )
    except IntegrityError:
        await message.answer(
            text=f'Рады вас видеть снова {user.first_name}😊\n'
                 'Напомню, я бот-помощник,  для ухода за вашими питомцами 🦎🐍🦖\n',
        )


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


@router.message(F.text == 'Профиль')
async def send_answer(message: Message):
    await message.answer(text=LEXICON_RU['profile'])


@router.message()
async def send_answer(message: Message):
    """Хэндлер для сообщений, которые не попали в другие хэндлеры"""
    await message.answer(text=LEXICON_RU['other_answer'])
