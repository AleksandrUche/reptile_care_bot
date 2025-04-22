import asyncio

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

from config_data.config import BOT_TOKEN
from database.engine import async_session
from handlers.root_router import main_router
from keyboards.set_menu import set_main_menu
from logging import logger
from middlewares.db import DataBaseSession


async def main():
    await logger.ainfo("Starting bot...")

    storage = MemoryStorage()

    bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    dp = Dispatcher(storage=storage)

    dp.startup.register(set_main_menu)

    await logger.ainfo("Подключаем routers")
    dp.include_router(main_router)

    await logger.ainfo("Подключаем middlewares")
    dp.update.middleware(DataBaseSession(session_pool=async_session))

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
