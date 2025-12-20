import os
import json
import threading
import time
import logging
from kafka import KafkaConsumer, errors
from heapq import heappush, heappop
from django.utils import timezone
from .models import BloodRequest, BloodRequestValidation, LowStockAlert

logger = logging.getLogger(__name__)

# Kafka bootstrap server (Docker service name)
BOOTSTRAP_SERVERS = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

# Topics
TOPICS = ['blood-requests', 'blood-request-validation', 'low-stock-alerts']

# Priority queue for processing (optional, if you need priority)
PRIORITY_MAP = {'EMERGENCY': 0, 'URGENT': 1, 'NORMAL': 2}
priority_queue = []

_consumer = None
_consumer_lock = threading.Lock()


def get_consumer():
    """Lazy Kafka consumer initialization with retry"""
    global _consumer
    if _consumer is None:
        with _consumer_lock:
            if _consumer is None:
                while True:
                    try:
                        _consumer = KafkaConsumer(
                            *TOPICS,
                            bootstrap_servers=BOOTSTRAP_SERVERS,
                            group_id='notification-service-group',
                            auto_offset_reset='earliest',
                            enable_auto_commit=True,
                            value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                        )
                        logger.info(f"[Kafka] Connected to {BOOTSTRAP_SERVERS}")
                        break
                    except errors.NoBrokersAvailable:
                        logger.warning("[Kafka] Broker not available. Retrying in 5s...")
                        time.sleep(5)
    return _consumer


def process_message(topic, data):
    """Save messages to the database based on topic"""
    if topic == 'blood-requests':
        BloodRequest.objects.create(
            hospital_name=data.get('hospital_name') or data.get('hospital_id', 'Unknown'),
            hospital_id=data.get('hospital_id'),
            blood_type=data.get('blood_type'),
            quantity=data.get('quantity', 0),
            message=f"New request: {data.get('quantity')} units of {data.get('blood_type')} from {data.get('hospital_name') or data.get('hospital_id')}",
            payload=data
        )
        logger.info(f"[Kafka] Saved BloodRequest {data.get('request_id')}")

    elif topic == 'blood-request-validation':
        status = data.get('status', '').upper()
        BloodRequestValidation.objects.create(
            request_id=data.get('requestId') or data.get('request_id', 'Unknown'),
            hospital_name=data.get('hospital_name'),
            hospital_id=data.get('hospitalId') or data.get('hospital_id'),
            status=status,
            message=f"Request {data.get('requestId') or data.get('request_id')} is {status}",
            payload=data
        )
        logger.info(f"[Kafka] Saved BloodRequestValidation {data.get('request_id')}")

    elif topic == 'low-stock-alerts':
        LowStockAlert.objects.create(
            blood_type=data.get('blood_type'),
            current_units=data.get('current_units', 0),
            threshold=data.get('threshold'),
            message=f"LOW BLOOD ALERT: {data.get('blood_type')} has {data.get('current_units')} units (threshold {data.get('threshold')}).",
            payload=data
        )
        logger.info(f"[Kafka] Saved LowStockAlert {data.get('blood_type')}")


def consumer_thread():
    """Kafka consumer thread"""
    consumer = get_consumer()
    for message in consumer:
        msg = message.value
        topic = message.topic
        logger.info(f"[Kafka] Received message on {topic}: {msg}")
        process_message(topic, msg)


def start_consumer():
    """Start Kafka consumer in a daemon thread"""
    thread = threading.Thread(target=consumer_thread, daemon=True)
    thread.start()
    logger.info("[Kafka] Consumer thread started")
