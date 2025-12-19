"""
Kafka Producer for Hospital Service
Handles publishing events to Kafka topics
"""
from kafka import KafkaProducer
from kafka.errors import NoBrokersAvailable, KafkaTimeoutError, KafkaError
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv(
    "KAFKA_BOOTSTRAP_SERVERS", "localhost:9092"
)

_producer = None


def get_producer():
    """Get or create a singleton Kafka producer instance"""
    global _producer
    if _producer is None:
        try:
            _producer = KafkaProducer(
                bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                retries=5,
                acks="all",  # Wait for all replicas to acknowledge
                linger_ms=5,  # Wait up to 5ms to batch messages
                compression_type='gzip',  # Compress messages
                max_in_flight_requests_per_connection=1,  # Ensure ordering
                request_timeout_ms=30000,  # 30 seconds timeout
            )
            logger.info(f"[Kafka Producer] Initialized with servers: {KAFKA_BOOTSTRAP_SERVERS}")
        except NoBrokersAvailable as e:
            logger.error(f"[Kafka Producer] No brokers available: {e}")
            _producer = None
        except Exception as e:
            logger.error(f"[Kafka Producer] Failed to initialize: {e}")
            _producer = None
    return _producer


def send_event(topic, value, key=None):
    """
    Send an event to a Kafka topic
    
    Args:
        topic (str): Kafka topic name
        value (dict): Event payload dictionary
        key (str, optional): Message key for partitioning
    
    Returns:
        bool: True if sent successfully, False otherwise
    """
    producer = get_producer()
    if not producer:
        logger.warning(f"[Kafka Producer] Producer unavailable. Skipping event: {topic}")
        return False

    try:
        # Add timestamp if not present
        if 'timestamp' not in value:
            value['timestamp'] = datetime.utcnow().isoformat()
        
        # Send message
        future = producer.send(topic, value=value, key=key.encode('utf-8') if key else None)
        
        # Wait for acknowledgment (blocks until message is sent)
        record_metadata = future.get(timeout=10.0)
        
        logger.info(
            f"[Kafka Producer] ✅ Event published to topic: {topic}, "
            f"partition: {record_metadata.partition}, "
            f"offset: {record_metadata.offset}"
        )
        
        return True
        
    except KafkaTimeoutError as e:
        logger.error(f"[Kafka Producer] ❌ Timeout sending event to {topic}: {e}")
        return False
    except KafkaError as e:
        logger.error(f"[Kafka Producer] ❌ Kafka error sending event to {topic}: {e}")
        return False
    except Exception as e:
        logger.error(f"[Kafka Producer] ❌ Unexpected error sending event to {topic}: {e}")
        return False


def flush_producer():
    """Flush all pending messages in the producer"""
    producer = get_producer()
    if producer:
        try:
            producer.flush(timeout=10.0)
            logger.debug("[Kafka Producer] Flushed pending messages")
        except Exception as e:
            logger.error(f"[Kafka Producer] Error flushing: {e}")


def close_producer():
    """Close the producer connection"""
    global _producer
    if _producer:
        try:
            _producer.close()
            logger.info("[Kafka Producer] Producer closed")
        except Exception as e:
            logger.error(f"[Kafka Producer] Error closing producer: {e}")
        finally:
            _producer = None
