import os
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

_producer = None
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:9092')

_producer = None

def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            acks='all'
        )
    return _producer
def get_producer():
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8'),
            retries=5,
            acks='all'
        )
    return _producer

def publish_event(topic: str, payload: dict):
    try:
        producer = get_producer()
        producer = get_producer()
        future = producer.send(topic, payload)
        future.get(timeout=10)  
        future.get(timeout=10)  
        producer.flush()
        print(f"[Kafka Producer] Successfully published to {topic}: {payload}")
    except KafkaError as e:
        print(f"[Kafka Producer] Failed to publish to {topic}: {e}")
    except Exception as e:
        print(f"[Kafka Producer] Unexpected error: {e}")
