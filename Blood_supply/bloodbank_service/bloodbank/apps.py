from django.apps import AppConfig

class BloodbankConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'bloodbank'

    def ready(self):
        # Import here to avoid AppRegistryNotReady
        from .kafka_consumer import start_consumer_threads
        start_consumer_threads()