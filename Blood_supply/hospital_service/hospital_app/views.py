import uuid
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse
from .models import Patient, BloodRequest, HospitalInventory
from .serializers import (
    PatientSerializer, PatientCreateSerializer, PatientUpdateSerializer,
    BloodRequestSerializer, BloodRequestCreateSerializer,
    InventoryItemSerializer, HospitalInventoryUpdateSerializer
)
from .kafka_producer import send_event
from .kafka_events import create_blood_requested_event, create_patient_created_event, create_inventory_updated_event
from .kafka_topics import (
        HOSPITAL_BLOOD_REQUESTED,
        HOSPITAL_INVENTORY_UPDATED,
        HOSPITAL_PATIENT_CREATED
    )
import os


def create_error_response(error_message, status_code, path):
    """Helper function to create error response matching YAML spec"""
    return JsonResponse({
        'timestamp': timezone.now().isoformat(),
        'status': status_code,
        'error': error_message,
        'message': error_message,
        'path': path
    }, status=status_code)


# ==================== Patient Endpoints ====================

@api_view(['POST'])
def create_patient(request):
    """Create a new patient"""
    serializer = PatientCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        patient_id = str(uuid.uuid4())
        timestamp = datetime.utcnow().isoformat()
        
        patient = Patient.objects.create(
            patient_id=patient_id,
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            age=serializer.validated_data['age'],
            blood_type=serializer.validated_data['blood_type'],
            diagnosis=serializer.validated_data.get('diagnosis', '')
        )
        
        # Publish patient created event to Kafka
        event_data = create_patient_created_event(
            patient_id=patient_id,
            first_name=patient.first_name,
            last_name=patient.last_name,
            age=patient.age,
            blood_type=patient.blood_type,
            timestamp=timestamp
        )
        send_event(HOSPITAL_PATIENT_CREATED, event_data, key=patient_id)
        
        response_serializer = PatientSerializer(patient)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    return create_error_response(
        "Validation error: " + str(serializer.errors),
        status.HTTP_400_BAD_REQUEST,
        request.path
    )




@api_view(['GET', 'PUT'])
def update_patient(request, patientId):
    """Get patient (GET) or Update patient (PUT) by ID"""
    try:
        patient = Patient.objects.get(patient_id=patientId)
    except Patient.DoesNotExist:
        return create_error_response(
            "Patient not found",
            status.HTTP_404_NOT_FOUND,
            request.path
        )
    
    if request.method == 'GET':
        serializer = PatientSerializer(patient)
        return Response(serializer.data)
    
    # PUT: Update patient
    serializer = PatientUpdateSerializer(data=request.data, partial=True)
    if serializer.is_valid():
        for key, value in serializer.validated_data.items():
            setattr(patient, key, value)
        patient.save()
        
        response_serializer = PatientSerializer(patient)
        return Response(response_serializer.data)
    
    return create_error_response(
        "Validation error: " + str(serializer.errors),
        status.HTTP_400_BAD_REQUEST,
        request.path
    )


# ==================== Blood Request Endpoints ====================

@api_view(['GET', 'POST'])
def create_blood_request(request):
    """Create a new blood request (POST) or list all blood requests (GET)"""
    if request.method == 'GET':
        # List all blood requests
        requests = BloodRequest.objects.all()
        serializer = BloodRequestSerializer(requests, many=True)
        return Response(serializer.data)
    
    # POST: Create a new blood request
    serializer = BloodRequestCreateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return create_error_response(
            "Validation error: " + str(serializer.errors),
            status.HTTP_400_BAD_REQUEST,
            request.path
        )
    
    patient_id = serializer.validated_data['patientId']
    try:
        patient = Patient.objects.get(patient_id=patient_id)
    except Patient.DoesNotExist:
        return create_error_response(
            "Patient not found",
            status.HTTP_400_BAD_REQUEST,
            request.path
        )
    
    request_id = str(uuid.uuid4())
    timestamp = datetime.utcnow().isoformat()
    
    blood_request = BloodRequest.objects.create(
        request_id=request_id,
        patient=patient,
        blood_type=serializer.validated_data['bloodType'],
        units_required=serializer.validated_data['unitsRequired'],
        priority=serializer.validated_data['priority'],
        notes=serializer.validated_data.get('notes', ''),
        status='PENDING'
    )
    
    # Get hospital ID from settings or use default
    hospital_id = os.getenv("HOSPITAL_ID", "hospital-1")
    
    # Publish blood request event to Kafka
    event_data = create_blood_requested_event(
        request_id=request_id,
        hospital_id=hospital_id,
        patient_id=patient.patient_id,
        blood_type=blood_request.blood_type,
        quantity=blood_request.units_required,
        priority=blood_request.priority,
        notes=blood_request.notes,
        timestamp=timestamp
    )
    send_event(HOSPITAL_BLOOD_REQUESTED, event_data, key=request_id)
    
    response_serializer = BloodRequestSerializer(blood_request)
    return Response(response_serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def get_blood_request(request, requestId):
    """Get blood request by ID"""
    try:
        blood_request = BloodRequest.objects.get(request_id=requestId)
        serializer = BloodRequestSerializer(blood_request)
        return Response(serializer.data)
    except BloodRequest.DoesNotExist:
        return create_error_response(
            "Request not found",
            status.HTTP_404_NOT_FOUND,
            request.path
        )


# ==================== Hospital Inventory Endpoints ====================

@api_view(['GET'])
def get_hospital_inventory(request):
    """Get local hospital inventory"""
    inventory = HospitalInventory.objects.all()
    serializer = InventoryItemSerializer(inventory, many=True)
    return Response(serializer.data)


@api_view(['PUT'])
def update_hospital_inventory(request):
    """Update hospital inventory after receiving units"""
    serializer = HospitalInventoryUpdateSerializer(data=request.data)
    
    if not serializer.is_valid():
        return create_error_response(
            "Validation error: " + str(serializer.errors),
            status.HTTP_400_BAD_REQUEST,
            request.path
        )
    
    blood_type = serializer.validated_data['bloodType']
    units_received = serializer.validated_data['unitsReceived']
    timestamp = datetime.utcnow().isoformat()
    
    # Get or create inventory item
    inventory, created = HospitalInventory.objects.get_or_create(
        blood_type=blood_type,
        batch_number='',  # Default batch number
        defaults={'quantity': units_received}
    )
    
    if not created:
        inventory.quantity += units_received
        inventory.save()
    
    # Publish inventory updated event to Kafka
    event_data = create_inventory_updated_event(
        blood_type=blood_type,
        quantity=inventory.quantity,
        units_received=units_received,
        timestamp=timestamp
    )
    send_event(HOSPITAL_INVENTORY_UPDATED, event_data, key=blood_type)
    
    return Response({
        'message': 'Inventory updated successfully'
    })
