import json
import logging
import time
import json
import logging
import time
from django.core.management.base import BaseCommand
from django.conf import settings
from kafka import KafkaConsumer
from your_app.models import Notification

logger = logging.getLogger(__name__)
from django.conf import settings
from kafka import KafkaConsumer
from your_app.models import Notification

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Run Kafka consumer for notifications"
    help = "Run Kafka consumer for notifications"

    def handle(self, *args, **options):
        kafka_servers = getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', ['localhost:9092'])
        topics = ['blood-requests', 'blood-request-validation', 'low-stock-alerts']

        self.stdout.write(self.style.SUCCESS(f'Connecting to Kafka at {kafka_servers}...'))

        try:
            # Create consumer once, outside the loop
            consumer = KafkaConsumer(
                *topics,
                bootstrap_servers=kafka_servers,
                auto_offset_reset='earliest', # Gets everything from the start
                enable_auto_commit=True,
                group_id=None  # REMOVE THE GROUP ID TEMPORARILY
            )

            self.stdout.write(self.style.SUCCESS(
                'Notification consumer started — listening to: ' + ','.join(topics)
            ))

            while True:
                try:
                    for msg in consumer:
                        # Skip empty messages
                        if msg.value is None:
                            self.stdout.write(self.style.WARNING(f"Empty message on {msg.topic}, skipping"))
                            continue

                        # Parse JSON safely
                        try:
                            data = msg.value if isinstance(msg.value, dict) else json.loads(msg.value.decode('utf-8'))
                        except (json.JSONDecodeError, AttributeError, UnicodeDecodeError) as e:
                            self.stdout.write(self.style.ERROR(f"Invalid JSON on {msg.topic}: {msg.value} — {e}"))
                            continue

                        topic = msg.topic
                        self.stdout.write(self.style.NOTICE(f"Message on {topic}: {data}"))

                        # Handle messages
                        if topic == 'blood-requests':
                            message = f"New request: {data.get('quantity')} units of {data.get('blood_type')} from {data.get('hospital_name') or data.get('hospital_id')}"
                            Notification.objects.create(
                                event_type='hospital_request',
                                message=message,
                                hospital_name=data.get('hospital_name') or data.get('hospital_id'),
                                blood_type=data.get('blood_type'),
                                units=data.get('quantity'),
                                target='blood_bank',
                                payload=data
                            )

                        elif topic == 'blood-request-validation':
                            message = f"Request {data.get('request_id')} is {data.get('status')}"
                            Notification.objects.create(
                                event_type='request_status',
                                message=message,
                                hospital_name=data.get('hospital_name') or data.get('hospital_id'),
                                target='hospital',
                                payload=data
                            )

                        elif topic == 'low-stock-alerts':
                            message = f"LOW BLOOD ALERT: {data.get('blood_type')} has {data.get('current_units')} units (threshold {data.get('threshold')})."
                            Notification.objects.create(
                                event_type='low_blood',
                                message=message,
                                blood_type=data.get('blood_type'),
                                target='blood_bank',
                                payload=data
                            )

                        else:
                            Notification.objects.create(
                                event_type='system',
                                message=str(data),
                                target='system',
                                payload=data
                            )

                except KeyboardInterrupt:
                    self.stdout.write(self.style.WARNING('Consumer stopped by user'))
                    break
                except Exception:
                    logger.exception("Consumer crashed, retrying in 5 seconds...")
                    time.sleep(5)

        except Exception:
            logger.exception("Failed to start Kafka consumer")
