import uuid
from datetime import datetime
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
from django.http import JsonResponse
from .models import Patient
from .serializers import (
    PatientSerializer, PatientCreateSerializer, PatientUpdateSerializer,
)
from .kafka_producer import send_event


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
        patient = Patient.objects.create(
            patient_id=patient_id,
            first_name=serializer.validated_data['first_name'],
            last_name=serializer.validated_data['last_name'],
            age=serializer.validated_data['age'],
            blood_type=serializer.validated_data['blood_type'],
            diagnosis=serializer.validated_data.get('diagnosis', '')
        )
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
 