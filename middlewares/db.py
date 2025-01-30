from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from sqlalchemy.orm import sessionmaker


class DataBaseSession(BaseMiddleware):
    def __init__(self, session_pool: sessionmaker):
        self.session_pool = session_pool

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with self.session_pool() as session:
            data['session'] = session
            try:
                return await handler(event, data)
            except Exception as e:
                # В случае ошибки откатываем изменения
                await session.rollback()
                raise e
            finally:
                # Сессия автоматически закрывается
                pass