from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import default_state
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from keyboards.inline_keyboards.other_kb import main_menu_inline, back_to_main_menu
from lexicon.lexicon import LEXICON_RU
from services.registration_services import user_registration

router = Router(name='other')


@router.message(CommandStart())
async def start_handler(message: Message, session: AsyncSession):
    await user_registration(message, session)


@router.message(Command('menu'))
async def get_main_menu(message: Message):
    """Срабатывает на команду /menu (возврат в меню)"""
    await message.answer(
        text='📋Главное меню📋',
        reply_markup=main_menu_inline,
    )


@router.callback_query(F.data == 'back_to_main_menu')
async def get_main_menu_callback(callback: CallbackQuery):
    """Срабатывает на callback query (возврат в меню)"""
    await callback.answer()
    await callback.message.edit_text(
        text='📋Главное меню📋',
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
    await callback.message.edit_text(
        text='📋Подписка позволяет вам добавлять больше двух питомцев,\n'
        'создавать компании/группы, делится ими с другими пользователями\n'
        'для администрирования и работы. Выдавать определенную роль\n'
        'в компании это может быть как рабочий так и администратор.\n'
        '🙂 Без подписки вы можете пользоваться ботом, но добавлять больше двух\n'
        'питомцев нельзя а так же нельзя создавать дополнительные компании и\n'
        'группы животных.\n\n'
        '⭐Стоимость полного доступа:\n'
        '...₽ - 30 дней\n'
        '...₽ - 60 дней\n'
        '...₽ - 90 дней\n'
        '...₽ - 183 дня\n'
        '...₽ - 365 дней\n',
        reply_markup=back_to_main_menu,
    )
    await callback.answer()


@router.callback_query(F.data == 'about_bot')
async def process_buttons_press(callback: CallbackQuery):
    await callback.message.edit_text(
        text='🐾<b>О боте</b>\n\n'
        'Управляйте животными, фермами или питомниками легко!\n\n'
        'Этот бот поможет:\n\n'
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
        'Для заводчиков и всех, кто заботится о животных профессионально.\n',
        reply_markup=back_to_main_menu,
    )
    await callback.answer()


@router.callback_query(F.data == 'cancel_state', ~StateFilter(default_state))
async def cancel_state_handler(message: Message, state: FSMContext):
    """Выходит из машины состояния"""
    await state.clear()
    await message.answer('Действие отменено.')
