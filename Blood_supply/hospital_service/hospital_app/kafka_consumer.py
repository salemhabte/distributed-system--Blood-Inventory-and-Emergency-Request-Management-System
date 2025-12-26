# hospital_app/kafka_consumer.py
import os
import json
import threading
from kafka import KafkaConsumer
from .models import BloodRequest

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

consumer = KafkaConsumer(
    'blood-request-validation',
    bootstrap_servers=bootstrap_servers,
    group_id='hospital-status-group',
    auto_offset_reset='latest',  # Only new messages
    enable_auto_commit=True,
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def status_update_thread():
    print("[Hospital Kafka Consumer] Listening for validation results...")
    for message in consumer:
        data = message.value
        request_id = data.get('request_id')
        status = data.get('status')

        try:
            request = BloodRequest.objects.get(request_id=request_id)
            request.status = status
            request.save()
            print(f"[Hospital] Updated request {request_id} status to {status}")
        except BloodRequest.DoesNotExist:
            print(f"[Hospital] Request {request_id} not found — ignoring")

threading.Thread(target=status_update_thread, daemon=True).start()