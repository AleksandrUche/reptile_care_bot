from aiogram import Router, F
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from database.models.user_models import UserOrm
from keyboards.inline_keyboards import inline_keyboards
from keyboards.inline_keyboards.inline_keyboards import main_menu_inline
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
            reply_markup=inline_keyboards.my_profile,
        )


@router.message(Command(commands='menu'))
async def get_main_menu(message: Message):
    await message.answer(
        text='📋Главное меню',
        reply_markup=main_menu_inline
    )


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


@router.message()
async def send_answer(message: Message):
    """Хэндлер для сообщений, которые не попали в другие хэндлеры"""
    await message.answer(text=LEXICON_RU['other_answer'])
