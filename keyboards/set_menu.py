from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/start',
                   description='Начать'),
        BotCommand(command='/menu',
                   description='Главное меню'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
    ]

    await bot.set_my_commands(main_menu_commands)