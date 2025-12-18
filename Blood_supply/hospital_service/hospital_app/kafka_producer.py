# hospital_app/kafka_producer.py

import os
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:29092")

# Do NOT create producer here!
_producer = None

def get_producer():
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                retries=5,
                acks="all",
                linger_ms=5,
            )
            print("[Kafka Producer] Successfully connected")
        except Exception as e:
            print(f"[Kafka Producer] Connection failed: {e}")
            _producer = None
    return _producer

def publish_event(topic: str, payload: dict, timeout: float = 10.0) -> bool:
    producer = get_producer()
    if producer is None:
        print("[Kafka] Producer not available – message not sent")
        return False

    try:
        future = producer.send(topic, payload)
        future.get(timeout=timeout)
        producer.flush()
        print(f"[Kafka] Successfully published to topic '{topic}'")
        return True
    except KafkaError as e:
        print(f"[Kafka] Send failed: {e}")
        return False
    except Exception as e:
        print(f"[Kafka] Unexpected error: {e}")
        return False