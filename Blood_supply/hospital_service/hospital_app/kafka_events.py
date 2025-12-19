"""
Kafka event topic constants and event schemas for Hospital Service
"""

# Event topics published by Hospital Service
HOSPITAL_BLOOD_REQUESTED = "hospital.blood.requested"
HOSPITAL_INVENTORY_UPDATED = "hospital.inventory.updated"
HOSPITAL_PATIENT_CREATED = "hospital.patient.created"

# Event topics consumed by Hospital Service
BLOODBANK_BLOOD_APPROVED = "bloodbank.blood.approved"
BLOODBANK_BLOOD_REJECTED = "bloodbank.blood.rejected"
BLOODBANK_INVENTORY_UPDATED = "bloodbank.inventory.updated"
INVENTORY_LOWSTOCK = "inventory.lowstock"

# Event payload schemas
def create_blood_requested_event(request_id, hospital_id, patient_id, blood_type, quantity, priority, notes, timestamp):
    """Create event payload for hospital.blood.requested"""
    return {
        "request_id": request_id,
        "hospital_id": hospital_id,
        "patient_id": patient_id,
        "blood_type": blood_type,
        "quantity": quantity,
        "units_required": quantity,  # Alias for compatibility
        "priority": priority,
        "notes": notes,
        "timestamp": timestamp
    }

def create_inventory_updated_event(blood_type, quantity, units_received, timestamp):
    """Create event payload for hospital.inventory.updated"""
    return {
        "blood_type": blood_type,
        "quantity": quantity,
        "units_received": units_received,
        "timestamp": timestamp
    }

def create_patient_created_event(patient_id, first_name, last_name, age, blood_type, timestamp):
    """Create event payload for hospital.patient.created"""
    return {
        "patient_id": patient_id,
        "first_name": first_name,
        "last_name": last_name,
        "age": age,
        "blood_type": blood_type,
        "timestamp": timestamp
    }
