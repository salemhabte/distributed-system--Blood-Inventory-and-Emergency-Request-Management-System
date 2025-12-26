# hospital_app/kafka_consumer.py
import os
import json
import threading
import time
from kafka import KafkaConsumer
from kafka.errors import NoBrokersAvailable
from .models import BloodRequest

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

def get_kafka_consumer():
    while True:
        try:
            return KafkaConsumer(
                'blood-request-validation',
                bootstrap_servers=bootstrap_servers,
                group_id='hospital-status-group',
                auto_offset_reset='latest',  # Only new messages
                enable_auto_commit=True,
                value_deserializer=lambda x: json.loads(x.decode('utf-8'))
            )
        except NoBrokersAvailable:
            print("[Hospital Kafka Consumer] Broker unavailable. Retrying in 5 seconds...")
            time.sleep(5)
        except Exception as e:
            print(f"[Hospital Kafka Consumer] Error connecting: {e}")
            time.sleep(5)

consumer = None

def status_update_thread():
    global consumer
    print("[Hospital Kafka Consumer] Initializing...")
    consumer = get_kafka_consumer()
    print("[Hospital Kafka Consumer] Connected! Listening for validation results...")
    
    try:
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
    except Exception as e:
        print(f"[Hospital Kafka Consumer] Consumer loop failed: {e}")

threading.Thread(target=status_update_thread, daemon=True).start()
