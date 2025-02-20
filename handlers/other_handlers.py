from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards.inline_keyboards import main_menu_inline
from lexicon.lexicon import LEXICON_RU
from services.registration_services import user_registration

router = Router()


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    await user_registration(message, session)


@router.message(Command(commands='menu'))
async def get_main_menu(message: Message):
    await message.answer(
        text='📋Главное меню',
        reply_markup=main_menu_inline,
    )


@router.message(Command(commands='help'))
async def process_help_command(message: Message):
    await message.answer(text=LEXICON_RU['/help'])


@router.message()
async def send_answer(message: Message):
    """Хэндлер для сообщений, которые не попали в другие хэндлеры"""
    await message.answer(text=LEXICON_RU['other_answer'])


@router.callback_query(F.data == 'about_subscription')
async def process_buttons_press(callback: CallbackQuery):
    await callback.message.answer(
        text='📋Подписка позволяет вам добавлять больше двух питомцев, '
             'создавать компании/группы, делится ими с другими '
             'пользователями для администрирования и работы. Выдавать определенную роль '
             'в компании это может быть как рабочий так и администратор.\n'
             '🙂 Без подписки вы можете пользоваться ботом, но добавлять больше двух '
             'питомцев нельзя а так же нельзя создавать дополнительные компании и '
             'группы животных.\n\n'
             '⭐Стоимость полного доступа:\n'
             '...₽ - 30 дней\n'
             '...₽ - 60 дней\n'
             '...₽ - 90 дней\n'
             '...₽ - 183 дня\n'
             '...₽ - 365 дней\n'
    )
    await callback.answer()


@router.callback_query(F.data == 'about_bot')
async def process_buttons_press(callback: CallbackQuery):
    await callback.message.answer(
        text='🐾 О боте\n'
             'Управляйте животными, фермами или питомниками легко! Этот бот поможет:\n\n'
             '🏢 Создавать компании и группы для животных\n'
             '📊 Вести историю веса и здоровья питомцев\n'
             '⏰ Настраивать расписания кормлений с напоминаниями\n'
             '👥 Делиться доступом с помощниками\n'
             '💡 Автоматизировать рутину и сосредоточиться на главном\n\n'
             'Почему это удобно?\n'
             '✅ Все данные в одном месте\n'
             '✅ Совместная работа в реальном времени\n'
             '✅ Уведомления в Telegram-чате\n'
             '✅ Простой интерфейс даже для новичков\n'
             '🚀 Начните сейчас — добавьте первого питомца!\n\n'
             'Для заводчиков и всех, кто заботится о животных профессионально.\n'
    )
    await callback.answer()
