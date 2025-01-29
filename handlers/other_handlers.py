from aiogram import Router, F
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from keyboards.reply_keyboards import reply_keyboards
from lexicon.lexicon import LEXICON_RU

router = Router()


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=reply_keyboards.main_menu,
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
