# distributed-system--Blood-Inventory-and-Emergency-Request-Management-System
## Overview
This project is a distributed system designed to manage blood supply and emergency requests
between hospitals, blood banks, and notification services.

## Architecture
The system follows a microservices architecture where each service is deployed independently.

### Services
- Hospital Service
- Blood Bank Service
- Notification Service

## Communication Model
The system uses two communication styles:

### Synchronous Communication
- Implemented using REST APIs
- Used for direct request/response operations

### Asynchronous Communication
- Implemented using Apache Kafka (Publish/Subscribe)
- Used for event-driven communication between services

## Event Flow
1. Hospital Service publishes a blood request event.
2. Kafka brokers distribute the event.
3. Blood Bank Service consumes and processes the request.
4. Notification Service consumes the event and sends notifications.

## Technologies Used
- Django
- Docker
- Apache Kafka
- Zookeeper
- KafkaDrop
- Swagger (OpenAPI)
