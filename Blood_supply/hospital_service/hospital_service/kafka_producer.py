# kafka_producer.py
import os
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError

# Read broker address from env first, fallback to localhost:9092
KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")

def _make_producer():
    # Configure producer with sensible defaults; you can tune retries, acks etc.
    return KafkaProducer(
        bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        retries=5,           # try a few times on transient errors
        linger_ms=5,         # small batching latency
        acks="all",          # wait for leader+replicas (safer)
    )

# Create a single producer instance for the module
_producer = _make_producer()

def publish_event(topic: str, payload: dict, timeout: float = 10.0) -> bool:
    """
    Publish a JSON-serializable payload to the given Kafka topic.
    Returns True on success, False on failure.
    """
    try:
        # send returns a future; get() waits for ack
        future = _producer.send(topic, payload)
        # block until the send is acknowledged or timeout
        future.get(timeout=timeout)
        # flush to make sure the message is out (optional; producer.flush() is global)
        _producer.flush(0)
        return True
    except KafkaError as e:
        # handle/log error in real app
        print(f"[kafka_producer] publish failed: {e}")
        return False
    except Exception as exc:
        print(f"[kafka_producer] unexpected error: {exc}")
        return False
