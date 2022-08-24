from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from django.conf import settings
from django_apscheduler.jobstores import register_events

from user.services.report_service import get_reported_user_over_condition

from .views import db_to_csv


def start():
    scheduler = BackgroundScheduler(timezone=settings.TIME_ZONE)
    register_events(scheduler)

    # @scheduler.scheduled_job("interval", seconds=5, name="auto_csv")
    @scheduler.scheduled_job("interval", hours=4, name="auto_csv")
    def ready():
        db_to_csv()

    scheduler.add_job(
        get_reported_user_over_condition,
        trigger=CronTrigger(day_of_week="mon", hour="03", minute="00"),
        max_instances=1,
        name="check_reported_user",
    )

    scheduler.start()
