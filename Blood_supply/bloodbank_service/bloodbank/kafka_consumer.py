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

def get_consumer():
    """Get or create KafkaConsumer"""
    global _consumer
    if _consumer is None:
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
        except Exception as e:
            print(f"[Kafka Consumer] Connection failed: {e}")
            _consumer = None
            raise e
    return _consumer

def consumer_thread():
    """Consumer thread with robust retry logic"""
    global _consumer
    print("[Kafka Consumer] Consumer thread started.")
    
    while True:
        try:
            consumer = get_consumer()
            if consumer:
                for message in consumer:
                    try:
                        msg = message.value
                        prio = priority_map.get(msg.get("priority", "NORMAL"), 2)
                        submitted_at = msg.get("submitted_at", "")
                        heappush(priority_queue, (prio, submitted_at, msg))
                        print(f"[Kafka Consumer] Received request: {msg['request_id']} (priority: {msg.get('priority')})")
                    except Exception as e:
                        print(f"[Kafka Consumer] Error processing message: {e}")
            else:
                 # Should not happen if get_consumer raises, but safe check
                 time.sleep(5)

        except Exception as e:
            print(f"[Kafka Consumer] Connection/Consumption error: {e}. Retrying in 5 seconds...")
            # Reset consumer to force reconnection
            if _consumer:
                try:
                    _consumer.close()
                except:
                    pass
            _consumer = None
            time.sleep(5)


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
