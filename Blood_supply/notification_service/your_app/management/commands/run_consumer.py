from django.core.management.base import BaseCommand
from notification_service.kafka_consumer import get_consumer
from notification_service.kafka_producer import publish_event
import json


class Command(BaseCommand):
    help = "Runs the Kafka consumer for the Notification Service"

    def handle(self, *args, **kwargs):
        # Topics the Notification Service listens to
        topics = [
            "hospital.blood.requested",
            "bloodbank.blood.approved",
            "bloodbank.blood.rejected",
            "bloodbank.inventory.updated",
            "inventory.lowstock"
        ]

        consumer = get_consumer(topics)

        self.stdout.write(self.style.SUCCESS("📡 Notification Service Kafka Consumer is running..."))

        for message in consumer:
            event_data = message.value
            topic = message.topic

            print("\n--------------------------------------")
            print(f"📥 Received event from topic: {topic}")
            print(f"📦 Data: {json.dumps(event_data, indent=2)}")
            print("--------------------------------------\n")

            # TODO: Later you will save notification to DB
            # TODO: Then send in-app notifications
            # TODO: Then publish 'notification.send' event using publish_event()
            
            # Example sending notification event back into Kafka
            notification_event = {
                "notificationId": event_data.get("requestId", "unknown"),
                "recipientId": event_data.get("hospitalId", "unknown"),
                "recipientType": "HOSPITAL",
                "message": f"New event received on topic {topic}",
                "eventType": "REQUEST_CREATED",
                "timestamp": event_data.get("timestamp")
            }

            # publish_event("notification.send", notification_event)
            # print("📤 Published notification.send event")
