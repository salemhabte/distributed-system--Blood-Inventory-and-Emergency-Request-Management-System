from kafka import KafkaProducer
import json


producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'], 
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

# Example message
message = {
    "request_id": "REQ123",
    "hospital_name": "math",
    "blood_type": "A+",
    "quantity": 5
}

# Send message to 'hospital_requests' topic
producer.send('hospital_requests', message)
producer.flush()

print("Message sent!")
