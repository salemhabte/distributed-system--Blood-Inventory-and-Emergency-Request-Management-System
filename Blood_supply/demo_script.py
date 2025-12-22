#!/usr/bin/env python3
"""
Demo script showing how to use the Blood Bank Authentication System
"""

import requests
import json
import random

BASE_URL = "http://localhost:8003/api/auth"
BLOOD_BANK_URL = "http://localhost:8001/api/v1/blood-bank"
HOSPITAL_URL = "http://localhost:8000/api/v1/hospital"

def demo_blood_bank_admin():
    """Demonstrate blood bank admin functionality"""
    print("=" * 60)
    print("BLOOD BANK ADMIN DEMO")
    print("=" * 60)

    # Login with default admin account
    print("1. Logging in with default blood bank admin...")
    login_data = {
        "username": "bloodbank_admin",
        "password": "admin123"
    }

    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return None

    tokens = response.json()
    token = tokens['tokens']['access']
    print("✅ Blood bank admin logged in successfully")

    headers = {"Authorization": f"Bearer {token}"}

    # Check inventory
    print("\n2. Checking blood inventory...")
    try:
        response = requests.get(f"{BLOOD_BANK_URL}/inventory/", headers=headers)
        if response.status_code == 200:
            inventory = response.json()
            print(f"✅ Found {len(inventory)} blood types in inventory")
            for item in inventory[:3]:  # Show first 3
                print(f"   - {item['blood_type']}: {item['quantity']} units")
        else:
            print(f"❌ Failed to get inventory: {response.status_code}")

        unique_suffix = random.randint(1000, 9999)
        # Add blood batch (blood bank admin only)
        print("\n3. Adding blood batch (Blood Bank Admin only)...")
        batch_data = {
            "blood_type": "A+",
            "quantity": 10,
            "donation_date": "2025-12-20",
            "expiry_date": "2026-12-20",
            "batch_number": f"BB20251220A{unique_suffix}",
            "storage_location": "Refrigerator A1"
        }

        response = requests.post(f"{BLOOD_BANK_URL}/inventory/", json=batch_data, headers=headers)
        if response.status_code == 201:
            print("✅ Blood batch added successfully")
        else:
            print(f"❌ Failed to add batch: {response.status_code}")
            print(f"   Reason: {response.text}")

    except requests.exceptions.ConnectionError:
        print("⚠️ Blood bank service not available")

    return token

def demo_hospital_user():
    """Demonstrate hospital user functionality"""
    print("\n" + "=" * 60)
    print("HOSPITAL USER DEMO")
    print("=" * 60)

    # Register hospital user
    # Register hospital user
    print("1. Registering hospital user...")
    suffix = random.randint(1000, 9999)
    hospital_username = f"demo_hospital_{suffix}"
    reg_data = {
        "username": hospital_username,
        "email": f"demo{suffix}@hospital.com",
        "password": "demopass123",
        "password_confirm": "demopass123",
        "first_name": "Dr. Demo",
        "last_name": "Hospital",
        "role": "hospital",
        "organization_name": "Demo General Hospital",
        "phone_number": "+1555111111",
        "address": "123 Demo Hospital St"
    }

    response = requests.post(f"{BASE_URL}/register/", json=reg_data)
    if response.status_code != 201:
        print(f"❌ Registration failed: {response.status_code}")
        print(response.text)
        return None

    print("✅ Hospital user registered successfully")

    # Login
    print("\n2. Logging in hospital user...")
    login_data = {
        "username": hospital_username,
        "password": "demopass123"
    }

    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    if response.status_code != 200:
        print(f"❌ Login failed: {response.status_code}")
        return None

    tokens = response.json()
    token = tokens['tokens']['access']
    print(token)
    print("✅ Hospital user logged in successfully")
     
    headers = {"Authorization": f"Bearer {token}"}

    # Create patient
    print("\n3. Creating a patient...")
    try:
        patient_data = {
            "first_name": "Alice",
            "last_name": "Johnson",
            "date_of_birth": "1990-03-15",
            "gender": "F",
            "blood_type": "A+",
            "age": 33,  # Added required field
            "phone_number": "+1555222222",
            "address": "456 Patient St",
            "emergency_contact_name": "Bob Johnson",
            "emergency_contact_phone": "+1555333333"
        }

        response = requests.post(f"{HOSPITAL_URL}/patients", json=patient_data, headers=headers)
        if response.status_code == 201:
            patient = response.json()
            patient_id = patient['patient_id']
            print(f"✅ Patient created with ID: {patient_id}")

            # Create blood request
            print("\n4. Creating blood request...")
            request_data = {
                "patient": str(patient_id),
                "blood_type": "A+",
                "units_required": 3,
                "priority": "URGENT",
                "notes": "Scheduled surgery"
            }

            response = requests.post(f"{HOSPITAL_URL}/blood-requests", json=request_data, headers=headers)
            if response.status_code == 201:
                blood_request = response.json()
                print(f"✅ Blood request created with ID: {blood_request['request_id']}")
                print(f"   Status: {blood_request['status']}")
                print(f"   Blood Type: {blood_request['blood_type']}")
                print(f"   Units Required: {blood_request['units_required']}")
            else:
                print(f"❌ Failed to create blood request: {response.status_code}")
                print(f"   Reason: {response.text}")

            # View all blood requests
            print("\n5. Viewing all blood requests...")
            response = requests.get(f"{HOSPITAL_URL}/blood-requests", headers=headers)
            if response.status_code == 200:
                requests_list = response.json()
                print(f"✅ Found {len(requests_list)} blood requests")
            else:
                print(f"❌ Failed to get requests: {response.status_code}")

        else:
            print(f"❌ Failed to create patient: {response.status_code}")
            print(f"   Reason: {response.text}")

    except requests.exceptions.ConnectionError:
        print("⚠️ Hospital service not available")

    return token

def main():
    print("🏥 Blood Bank Authentication System Demo")
    print("This demo shows both Blood Bank Admin and Hospital User workflows\n")

    # Wait for services
    import time
    print("⏳ Waiting for services to start...")
    time.sleep(15)

    # Demo blood bank admin
    bb_token = demo_blood_bank_admin()

    # Demo hospital user
    hospital_token = demo_hospital_user()

    print("\n" + "=" * 60)
    print("DEMO COMPLETED!")
    print("=" * 60)
    print("Summary:")
    print("✅ Blood Bank Admin: Can manage inventory and process requests")
    print("✅ Hospital Users: Can register, create patients, and request blood")
    print("\nNext steps:")
    print("- Use the web interface at http://localhost:8003/admin/ (login: bloodbank_admin/admin123)")
    print("- Test the APIs with the provided tokens")
    print("- Monitor Kafka messages for real-time updates")

if __name__ == "__main__":
    main()
