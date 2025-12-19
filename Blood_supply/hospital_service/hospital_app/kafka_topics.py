"""
Kafka topic definitions for Hospital Service
Centralized topic names used by producers and consumers
"""

# ==============================
# Hospital Service Topics
# ==============================

# Emitted when a new patient is registered
HOSPITAL_PATIENT_CREATED = "hospital.patient.created"

# Emitted when a hospital creates a blood request
HOSPITAL_BLOOD_REQUESTED = "hospital.blood.requested"

# Emitted when hospital inventory is updated
HOSPITAL_INVENTORY_UPDATED = "hospital.inventory.updated"


# ==============================
# Optional: Topic Metadata
# ==============================

TOPIC_METADATA = {
    HOSPITAL_PATIENT_CREATED: {
        "description": "Event emitted when a new patient is created",
        "producer": "hospital-service",
        "consumers": ["notification-service"]
    },
    HOSPITAL_BLOOD_REQUESTED: {
        "description": "Event emitted when a hospital requests blood units",
        "producer": "hospital-service",
        "consumers": ["bloodbank-service", "notification-service"]
    },
    HOSPITAL_INVENTORY_UPDATED: {
        "description": "Event emitted when hospital inventory is updated",
        "producer": "hospital-service",
        "consumers": ["notification-service"]
    }
}
