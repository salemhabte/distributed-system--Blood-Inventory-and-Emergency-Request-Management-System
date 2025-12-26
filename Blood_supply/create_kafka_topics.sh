#!/bin/bash
# Script to create Kafka topics manually if needed

echo "Creating Kafka topics..."

# Create low_blood_alert topic
docker-compose exec -T kafka kafka-topics.sh \
  --create \
  --bootstrap-server localhost:29092 \
  --topic low_blood_alert \
  --partitions 1 \
  --replication-factor 1 \
  --if-not-exists

# Create blood-requests topic
docker-compose exec -T kafka kafka-topics.sh \
  --create \
  --bootstrap-server localhost:29092 \
  --topic blood-requests \
  --partitions 1 \
  --replication-factor 1 \
  --if-not-exists

# Create blood-request-validation topic
docker-compose exec -T kafka kafka-topics.sh \
  --create \
  --bootstrap-server localhost:29092 \
  --topic blood-request-validation \
  --partitions 1 \
  --replication-factor 1 \
  --if-not-exists

# List all topics
echo "Listing all topics:"
docker-compose exec -T kafka kafka-topics.sh \
  --list \
  --bootstrap-server localhost:29092

echo "Done!"

