from django.core.management.base import BaseCommand
from hospital_app.kafka_consumer import get_consumer
from hospital_app.models import BloodRequest, HospitalInventory
from django.utils import timezone
import json


class Command(BaseCommand):
    help = "Runs the Kafka consumer for the Hospital Service"

    def handle(self, *args, **kwargs):
        # Topics the Hospital Service listens to (responses from bloodbank)
        topics = [
            "bloodbank.blood.approved",
            "bloodbank.blood.rejected",
        ]

        consumer = get_consumer(topics)

        self.stdout.write(self.style.SUCCESS("📡 Hospital Service Kafka Consumer is running..."))
        self.stdout.write(self.style.SUCCESS(f"👂 Listening to topics: {', '.join(topics)}"))

        for message in consumer:
            event_data = message.value
            topic = message.topic

            print("\n--------------------------------------")
            print(f"📥 Received event from topic: {topic}")
            print(f"📦 Data: {json.dumps(event_data, indent=2)}")
            print("--------------------------------------\n")

            request_id = event_data.get("request_id")
            if not request_id:
                self.stdout.write(
                    self.style.WARNING(f"⚠️  Missing request_id in event data. Skipping...")
                )
                continue

            try:
                blood_request = BloodRequest.objects.get(request_id=request_id)
                
                if topic == "bloodbank.blood.approved":
                    blood_request.status = 'APPROVED'
                    blood_request.processed_at = timezone.now()
                    
                    # Update hospital inventory when request is approved
                    blood_type = blood_request.blood_type
                    units_received = blood_request.units_required
                    
                    inventory, created = HospitalInventory.objects.get_or_create(
                        blood_type=blood_type,
                        batch_number='',
                        defaults={'quantity': units_received}
                    )
                    
                    if not created:
                        inventory.quantity += units_received
                        inventory.save()
                    
                    blood_request.save()
                    self.stdout.write(
                        self.style.SUCCESS(f"✅ Updated request {request_id} to APPROVED and inventory updated")
                    )
                    
                elif topic == "bloodbank.blood.rejected":
                    blood_request.status = 'REJECTED'
                    blood_request.processed_at = timezone.now()
                    # Update notes if reason provided in rejection
                    if event_data.get("reason"):
                        blood_request.notes = f"{blood_request.notes}\nRejection reason: {event_data.get('reason')}".strip()
                    blood_request.save()
                    self.stdout.write(
                        self.style.ERROR(f"❌ Updated request {request_id} to REJECTED")
                    )
                    
            except BloodRequest.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(
                        f"⚠️  Request {request_id} not found in database. "
                        "This may be from a different hospital or an old request."
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"❌ Error processing event: {str(e)}")
                )
