from kafka import KafkaProducer
import json
from django.conf import settings

producer = KafkaProducer(
    bootstrap_servers=getattr(settings, 'KAFKA_BOOTSTRAP_SERVERS', ['localhost:9092']),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

def send_event(topic, value):
    producer.send(topic, value)
    producer.flush()
