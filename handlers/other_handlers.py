from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from lexicon.lexicon import LEXICON_RU

router = Router()

button1 = KeyboardButton(text='Добавить питомца')
button2 = KeyboardButton(text='Мои питомцы')
keyboard = [[button1, button2]]

my_keyboard = ReplyKeyboardMarkup(
    keyboard=keyboard,
    resize_keyboard=True
)


@router.message(CommandStart())
async def process_start_command(message: Message):
    await message.answer(
        text=LEXICON_RU['/start'],
        reply_markup=my_keyboard,
    )


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


@router.message()
async def send_answer(message: Message):
    """Хэндлер для сообщений, которые не попали в другие хэндлеры"""
    await message.answer(text=LEXICON_RU['other_answer'])