from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import register_events

from .views import db_to_csv


def start():
    scheduler = BackgroundScheduler()
    register_events(scheduler)

    @scheduler.scheduled_job("interval", hours=4, name="auto_csv")
    def ready():
        db_to_csv()

    scheduler.start()
