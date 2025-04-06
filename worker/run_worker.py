import logging

from saq import CronJob, Queue
from saq.types import SettingsDict

from config_data.config import REDIS_URL
from tasks.feeding_events import run_check_feeding_events
from tasks.reminder_feedings import run_reminder_of_feedings

logger = logging.getLogger(__name__)
logger.info('Run Worker')

bot_queue = Queue.from_url(REDIS_URL)

worker_settings = SettingsDict(
    queue=bot_queue,
    functions=[],
    concurrency=10,
    cron_jobs=[
        CronJob(
            function=run_check_feeding_events,
            cron="*/2 * * * *", # каждые 2 минуты
        ),
        CronJob(
            function=run_reminder_of_feedings,
            cron="0 * * * *", # каждый час в 00 минут
        )
    ],
)
