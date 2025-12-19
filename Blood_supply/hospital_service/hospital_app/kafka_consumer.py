"""
Kafka Consumer for Hospital Service
Handles consuming events from Kafka topics
"""
import json
import os
import logging
from kafka import KafkaConsumer
from kafka.errors import KafkaError, NoBrokersAvailable

logger = logging.getLogger(__name__)

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")


def get_consumer(topics, group_id="hospital-service-group", auto_offset_reset="earliest"):
    """
    Create and return a Kafka consumer for given topics
    
    Args:
        topics (list): List of topic names to subscribe to
        group_id (str): Consumer group ID
        auto_offset_reset (str): Where to start reading if no offset exists
    
    Returns:
        KafkaConsumer: Configured consumer instance or None if failed
    """
    try:
        consumer = KafkaConsumer(
            *topics,
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS.split(','),
            value_deserializer=lambda v: json.loads(v.decode('utf-8')) if v else None,
            key_deserializer=lambda k: k.decode('utf-8') if k else None,
            auto_offset_reset=auto_offset_reset,
            enable_auto_commit=True,
            auto_commit_interval_ms=1000,  # Commit every second
            group_id=group_id,
            consumer_timeout_ms=60000,  # Timeout after 60s of no messages
            max_poll_records=10,  # Process up to 10 messages at a time
            session_timeout_ms=30000,  # 30 seconds
            heartbeat_interval_ms=3000,  # 3 seconds
        )
        logger.info(f"[Kafka Consumer] ✅ Initialized consumer group: {group_id}")
        logger.info(f"[Kafka Consumer] 👂 Subscribed to topics: {', '.join(topics)}")
        return consumer
    except NoBrokersAvailable as e:
        logger.error(f"[Kafka Consumer] ❌ No brokers available: {e}")
        return None
    except Exception as e:
        logger.error(f"[Kafka Consumer] ❌ Failed to create consumer: {e}")
        return None


def close_consumer(consumer):
    """Safely close a Kafka consumer"""
    if consumer:
        try:
            consumer.close()
            logger.info("[Kafka Consumer] Consumer closed")
        except Exception as e:
            logger.error(f"[Kafka Consumer] Error closing consumer: {e}")
