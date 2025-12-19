# kafka_producer.py
import os
import json
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Use Docker service name by default
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

_producer = None

def get_producer() -> KafkaProducer:
    """Lazy initialization of Kafka producer."""
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5,
            linger_ms=5,
            acks="all",
        )
    return _producer
# Use Docker service name by default
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "kafka:9092")

_producer = None

def get_producer() -> KafkaProducer:
    """Lazy initialization of Kafka producer."""
    global _producer
    if _producer is None:
        _producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda v: json.dumps(v).encode("utf-8"),
            retries=5,
            linger_ms=5,
            acks="all",
        )
    return _producer

def publish_event(topic: str, payload: dict, timeout: float = 10.0) -> bool:
    """Publish a JSON message to Kafka safely."""
    """Publish a JSON message to Kafka safely."""
    try:
        producer = get_producer()
        future = producer.send(topic, payload)
        producer = get_producer()
        future = producer.send(topic, payload)
        future.get(timeout=timeout)
        producer.flush()
        print(f"[Kafka Producer] Successfully published to {topic}: {payload}")
        producer.flush()
        print(f"[Kafka Producer] Successfully published to {topic}: {payload}")
        return True
    except KafkaError as e:
        print(f"[Kafka Producer] KafkaError: {e}")
        print(f"[Kafka Producer] KafkaError: {e}")
        return False
    except Exception as exc:
        print(f"[Kafka Producer] Unexpected error: {exc}")
        print(f"[Kafka Producer] Unexpected error: {exc}")
        return False