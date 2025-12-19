from django.core.management.base import BaseCommand
from hospital_app.kafka_consumer import get_consumer, close_consumer
from hospital_app.models import BloodRequest, HospitalInventory
from hospital_app.kafka_events import (
    BLOODBANK_BLOOD_APPROVED, BLOODBANK_BLOOD_REJECTED,
    BLOODBANK_INVENTORY_UPDATED, INVENTORY_LOWSTOCK
)
from django.utils import timezone
import json
import logging
import signal
import sys

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Runs the Kafka consumer for the Hospital Service"
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.consumer = None
        self.should_stop = False

    def add_arguments(self, parser):
        parser.add_argument(
            '--timeout',
            type=int,
            default=60,
            help='Consumer timeout in seconds (default: 60)',
        )

    def signal_handler(self, sig, frame):
        """Handle shutdown signals gracefully"""
        self.stdout.write(self.style.WARNING("\n🛑 Shutting down consumer..."))
        self.should_stop = True
        if self.consumer:
            close_consumer(self.consumer)
        sys.exit(0)

    def handle(self, *args, **kwargs):
        # Register signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
        
        # Topics the Hospital Service listens to (responses from bloodbank)
        topics = [
            BLOODBANK_BLOOD_APPROVED,
            BLOODBANK_BLOOD_REJECTED,
            BLOODBANK_INVENTORY_UPDATED,
            INVENTORY_LOWSTOCK,
        ]

        self.consumer = get_consumer(topics)
        
        if not self.consumer:
            self.stdout.write(
                self.style.ERROR("❌ Failed to initialize Kafka consumer. Exiting...")
            )
            return

        self.stdout.write(self.style.SUCCESS("📡 Hospital Service Kafka Consumer is running..."))
        self.stdout.write(self.style.SUCCESS(f"👂 Listening to topics: {', '.join(topics)}"))
        self.stdout.write(self.style.WARNING("Press Ctrl+C to stop...\n"))

        try:
            for message in self.consumer:
                if self.should_stop:
                    break
                    
                event_data = message.value
                topic = message.topic

                self.stdout.write("\n" + "="*50)
                self.stdout.write(f"📥 Received event from topic: {topic}")
                self.stdout.write(f"📦 Data: {json.dumps(event_data, indent=2)}")
                self.stdout.write("="*50 + "\n")

                try:
                    if topic == BLOODBANK_BLOOD_APPROVED:
                        self._handle_blood_approved(event_data)
                    elif topic == BLOODBANK_BLOOD_REJECTED:
                        self._handle_blood_rejected(event_data)
                    elif topic == BLOODBANK_INVENTORY_UPDATED:
                        self._handle_inventory_updated(event_data)
                    elif topic == INVENTORY_LOWSTOCK:
                        self._handle_low_stock(event_data)
                    else:
                        self.stdout.write(
                            self.style.WARNING(f"⚠️  Unknown topic: {topic}")
                        )
                except Exception as e:
                    logger.error(f"Error processing message from {topic}: {e}", exc_info=True)
                    self.stdout.write(
                        self.style.ERROR(f"❌ Error processing event: {str(e)}")
                    )
                    
        except KeyboardInterrupt:
            self.stdout.write(self.style.WARNING("\n🛑 Interrupted by user"))
        except Exception as e:
            logger.error(f"Consumer error: {e}", exc_info=True)
            self.stdout.write(self.style.ERROR(f"❌ Consumer error: {str(e)}"))
        finally:
            if self.consumer:
                close_consumer(self.consumer)
            self.stdout.write(self.style.SUCCESS("✅ Consumer stopped gracefully"))

    def _handle_blood_approved(self, event_data):
        """Handle blood request approval event"""
        request_id = event_data.get("request_id")
        if not request_id:
            self.stdout.write(
                self.style.WARNING("⚠️  Missing request_id in approval event. Skipping...")
            )
            return

        try:
            blood_request = BloodRequest.objects.get(request_id=request_id)
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
                self.style.SUCCESS(
                    f"✅ Request {request_id} APPROVED. "
                    f"Inventory updated: {blood_type} +{units_received} units (Total: {inventory.quantity})"
                )
            )
        except BloodRequest.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Request {request_id} not found in database. "
                    "This may be from a different hospital or an old request."
                )
            )

    def _handle_blood_rejected(self, event_data):
        """Handle blood request rejection event"""
        request_id = event_data.get("request_id")
        if not request_id:
            self.stdout.write(
                self.style.WARNING("⚠️  Missing request_id in rejection event. Skipping...")
            )
            return

        try:
            blood_request = BloodRequest.objects.get(request_id=request_id)
            blood_request.status = 'REJECTED'
            blood_request.processed_at = timezone.now()
            
            # Update notes if reason provided in rejection
            if event_data.get("reason"):
                rejection_note = f"\nRejection reason: {event_data.get('reason')}"
                blood_request.notes = (blood_request.notes or "") + rejection_note
            
            blood_request.save()
            self.stdout.write(
                self.style.ERROR(
                    f"❌ Request {request_id} REJECTED. "
                    f"Reason: {event_data.get('reason', 'No reason provided')}"
                )
            )
        except BloodRequest.DoesNotExist:
            self.stdout.write(
                self.style.WARNING(
                    f"⚠️  Request {request_id} not found in database."
                )
            )

    def _handle_inventory_updated(self, event_data):
        """Handle bloodbank inventory updated event (for reference)"""
        blood_type = event_data.get("blood_type")
        quantity = event_data.get("quantity")
        self.stdout.write(
            self.style.SUCCESS(
                f"ℹ️  Bloodbank inventory updated: {blood_type} = {quantity} units"
            )
        )

    def _handle_low_stock(self, event_data):
        """Handle low stock warning event"""
        blood_type = event_data.get("blood_type")
        quantity = event_data.get("quantity")
        threshold = event_data.get("threshold", 50)
        self.stdout.write(
            self.style.WARNING(
                f"⚠️  LOW STOCK ALERT: {blood_type} = {quantity} units (Threshold: {threshold})"
            )
        )
