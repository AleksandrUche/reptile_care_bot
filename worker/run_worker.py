import sys

from loguru import logger
from saq import CronJob, Queue
from saq.types import SettingsDict

from config_data.config import REDIS_URL
from tasks.feeding_events import run_check_feeding_events
from tasks.reminder_feedings import run_reminder_of_feedings

logger.remove()
logger.add(
    sys.stderr,
    format='<green>{time:DD-MM-YYYY HH:mm:ss}</green> | <level>{level}</level> | '
    '<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - '
    '<level>{message}</level>',
    level='INFO',
)

bot_queue = Queue.from_url(REDIS_URL)


async def startup(ctx):
    logger.info('Запущен Worker SAQ!')


async def shutdown(ctx):
    logger.info('Остановлен Worker SAQ!')


worker_settings = SettingsDict(
    queue=bot_queue,
    functions=[],
    concurrency=10,
    cron_jobs=[
        CronJob(
            function=run_check_feeding_events,
            cron='*/2 * * * *',  # каждые 2 минуты
        ),
        CronJob(
            function=run_reminder_of_feedings,
            cron='0 * * * *',  # каждый час в 00 минут
        ),
    ],
    startup=startup,
    shutdown=shutdown,
)
