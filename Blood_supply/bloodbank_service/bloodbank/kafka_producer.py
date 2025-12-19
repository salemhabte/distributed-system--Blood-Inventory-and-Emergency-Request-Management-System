# bloodbank/kafka_producer.py
import os
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,
    acks='all'
)

def publish_event(topic: str, payload: dict):
    try:
        future = producer.send(topic, payload)
        future.get(timeout=10)  # Wait for ack
        producer.flush()
        print(f"[Kafka Producer] Successfully published to {topic}: {payload}")
    except KafkaError as e:
        print(f"[Kafka Producer] Failed to publish to {topic}: {e}")
    except Exception as e:
        print(f"[Kafka Producer] Unexpected error: {e}")