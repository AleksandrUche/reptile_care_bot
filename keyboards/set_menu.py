from aiogram import Bot
from aiogram.types import BotCommand


async def set_main_menu(bot: Bot):
    main_menu_commands = [
        BotCommand(command='/group',
                   description='Группы'),
        BotCommand(command='/add_pet',
                   description='Добавить питомца'),
        BotCommand(command='/feeding',
                   description='Кормлениe'),
        BotCommand(command='/pets',
                   description='Питомцы'),
        BotCommand(command='/help',
                   description='Справка по работе бота'),
        BotCommand(command='/support',
                   description='Поддержка'),
    ]

    await bot.set_my_commands(main_menu_commands)