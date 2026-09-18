from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'core'

    def ready(self):
        import core.apis.signals.track_signal
        import core.apis.signals.notification_signals
        import core.apis.signals.tasks_signals