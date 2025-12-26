# bloodbank/kafka_consumer.py
import os
import json
import threading
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from heapq import heappush, heappop
from django.utils import timezone
from django.db import models
from .models import InventoryItem
from .kafka_producer import publish_event

# Use Docker service port by default (internal port 29092)
BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")
TOPIC = "blood-requests"

priority_map = {"EMERGENCY": 0, "URGENT": 1, "NORMAL": 2}
priority_queue = []

_consumer = None

def get_consumer(max_retries=10, retry_delay=5):
    """Lazy init KafkaConsumer with retry logic"""
    global _consumer
    if _consumer is None:
        for attempt in range(max_retries):
            try:
                _consumer = KafkaConsumer(
                    TOPIC,
                    bootstrap_servers=BOOTSTRAP_SERVERS,
                    group_id="bloodbank-priority-group",
                    auto_offset_reset="earliest",
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode("utf-8")),
                    consumer_timeout_ms=1000  # Timeout for polling
                )
                print(f"[Kafka Consumer] Successfully connected to Kafka at {BOOTSTRAP_SERVERS}")
                return _consumer
            except NoBrokersAvailable as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"[Kafka Consumer] Kafka not available (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[Kafka Consumer] Failed to connect to Kafka after {max_retries} attempts: {e}")
                    raise
            except Exception as e:
                print(f"[Kafka Consumer] Unexpected error connecting to Kafka: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise
    return _consumer

def process_request(msg):
    """Process blood request from queue"""
    try:
        available = (
            InventoryItem.objects.filter(
                blood_type=msg["blood_type"],
                expiry_date__gt=timezone.now().date()
            )
            .aggregate(total=models.Sum("quantity"))["total"]
            or 0
        )
    except Exception as e:
        print(f"[Kafka Consumer] Error calculating available blood: {e}")
        available = 0

    if available >= msg["units_required"]:
        remaining = msg["units_required"]
        for item in InventoryItem.objects.filter(blood_type=msg["blood_type"]).order_by("expiry_date"):
            if remaining <= 0:
                break
            if item.quantity >= remaining:
                item.quantity -= remaining
                item.save()
                remaining = 0
            else:
                remaining -= item.quantity
                item.quantity = 0
                item.save()

        response = {
            "request_id": msg["request_id"],
            "status": "APPROVED",
            "units_allocated": msg["units_required"],
            "allocated_at": timezone.now().isoformat()
        }
    else:
        response = {
            "request_id": msg["request_id"],
            "status": "REJECTED",
            "reason": "Insufficient stock"
        }

    try:
        publish_event("blood-request-validation", response)
        
        # Check for low stock after processing request
        from .inventory_utils import check_and_alert_low_stock
        check_and_alert_low_stock(msg["blood_type"])
    except Exception as e:
        print(f"[Kafka Consumer] Error publishing validation response: {e}")

def processor_thread():
    while True:
        if priority_queue:
            _, _, msg = heappop(priority_queue)
            process_request(msg)
        threading.Event().wait(0.5)

def consumer_thread():
    """Consumer thread with retry logic"""
    consumer = None
    while consumer is None:
        try:
            consumer = get_consumer()
        except Exception as e:
            print(f"[Kafka Consumer] Failed to initialize consumer: {e}. Retrying in 10 seconds...")
            time.sleep(10)
    
    print("[Kafka Consumer] Consumer thread started, listening for messages...")
    try:
        for message in consumer:
            try:
                msg = message.value
                prio = priority_map.get(msg.get("priority", "NORMAL"), 2)
                submitted_at = msg.get("submitted_at", "")
                heappush(priority_queue, (prio, submitted_at, msg))
                print(f"[Kafka Consumer] Received request: {msg['request_id']} (priority: {msg.get('priority')})")
            except Exception as e:
                print(f"[Kafka Consumer] Error processing message: {e}")
    except Exception as e:
        print(f"[Kafka Consumer] Consumer thread error: {e}. Restarting...")
        global _consumer
        _consumer = None
        # Restart the thread
        threading.Thread(target=consumer_thread, daemon=True).start()

def start_consumer_threads():
    """Start consumer and processor threads lazily with error handling"""
    try:
        # Start processor thread (doesn't need Kafka)
        threading.Thread(target=processor_thread, daemon=True).start()
        print("[Kafka] Processor thread started")
        
        # Start consumer thread (will retry if Kafka is not ready)
        threading.Thread(target=consumer_thread, daemon=True).start()
        print("[Kafka] Consumer thread starting (will connect when Kafka is ready)...")
    except Exception as e:
        print(f"[Kafka] Error starting consumer threads: {e}")
        # Don't crash the app if Kafka is not available
