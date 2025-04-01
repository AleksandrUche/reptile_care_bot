import logging

from saq import CronJob, Queue
from saq.types import SettingsDict

from config_data.config import REDIS_URL
from tasks.feeding_events import run_check_feeding_events
from tasks.reminder_feedings import run_reminder_of_feedings

logger = logging.getLogger(__name__)

bot_queue = Queue.from_url(REDIS_URL)

worker_settings = SettingsDict(
    queue=bot_queue,
    functions=[],
    concurrency=5,
    cron_jobs=[
        CronJob(
            function=run_check_feeding_events,
            cron="* * * * */5", # каждые 5 минут
        ),
        CronJob(
            function=run_reminder_of_feedings,
            cron="* * * */1", # каждый час
        ),
    ],
)
