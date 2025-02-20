import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import BOT_TOKEN
from database.engine import async_session
from handlers import user_handler, other_handlers, pet_hendlers
from keyboards.set_menu import set_main_menu
from middlewares.db import DataBaseSession

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

    logger.info('Starting bot')

    storage = MemoryStorage()

    bot = Bot(
        token=BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
    dp = Dispatcher(storage=storage)

    dp.startup.register(set_main_menu)

    logger.info('Подключаем роутеры')
    dp.include_router(user_handler.router)
    dp.include_router(pet_hendlers.router)

    dp.include_router(other_handlers.router)


    logger.info('Подключаем миддлвари')
    dp.update.middleware(DataBaseSession(session_pool=async_session))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
