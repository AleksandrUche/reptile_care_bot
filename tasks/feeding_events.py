import asyncio
import logging
from datetime import time, datetime, timezone
from typing import Optional

from aiogram import Bot
from aiogram.exceptions import TelegramAPIError
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from config_data.config import BOT_TOKEN
from database.engine import async_session
from database.models.pets_models import CompanyOrm, PetOrm, FeedingScheduleOrm
from database.models.user_models import UserOrm
from keyboards.inline_keyboards.inline_keyboards import shedule_feeding_approve

logger = logging.getLogger(__name__)


async def _get_feeding_schedule(session: AsyncSession) -> Optional[list]:
    """Отдает расписание кормлений, у которых дата и время меньше текущей даты и времени"""
    try:
        stmt = (
            select(FeedingScheduleOrm)
            .options(
                joinedload(FeedingScheduleOrm.pet)
                .joinedload(PetOrm.company)
                .joinedload(CompanyOrm.user)
                .load_only(
                    UserOrm.telegram_id,
                )
            )
            .filter(
                FeedingScheduleOrm.scheduled_time <= datetime.now(timezone.utc),
                FeedingScheduleOrm.is_active == True
            )
            .order_by(FeedingScheduleOrm.scheduled_time)
        )
        result = await session.execute(stmt)
        return result.scalars().all()
    except Exception as e:
        logger.info(
            f'Не удалось найти запланированные кормления: {e}', exc_info=True
        )
        return None


async def _send_notification_safe(
    bot, feeding: FeedingScheduleOrm, session: AsyncSession
):
    """Безопасная отправка уведомления с повторными попытками"""
    for _ in range(2):
        try:
            await bot.send_message(
                chat_id=feeding.pet.company.user.telegram_id,
                text=f'⏰ Пора покормить {feeding.pet.name}!\n'
                     f'Вид: {feeding.pet.view}\n'
                     f'Морфа: {feeding.pet.morph}\n'
                     f'Описание: {feeding.description}\n'
                     f'Пол питомца: {feeding.pet.gender.value}\n'
                     f'Дата кормления: {feeding.scheduled_time}'
                ,
                reply_markup=shedule_feeding_approve,
            )
            feeding.is_active = False
            await session.commit()
            return
        except TelegramAPIError as e:
            if "retry after" in str(e):
                wait_time = int(str(e).split()[-1])
                logger.warning(f"Флуд-контроль, ждем {wait_time} секунд")
                await asyncio.sleep(wait_time + 1)
            else:
                raise
    raise TelegramAPIError("Не удалось отправить сообщение после 2 попыток")


async def run_check_feeding_events(ctx):
    """Проверяет расписание кормлений и отправляет уведомления"""
    logger.info("Проверяю события кормления...")
    async with async_session() as session:
        try:
            feedings = await _get_feeding_schedule(session)

            if not feedings:
                return None

            bot = Bot(token=BOT_TOKEN)
            for feeding in feedings:
                try:
                    await _send_notification_safe(bot, feeding, session)
                    time.sleep(0.05)
                except Exception as e:
                    await session.rollback()
                    logger.info(
                        f'Не удалось отправить сообщение пользователю о кормлении: {e}',
                        exc_info=True
                    )

        except Exception as e:
            logger.info(
                f'Не удалось найти запланированные кормления: {e}', exc_info=True
            )




if __name__ == '__main__':
    # Тестовый запуск
    async def test_func():
        async with async_session() as session:
            aa = await _get_feeding_schedule(session)
            bot = Bot(token=BOT_TOKEN)
            await _send_notification_safe(bot, aa[0], session)
    asyncio.run(test_func())
