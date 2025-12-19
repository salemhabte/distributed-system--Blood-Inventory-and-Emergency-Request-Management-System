import os
import json
import threading
from kafka import KafkaConsumer
from heapq import heappush, heappop
from django.utils import timezone
from django.db import models
from .models import InventoryItem
from .kafka_producer import publish_event

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

priority_map = {'EMERGENCY': 0, 'URGENT': 1, 'NORMAL': 2}
priority_queue = []

_consumer = None
_consumer_lock = threading.Lock()


def get_consumer():
    """
    Lazy Kafka consumer initialization.
    Kafka will NOT connect until this function is called.
    """
    global _consumer

    if _consumer is None:
        with _consumer_lock:
            if _consumer is None:
                _consumer = KafkaConsumer(
                    'blood-requests',
                    bootstrap_servers=bootstrap_servers,
                    group_id='bloodbank-priority-group',
                    auto_offset_reset='earliest',
                    enable_auto_commit=True,
                    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
                )
    return _consumer


def process_request(msg):
    available = InventoryItem.objects.filter(
        blood_type=msg['blood_type'],
        expiry_date__gt=timezone.now().date()
    ).aggregate(total=models.Sum('quantity'))['total'] or 0

    if available >= msg['units_required']:
        remaining = msg['units_required']
        for item in InventoryItem.objects.filter(
            blood_type=msg['blood_type']
        ).order_by('expiry_date'):
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
            'request_id': msg['request_id'],
            'status': 'APPROVED',
            'units_allocated': msg['units_required'],
            'allocated_at': timezone.now().isoformat()
        }
    else:
        response = {
            'request_id': msg['request_id'],
            'status': 'REJECTED',
            'reason': 'Insufficient stock'
        }

    publish_event('blood-request-validation', response)


def processor_thread():
    while True:
        if priority_queue:
            _, _, msg = heappop(priority_queue)
            process_request(msg)
        threading.Event().wait(0.5)


def consumer_thread():
    consumer = get_consumer()   # Kafka connects ONLY here
    for message in consumer:
        msg = message.value
        prio = priority_map.get(msg.get('priority', 'NORMAL'), 2)
        submitted_at = msg.get('submitted_at', '')
        heappush(priority_queue, (prio, submitted_at, msg))
        print(
            f"[Kafka Consumer] Received request: "
            f"{msg['request_id']} (priority: {msg.get('priority')})"
        )


def start_consumer_threads():
    """
    Explicit entry point.
    Safe to call ONLY when Django server starts.
    """
    threading.Thread(target=consumer_thread, daemon=True).start()
    threading.Thread(target=processor_thread, daemon=True).start()
    print("[Kafka] Priority consumer threads started")
