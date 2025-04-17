from django.apps import AppConfig


class LabsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'labs'

    def ready(self):
        # Import and register the signals
        import labs.signals