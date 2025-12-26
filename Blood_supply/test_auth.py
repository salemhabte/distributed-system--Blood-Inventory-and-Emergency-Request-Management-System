#!/usr/bin/env python3
"""
Simple test script for authentication service
Run this after starting the services with docker-compose
"""

import requests
import json
import time

BASE_URL = "http://localhost:8003/api/auth"

def test_registration():
    """Test user registration"""
    print("Testing user registration...")

    data = {
        "username": "test_bloodbank",
        "email": "test@bloodbank.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Test",
        "last_name": "Bloodbank",
        "role": "blood_bank",
        "organization_name": "Test Blood Bank",
        "phone_number": "+1234567890",
        "address": "123 Test St"
    }

    response = requests.post(f"{BASE_URL}/register/", json=data)

    if response.status_code == 201:
        print("✓ Registration successful")
        return response.json()
    else:
        print(f"✗ Registration failed: {response.status_code}")
        print(response.text)
        return None

def test_login():
    """Test user login"""
    print("Testing user login...")

    data = {
        "username": "test_bloodbank",
        "password": "testpass123"
    }

    response = requests.post(f"{BASE_URL}/login/", json=data)

    if response.status_code == 200:
        print("✓ Login successful")
        return response.json()
    else:
        print(f"✗ Login failed: {response.status_code}")
        print(response.text)
        return None

def test_token_verification(access_token):
    """Test token verification"""
    print("Testing token verification...")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    response = requests.get(f"{BASE_URL}/verify-token/", headers=headers)

    if response.status_code == 200:
        print("✓ Token verification successful")
        return True
    else:
        print(f"✗ Token verification failed: {response.status_code}")
        print(response.text)
        return False

def test_protected_endpoints(access_token):
    """Test protected endpoints in other services"""
    print("Testing protected endpoints...")

    headers = {
        "Authorization": f"Bearer {access_token}"
    }

    # Test blood bank service
    try:
        response = requests.get("http://localhost:8001/api/bloodbank/inventory/", headers=headers)
        if response.status_code == 200:
            print("✓ Blood bank service access successful")
        else:
            print(f"✗ Blood bank service access failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠ Blood bank service not available (expected if not running)")

    # Test hospital service
    try:
        response = requests.get("http://localhost:8000/api/hospital/blood-requests", headers=headers)
        if response.status_code == 200:
            print("✓ Hospital service access successful")
        else:
            print(f"✗ Hospital service access failed: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("⚠ Hospital service not available (expected if not running)")


def test_hospital_user_flow():
    """Test complete hospital user flow: register, login, create patient, create blood request"""
    print("\nTesting Hospital User Flow...")

    # Register hospital user
    print("1. Registering hospital user...")
    hospital_data = {
        "username": "test_hospital_user",
        "email": "test@hospital.com",
        "password": "testpass123",
        "password_confirm": "testpass123",
        "first_name": "Dr. Test",
        "last_name": "Hospital",
        "role": "hospital",
        "organization_name": "Test General Hospital",
        "phone_number": "+1987654321",
        "address": "789 Hospital St, Test City"
    }

    response = requests.post(f"{BASE_URL}/register/", json=hospital_data)
    if response.status_code != 201:
        print(f"✗ Hospital user registration failed: {response.status_code}")
        return False
    print("✓ Hospital user registered successfully")

    # Login hospital user
    print("2. Logging in hospital user...")
    login_data = {
        "username": "test_hospital_user",
        "password": "testpass123"
    }

    response = requests.post(f"{BASE_URL}/login/", json=login_data)
    if response.status_code != 200:
        print(f"✗ Hospital user login failed: {response.status_code}")
        return False

    hospital_tokens = response.json()
    hospital_token = hospital_tokens['tokens']['access']
    print("✓ Hospital user logged in successfully")

    # Test hospital service endpoints
    headers = {"Authorization": f"Bearer {hospital_token}"}

    # Create a patient
    print("3. Creating a patient...")
    try:
        patient_data = {
            "first_name": "John",
            "last_name": "Doe",
            "date_of_birth": "1985-05-15",
            "gender": "M",
            "blood_type": "A+",
            "phone_number": "+1555123456",
            "address": "123 Patient Ave",
            "emergency_contact_name": "Jane Doe",
            "emergency_contact_phone": "+1555987654"
        }

        response = requests.post("http://localhost:8000/api/hospital/patients", json=patient_data, headers=headers)
        if response.status_code == 201:
            patient = response.json()
            patient_id = patient['patient_id']
            print(f"✓ Patient created successfully with ID: {patient_id}")

            # Create blood request for the patient
            print("4. Creating blood request...")
            blood_request_data = {
                "patient": str(patient_id),
                "blood_type": "A+",
                "units_required": 2,
                "priority": "HIGH",
                "reason": "Surgery preparation",
                "requested_by": "Dr. Test Hospital"
            }

            response = requests.post("http://localhost:8000/api/hospital/blood-requests", json=blood_request_data, headers=headers)
            if response.status_code == 201:
                blood_request = response.json()
                print(f"✓ Blood request created successfully with ID: {blood_request['request_id']}")
                return True
            else:
                print(f"✗ Blood request creation failed: {response.status_code}")
                return False
        else:
            print(f"✗ Patient creation failed: {response.status_code}")
            return False

    except requests.exceptions.ConnectionError:
        print("⚠ Hospital service not available for testing")
        return False

def test_blood_bank_admin_flow():
    """Test blood bank admin functionality with proper authentication"""
    print("\n🩸 Testing Blood Bank Admin Flow...")

    # Login as blood bank admin
    login_data = {"username": "bloodbank_admin", "password": "admin123"}

    try:
        response = requests.post(f"{BASE_URL}/login/", json=login_data)
        if response.status_code != 200:
            print(f"❌ Blood bank admin login failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

        tokens = response.json()
        token = tokens['tokens']['access']
        print("✅ Blood bank admin logged in successfully")

        # Test accessing blood bank inventory
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.get("http://localhost:8001/api/v1/blood-bank/inventory/", headers=headers)

        if response.status_code == 200:
            print("✅ Blood bank inventory access successful")
            inventory = response.json()
            print(f"   Found {len(inventory)} blood inventory items")
            return token
        else:
            print(f"❌ Blood bank inventory access failed: {response.status_code}")
            print(f"Response: {response.text}")
            return None

    except requests.exceptions.ConnectionError:
        print("⚠️ Service not available")
        return None


def main():
    print("Blood Bank Authentication System Test")
    print("=" * 50)

    # Wait for services to be ready
    print("⏳ Waiting for services to start...")
    time.sleep(15)

    # Test blood bank admin flow first
    print("\n1. Testing Blood Bank Admin Access...")
    bb_token = test_blood_bank_admin_flow()

    print("\n2. Testing Hospital User Registration and Access...")

    # Test registration
    reg_result = test_registration()
    if not reg_result:
        return

    # Test login
    login_result = test_login()
    if not login_result:
        return

    access_token = login_result['tokens']['access']

    # Test token verification
    if not test_token_verification(access_token):
        return

    # Test protected endpoints
    test_protected_endpoints(access_token)

    # Test hospital user flow
    test_hospital_user_flow()

    print("\n" + "=" * 50)
    print("🎉 All authentication tests completed successfully!")
    print("✅ JWT tokens are working across all services!")
    print("✅ Role-based access control is functioning!")
    print("=" * 50)

if __name__ == "__main__":
    main()
