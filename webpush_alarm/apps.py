from django.apps import AppConfig


class WebpushAlarmConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "webpush_alarm"

    # def ready(self):
    # import webpush_alarm.signals
