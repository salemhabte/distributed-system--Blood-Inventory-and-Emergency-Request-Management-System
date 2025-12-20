# bloodbank/kafka_producer.py
import os
import json
import time
from kafka import KafkaProducer
from kafka.errors import KafkaError

bootstrap_servers = os.getenv('KAFKA_BOOTSTRAP_SERVERS', 'kafka:29092')

producer = KafkaProducer(
    bootstrap_servers=bootstrap_servers,
    value_serializer=lambda v: json.dumps(v).encode('utf-8'),
    retries=5,
    acks='all'
)

def publish_event(topic: str, payload: dict, max_retries: int = 3, retry_delay_seconds: int = 2):
    for attempt in range(max_retries):
        try:
            future = producer.send(topic, payload)
            record_metadata = future.get(timeout=10)  # Wait for ack
            producer.flush()
            print(f"[Kafka Producer] Successfully published to {topic} on attempt {attempt + 1}: {payload}")
            print(f"  Partition: {record_metadata.partition}, Offset: {record_metadata.offset}")
            return # Exit on success
        except KafkaError as e:
            print(f"[Kafka Producer] Attempt {attempt + 1} failed for {topic}: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print(f"[Kafka Producer] All {max_retries} attempts failed for {topic}.")
        except Exception as e:
            print(f"[Kafka Producer] Unexpected error on attempt {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                print(f"  Retrying in {retry_delay_seconds} seconds...")
                time.sleep(retry_delay_seconds)
            else:
                print(f"[Kafka Producer] All {max_retries} attempts failed for {topic} due to unexpected error.")