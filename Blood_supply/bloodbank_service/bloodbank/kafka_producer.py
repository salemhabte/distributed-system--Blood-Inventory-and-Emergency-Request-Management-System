
import os
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError, NoBrokersAvailable

# Use internal Docker port (29092) by default
bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

_producer = None

def get_producer(max_retries=10, retry_delay=5):
    """Get or create Kafka producer with retry logic"""
    global _producer
    if _producer is None:
        for attempt in range(max_retries):
            try:
                _producer = KafkaProducer(
                    bootstrap_servers=bootstrap_servers,
                    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                    retries=5,
                    acks='all',
                    request_timeout_ms=30000
                )
                print(f"[Kafka Producer] Successfully connected to Kafka at {bootstrap_servers}")
                return _producer
            except NoBrokersAvailable as e:
                if attempt < max_retries - 1:
                    wait_time = retry_delay * (attempt + 1)
                    print(f"[Kafka Producer] Kafka not available (attempt {attempt + 1}/{max_retries}). Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"[Kafka Producer] Failed to connect to Kafka after {max_retries} attempts: {e}")
                    # Don't raise - allow service to start without Kafka
                    return None
            except Exception as e:
                print(f"[Kafka Producer] Unexpected error connecting to Kafka: {e}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    print(f"[Kafka Producer] Will continue without Kafka producer")
                    return None
    return _producer

def publish_event(topic: str, payload: dict):
    """Publish event to Kafka topic with error handling"""
    try:
        producer = get_producer()
        if producer is None:
            print(f"[Kafka Producer] Cannot publish - Kafka producer not available")
            return False
        
        future = producer.send(topic, payload)
        future.get(timeout=10)  
        producer.flush()
        print(f"[Kafka Producer] Successfully published to {topic}: {payload}")
        return True
    except KafkaError as e:
        print(f"[Kafka Producer] Failed to publish to {topic}: {e}")
        return False
    except Exception as e:
        print(f"[Kafka Producer] Unexpected error publishing to {topic}: {e}")
        return False
