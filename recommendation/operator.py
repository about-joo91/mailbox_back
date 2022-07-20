from apscheduler.schedulers.background import BackgroundScheduler
from django_apscheduler.jobstores import DjangoJobStore, register_events

from .views import test


def start():
    scheduler = BackgroundScheduler()
    scheduler.add_jobstore(DjangoJobStore(), "djangojobstore")
    register_events(scheduler)

    @scheduler.scheduled_job("cron", minute="*/1", name="auto_mail")
    def db():
        test()

    scheduler.start()
