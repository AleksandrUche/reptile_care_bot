from aiogram import Router
from aiogram.filters import Command
from aiogram.filters import CommandStart
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards.inline_keyboards import main_menu_inline
from lexicon.lexicon import LEXICON_RU
from services.registration.registration import user_registration

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    await user_registration(message, session)


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
