from django.apps import AppConfig
import logging
import os

logger = logging.getLogger(__name__)

class YourAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'your_app'

    def ready(self):
        import sys
        if 'makemigrations' in sys.argv or 'migrate' in sys.argv:
            return

        # Auto-start Kafka consumer if enabled
        if os.environ.get('RUN_KAFKA_CONSUMER', 'true').lower() == 'true':
            try:
                from .run_consumer import start_consumer
                start_consumer()
                logger.info("[YourApp] Kafka consumer auto-started")
            except Exception as e:
                logger.error(f"[YourApp] Failed to start Kafka consumer: {e}")
