from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable
import json
import os

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
)

_producer = None


def get_producer():
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5,
                acks="all",
            )
        except NoBrokersAvailable:
            print("[kafka_producer] Kafka not available, producer disabled")
            _producer = None
    return _producer


def send_event(topic, value):
    producer = get_producer()
    if not producer:
        print(f"[kafka_producer] Skipping event, Kafka unavailable: {topic}")
        return

    try:
        future = producer.send(topic, value)
        future.get(timeout=10.0)
        producer.flush()
    except Exception as e:
        print(f"[kafka_producer] Error sending event to {topic}: {e}")
