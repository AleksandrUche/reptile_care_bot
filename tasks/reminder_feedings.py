import asyncio
import logging
from datetime import time
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


async def _get_feedings_reminder(session: AsyncSession) -> Optional[list]:
    """
    Отдает расписание кормлений, у которых первое уведомление пользователю приходило и
    активно поле "Напомнить" (remind = True)
    """
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
                FeedingScheduleOrm.is_active == False,
                FeedingScheduleOrm.remind == True,
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


async def _send_notification_safe(bot, feeding: FeedingScheduleOrm):
    """Безопасная отправка уведомления с повторными попытками"""
    for _ in range(2):
        try:
            await bot.send_message(
                chat_id=feeding.pet.company.user.telegram_id,
                text=f'⏰ Напоминаю, пора покормить {feeding.pet.name}!\n'
                     f'Вид: {feeding.pet.view}\n'
                     f'Морфа: {feeding.pet.morph}\n'
                     f'Пол: {feeding.pet.gender.value}\n',
                reply_markup=shedule_feeding_approve,
            )
            return
        except TelegramAPIError as e:
            if "retry after" in str(e):
                wait_time = int(str(e).split()[-1])
                logger.warning(f"Флуд-контроль, ждем {wait_time} секунд")
                await asyncio.sleep(wait_time + 1)
            else:
                raise
    raise TelegramAPIError("Не удалось отправить сообщение после 2 попыток")


async def run_reminder_of_feedings(ctx):
    """
    Проверяет расписание кормлений, у которых пользователь поставил
    отметку «напомнить позже», и отправляет уведомление.
    """
    logger.info("Проверяю события повторного напоминания кормлений...")
    async with async_session() as session:
        try:
            feedings = await _get_feedings_reminder(session)

            if not feedings:
                return None

            bot = Bot(token=BOT_TOKEN)
            for feeding in feedings:
                try:
                    await _send_notification_safe(bot, feeding)
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